from __future__ import annotations

from abc import ABC, abstractmethod

import httpx

from diligence.models import SearchItem, SourceName, SourceResult


class Adapter(ABC):
    source: SourceName

    @abstractmethod
    async def search(self, client: httpx.AsyncClient, query: str, limit: int) -> SourceResult:
        raise NotImplementedError


def warn_result(source: SourceName, query: str, message: str) -> SourceResult:
    return SourceResult(source=source, query=query, items=[], warnings=[message])


def trim_items(items: list[SearchItem], limit: int) -> list[SearchItem]:
    return items[: max(limit, 0)]
