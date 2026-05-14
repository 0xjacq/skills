from __future__ import annotations

import asyncio
import os
import shutil
import sys
from pathlib import Path

from diligence.adapters import ADAPTERS, normalize_source_name
from diligence.http import async_client, cache_dir
from diligence.models import CollectResult, DoctorResult, SourceName, SourceResult
from diligence.normalize import dedupe_items

DEFAULT_SOURCES: tuple[SourceName, ...] = (
    "repo_posts",
    "github",
    "ecosystems",
    "npm",
    "pypi",
    "hn",
    "huggingface",
    "openalex",
    "arxiv",
    "directory_seeds",
)
REPO_SKILL_RELATIVE_PATH = Path(".agents/skills/prebuild-diligence/SKILL.md")


async def source_search(source: str, query: str, limit: int = 20) -> SourceResult:
    source_name = normalize_source_name(source)
    adapter_type = ADAPTERS.get(source_name)
    if adapter_type is None:
        known = ", ".join(sorted(ADAPTERS))
        return SourceResult(
            source="directory_seeds",
            query=query,
            items=[],
            warnings=[f"unknown source '{source}'. Known sources: {known}"],
        )
    async with async_client() as client:
        return await adapter_type().search(client, query, limit)


async def collect_all(
    query: str,
    *,
    limit: int = 20,
    sources: tuple[SourceName, ...] = DEFAULT_SOURCES,
) -> CollectResult:
    warnings: list[str] = []
    async with async_client() as client:
        tasks = [ADAPTERS[source]().search(client, query, limit) for source in sources]
        results = await asyncio.gather(*tasks, return_exceptions=True)

    items = []
    for source, result in zip(sources, results, strict=False):
        if isinstance(result, Exception):
            warnings.append(f"{source} failed: {type(result).__name__}: {result}")
            continue
        items.extend(result.items)
        warnings.extend(result.warnings)

    return CollectResult(query=query, items=dedupe_items(items), warnings=warnings)


def doctor() -> DoctorResult:
    warnings: list[str] = []
    checks = {
        "python_3_11_plus": sys.version_info >= (3, 11),
        "cache_dir_writable": _can_write(cache_dir()),
        "repo_skill_path_present": _repo_skill_path_present(),
        "npx_available": shutil.which("npx") is not None,
        "gemini_cli_available": shutil.which("gemini") is not None,
        "gemini_api_key_present": bool(os.getenv("GEMINI_API_KEY")),
        "google_cloud_project_present": bool(os.getenv("GOOGLE_CLOUD_PROJECT")),
        "google_cloud_location_present": bool(os.getenv("GOOGLE_CLOUD_LOCATION")),
        "firecrawl_cli_available": shutil.which("firecrawl") is not None,
        "firecrawl_api_key_present": bool(os.getenv("FIRECRAWL_API_KEY")),
        "github_token_present": bool(os.getenv("GITHUB_TOKEN")),
    }
    if not checks["repo_skill_path_present"]:
        warnings.append(
            "Repo Codex skill is not discoverable at .agents/skills/prebuild-diligence/SKILL.md."
        )
    if not checks["gemini_cli_available"]:
        warnings.append(
            "Gemini CLI is unavailable; the optional Gemini validation branch will be skipped."
        )
    if not checks["firecrawl_cli_available"] and not checks["firecrawl_api_key_present"]:
        warnings.append("Firecrawl CLI is unavailable and FIRECRAWL_API_KEY is not set.")
    if not checks["github_token_present"]:
        warnings.append("GITHUB_TOKEN is not set; GitHub API rate limits will be lower.")
    required = ["python_3_11_plus", "cache_dir_writable", "repo_skill_path_present"]
    return DoctorResult(ok=all(checks[name] for name in required), checks=checks, warnings=warnings)


def _can_write(path: Path) -> bool:
    try:
        path.mkdir(parents=True, exist_ok=True)
        probe = path / ".write-test"
        probe.write_text("ok", encoding="utf-8")
        probe.unlink(missing_ok=True)
        return True
    except OSError:
        return False


def _repo_skill_path_present(start: Path | None = None) -> bool:
    current = (start or Path.cwd()).resolve()
    for candidate_root in (current, *current.parents):
        if (candidate_root / REPO_SKILL_RELATIVE_PATH).is_file():
            return True
        if (candidate_root / ".git").exists():
            break
    return False
