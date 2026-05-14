from __future__ import annotations

import asyncio
import math
import re
from collections import defaultdict
from typing import Iterable
from urllib.parse import urlsplit

from diligence.adapters import ADAPTERS
from diligence.collect import DEFAULT_SOURCES
from diligence.http import async_client
from diligence.models import QueryPlan, SearchCandidate, SearchItem, SearchResult, SourceName, SourceResult
from diligence.normalize import canonical_url, compact_text, lexical_score
from diligence.query_intent import QueryIntent, SearchMode, apply_mode_override, classify_query_intent

STOPWORDS = {
    "a",
    "already",
    "an",
    "and",
    "are",
    "build",
    "can",
    "complete",
    "exists",
    "exist",
    "find",
    "for",
    "from",
    "help",
    "idea",
    "just",
    "like",
    "our",
    "project",
    "projects",
    "searching",
    "ship",
    "software",
    "startup",
    "that",
    "the",
    "there",
    "these",
    "this",
    "tool",
    "tools",
    "usable",
    "use",
    "useable",
    "using",
    "where",
    "with",
}

PHRASE_HINTS = (
    "agent framework",
    "agent marketplace",
    "agent platform",
    "api client",
    "bounty marketplace",
    "developer tools",
    "existence check",
    "idea validation",
    "meta engine",
    "meta search",
    "prior art",
    "search aggregation",
    "search aggregator",
    "software bounty",
    "software catalog",
    "software discovery",
    "startup research",
    "tool discovery",
    "unified search",
)

RESEARCH_PHRASES = ("research paper", "research papers", "academic paper", "benchmark paper")
PACKAGE_LIKE_RE = re.compile(r"^[A-Za-z0-9@][A-Za-z0-9._/@-]{0,63}$")
MODE_VALUES: tuple[SearchMode, ...] = ("auto", "idea-market", "technical-reuse", "market-discovery", "research-discovery")
QUERY_EXPANSIONS = {
    "software discovery": ["metasearch", "tool discovery", "open source discovery", "prior art", "idea validation"],
    "meta search": ["metasearch", "search aggregation", "federated search"],
    "meta engine": ["metasearch", "search aggregation", "unified search", "tool discovery", "prior art"],
    "prior art": ["existence check", "novelty search", "idea validation"],
    "search aggregation": ["metasearch", "federated search", "unified search"],
    "tool discovery": ["metasearch", "software discovery", "developer tools"],
}
TECHNICAL_ROUTE_TERMS = ("cli", "framework", "mcp", "open source", "package", "plugin", "sdk", "skill")
MODEL_ROUTE_TERMS = ("dataset", "hugging face", "llm", "model")
FIT_LABEL_TERMS = {
    "agent_platform": ("ai agent", "agent platform", "agentic", "autonomous agent", "multi-agent"),
    "idea_validation": ("idea validation", "lean canvas", "landing page", "validation score", "validate your idea"),
    "marketplace": ("agent for hire", "auction", "bounty", "freelancer", "gig", "hire", "marketplace", "rental"),
    "mcp": ("mcp", "model context protocol"),
    "open_source": ("github", "open source", "self-hosted"),
    "prior_art": ("existence check", "novelty", "novelty report", "patent", "prior art"),
    "startup_discovery": ("startup discovery", "startup exploration", "startup ideas", "startup research"),
    "tool_discovery": ("developer tools", "open source discovery", "software catalog", "software discovery", "tool discovery"),
}
POSITIVE_DISCOVERY_TERMS = (
    "catalog",
    "developer",
    "discovery",
    "federated",
    "idea",
    "index",
    "marketplace",
    "meta",
    "metasearch",
    "platform",
    "prior",
    "search",
    "software",
    "startup",
    "tool",
    "unified",
    "validation",
)
NEGATIVE_DISCOVERY_TERMS = (
    "attack surface",
    "dns",
    "eureka",
    "failover",
    "load balancing",
    "microcontrollers",
    "registry",
    "resilient",
    "service discovery",
    "spring cloud",
    "subdomain",
)
DOMAIN_NEGATIVE_TERMS = (
    "asset discovery",
    "bug bounty",
    "causal",
    "cloudflare",
    "content discovery",
    "cybersecurity",
    "deep prior",
    "directory busting",
    "dns",
    "ethereum",
    "microservice",
    "network device",
    "osint",
    "passive url",
    "pentest",
    "pentesting",
    "port monitoring",
    "prior learning",
    "proteomics",
    "rpc",
    "security",
    "service management",
    "service discovery",
    "subdomain",
    "transfer learning",
    "troubleshooting",
    "vulnerability",
    "web content discovery",
)
REFERENCE_BENCHMARK_ALIASES = (
    "duolingo/metasearch",
    "hubgrep",
    "idea reality",
    "idea-reality-mcp",
    "open source discovery hub",
    "priorart",
    "swirl-search",
    "tool compass",
)
SEED_METADATA = {
    "repo_posts search": ("repo_catalog", "medium"),
    "There's An AI For That search": ("ai_tool_directory", "high"),
    "Futurepedia search": ("ai_tool_directory", "medium"),
    "IdeaSearch search": ("idea_directory", "high"),
    "Product Hunt search": ("launch_directory", "high"),
    "Hacker News Search": ("discussion_directory", "high"),
}
SOURCE_WEIGHTS = {
    "github": 1.0,
    "repo_posts": 0.9,
    "ecosystems": 0.8,
    "npm": 0.75,
    "pypi": 0.75,
    "hn": 0.55,
    "huggingface": 0.6,
    "openalex": 0.45,
    "arxiv": 0.45,
}


