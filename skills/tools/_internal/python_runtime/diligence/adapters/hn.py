from __future__ import annotations

from typing import Any

import httpx

from diligence.adapters.base import Adapter, trim_items, warn_result
from diligence.http import get_json
from diligence.models import SearchItem, Signals, SourceResult
from diligence.normalize import compact_text

API_URL = "https://hn.algolia.com/api/v1/search"


class HNAdapter(Adapter):
    source = "hn"

    async def search(self, client: httpx.AsyncClient, query: str, limit: int) -> SourceResult:
        params = {"query": query, "tags": "story", "hitsPerPage": max(1, min(limit, 50))}
        try:
            payload = await get_json(client, API_URL, params=params)
            items = [self._item(raw) for raw in payload.get("hits", []) if isinstance(raw, dict)]
            return SourceResult(source=self.source, query=query, items=trim_items(items, limit))
        except Exception as exc:
            return warn_result(self.source, query, f"hacker news failed: {type(exc).__name__}: {exc}")

    def _item(self, raw: dict[str, Any]) -> SearchItem:
        object_id = str(raw.get("objectID") or "")
        url = str(raw.get("url") or f"https://news.ycombinator.com/item?id={object_id}")
        return SearchItem(
            title=str(raw.get("title") or raw.get("story_title") or "Hacker News story"),
            url=url,
            source=self.source,
            artifact_type="thread",
            summary=compact_text(str(raw.get("story_text") or raw.get("comment_text") or "")),
            signals=Signals(points=raw.get("points"), last_updated=raw.get("created_at")),
            raw={"object_id": object_id, "num_comments": raw.get("num_comments"), "author": raw.get("author")},
        )
