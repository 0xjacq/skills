from __future__ import annotations

import re
from typing import Any

import httpx

from diligence.adapters.base import Adapter, trim_items, warn_result
from diligence.http import get_json
from diligence.models import SearchItem, Signals, SourceResult
from diligence.normalize import compact_text, lexical_score

INDEX_URL = "https://tom-doerr.github.io/repo_posts/assets/search-index.json"
BASE_URL = "https://tom-doerr.github.io/repo_posts"
MARKDOWN_LINK_RE = re.compile(r"\[([^\]]+)\]\((https?://[^)]+)\)")


def _entry_url(entry: dict[str, Any]) -> tuple[str, str]:
    title = str(entry.get("title") or entry.get("t") or "")
    match = MARKDOWN_LINK_RE.search(title)
    if match:
        return match.group(1).strip(), match.group(2).strip()

    path = str(entry.get("url") or entry.get("u") or "").strip()
    if path.startswith("http"):
        return title, path
    if path.startswith("/"):
        return title, BASE_URL + path
    return title, f"{BASE_URL}/{path}" if path else BASE_URL


def items_from_index(entries: list[dict[str, Any]], query: str, limit: int) -> list[SearchItem]:
    scored: list[tuple[float, SearchItem]] = []
    for entry in entries:
        title, url = _entry_url(entry)
        summary = compact_text(str(entry.get("summary") or entry.get("s") or entry.get("description") or ""))
        score = lexical_score(query, title, summary)
        if score <= 0:
            continue
        scored.append(
            (
                score,
                SearchItem(
                    title=compact_text(title, max_length=160) or "repo_posts entry",
                    url=url,
                    source="repo_posts",
                    artifact_type="repo",
                    summary=summary,
                    signals=Signals(),
                    raw={"lexical_score": score, "entry": entry},
                ),
            )
        )
    scored.sort(key=lambda pair: pair[0], reverse=True)
    return trim_items([item for _, item in scored], limit)


class RepoPostsAdapter(Adapter):
    source = "repo_posts"

    async def search(self, client: httpx.AsyncClient, query: str, limit: int) -> SourceResult:
        try:
            payload = await get_json(client, INDEX_URL)
            entries = payload if isinstance(payload, list) else payload.get("documents", [])
            if not isinstance(entries, list):
                return warn_result(self.source, query, "repo_posts returned an unexpected index shape")
            return SourceResult(source=self.source, query=query, items=items_from_index(entries, query, limit))
        except Exception as exc:
            return warn_result(self.source, query, f"repo_posts failed: {type(exc).__name__}: {exc}")
