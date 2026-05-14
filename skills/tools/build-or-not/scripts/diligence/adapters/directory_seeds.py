from __future__ import annotations

from urllib.parse import quote_plus

import httpx

from diligence.adapters.base import Adapter
from diligence.models import SearchItem, SourceResult


class DirectorySeedsAdapter(Adapter):
    source = "directory_seeds"

    async def search(self, client: httpx.AsyncClient, query: str, limit: int) -> SourceResult:
        del client
        encoded = quote_plus(query)
        templates = [
            ("repo_posts search", f"https://tom-doerr.github.io/repo_posts/?q={encoded}"),
            ("There's An AI For That search", f"https://theresanaiforthat.com/s/{encoded}/"),
            ("Futurepedia search", f"https://www.futurepedia.io/?search={encoded}"),
            ("IdeaSearch search", f"https://ideasearch.ai/?q={encoded}"),
            ("Product Hunt search", f"https://www.producthunt.com/search?q={encoded}"),
            ("Hacker News Search", f"https://hn.algolia.com/?q={encoded}"),
        ]
        items = [
            SearchItem(
                title=title,
                url=url,
                source=self.source,
                artifact_type="directory_entry",
                summary="Seed URL for Codex Exa/Firecrawl deepening when direct API access is unavailable.",
                raw={"query": query, "use_with": ["exa", "firecrawl"]},
            )
            for title, url in templates[: max(0, limit)]
        ]
        return SourceResult(source=self.source, query=query, items=items)
