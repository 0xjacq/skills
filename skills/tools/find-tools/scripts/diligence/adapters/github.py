from __future__ import annotations

import asyncio
import os
import time
from typing import Any

import httpx

from diligence.adapters.base import Adapter, trim_items, warn_result
from diligence.models import SearchItem, Signals, SourceResult
from diligence.normalize import compact_text

API_URL = "https://api.github.com/search/repositories"
MAX_RATE_LIMIT_WAIT_SECONDS = 60


class GitHubAdapter(Adapter):
    source = "github"

    async def search(self, client: httpx.AsyncClient, query: str, limit: int) -> SourceResult:
        headers: dict[str, str] = {}
        token = os.getenv("GITHUB_TOKEN")
        if token:
            headers["Authorization"] = f"Bearer {token}"
        params = {
            "q": f"{query} in:name,description,readme",
            "per_page": max(1, min(limit, 50)),
        }
        try:
            payload, warnings = await self._search_with_rate_limit_retry(client, params=params, headers=headers)
            items = [self._item(raw) for raw in payload.get("items", []) if isinstance(raw, dict)]
            return SourceResult(source=self.source, query=query, items=trim_items(items, limit), warnings=warnings)
        except Exception as exc:
            return warn_result(self.source, query, f"github failed: {type(exc).__name__}: {exc}")

    async def _search_with_rate_limit_retry(
        self,
        client: httpx.AsyncClient,
        *,
        params: dict[str, Any],
        headers: dict[str, str],
    ) -> tuple[dict[str, Any], list[str]]:
        warnings: list[str] = []
        try:
            return await self._search_once(client, params=params, headers=headers), warnings
        except httpx.HTTPStatusError as exc:
            if not self._is_search_rate_limit(exc):
                raise

            wait_seconds = self._rate_limit_wait_seconds(exc.response)
            if wait_seconds <= 0:
                raise

            warnings.append(
                f"github search rate limit reached; waiting {wait_seconds}s for quota reset before retrying."
            )
            await asyncio.sleep(wait_seconds)
            return await self._search_once(client, params=params, headers=headers), warnings

    async def _search_once(
        self,
        client: httpx.AsyncClient,
        *,
        params: dict[str, Any],
        headers: dict[str, str],
    ) -> dict[str, Any]:
        response = await client.get(API_URL, params=params, headers=headers)
        response.raise_for_status()
        return response.json()

    def _is_search_rate_limit(self, exc: httpx.HTTPStatusError) -> bool:
        response = exc.response
        if response.status_code != 403:
            return False
        resource = response.headers.get("x-ratelimit-resource", "")
        body = response.text.lower()
        return resource == "search" and "rate limit" in body

    def _rate_limit_wait_seconds(self, response: httpx.Response) -> int:
        reset_header = response.headers.get("x-ratelimit-reset")
        if not reset_header:
            return 0
        try:
            reset_epoch = int(reset_header)
        except ValueError:
            return 0
        remaining = max(0, reset_epoch - int(time.time()))
        if remaining <= 0:
            return 1
        return min(remaining, MAX_RATE_LIMIT_WAIT_SECONDS)

    def _item(self, raw: dict[str, Any]) -> SearchItem:
        license_data = raw.get("license") if isinstance(raw.get("license"), dict) else {}
        return SearchItem(
            title=str(raw.get("full_name") or raw.get("name") or "GitHub repository"),
            url=str(raw.get("html_url") or ""),
            source=self.source,
            artifact_type="repo",
            summary=compact_text(str(raw.get("description") or "")),
            signals=Signals(
                stars=raw.get("stargazers_count"),
                forks=raw.get("forks_count"),
                last_updated=raw.get("updated_at"),
                license=license_data.get("spdx_id"),
            ),
            raw={
                "language": raw.get("language"),
                "topics": raw.get("topics", []),
                "open_issues": raw.get("open_issues_count"),
                "pushed_at": raw.get("pushed_at"),
            },
        )