def build_query_plan(query: str, *, depth: str = "quick", mode: SearchMode = "auto") -> QueryPlan:
    _validate_mode(mode)
    intent = apply_mode_override(classify_query_intent(query), mode)
    normalized = _normalize_query(query)
    facets = _build_facets(query, normalized, intent)
    query_clusters = _build_query_clusters(query, normalized, facets, intent)
    enabled_sources, suppressed_sources = _route_sources(query, depth, intent, query_clusters)
    source_queries = _build_source_queries(query, intent, facets, enabled_sources, query_clusters)
    filtered_enabled = [source for source in enabled_sources if source_queries.get(source)]
    filtered_suppressed = sorted(set(suppressed_sources + [source for source in enabled_sources if not source_queries.get(source)]))
    return QueryPlan(
        query=query,
        depth=depth,  # type: ignore[arg-type]
        intent=intent.intent,
        facets=facets,
        query_clusters=query_clusters,
        enabled_sources=filtered_enabled,
        suppressed_sources=filtered_suppressed,
        source_queries=source_queries,
        context7_attempted=False,
        context7_status=_context7_status(intent),
    )


async def search_projects(query: str, *, depth: str = "quick", limit: int = 5, mode: SearchMode = "auto") -> SearchResult:
    plan = build_query_plan(query, depth=depth, mode=mode)
    source_results = await _run_plan(plan, limit=limit)
    warnings: list[str] = []
    candidate_inputs: list[SearchItem] = []
    exploration_urls: list[SearchItem] = []

    for result in source_results:
        warnings.extend(result.warnings)
        for item in result.items:
            if item.source == "directory_seeds":
                exploration_urls.append(_annotate_exploration_item(item, plan))
            else:
                candidate_inputs.append(item)

    candidates = _rank_and_group_candidates(query, plan, candidate_inputs, limit)
    return SearchResult(
        query=query,
        query_plan=plan,
        candidates=candidates,
        exploration_urls=exploration_urls,
        warnings=warnings,
    )


async def _run_plan(plan: QueryPlan, limit: int) -> list[SourceResult]:
    tasks: list[asyncio.Future[SourceResult] | asyncio.Task[SourceResult]] = []
    async with async_client() as client:
        for source_name in plan.enabled_sources:
            adapter_type = ADAPTERS[source_name]
            for source_query in plan.source_queries.get(source_name, []):
                tasks.append(asyncio.create_task(adapter_type().search(client, source_query, limit)))
        results = await asyncio.gather(*tasks, return_exceptions=True)

    source_results: list[SourceResult] = []
    for result in results:
        if isinstance(result, Exception):
            source_results.append(
                SourceResult(
                    source="directory_seeds",
                    query=plan.query,
                    warnings=[f"search plan execution failed: {type(result).__name__}: {result}"],
                )
            )
            continue
        source_results.append(result)
    return source_results


