from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

SourceName = Literal[
    "github",
    "repo_posts",
    "ecosystems",
    "npm",
    "pypi",
    "hn",
    "huggingface",
    "openalex",
    "arxiv",
    "directory_seeds",
]

ArtifactType = Literal[
    "repo",
    "package",
    "paper",
    "thread",
    "product",
    "directory_entry",
    "model",
    "space",
    "dataset",
    "unknown",
]


class Signals(BaseModel):
    model_config = ConfigDict(extra="allow")

    stars: int | None = None
    points: int | None = None
    downloads: int | None = None
    forks: int | None = None
    last_updated: str | None = None
    license: str | None = None


class SearchItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str
    url: str
    source: SourceName
    artifact_type: ArtifactType = "unknown"
    summary: str = ""
    signals: Signals = Field(default_factory=Signals)
    raw: dict[str, Any] = Field(default_factory=dict)


class RetrievalPolicy(BaseModel):
    primary: str = "exa"
    secondary: str = "cli_structured_sources"
    deepening: str = "firecrawl"
    firecrawl_max_pages: int = 5


class CollectResult(BaseModel):
    query: str
    retrieval_policy: RetrievalPolicy = Field(default_factory=RetrievalPolicy)
    items: list[SearchItem] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class SourceResult(BaseModel):
    source: SourceName
    query: str
    items: list[SearchItem] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class DoctorResult(BaseModel):
    ok: bool
    checks: dict[str, bool]
    warnings: list[str] = Field(default_factory=list)


class QueryPlan(BaseModel):
    query: str
    depth: Literal["quick", "deep"] = "quick"
    intent: Literal["technical_reuse", "market_discovery", "research_discovery", "idea_market_discovery", "general"]
    facets: dict[str, str] = Field(default_factory=dict)
    query_clusters: dict[str, list[str]] = Field(default_factory=dict)
    enabled_sources: list[SourceName] = Field(default_factory=list)
    suppressed_sources: list[SourceName] = Field(default_factory=list)
    source_queries: dict[str, list[str]] = Field(default_factory=dict)
    context7_attempted: bool = False
    context7_status: str = "not_applicable"


class SearchCandidate(BaseModel):
    canonical_name: str
    artifact_type: ArtifactType = "unknown"
    url: str
    summary: str = ""
    sources: list[SourceName] = Field(default_factory=list)
    fit_labels: list[str] = Field(default_factory=list)
    score: float = 0.0
    score_breakdown: dict[str, float] = Field(default_factory=dict)
    evidence: list[SearchItem] = Field(default_factory=list)


class SearchResult(BaseModel):
    query: str
    query_plan: QueryPlan
    candidates: list[SearchCandidate] = Field(default_factory=list)
    exploration_urls: list[SearchItem] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
