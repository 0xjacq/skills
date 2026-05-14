from __future__ import annotations

from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Awaitable, Callable
from urllib.parse import urlsplit
from uuid import uuid4

from diligence.models import SearchCandidate, SearchItem, SearchResult
from diligence.normalize import canonical_url, compact_text, lexical_score
from diligence.search import build_query_plan, search_projects
from prebuild_engine.artifacts import artifact_paths, write_build_or_not_artifacts
from prebuild_engine.exa import search_exa
from prebuild_engine.models import (
    BuildOrNotCandidate,
    BuildOrNotResult,
    CandidateEvidence,
    Confidence,
    CorroborationSummary,
    EvidenceKind,
    ExaSearchHit,
    Verdict,
)

PRIMARY_STRUCTURED_SOURCES = {"github", "npm", "pypi", "ecosystems", "huggingface"}
SECONDARY_STRUCTURED_SOURCES = {"repo_posts", "directory_seeds"}
DISCUSSION_STRUCTURED_SOURCES = {"hn"}


async def run_build_or_not(
    capability: str,
    *,
    limit: int = 8,
    run_id: str | None = None,
    artifacts_root: Path | None = None,
    search_projects_fn: Callable[..., Awaitable[SearchResult]] = search_projects,
    search_exa_fn: Callable[..., Awaitable[tuple[list[ExaSearchHit], list[str]]]] = search_exa,
) -> BuildOrNotResult:
    mode = _mode_for_plan(capability)
    resolved_run_id = run_id or _make_run_id()
    plan = build_query_plan(capability, depth="deep", mode=mode)
    structured = await search_projects_fn(
        capability,
        depth="deep",
        limit=limit,
        mode=mode,
    )
    exa_queries = _build_exa_queries(plan)
    exa_hits, exa_warnings = await search_exa_fn(exa_queries)

    candidates = _merge_candidates(structured.candidates, exa_hits, limit=limit)
    verdict, confidence, rationale, action = _decide_verdict(
        candidates,
        exa_hits=exa_hits,
        exa_available=not any("EXA_API_KEY is not set" in warning for warning in exa_warnings),
    )
    generated_at = datetime.now(UTC).isoformat()
    result = BuildOrNotResult(
        capability=capability,
        generated_at=generated_at,
        run_id=resolved_run_id,
        verdict=verdict,
        confidence=confidence,
        verdict_rationale=rationale,
        recommended_action=action,
        evidence_policy=(
            "Important claims should cite primary evidence when available, prefer two corroborating "
            "signals when possible, and fold freshness into confidence."
        ),
        query_plan=plan,
        exa_queries=exa_queries,
        leading_candidates=candidates[:limit],
        exa_hits=exa_hits,
        structured_search=structured,
        warnings=structured.warnings + exa_warnings,
        artifacts=artifact_paths("build-or-not", resolved_run_id, base_dir=artifacts_root),
    )
    return write_build_or_not_artifacts(result)


def _make_run_id() -> str:
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    return f"build-or-not-{stamp}-{uuid4().hex[:8]}"


def _mode_for_plan(query: str) -> str:
    lowered = query.lower()
    if any(term in lowered for term in ("startup", "marketplace", "company", "competitor", "alternative")):
        return "idea-market"
    if any(term in lowered for term in ("framework", "sdk", "package", "mcp", "plugin", "library", "open source")):
        return "technical-reuse"
    return "auto"


def _build_exa_queries(plan) -> list[dict[str, str]]:
    seen: set[str] = set()
    queries: list[dict[str, str]] = []

    def add(family: str, query: str) -> None:
        normalized = query.strip()
        if not normalized or normalized in seen:
            return
        seen.add(normalized)
        queries.append({"family": family, "query": normalized})

    add("broad", plan.query)
    add("prior_art", f"{plan.facets['functional']} prior art existing product open source")
    add("reuse", f"{plan.facets['technical']} tool framework package")
    for family, values in plan.query_clusters.items():
        for value in values[:2]:
            add(family, value)
    add("alternatives", f"{plan.facets['market']} alternatives")
    return queries[:6]


def _merge_candidates(
    structured_candidates: list[SearchCandidate],
    exa_hits: list[ExaSearchHit],
    *,
    limit: int,
) -> list[BuildOrNotCandidate]:
    merged: list[BuildOrNotCandidate] = []
    used_web_urls: set[str] = set()

    for candidate in structured_candidates:
        matching_hits = [
            hit
            for hit in exa_hits
            if _candidate_matches_hit(candidate, hit)
        ]
        used_web_urls.update(canonical_url(hit.url) for hit in matching_hits)
        merged.append(_build_structured_candidate(candidate, matching_hits))

    for hit in exa_hits:
        url_key = canonical_url(hit.url)
        if url_key in used_web_urls:
            continue
        merged.append(_build_web_only_candidate(hit))

    merged.sort(key=lambda item: item.strength_score, reverse=True)
    return merged[: max(limit, 5)]