def _build_facets(query: str, normalized: str, intent: QueryIntent) -> dict[str, str]:
    detected_phrases = [phrase for phrase in PHRASE_HINTS if f" {phrase} " in f" {normalized} "]
    concise = _compact_query(normalized)
    functional = detected_phrases[0] if detected_phrases else concise
    technical_tokens = intent.matched_technical_phrases or intent.matched_technical_terms
    technical = " ".join(technical_tokens[:3]).strip() or functional
    market_tokens = intent.matched_market_terms or intent.matched_idea_market_terms
    market = " ".join(market_tokens[:3]).strip() or functional
    research = " ".join(intent.matched_research_terms[:3]).strip()
    if not research and any(phrase in normalized for phrase in RESEARCH_PHRASES):
        research = next(phrase for phrase in RESEARCH_PHRASES if phrase in normalized)

    return {
        "functional": functional,
        "technical": technical,
        "market": market,
        "research": research or concise,
    }


def _build_query_clusters(
    query: str,
    normalized: str,
    facets: dict[str, str],
    intent: QueryIntent,
) -> dict[str, list[str]]:
    if intent.intent == "idea_market_discovery":
        return _idea_market_query_clusters(query, normalized, facets, intent)
    if intent.intent == "technical_reuse":
        return _technical_reuse_query_clusters(query, normalized, facets, intent)

    general_queries = _general_candidate_queries(query, facets)
    package_queries = _package_candidate_queries(query, facets)
    research_queries = _dedupe_preserve_order([facets["research"], facets["functional"]])
    clusters = {"primary": general_queries[:4]}
    if package_queries:
        clusters["package"] = package_queries[:4]
    if intent.intent == "research_discovery":
        clusters["research"] = research_queries[:3]
    return {name: values for name, values in clusters.items() if values}


def _idea_market_query_clusters(
    query: str,
    normalized: str,
    facets: dict[str, str],
    intent: QueryIntent,
) -> dict[str, list[str]]:
    del query
    clusters: dict[str, list[str]] = {
        "problem_domain": [],
        "solution_form": [],
        "commercial_model": [],
        "startup_context": [],
    }

    if "agent" in normalized:
        clusters["problem_domain"].extend(["ai agent", "autonomous agent"])
        clusters["solution_form"].append("agent platform")
    if any(term in normalized for term in ("marketplace", "rent", "rental", "hire", "gig", "freelancer", "agency")):
        clusters["solution_form"].append("agent marketplace" if "agent" in normalized else "startup marketplace")
        clusters["commercial_model"].extend(["agent for hire", "freelancer marketplace", "service marketplace"])
    if any(term in normalized for term in ("bounty", "bid", "auction")):
        clusters["commercial_model"].extend(["software bounty marketplace", "project bounty platform", "auction marketplace"])
    if any(term in normalized for term in ("startup", "founder")):
        clusters["startup_context"].extend(["startup discovery", "startup research", "startup idea validation"])
    if any(term in normalized for term in ("idea", "validation", "validate")):
        clusters["startup_context"].extend(["idea validation", "product idea validation"])
    if "project" in normalized:
        clusters["startup_context"].append("project discovery")
    if any(term in normalized for term in ("prior", "novelty", "existence")):
        clusters["startup_context"].extend(["prior art", "existence check", "novelty search"])
    if any(term in normalized for term in TECHNICAL_ROUTE_TERMS):
        clusters.setdefault("technical_reuse", []).extend(["mcp server", "agent skill", "open source tool"])
    if any(term in normalized for term in ("tool", "tools", "open source", "project")):
        clusters["solution_form"].extend(["open source project", "software discovery tool"])

    fallback_domain = _compact_query(normalized, max_terms=3)
    if fallback_domain:
        clusters["problem_domain"].append(fallback_domain)
    clusters["solution_form"].append(facets["functional"])
    clusters["startup_context"].append(facets["market"])

    return {
        name: [candidate for candidate in _dedupe_preserve_order(values) if _source_query_is_valid(candidate)]
        for name, values in clusters.items()
        if any(_source_query_is_valid(candidate) for candidate in values)
    }


