from __future__ import annotations

from diligence.adapters.base import Adapter
from diligence.adapters.directory_seeds import DirectorySeedsAdapter
from diligence.adapters.ecosystems import EcosystemsAdapter
from diligence.adapters.github import GitHubAdapter
from diligence.adapters.hn import HNAdapter
from diligence.adapters.huggingface import HuggingFaceAdapter
from diligence.adapters.npm import NpmAdapter
from diligence.adapters.openalex_arxiv import ArxivAdapter, OpenAlexAdapter
from diligence.adapters.pypi import PyPIAdapter
from diligence.adapters.repo_posts import RepoPostsAdapter
from diligence.models import SourceName

ADAPTERS: dict[SourceName, type[Adapter]] = {
    "repo_posts": RepoPostsAdapter,
    "github": GitHubAdapter,
    "ecosystems": EcosystemsAdapter,
    "npm": NpmAdapter,
    "pypi": PyPIAdapter,
    "hn": HNAdapter,
    "huggingface": HuggingFaceAdapter,
    "openalex": OpenAlexAdapter,
    "arxiv": ArxivAdapter,
    "directory_seeds": DirectorySeedsAdapter,
}

ALIASES: dict[str, SourceName] = {
    "repo-posts": "repo_posts",
    "repos": "github",
    "ecosyste.ms": "ecosystems",
    "hackernews": "hn",
    "hacker-news": "hn",
    "hf": "huggingface",
    "open-alex": "openalex",
    "directories": "directory_seeds",
    "directory-seeds": "directory_seeds",
}


def normalize_source_name(value: str) -> SourceName:
    normalized = value.strip().lower().replace(" ", "_")
    return ALIASES.get(normalized, normalized)  # type: ignore[return-value]
