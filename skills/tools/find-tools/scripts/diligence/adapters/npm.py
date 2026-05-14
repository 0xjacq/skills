from __future__ import annotations

from typing import Any

import httpx

from diligence.adapters.base import Adapter, trim_items, warn_result
from diligence.http import get_json
from diligence.models import SearchItem, Signals, SourceResult
from diligence.normalize import compact_text

API_URL = "https://registry.npmjs.org/-/v1/search"


class NpmAdapter(Adapter):
    source = "npm"

    async def search(self, client: httpx.AsyncClient, query: str, limit: int) -> SourceResult:
        params = {"text": query, "size": max(1, min(limit, 50))}
        try:
            payload = await get_json(client, API_URL, params=params)
            items = [self._item(raw) for raw in payload.get("objects", []) if isinstance(raw, dict)]
            return SourceResult(source=self.source, query=query, items=trim_items(items, limit))
        except Exception as exc:
            return warn_result(self.source, query, f"npm failed: {type(exc).__name__}: {exc}")

    def _item(self, raw: dict[str, Any]) -> SearchItem:
        package = raw.get("package") if isinstance(raw.get("package"), dict) else {}
        name = str(package.get("name") or "npm package")
        links = package.get("links") if isinstance(package.get("links"), dict) else {}
        return SearchItem(
            title=name,
            url=str(links.get("npm") or f"https://www.npmjs.com/package/{name}"),
            source=self.source,
            artifact_type="package",
            summary=compact_text(str(package.get("description") or "")),
            signals=Signals(last_updated=package.get("date")),
            raw={
                "version": package.get("version"),
                "publisher": package.get("publisher"),
                "keywords": package.get("keywords", []),
                "links": links,
                "score": raw.get("score"),
            },
        )