def _technical_reuse_query_clusters(
    query: str,
    normalized: str,
    facets: dict[str, str],
    intent: QueryIntent,
) -> dict[str, list[str]]:
    technical_queries = _technical_candidate_queries(query, normalized, facets, intent)
    package_queries = _dedupe_preserve_order(_package_candidate_queries(query, facets) + technical_queries[:2])
    return {
        "primary": technical_queries[:6],
        "package": package_queries[:4],
    }


def _route_sources(
    query: str,
    depth: str,
    intent: QueryIntent,
    query_clusters: dict[str, list[str]],
) -> tuple[list[SourceName], list[SourceName]]:
    enabled: list[SourceName] = ["repo_posts", "github", "hn", "directory_seeds"]
    suppressed: list[SourceName] = [source for source in DEFAULT_SOURCES if source not in enabled]
    normalized = _normalize_query(query)
    is_package_like = _is_package_like(query)
    wants_research = intent.intent == "research_discovery"
    has_technical_routing = bool(intent.matched_technical_terms or intent.matched_technical_phrases)
    has_model_signal = any(term in normalized for term in MODEL_ROUTE_TERMS)

    if is_package_like and "ecosystems" not in enabled:
        enabled.append("ecosystems")
        suppressed.remove("ecosystems")

    if depth == "deep":
        if intent.intent == "technical_reuse":
            for source in ("npm", "pypi", "ecosystems", "huggingface"):
                _enable_source(enabled, suppressed, source)
        elif intent.intent == "idea_market_discovery":
            if has_technical_routing or query_clusters.get("technical_reuse"):
                for source in ("npm", "pypi", "ecosystems"):
                    _enable_source(enabled, suppressed, source)
            if has_model_signal:
                _enable_source(enabled, suppressed, "huggingface")
        elif wants_research:
            for source in ("openalex", "arxiv", "huggingface"):
                _enable_source(enabled, suppressed, source)

    if wants_research:
        for source in ("openalex", "arxiv"):
            _enable_source(enabled, suppressed, source)

    if intent.intent == "market_discovery":
        for source in ("npm", "pypi", "ecosystems", "huggingface", "openalex", "arxiv"):
            _disable_source(enabled, suppressed, source)

    if intent.intent == "idea_market_discovery" and not has_model_signal:
        _disable_source(enabled, suppressed, "huggingface")

    return enabled, sorted(set(suppressed))


def _build_source_queries(
    query: str,
    intent: QueryIntent,
    facets: dict[str, str],
    enabled_sources: Iterable[SourceName],
    query_clusters: dict[str, list[str]],
) -> dict[str, list[str]]:
    source_queries: dict[str, list[str]] = {}
    general_queries = query_clusters.get("primary", _general_candidate_queries(query, facets))
    research_queries = query_clusters.get("research", _dedupe_preserve_order([facets["research"], facets["functional"]]))
    package_queries = query_clusters.get("package", _package_candidate_queries(query, facets))

    for source in enabled_sources:
        if source == "directory_seeds":
            source_queries[source] = [query]
        elif intent.intent == "idea_market_discovery":
            source_queries[source] = _idea_market_source_queries(source, query_clusters, package_queries, facets)
        elif intent.intent == "technical_reuse":
            source_queries[source] = _technical_reuse_source_queries(source, query, general_queries, package_queries, facets)
        elif source in {"github", "repo_posts", "hn"}:
            source_queries[source] = general_queries[:3]
        elif source in {"npm", "pypi", "ecosystems"}:
            source_queries[source] = package_queries[:4]
        elif source in {"openalex", "arxiv"}:
            source_queries[source] = research_queries[:2]
        elif source == "huggingface":
            source_queries[source] = research_queries[:1] if intent.intent == "research_discovery" else general_queries[:1]
        else:
            source_queries[source] = [query]
    return {source: [candidate for candidate in queries if candidate] for source, queries in source_queries.items()}


def _technical_reuse_source_queries(
    source: SourceName,
    query: str,
    general_queries: list[str],
    package_queries: list[str],
    facets: dict[str, str],
) -> list[str]:
    if source == "github":
        candidates = general_queries[:6]
    elif source == "repo_posts":
        candidates = general_queries[:2]
    elif source == "hn":
        candidates = general_queries[:2]
    elif source in {"npm", "pypi", "ecosystems"}:
        candidates = package_queries[:4]
    elif source == "huggingface":
        candidates = general_queries[:1]
    else:
        candidates = [query, facets["technical"], facets["functional"]]
    return _dedupe_preserve_order(candidate for candidate in candidates if _source_query_is_valid(candidate))


