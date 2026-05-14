from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Awaitable, Callable

from diligence.models import SearchResult
from diligence.search import build_query_plan, search_projects
from prebuild_engine.artifacts import artifact_paths, write_find_tools_artifacts
from prebuild_engine.build_or_not import _build_exa_queries, _make_run_id, _merge_candidates, _mode_for_plan
from prebuild_engine.exa import search_exa
from prebuild_engine.models import BuildOrNotCandidate, Confidence, ExaSearchHit, FindToolsDecision, FindToolsResult


async def run_find_tools(
    query: str,
    *,
    limit: int = 8,
    run_id: str | None = None,
    artifacts_root: Path | None = None,
    search_projects_fn: Callable[..., Awaitable[SearchResult]] = search_projects,
    search_exa_fn: Callable[..., Awaitable[tuple[list[ExaSearchHit], list[str]]]] = search_exa,
) -> FindToolsResult:
    mode = _mode_for_plan(query)
    resolved_run_id = run_id or f"find-tools-{_make_run_id().split('build-or-not-', 1)[-1]}"
    plan = build_query_plan(query, depth="deep", mode=mode)
    structured = await search_projects_fn(query, depth="deep", limit=limit, mode=mode)
    exa_queries = _build_exa_queries(plan)
    exa_hits, exa_warnings = await search_exa_fn(exa_queries)
    candidates = _merge_candidates(structured.candidates, exa_hits, limit=limit)
    decision, confidence, rationale = _decide_find_tools(candidates, exa_warnings)
    best_fit, alternatives, near_misses = _partition_candidates(candidates, decision)
    recommended_artifact_type = best_fit.artifact_type if best_fit is not None else (
        alternatives[0].artifact_type if alternatives else None
    )

    result = FindToolsResult(
        query=query,
        generated_at=datetime.now(UTC).isoformat(),
        run_id=resolved_run_id,
        decision=decision,
        confidence=confidence,
        selection_rationale=rationale,
        recommended_artifact_type=recommended_artifact_type,
        query_plan=plan,
        exa_queries=exa_queries,
        best_fit=best_fit,
        alternatives=alternatives,
        near_misses=near_misses,
        exa_hits=exa_hits,
        structured_search=structured,
        warnings=structured.warnings + exa_warnings,
        artifacts=artifact_paths("find-tools", resolved_run_id, base_dir=artifacts_root),
    )
    return write_find_tools_artifacts(result)


def _decide_find_tools(
    candidates: list[BuildOrNotCandidate],
    exa_warnings: list[str],
) -> tuple[FindToolsDecision, Confidence, str]:
    exa_available = not any("EXA_API_KEY is not set" in warning for warning in exa_warnings)
    top = candidates[0] if candidates else None
    if not exa_available:
        return (
            "needs_manual_review",
            "low",
            "Exa-first discovery did not run, so the runtime cannot recommend a tool with normal confidence.",
        )
    if top and (
        top.corroboration.primary_count >= 1
        or len(top.corroboration.structured_sources) >= 2
        or top.strength_score >= 1.6
    ):
        confidence: Confidence = "high" if top.corroboration.primary_count >= 2 or top.strength_score >= 2.1 else "medium"
        return (
            "best_fit_found",
            confidence,
            "A strongest candidate surfaced with enough corroboration to recommend it as the current best fit.",
        )
    if candidates:
        confidence = "medium" if len(candidates) >= 2 else "low"
        return (
            "no_clear_fit",
            confidence,
            "Some tools surfaced, but no candidate met the threshold for a strong single recommendation.",
        )
    return (
        "no_clear_fit",
        "medium",
        "No credible tool candidate was corroborated across Exa-first discovery and the structured-source shortlist.",
    )


def _partition_candidates(
    candidates: list[BuildOrNotCandidate],
    decision: FindToolsDecision,
) -> tuple[BuildOrNotCandidate | None, list[BuildOrNotCandidate], list[BuildOrNotCandidate]]:
    if not candidates:
        return None, [], []
    if decision == "best_fit_found":
        best_fit = candidates[0]
        alternatives = candidates[1:4]
        near_misses = [candidate for candidate in candidates[4:8] if candidate.confidence == "low"]
        return best_fit, alternatives, near_misses

    alternatives = candidates[:4]
    near_misses = candidates[4:8]
    if not near_misses:
        near_misses = [candidate for candidate in alternatives if candidate.confidence == "low"]
        alternatives = [candidate for candidate in alternatives if candidate.confidence != "low"]
    return None, alternatives, near_misses
