from __future__ import annotations

import re
from typing import Any

import httpx

from diligence.adapters.base import Adapter, warn_result
from diligence.http import get_json
from diligence.models import SearchItem, Signals, SourceResult
from diligence.normalize import compact_text

PACKAGE_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,213}$")


class PyPIAdapter(Adapter):
    source = "pypi"

    async def search(self, client: httpx.AsyncClient, query: str, limit: int) -> SourceResult:
        package_name = query.strip()
        if limit <= 0 or not PACKAGE_RE.match(package_name):
            return SourceResult(source=self.source, query=query, items=[])
        try:
            payload = await get_json(client, f"https://pypi.org/pypi/{package_name}/json")
            return SourceResult(source=self.source, query=query, items=[self._item(payload)])
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 404:
                return SourceResult(source=self.source, query=query, items=[])
            return warn_result(self.source, query, f"pypi failed: HTTP {exc.response.status_code}")
        except Exception as exc:
            return warn_result(self.source, query, f"pypi failed: {type(exc).__name__}: {exc}")

    def _item(self, payload: dict[str, Any]) -> SearchItem:
        info = payload.get("info") if isinstance(payload.get("info"), dict) else {}
        name = str(info.get("name") or "PyPI package")
        urls = info.get("project_urls") if isinstance(info.get("project_urls"), dict) else {}
        return SearchItem(
            title=name,
            url=str(info.get("package_url") or f"https://pypi.org/project/{name}/"),
            source=self.source,
            artifact_type="package",
            summary=compact_text(str(info.get("summary") or info.get("description") or "")),
            signals=Signals(license=info.get("license")),
            raw={
                "version": info.get("version"),
                "author": info.get("author"),
                "home_page": info.get("home_page"),
                "project_urls": urls,
                "classifiers": info.get("classifiers", []),
            },
        )