def _idea_market_source_queries(
    source: SourceName,
    query_clusters: dict[str, list[str]],
    package_queries: list[str],
    facets: dict[str, str],
) -> list[str]:
    if source in {"github", "repo_posts"}:
        candidates = (
            query_clusters.get("solution_form", [])[:2]
            + query_clusters.get("problem_domain", [])[:2]
            + query_clusters.get("commercial_model", [])[:2]
            + query_clusters.get("startup_context", [])[:1]
        )
    elif source == "hn":
        candidates = (
            query_clusters.get("startup_context", [])[:2]
            + query_clusters.get("commercial_model", [])[:2]
            + query_clusters.get("solution_form", [])[:1]
        )
    elif source in {"npm", "pypi", "ecosystems"}:
        candidates = query_clusters.get("technical_reuse", [])[:2] + package_queries[:2]
    elif source == "huggingface":
        candidates = query_clusters.get("problem_domain", [])[:1]
    else:
        candidates = [facets["functional"]]
    return _dedupe_preserve_order(candidate for candidate in candidates if _source_query_is_valid(candidate))


def _package_candidate_queries(query: str, facets: dict[str, str]) -> list[str]:
    stripped = query.strip()
    if _is_package_like(stripped):
        return [stripped]

    candidates: list[str] = []
    normalized = _normalize_query(query)
    for phrase in PHRASE_HINTS:
        if f" {phrase} " in f" {normalized} " and len(phrase.split()) <= 3:
            candidates.append(phrase)
    technical = facets["technical"]
    if technical and technical != facets["functional"]:
        candidates.append(technical)
    concise = _compact_query(normalized, max_terms=3)
    if concise:
        candidates.append(concise)
    return [candidate for candidate in _dedupe_preserve_order(candidates) if _source_query_is_valid(candidate)]


def _general_candidate_queries(query: str, facets: dict[str, str]) -> list[str]:
    normalized = _normalize_query(query)
    detected_phrases = [phrase for phrase in PHRASE_HINTS if f" {phrase} " in f" {normalized} "]
    candidates: list[str] = []
    if len(detected_phrases) >= 2:
        candidates.append(" ".join(detected_phrases[:2]))
    if "software discovery" in detected_phrases and "meta engine" in detected_phrases:
        candidates.extend(["metasearch", "search aggregation", "tool discovery"])
    for phrase in detected_phrases:
        candidates.extend(QUERY_EXPANSIONS.get(phrase, []))
    candidates.extend(detected_phrases[:3])
    candidates.extend([facets["functional"], facets["technical"], _compact_query(normalized)])
    return [candidate for candidate in _dedupe_preserve_order(candidates) if candidate]


def _technical_candidate_queries(
    query: str,
    normalized: str,
    facets: dict[str, str],
    intent: QueryIntent,
) -> list[str]:
    candidates: list[str] = []
    candidates.extend(intent.matched_technical_phrases[:4])
    candidates.extend(intent.matched_technical_terms[:3])

    if "agent" in normalized:
        candidates.extend(["agent framework", "multi agent framework"])
    has_self_improvement_signal = any(
        phrase in normalized
        for phrase in ("self improving", "self learning", "self evolving", "self healing", "self improvement", "evolution")
    )
    if has_self_improvement_signal:
        candidates.append("self improving agent")

    if any(term in normalized for term in ("orchestration", "workflow", "runtime")):
        candidates.extend(["agent workflow engine", "multi agent orchestration", "agent runtime"])

    if "autonomous" in normalized:
        candidates.extend(["autonomous agent framework", "autonomous agent runtime"])

    if any(term in normalized for term in ("memory", "persistent", "stateful")):
        candidates.extend(["agent memory", "long term memory"])

    candidates.extend(_general_candidate_queries(query, facets))
    candidates.extend([facets["technical"], facets["functional"], _compact_query(normalized, max_terms=4)])
    return [candidate for candidate in _dedupe_preserve_order(candidates) if _source_query_is_valid(candidate)]


