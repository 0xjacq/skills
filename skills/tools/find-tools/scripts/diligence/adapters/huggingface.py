from __future__ import annotations

from typing import Any

import httpx

from diligence.adapters.base import Adapter, trim_items
from diligence.http import get_json
from diligence.models import SearchItem, Signals, SourceResult
from diligence.normalize import compact_text

API_BASE = "https://huggingface.co/api"


class HuggingFaceAdapter(Adapter):
    source = "huggingface"

    async def search(self, client: httpx.AsyncClient, query: str, limit: int) -> SourceResult:
        warnings: list[str] = []
        items: list[SearchItem] = []
        per_kind = max(1, min(limit, 20))
        for endpoint, artifact_type, prefix in [
            ("models", "model", ""),
            ("datasets", "dataset", "datasets/"),
            ("spaces", "space", "spaces/"),
        ]:
            try:
                payload = await get_json(
                    client,
                    f"{API_BASE}/{endpoint}",
                    params={"search": query, "limit": per_kind},
                )
                if isinstance(payload, list):
                    items.extend(self._item(raw, artifact_type, prefix) for raw in payload if isinstance(raw, dict))
            except Exception as exc:
                warnings.append(f"huggingface {endpoint} failed: {type(exc).__name__}: {exc}")
        return SourceResult(source=self.source, query=query, items=trim_items(items, limit), warnings=warnings)

    def _item(self, raw: dict[str, Any], artifact_type: str, prefix: str) -> SearchItem:
        item_id = str(raw.get("id") or raw.get("modelId") or raw.get("datasetId") or raw.get("name") or "")
        tags = raw.get("tags") if isinstance(raw.get("tags"), list) else []
        return SearchItem(
            title=item_id or "Hugging Face artifact",
            url=f"https://huggingface.co/{prefix}{item_id}",
            source=self.source,
            artifact_type=artifact_type,  # type: ignore[arg-type]
            summary=compact_text(" ".join(str(tag) for tag in tags[:12])),
            signals=Signals(
                downloads=raw.get("downloads"),
                last_updated=raw.get("lastModified") or raw.get("updatedAt"),
                license=raw.get("license"),
            ),
            raw={"likes": raw.get("likes"), "pipeline_tag": raw.get("pipeline_tag"), "tags": tags},
        )
