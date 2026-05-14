from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from diligence.models import QueryPlan, SearchResult

Verdict = Literal["reuse_existing", "adapt_existing", "build_new", "needs_manual_review"]
FindToolsDecision = Literal["best_fit_found", "no_clear_fit", "needs_manual_review"]
Confidence = Literal["low", "medium", "high"]
EvidenceKind = Literal["primary", "secondary", "discussion"]


class ExaSearchHit(BaseModel):
    query_family: str
    query: str
    title: str
    url: str
    summary: str = ""
    published_date: str | None = None
    author: str | None = None
    score: float | None = None
    evidence_kind: EvidenceKind


class CandidateEvidence(BaseModel):
    kind: EvidenceKind
    source: str
    title: str
    url: str
    summary: str = ""


class CorroborationSummary(BaseModel):
    primary_count: int = 0
    secondary_count: int = 0
    discussion_count: int = 0
    structured_sources: list[str] = Field(default_factory=list)
    web_hits: int = 0


class BuildOrNotCandidate(BaseModel):
    name: str
    artifact_type: str
    url: str
    summary: str = ""
    fit_labels: list[str] = Field(default_factory=list)
    confidence: Confidence = "low"
    corroboration: CorroborationSummary = Field(default_factory=CorroborationSummary)
    strength_score: float = 0.0
    rationale: str = ""
    evidence: list[CandidateEvidence] = Field(default_factory=list)


class ArtifactPaths(BaseModel):
    output_dir: str
    result_json: str
    canonical_report: str
    html_report: str
    audit_bundle: str


class BuildOrNotResult(BaseModel):
    capability: str
    generated_at: str
    run_id: str
    verdict: Verdict
    confidence: Confidence
    verdict_rationale: str
    recommended_action: str
    evidence_policy: str
    query_plan: QueryPlan
    exa_queries: list[dict[str, str]] = Field(default_factory=list)
    leading_candidates: list[BuildOrNotCandidate] = Field(default_factory=list)
    exa_hits: list[ExaSearchHit] = Field(default_factory=list)
    structured_search: SearchResult
    warnings: list[str] = Field(default_factory=list)
    artifacts: ArtifactPaths


class FindToolsResult(BaseModel):
    query: str
    generated_at: str
    run_id: str
    decision: FindToolsDecision
    confidence: Confidence
    selection_rationale: str
    recommended_artifact_type: str | None = None
    query_plan: QueryPlan
    exa_queries: list[dict[str, str]] = Field(default_factory=list)
    best_fit: BuildOrNotCandidate | None = None
    alternatives: list[BuildOrNotCandidate] = Field(default_factory=list)
    near_misses: list[BuildOrNotCandidate] = Field(default_factory=list)
    exa_hits: list[ExaSearchHit] = Field(default_factory=list)
    structured_search: SearchResult
    warnings: list[str] = Field(default_factory=list)
    artifacts: ArtifactPaths


class AuditManifest(BaseModel):
    tool_name: str
    run_id: str
    generated_at: str
    query: str
    decision: str
    confidence: Confidence
    files: dict[str, str]
    warnings: list[str] = Field(default_factory=list)