def _rank_and_group_candidates(
    query: str,
    plan: QueryPlan,
    items: list[SearchItem],
    limit: int,
) -> list[SearchCandidate]:
    grouped: dict[str, list[SearchItem]] = defaultdict(list)
    for item in items:
        grouped[_group_key(item)].append(item)

    candidates: list[SearchCandidate] = []
    for group_items in grouped.values():
        scored_items = sorted(group_items, key=lambda item: _item_score(query, plan, item), reverse=True)
        best = scored_items[0]
        unique_sources = sorted({item.source for item in group_items})
        corroboration_bonus = 0.3 * max(0, len(unique_sources) - 1)
        base_score = _item_score(query, plan, best)
        fit_labels = sorted({label for item in group_items for label in _fit_labels(item)})
        total_score = round(base_score + corroboration_bonus, 4)
        candidates.append(
            SearchCandidate(
                canonical_name=_canonical_name(best),
                artifact_type=best.artifact_type,
                url=_canonical_candidate_url(group_items),
                summary=best.summary,
                sources=unique_sources,
                fit_labels=fit_labels,
                score=total_score,
                score_breakdown={
                    "base": round(base_score, 4),
                    "corroboration": round(corroboration_bonus, 4),
                },
                evidence=scored_items,
            )
        )

    candidates.sort(key=lambda candidate: candidate.score, reverse=True)
    return candidates[: max(limit, 0)]


def _item_score(query: str, plan: QueryPlan, item: SearchItem) -> float:
    searchable_text = _searchable_text(item)
    fit_labels = _fit_labels(item)
    lexical = lexical_score(_ranking_query(query, plan), item.title, item.summary, searchable_text)
    source_weight = SOURCE_WEIGHTS.get(item.source, 0.2)
    artifact_bonus = _artifact_bonus(plan.intent, item.artifact_type)
    source_fit_bonus = _source_fit_bonus(plan.intent, item.source)
    popularity_bonus = _popularity_bonus(item)
    freshness_bonus = 0.15 if item.signals.last_updated else 0.0
    semantic_bonus = _semantic_bonus(plan, searchable_text, fit_labels)
    reference_bonus = _reference_bonus(plan.intent, searchable_text)
    penalties = _penalties(plan, item, searchable_text, fit_labels)
    return lexical * 3.0 + source_weight + artifact_bonus + source_fit_bonus + popularity_bonus + freshness_bonus + semantic_bonus + reference_bonus - penalties


def _artifact_bonus(intent: str, artifact_type: str) -> float:
    if intent == "technical_reuse":
        return {
            "repo": 0.7,
            "package": 0.8,
            "thread": 0.15,
            "paper": -0.8,
            "model": 0.4,
            "dataset": 0.2,
            "space": 0.25,
        }.get(artifact_type, 0.0)
    if intent == "idea_market_discovery":
        return {
            "repo": 0.35,
            "package": 0.4,
            "thread": 0.45,
            "product": 0.55,
            "paper": -1.0,
        }.get(artifact_type, 0.0)
    if intent == "market_discovery":
        return {
            "thread": 0.35,
            "repo": 0.2,
            "package": 0.1,
            "paper": -0.9,
        }.get(artifact_type, 0.0)
    if intent == "research_discovery":
        return {
            "paper": 0.9,
            "dataset": 0.5,
            "model": 0.45,
            "space": 0.2,
            "repo": 0.1,
            "thread": -0.5,
        }.get(artifact_type, 0.0)
    return {
        "repo": 0.4,
        "package": 0.35,
        "thread": 0.1,
        "paper": -0.3,
    }.get(artifact_type, 0.0)


def _source_fit_bonus(intent: str, source: SourceName) -> float:
    if intent == "idea_market_discovery":
        return {
            "github": 0.15,
            "hn": 0.25,
            "npm": 0.1,
            "pypi": 0.1,
            "repo_posts": 0.15,
        }.get(source, 0.0)
    return 0.0


def _popularity_bonus(item: SearchItem) -> float:
    values = [item.signals.stars, item.signals.downloads, item.signals.points, item.signals.forks]
    numeric = max((value for value in values if isinstance(value, int) and value > 0), default=0)
    if numeric <= 0:
        return 0.0
    return min(math.log10(1 + numeric) / 5.0, 0.45)