def _build_structured_candidate(candidate: SearchCandidate, hits: list[ExaSearchHit]) -> BuildOrNotCandidate:
    evidence: list[CandidateEvidence] = []
    counts = defaultdict(int)
    structured_sources: list[str] = []

    for item in candidate.evidence:
        kind = _structured_evidence_kind(item)
        counts[kind] += 1
        if item.source not in structured_sources:
            structured_sources.append(item.source)
        evidence.append(
            CandidateEvidence(
                kind=kind,
                source=item.source,
                title=item.title,
                url=item.url,
                summary=compact_text(item.summary, max_length=180),
            )
        )

    for hit in hits:
        counts[hit.evidence_kind] += 1
        evidence.append(
            CandidateEvidence(
                kind=hit.evidence_kind,
                source=f"exa:{hit.query_family}",
                title=hit.title,
                url=hit.url,
                summary=hit.summary,
            )
        )

    confidence = _candidate_confidence(counts, hits=hits, structured_sources=structured_sources)
    rationale_bits = []
    if hits:
        rationale_bits.append(f"{len(hits)} Exa corroboration hit(s)")
    if structured_sources:
        rationale_bits.append(f"structured sources: {', '.join(structured_sources)}")
    if candidate.fit_labels:
        rationale_bits.append(f"fit labels: {', '.join(candidate.fit_labels)}")

    return BuildOrNotCandidate(
        name=candidate.canonical_name,
        artifact_type=candidate.artifact_type,
        url=candidate.url,
        summary=compact_text(candidate.summary, max_length=220),
        fit_labels=candidate.fit_labels,
        confidence=confidence,
        corroboration=CorroborationSummary(
            primary_count=counts["primary"],
            secondary_count=counts["secondary"],
            discussion_count=counts["discussion"],
            structured_sources=structured_sources,
            web_hits=len(hits),
        ),
        strength_score=round(
            candidate.score
            + counts["primary"] * 0.55
            + counts["secondary"] * 0.3
            + counts["discussion"] * 0.1
            + min(len(structured_sources), 3) * 0.2,
            3,
        ),
        rationale="; ".join(rationale_bits) or "Structured shortlist candidate.",
        evidence=evidence,
    )


def _build_web_only_candidate(hit: ExaSearchHit) -> BuildOrNotCandidate:
    counts = defaultdict(int)
    counts[hit.evidence_kind] += 1
    title = compact_text(hit.title, max_length=120)
    return BuildOrNotCandidate(
        name=title,
        artifact_type=_artifact_type_from_url(hit.url),
        url=hit.url,
        summary=hit.summary or "Surfaced from Exa web discovery without structured corroboration yet.",
        confidence="low" if hit.evidence_kind != "primary" else "medium",
        corroboration=CorroborationSummary(
            primary_count=counts["primary"],
            secondary_count=counts["secondary"],
            discussion_count=counts["discussion"],
            structured_sources=[],
            web_hits=1,
        ),
        strength_score=round(0.45 + counts["primary"] * 0.5 + counts["secondary"] * 0.2, 3),
        rationale=f"Exa-only {hit.evidence_kind} signal from `{hit.query_family}` query family.",
        evidence=[
            CandidateEvidence(
                kind=hit.evidence_kind,
                source=f"exa:{hit.query_family}",
                title=hit.title,
                url=hit.url,
                summary=hit.summary,
            )
        ],
    )


def _candidate_matches_hit(candidate: SearchCandidate, hit: ExaSearchHit) -> bool:
    if canonical_url(candidate.url) == canonical_url(hit.url):
        return True
    return max(
        lexical_score(candidate.canonical_name, hit.title, hit.summary),
        lexical_score(candidate.summary, hit.title, hit.summary),
    ) >= 0.45


def _structured_evidence_kind(item: SearchItem) -> EvidenceKind:
    if item.source in PRIMARY_STRUCTURED_SOURCES:
        return "primary"
    if item.source in DISCUSSION_STRUCTURED_SOURCES:
        return "discussion"
    if item.source in SECONDARY_STRUCTURED_SOURCES:
        return "secondary"
    return "secondary"


def _candidate_confidence(
    counts: dict[str, int],
    *,
    hits: list[ExaSearchHit],
    structured_sources: list[str],
) -> Confidence:
    if counts["primary"] >= 2 and (hits or len(structured_sources) >= 2):
        return "high"
    if counts["primary"] >= 1 or counts["secondary"] >= 2 or len(structured_sources) >= 2:
        return "medium"
    return "low"


def _artifact_type_from_url(url: str) -> str:
    host = urlsplit(url).netloc.lower()
    if "github.com" in host:
        return "repo"
    if "npmjs.com" in host or "pypi.org" in host:
        return "package"
    return "product"


def _decide_verdict(
    candidates: list[BuildOrNotCandidate],
    *,
    exa_hits: list[ExaSearchHit],
    exa_available: bool,
) -> tuple[Verdict, Confidence, str, str]:
    top = candidates[0] if candidates else None
    if top and (
        top.corroboration.primary_count >= 2
        or (top.corroboration.primary_count >= 1 and len(top.corroboration.structured_sources) >= 2)
        or top.strength_score >= 2.1
    ):
        return (
            "reuse_existing",
            "high" if exa_available else "medium",
            "A credible existing solution surfaced with corroboration across web discovery and structured sources.",
            "Default to the top existing candidate first. Only build new capability around gaps that remain after evaluation.",
        )

    if top and (
        top.corroboration.primary_count >= 1
        or top.corroboration.secondary_count >= 2
        or len(top.corroboration.structured_sources) >= 2
        or len(exa_hits) >= 4
    ):
        return (
            "adapt_existing",
            "medium",
            "Existing products, repos, or packages surfaced, but the evidence is not strong enough to treat one option as a clear drop-in replacement.",
            "Treat reuse or adaptation as the default path. Validate the leading gaps before allocating time to a greenfield build.",
        )

    if not exa_available:
        return (
            "needs_manual_review",
            "low",
            "The structured shortlist alone is not enough to justify a greenfield build because Exa-first discovery did not run.",
            "Run the workflow again with EXA_API_KEY configured, or add external web evidence before deciding to build new.",
        )

    return (
        "build_new",
        "medium" if not candidates else "low",
        "No credible solution was corroborated across Exa-first discovery and the structured-source shortlist.",
        "A greenfield build is reasonable, but keep the audit bundle so the decision can be re-checked later.",
    )
