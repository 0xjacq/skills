from __future__ import annotations

import asyncio
import os
from urllib.parse import urlsplit

import httpx

from diligence.normalize import canonical_url, compact_text
from prebuild_engine.models import EvidenceKind, ExaSearchHit

EXA_SEARCH_URL = "https://api.exa.ai/search"
DISCUSSION_HOSTS = ("news.ycombinator.com", "reddit.com", "lobste.rs", "stackoverflow.com")
SECONDARY_HOSTS = (
    "futurepedia.io",
    "producthunt.com",
    "g2.com",
    "capterra.com",
    "alternative.to",
    "theresanaiforthat.com",
)


async def search_exa(
    queries: list[dict[str, str]],
    *,
    num_results: int = 5,
    client_factory: callable | None = None,
    api_key: str | None = None,
) -> tuple[list[ExaSearchHit], list[str]]:
    key = api_key or os.getenv("EXA_API_KEY")
    if not key:
        return [], ["EXA_API_KEY is not set; Exa-first discovery was skipped."]

    async def _default_client() -> httpx.AsyncClient:
        return httpx.AsyncClient(timeout=httpx.Timeout(20.0, connect=10.0), follow_redirects=True)

    factory = client_factory or _default_client
    async with await factory() as client:
        tasks = [
            asyncio.create_task(_search_once(client, query_spec, key=key, num_results=num_results))
            for query_spec in queries
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

    hits: list[ExaSearchHit] = []
    warnings: list[str] = []
    seen_urls: set[str] = set()
    for query_spec, result in zip(queries, results, strict=False):
        if isinstance(result, Exception):
            warnings.append(
                f"Exa search failed for `{query_spec['family']}`: {type(result).__name__}: {result}"
            )
            continue
        for hit in result:
            url_key = canonical_url(hit.url)
            if url_key in seen_urls:
                continue
            seen_urls.add(url_key)
            hits.append(hit)
    return hits, warnings


async def _search_once(
    client: httpx.AsyncClient,
    query_spec: dict[str, str],
    *,
    key: str,
    num_results: int,
) -> list[ExaSearchHit]:
    response = await client.post(
        EXA_SEARCH_URL,
        headers={"x-api-key": key, "accept": "application/json", "content-type": "application/json"},
        json={
            "query": query_spec["query"],
            "type": "auto",
            "numResults": num_results,
            "contents": {"highlights": {"maxCharacters": 500}},
        },
    )
    response.raise_for_status()
    payload = response.json()
    return [
        ExaSearchHit(
            query_family=query_spec["family"],
            query=query_spec["query"],
            title=item.get("title") or item.get("url") or "Untitled result",
            url=item["url"],
            summary=compact_text(" ".join(item.get("highlights") or []), max_length=320),
            published_date=item.get("publishedDate"),
            author=item.get("author"),
            score=item.get("score"),
            evidence_kind=_classify_url(item["url"]),
        )
        for item in payload.get("results", [])
        if item.get("url")
    ]


def _classify_url(url: str) -> EvidenceKind:
    host = urlsplit(url).netloc.lower()
    if host.startswith("www."):
        host = host[4:]
    if any(host.endswith(name) for name in DISCUSSION_HOSTS):
        return "discussion"
    if any(host.endswith(name) for name in SECONDARY_HOSTS):
        return "secondary"
    return "primary"

