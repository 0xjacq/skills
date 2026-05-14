from __future__ import annotations

import re
from typing import Literal

from pydantic import BaseModel, Field

SearchMode = Literal["auto", "idea-market", "technical-reuse", "market-discovery", "research-discovery"]

TECHNICAL_TERMS = (
    "api",
    "cli",
    "client",
    "framework",
    "integration",
    "library",
    "mcp",
    "npm",
    "package",
    "plugin",
    "pypi",
    "sdk",
    "toolkit",
    "wrapper",
)

TECHNICAL_PHRASES = (
    "agent orchestration",
    "agent runtime",
    "agent framework",
    "api client",
    "developer tool",
    "multi agent",
    "multi agent workflow",
    "open source library",
    "open source package",
    "open source sdk",
    "open source tool",
    "repo to build on",
    "something i can use",
    "tool i can use",
    "workflow engine",
)

MARKET_TERMS = (
    "alternative",
    "alternatives",
    "auction",
    "bounty",
    "company",
    "competitor",
    "funding",
    "gig",
    "hire",
    "launch",
    "marketplace",
    "platform",
    "pricing",
    "product hunt",
    "rent",
    "rental",
    "saas",
    "startup",
)

IDEA_MARKET_TERMS = (
    "agency",
    "auction",
    "bounty",
    "feedback",
    "freelancer",
    "gig",
    "hire",
    "idea",
    "launch",
    "marketplace",
    "novelty",
    "platform",
    "prior",
    "rent",
    "rental",
    "ship",
    "startup",
    "validate",
    "validation",
)

PURE_MARKET_TERMS = ("alternative", "alternatives", "competitor", "company", "funding", "pricing", "product hunt", "saas")


class QueryIntent(BaseModel):
    query: str
    intent: Literal["technical_reuse", "market_discovery", "research_discovery", "idea_market_discovery", "general"]
    context7_candidate: bool
    matched_technical_terms: list[str] = Field(default_factory=list)
    matched_technical_phrases: list[str] = Field(default_factory=list)
    matched_market_terms: list[str] = Field(default_factory=list)
    matched_idea_market_terms: list[str] = Field(default_factory=list)
    matched_research_terms: list[str] = Field(default_factory=list)
    reason: str


RESEARCH_TERMS = (
    "academic",
    "arxiv",
    "benchmark",
    "citation",
    "dataset",
    "method",
    "model",
    "paper",
    "papers",
    "research",
)


def classify_query_intent(query: str) -> QueryIntent:
    normalized = _normalize_query(query)
    technical_terms = _match_terms(normalized, TECHNICAL_TERMS)
    technical_phrases = _match_phrases(normalized, TECHNICAL_PHRASES)
    market_terms = _match_phrases(normalized, MARKET_TERMS)
    idea_market_terms = _match_terms(normalized, IDEA_MARKET_TERMS)
    research_terms = _match_terms(normalized, RESEARCH_TERMS)

    has_technical_signal = bool(technical_terms or technical_phrases)
    has_market_signal = bool(market_terms)
    has_idea_market_signal = bool(idea_market_terms)
    has_research_signal = bool(research_terms)
    pure_market_only = bool(_match_terms(normalized, PURE_MARKET_TERMS))

    if has_technical_signal:
        reason = "explicit technical reuse signals detected"
        if has_market_signal:
            reason += "; keep Context7 enabled because the query is mixed but tool-oriented"
        if has_research_signal:
            reason += "; research terms detected but technical routing stays primary"
        return QueryIntent(
            query=query,
            intent="technical_reuse",
            context7_candidate=True,
            matched_technical_terms=technical_terms,
            matched_technical_phrases=technical_phrases,
            matched_market_terms=market_terms,
            matched_idea_market_terms=idea_market_terms,
            matched_research_terms=research_terms,
            reason=reason,
        )

    if has_research_signal:
        return QueryIntent(
            query=query,
            intent="research_discovery",
            context7_candidate=False,
            matched_market_terms=market_terms,
            matched_idea_market_terms=idea_market_terms,
            matched_research_terms=research_terms,
            reason="research-oriented terms detected without explicit technical reuse terms",
        )

    if has_idea_market_signal and (not pure_market_only or len(idea_market_terms) > len(market_terms)):
        return QueryIntent(
            query=query,
            intent="idea_market_discovery",
            context7_candidate=False,
            matched_market_terms=market_terms,
            matched_idea_market_terms=idea_market_terms,
            matched_research_terms=research_terms,
            reason="idea-to-market signals detected; prefer mixed project/startup/tool discovery over simple market discovery",
        )

    if has_market_signal:
        return QueryIntent(
            query=query,
            intent="market_discovery",
            context7_candidate=False,
            matched_market_terms=market_terms,
            matched_idea_market_terms=idea_market_terms,
            matched_research_terms=research_terms,
            reason="market or startup discovery signals detected without explicit technical reuse terms",
        )

    return QueryIntent(
        query=query,
        intent="general",
        context7_candidate=False,
        matched_idea_market_terms=idea_market_terms,
        matched_research_terms=research_terms,
        reason="no explicit technical reuse terms detected; stay conservative and skip Context7",
    )


def should_use_context7(query: str) -> bool:
    return classify_query_intent(query).context7_candidate


def apply_mode_override(intent: QueryIntent, mode: SearchMode) -> QueryIntent:
    if mode == "auto":
        return intent

    override_map = {
        "technical-reuse": "technical_reuse",
        "market-discovery": "market_discovery",
        "research-discovery": "research_discovery",
        "idea-market": "idea_market_discovery",
    }
    overridden_intent = override_map[mode]
    context7_candidate = overridden_intent == "technical_reuse" or (
        overridden_intent == "idea_market_discovery"
        and bool(intent.matched_technical_terms or intent.matched_technical_phrases)
    )

    return QueryIntent(
        query=intent.query,
        intent=overridden_intent,  # type: ignore[arg-type]
        context7_candidate=context7_candidate,
        matched_technical_terms=intent.matched_technical_terms,
        matched_technical_phrases=intent.matched_technical_phrases,
        matched_market_terms=intent.matched_market_terms,
        matched_idea_market_terms=intent.matched_idea_market_terms,
        matched_research_terms=intent.matched_research_terms,
        reason=f"forced by search mode `{mode}`; base classifier: {intent.reason}",
    )


def _normalize_query(query: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", query.lower())).strip()


def _match_terms(normalized_query: str, candidates: tuple[str, ...]) -> list[str]:
    tokens = set(normalized_query.split())
    return [term for term in candidates if term in tokens]


def _match_phrases(normalized_query: str, candidates: tuple[str, ...]) -> list[str]:
    haystack = f" {normalized_query} "
    return [phrase for phrase in candidates if f" {phrase} " in haystack]
