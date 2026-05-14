from __future__ import annotations

from pathlib import Path
from typing import Any

import httpx

USER_AGENT = "prebuild-diligence-engine/0.1 (+https://github.com/local/prebuild-diligence-engine)"


def cache_dir() -> Path:
    root = Path.cwd() / ".cache" / "diligence" / "http"
    root.mkdir(parents=True, exist_ok=True)
    return root


def async_client() -> httpx.AsyncClient:
    headers = {"User-Agent": USER_AGENT, "Accept": "application/json, text/plain;q=0.9, */*;q=0.8"}
    timeout = httpx.Timeout(12.0, connect=8.0)
    try:
        from hishel import AsyncSqliteStorage
        from hishel.httpx import AsyncCacheTransport

        transport = AsyncCacheTransport(
            next_transport=httpx.AsyncHTTPTransport(retries=1),
            storage=AsyncSqliteStorage(base_path=cache_dir()),
        )
        return httpx.AsyncClient(headers=headers, timeout=timeout, transport=transport, follow_redirects=True)
    except Exception:
        transport = httpx.AsyncHTTPTransport(retries=1)
        return httpx.AsyncClient(headers=headers, timeout=timeout, transport=transport, follow_redirects=True)


async def get_json(client: httpx.AsyncClient, url: str, **kwargs: Any) -> Any:
    response = await client.get(url, **kwargs)
    response.raise_for_status()
    return response.json()


async def get_text(client: httpx.AsyncClient, url: str, **kwargs: Any) -> str:
    response = await client.get(url, **kwargs)
    response.raise_for_status()
    return response.text
