from __future__ import annotations

import xml.etree.ElementTree as ET
from typing import Any

import httpx

from diligence.adapters.base import Adapter, trim_items, warn_result
from diligence.http import get_json, get_text
from diligence.models import SearchItem, Signals, SourceResult
from diligence.normalize import compact_text

OPENALEX_URL = "https://api.openalex.org/works"
ARXIV_URL = "https://export.arxiv.org/api/query"
ATOM_NS = {"atom": "http://www.w3.org/2005/Atom"}


def _abstract_from_inverted_index(value: Any) -> str:
    if not isinstance(value, dict):
        return ""
    positions: list[tuple[int, str]] = []
    for word, indexes in value.items():
        if isinstance(indexes, list):
            positions.extend((int(index), str(word)) for index in indexes if isinstance(index, int))
    return " ".join(word for _, word in sorted(positions))


class OpenAlexAdapter(Adapter):
    source = "openalex"

    async def search(self, client: httpx.AsyncClient, query: str, limit: int) -> SourceResult:
        params = {
            "search": query,
            "per-page": max(1, min(limit, 25)),
            "select": "id,display_name,publication_year,cited_by_count,doi,primary_location,abstract_inverted_index,type",
        }
        try:
            payload = await get_json(client, OPENALEX_URL, params=params)
            items = [self._item(raw) for raw in payload.get("results", []) if isinstance(raw, dict)]
            return SourceResult(source=self.source, query=query, items=trim_items(items, limit))
        except Exception as exc:
            return warn_result(self.source, query, f"openalex failed: {type(exc).__name__}: {exc}")

    def _item(self, raw: dict[str, Any]) -> SearchItem:
        location = raw.get("primary_location") if isinstance(raw.get("primary_location"), dict) else {}
        landing_page = str(location.get("landing_page_url") or raw.get("doi") or raw.get("id") or "")
        return SearchItem(
            title=str(raw.get("display_name") or "OpenAlex work"),
            url=landing_page,
            source=self.source,
            artifact_type="paper",
            summary=compact_text(_abstract_from_inverted_index(raw.get("abstract_inverted_index"))),
            signals=Signals(points=raw.get("cited_by_count"), last_updated=str(raw.get("publication_year") or "")),
            raw={"openalex_id": raw.get("id"), "doi": raw.get("doi"), "type": raw.get("type")},
        )


class ArxivAdapter(Adapter):
    source = "arxiv"

    async def search(self, client: httpx.AsyncClient, query: str, limit: int) -> SourceResult:
        params = {
            "search_query": f"all:{query}",
            "start": 0,
            "max_results": max(1, min(limit, 25)),
            "sortBy": "relevance",
        }
        try:
            text = await get_text(client, ARXIV_URL, params=params)
            root = ET.fromstring(text)
            entries = root.findall("atom:entry", ATOM_NS)
            return SourceResult(
                source=self.source,
                query=query,
                items=trim_items([self._item(entry) for entry in entries], limit),
            )
        except Exception as exc:
            return warn_result(self.source, query, f"arxiv failed: {type(exc).__name__}: {exc}")

    def _text(self, entry: ET.Element, name: str) -> str:
        node = entry.find(f"atom:{name}", ATOM_NS)
        return node.text.strip() if node is not None and node.text else ""

    def _item(self, entry: ET.Element) -> SearchItem:
        title = self._text(entry, "title")
        url = self._text(entry, "id")
        authors = [node.text for node in entry.findall("atom:author/atom:name", ATOM_NS) if node.text]
        return SearchItem(
            title=compact_text(title, max_length=180) or "arXiv paper",
            url=url,
            source=self.source,
            artifact_type="paper",
            summary=compact_text(self._text(entry, "summary")),
            signals=Signals(last_updated=self._text(entry, "updated")),
            raw={"published": self._text(entry, "published"), "authors": authors},
        )