def _semantic_bonus(plan: QueryPlan, searchable_text: str, fit_labels: list[str]) -> float:
    if plan.intent == "research_discovery":
        return 0.0

    bonus = 0.0
    if plan.intent in {"general", "technical_reuse"}:
        if "tool_discovery" in fit_labels:
            bonus += 0.7
        if "metasearch" in searchable_text:
            bonus += 0.55
        if "search aggregation" in searchable_text or "search aggregator" in searchable_text:
            bonus += 0.45
        if "unified search" in searchable_text or "federated search" in searchable_text:
            bonus += 0.35
        if "open_source" in fit_labels and ("tool_discovery" in fit_labels or "mcp" in fit_labels):
            bonus += 0.25
        return bonus

    if plan.intent == "idea_market_discovery":
        label_weights = {
            "idea_validation": 0.55,
            "prior_art": 0.6,
            "startup_discovery": 0.55,
            "tool_discovery": 0.45,
            "marketplace": 0.75,
            "agent_platform": 0.65,
            "mcp": 0.3,
            "open_source": 0.15,
        }
        bonus += sum(label_weights.get(label, 0.0) for label in fit_labels)
        if "search" in searchable_text and any(term in searchable_text for term in ("idea", "startup", "project", "tool")):
            bonus += 0.2
    return bonus


def _reference_bonus(intent: str, searchable_text: str) -> float:
    if intent not in {"general", "technical_reuse", "idea_market_discovery"}:
        return 0.0
    return 0.15 if any(alias in searchable_text for alias in REFERENCE_BENCHMARK_ALIASES) else 0.0


def _penalties(plan: QueryPlan, item: SearchItem, searchable_text: str, fit_labels: list[str]) -> float:
    title_lower = item.title.lower()
    summary_lower = item.summary.lower()
    penalty = 0.0
    if "awesome" in title_lower or "awesome" in summary_lower:
        penalty += 1.2
    if plan.intent != "research_discovery" and item.artifact_type == "paper":
        penalty += 1.3
    if item.source == "hn" and not item.summary and not item.raw.get("num_comments"):
        penalty += 0.1

    if plan.intent in {"general", "technical_reuse", "idea_market_discovery"}:
        positive_matches = sum(term in searchable_text for term in POSITIVE_DISCOVERY_TERMS)
        negative_matches = sum(term in searchable_text for term in NEGATIVE_DISCOVERY_TERMS)
        if positive_matches == 0:
            penalty += 0.9
        elif positive_matches == 1:
            penalty += 0.35
        if "discovery" in searchable_text and not any(
            term in searchable_text for term in ("search", "tool", "prior art", "validation", "catalog", "index", "meta")
        ):
            penalty += 0.8
        if "meta" in searchable_text and not any(
            term in searchable_text for term in ("search", "aggregation", "aggregator", "federated", "unified")
        ):
            penalty += 0.7
        penalty += 0.6 * negative_matches
        penalty += 0.45 * sum(term in searchable_text for term in DOMAIN_NEGATIVE_TERMS)

    if plan.intent == "idea_market_discovery":
        relevant_fit_labels = {"agent_platform", "idea_validation", "marketplace", "prior_art", "startup_discovery", "tool_discovery"}
        if not relevant_fit_labels.intersection(fit_labels):
            penalty += 0.9
        if "prior_art" in plan.query_clusters and any(term in searchable_text for term in ("prior learning", "deep prior", "transfer learning")):
            penalty += 1.3
        if "idea_validation" in " ".join(plan.query_clusters.get("startup_context", [])) and "server testing" in searchable_text:
            penalty += 1.1
    return penalty


def _fit_labels(item: SearchItem) -> list[str]:
    searchable_text = _searchable_text(item)
    labels = [label for label, terms in FIT_LABEL_TERMS.items() if any(term in searchable_text for term in terms)]
    if item.artifact_type == "repo" and "open_source" not in labels:
        labels.append("open_source")
    if item.source in {"npm", "pypi", "ecosystems"} and "open_source" not in labels:
        labels.append("open_source")
    return sorted(set(labels))


