from __future__ import annotations

import re
from urllib.parse import urlsplit, urlunsplit


def canonical_url(url: str) -> str:
    if not url:
        return url
    if url.startswith("//"):
        url = "https:" + url
    parts = urlsplit(url)
    if not parts.scheme:
        url = "https://" + url
        parts = urlsplit(url)
    netloc = parts.netloc.lower()
    if netloc.startswith("www."):
        netloc = netloc[4:]
    path = re.sub(r"/+$", "", parts.path)
    return urlunsplit((parts.scheme.lower(), netloc, path, "", ""))


def compact_text(value: str | None, *, max_length: int = 500) -> str:
    text = re.sub(r"\s+", " ", value or "").strip()
    if len(text) <= max_length:
        return text
    return text[: max_length - 1].rstrip() + "..."


def tokenize(text: str) -> set[str]:
    return {t for t in re.findall(r"[a-z0-9][a-z0-9._-]{1,}", text.lower()) if len(t) > 2}


def lexical_score(query: str, *fields: str) -> float:
    q = tokenize(query)
    if not q:
        return 0.0
    haystack = tokenize(" ".join(fields))
    if not haystack:
        return 0.0
    return len(q & haystack) / len(q)


def dedupe_items(items):
    seen: set[tuple[str, str]] = set()
    deduped = []
    for item in items:
        key = (item.source, canonical_url(item.url))
        if key in seen:
            continue
        seen.add(key)
        deduped.append(item)
    return deduped
