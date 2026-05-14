from __future__ import annotations

import re
from typing import Any
from urllib.parse import quote

import httpx

from diligence.adapters.base import Adapter, trim_items, warn_result
from diligence.http import get_json
from diligence.models import SearchItem, Signals, SourceResult
from diligence.normalize import compact_text

PACKAGE_URL_TEMPLATE = "https://packages.ecosyste.ms/api/v1/registries/{registry}/packages/{package}"
REPO_LOOKUP_URL = "https://repos.ecosyste.ms/api/v1/repositories/lookup"
PACKAGE_RE = re.compile(r"^[A-Za-z0-9@][A-Za-z0-9._/@-]{0,213}$")
REGISTRIES = ("npmjs.org", "pypi.org")


class EcosystemsAdapter(Adapter):
    source = "ecosystems"

    async def search(self, client: httpx.AsyncClient, query: str, limit: int) -> SourceResult:
        normalized = query.strip()
        if normalized.startswith(("http://", "https://", "pkg:")):
            return await self._repo_lookup(client, normalized, query)
        if " " in normalized or not PACKAGE_RE.match(normalized):
            return SourceResult(source=self.source, query=query, items=[])
        items: list[SearchItem] = []
        warnings: list[str] = []
        for registry in REGISTRIES:
            url = PACKAGE_URL_TEMPLATE.format(registry=registry, package=quote(normalized, safe=""))
            try:
                payload = await get_json(client, url)
                if isinstance(payload, dict):
                    items.append(self._package_item(payload))
            except httpx.HTTPStatusError as exc:
                if exc.response.status_code != 404:
                    warnings.append(f"ecosyste.ms {registry} failed: HTTP {exc.response.status_code}")
            except Exception as exc:
                warnings.append(f"ecosyste.ms {registry} failed: {type(exc).__name__}: {exc}")
        return SourceResult(source=self.source, query=query, items=trim_items(items, limit), warnings=warnings)

    async def _repo_lookup(self, client: httpx.AsyncClient, normalized: str, query: str) -> SourceResult:
        params = {"purl": normalized} if normalized.startswith("pkg:") else {"url": normalized}
        try:
            payload = await get_json(client, REPO_LOOKUP_URL, params=params)
            if not isinstance(payload, dict):
                return SourceResult(source=self.source, query=query, items=[])
            return SourceResult(source=self.source, query=query, items=[self._repo_item(payload)])
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 404:
                return SourceResult(source=self.source, query=query, items=[])
            return warn_result(self.source, query, f"ecosyste.ms failed: HTTP {exc.response.status_code}")
        except Exception as exc:
            return warn_result(self.source, query, f"ecosyste.ms failed: {type(exc).__name__}: {exc}")

    def _repo_item(self, raw: dict[str, Any]) -> SearchItem:
        owner = raw.get("owner") if isinstance(raw.get("owner"), str) else None
        name = str(raw.get("name") or raw.get("full_name") or raw.get("repository_url") or "ecosyste.ms repo")
        full_name = f"{owner}/{name}" if owner and "/" not in name else name
        return SearchItem(
            title=full_name,
            url=str(raw.get("html_url") or raw.get("url") or raw.get("repository_url") or ""),
            source=self.source,
            artifact_type="repo",
            summary=compact_text(str(raw.get("description") or "")),
            signals=Signals(
                stars=raw.get("stars") or raw.get("stargazers_count"),
                forks=raw.get("forks") or raw.get("forks_count"),
                last_updated=raw.get("updated_at") or raw.get("pushed_at"),
                license=raw.get("license"),
            ),
            raw={
                "host": raw.get("host"),
                "language": raw.get("language"),
                "topics": raw.get("topics", []),
                "packages_count": raw.get("packages_count"),
            },
        )

    def _package_item(self, raw: dict[str, Any]) -> SearchItem:
        name = str(raw.get("name") or raw.get("normalized_name") or "ecosyste.ms package")
        registry = raw.get("registry") if isinstance(raw.get("registry"), dict) else {}
        repository_url = str(raw.get("repository_url") or "")
        licenses = raw.get("licenses")
        license_text = ", ".join(licenses) if isinstance(licenses, list) else licenses
        return SearchItem(
            title=name,
            url=str(raw.get("html_url") or raw.get("homepage") or repository_url or raw.get("url") or ""),
            source=self.source,
            artifact_type="package",
            summary=compact_text(str(raw.get("description") or "")),
            signals=Signals(
                downloads=raw.get("downloads"),
                stars=raw.get("stargazers_count"),
                forks=raw.get("forks_count"),
                last_updated=raw.get("updated_at") or raw.get("latest_release_published_at"),
                license=license_text,
            ),
            raw={
                "ecosystem": raw.get("ecosystem") or registry.get("ecosystem"),
                "registry": registry.get("name"),
                "repository_url": repository_url,
                "dependent_repos_count": raw.get("dependent_repos_count"),
                "dependent_packages_count": raw.get("dependent_packages_count"),
            },
        )