def _annotate_exploration_item(item: SearchItem, plan: QueryPlan) -> SearchItem:
    family, priority = SEED_METADATA.get(item.title, ("general_directory", "medium"))
    query_cluster = next((name for name, values in plan.query_clusters.items() if values), "primary")
    intended_use = "firecrawl_directory_deepening" if family in {"ai_tool_directory", "launch_directory"} else "exa_broadening"
    return item.model_copy(
        update={
            "raw": {
                **item.raw,
                "family": family,
                "priority": priority,
                "query_cluster": query_cluster,
                "intended_use": intended_use,
            }
        }
    )


def _group_key(item: SearchItem) -> str:
    repository_url = item.raw.get("repository_url")
    if isinstance(repository_url, str) and repository_url:
        return f"repo:{canonical_url(repository_url)}"
    url = canonical_url(item.url)
    parts = urlsplit(url)
    if parts.netloc == "github.com":
        segments = [segment for segment in parts.path.split("/") if segment]
        if len(segments) >= 2:
            return f"github:{segments[0].lower()}/{segments[1].lower()}"
    return f"url:{url}"


def _canonical_name(item: SearchItem) -> str:
    repository_url = item.raw.get("repository_url")
    if isinstance(repository_url, str) and repository_url:
        parts = urlsplit(repository_url)
        segments = [segment for segment in parts.path.split("/") if segment]
        if len(segments) >= 2:
            return f"{segments[0]}/{segments[1]}"
    return item.title


def _canonical_candidate_url(items: list[SearchItem]) -> str:
    for item in items:
        repository_url = item.raw.get("repository_url")
        if isinstance(repository_url, str) and repository_url:
            return repository_url
    return items[0].url


def _context7_status(intent: QueryIntent) -> str:
    if intent.context7_candidate:
        return "planned_optional_agent_side"
    return "skipped_not_technical"


def _ranking_query(query: str, plan: QueryPlan) -> str:
    candidates = [plan.facets["functional"], plan.facets["technical"], plan.facets["market"]]
    if plan.intent == "research_discovery":
        candidates.append(plan.facets["research"])
    for queries in plan.query_clusters.values():
        candidates.extend(queries[:2])
    for source_queries in plan.source_queries.values():
        candidates.extend(source_queries[:1])
    return " ".join(_dedupe_preserve_order(candidates)) or query


def _searchable_text(item: SearchItem) -> str:
    chunks = [item.title, item.summary]
    for value in item.raw.values():
        if isinstance(value, str):
            chunks.append(value)
        elif isinstance(value, list):
            chunks.extend(str(entry) for entry in value if isinstance(entry, str))
        elif isinstance(value, dict):
            chunks.extend(str(entry) for entry in value.values() if isinstance(entry, str))
    return " ".join(chunks).lower()


def _normalize_query(query: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", query.lower())).strip()


def _compact_query(normalized_query: str, *, max_terms: int = 4) -> str:
    tokens = [token for token in normalized_query.split() if token not in STOPWORDS]
    return " ".join(tokens[:max_terms]) or normalized_query


def _dedupe_preserve_order(values: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    deduped: list[str] = []
    for value in values:
        compacted = compact_text(str(value), max_length=120).strip()
        if not compacted or compacted in seen:
            continue
        seen.add(compacted)
        deduped.append(compacted)
    return deduped


def _enable_source(enabled: list[SourceName], suppressed: list[SourceName], source: SourceName) -> None:
    if source not in enabled:
        enabled.append(source)
    if source in suppressed:
        suppressed.remove(source)


def _disable_source(enabled: list[SourceName], suppressed: list[SourceName], source: SourceName) -> None:
    if source in enabled:
        enabled.remove(source)
    if source not in suppressed:
        suppressed.append(source)


def _is_package_like(query: str) -> bool:
    normalized = query.strip()
    return " " not in normalized and bool(PACKAGE_LIKE_RE.match(normalized))


def _source_query_is_valid(query: str) -> bool:
    return bool(query) and len(query.split()) <= 4 and len(query) <= 48


def _validate_mode(mode: str) -> None:
    if mode not in MODE_VALUES:
        raise ValueError(f"unsupported search mode: {mode}")
