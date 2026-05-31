from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import unicodedata
from datetime import datetime, timezone
from html import escape
from pathlib import Path
from typing import Any


EXPECTED_SCHEMA_VERSION = 1
SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_HUB_TITLE = "Study Hub"
DEFAULT_LIBRARY_DIR = "library"
DEFAULT_CATALOG_PATH = "library/catalog.json"


class HubValidationError(ValueError):
    """Raised when the target directory is not a compatible study hub repo."""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Publish a study-sheet HTML artifact into a study hub repo clone.")
    parser.add_argument("--hub-dir", required=True, help="Path to a local clone of the study hub repo.")
    parser.add_argument("--html", required=True, help="Path to the generated study-sheet HTML artifact.")
    parser.add_argument("--title", help="Optional title override.")
    parser.add_argument("--summary", help="Optional summary override.")
    parser.add_argument("--source-kind", help="Optional source kind override.")
    parser.add_argument("--tag", action="append", default=[], help="Optional repeated tag override.")
    parser.add_argument("--commit", action="store_true", help="Create a local git commit after publishing.")
    parser.add_argument("--push", action="store_true", help="Push the commit to the configured remote after publishing.")
    return parser.parse_args()


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def slugify(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii").lower()
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_text).strip("-")
    return slug or "study-sheet"


def extract_metadata_from_html(html_text: str, html_path: Path) -> dict[str, Any]:
    match = re.search(
        r'<script[^>]+id=["\']study-sheet-data["\'][^>]*>(.*?)</script>',
        html_text,
        flags=re.IGNORECASE | re.DOTALL,
    )
    payload: dict[str, Any] = {}
    if match:
        payload = json.loads(match.group(1).strip())

    document = payload.get("document") if isinstance(payload.get("document"), dict) else {}
    title = first_nonempty(
        document.get("title"),
        extract_tag_text(html_text, "h1"),
        extract_tag_text(html_text, "title"),
        html_path.stem,
        "Study Sheet",
    )
    summary = first_nonempty(
        document.get("summary"),
        extract_first_paragraph(html_text),
        "Study notes",
    )
    raw_tags = document.get("tags")
    tags = [str(tag).strip() for tag in raw_tags if str(tag).strip()] if isinstance(raw_tags, list) else []
    source_kind = first_nonempty(document.get("source_kind"), "html")
    return {
        "title": title,
        "summary": summary,
        "tags": tags,
        "source_kind": source_kind,
    }


def first_nonempty(*values: Any) -> str:
    for value in values:
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def extract_tag_text(html_text: str, tag_name: str) -> str:
    match = re.search(rf"<{tag_name}[^>]*>(.*?)</{tag_name}>", html_text, flags=re.IGNORECASE | re.DOTALL)
    if not match:
        return ""
    return strip_html(match.group(1))


def extract_first_paragraph(html_text: str) -> str:
    match = re.search(r"<p[^>]*>(.*?)</p>", html_text, flags=re.IGNORECASE | re.DOTALL)
    if not match:
        return ""
    return strip_html(match.group(1))


def strip_html(value: str) -> str:
    without_tags = re.sub(r"<[^>]+>", " ", value)
    collapsed = re.sub(r"\s+", " ", without_tags)
    return collapsed.strip()


def load_json_file(path: Path, description: str) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise HubValidationError(f"Missing {description}: {path}") from exc
    except json.JSONDecodeError as exc:
        raise HubValidationError(f"Invalid JSON in {description}: {path}") from exc


def validate_hub_dir(hub_dir: Path) -> dict[str, Any]:
    sentinel_path = hub_dir / ".study-hub.json"
    sentinel = load_json_file(sentinel_path, ".study-hub.json")
    if not isinstance(sentinel, dict):
        raise HubValidationError("Hub sentinel must be a JSON object.")

    schema_version = sentinel.get("schema_version")
    if schema_version != EXPECTED_SCHEMA_VERSION:
        raise HubValidationError(
            f"Unsupported hub schema version {schema_version!r}; expected {EXPECTED_SCHEMA_VERSION}."
        )

    library_dir = hub_dir / str(sentinel.get("library_dir") or DEFAULT_LIBRARY_DIR)
    catalog_path = hub_dir / str(sentinel.get("catalog_path") or DEFAULT_CATALOG_PATH)
    index_path = hub_dir / str(sentinel.get("index_path") or "index.html")
    hub_title = str(sentinel.get("hub_title") or DEFAULT_HUB_TITLE)

    if not library_dir.is_dir():
        raise HubValidationError(f"Hub library directory is missing: {library_dir}")

    catalog = load_json_file(catalog_path, "catalog.json")
    if not isinstance(catalog, list):
        raise HubValidationError("Hub catalog must be a JSON array.")

    return {
        "hub_dir": hub_dir,
        "library_dir": library_dir,
        "catalog_path": catalog_path,
        "index_path": index_path,
        "hub_title": hub_title,
        "catalog": catalog,
    }


def unique_slug(base_slug: str, catalog: list[dict[str, Any]]) -> str:
    existing = {str(entry.get("slug", "")).strip() for entry in catalog}
    if base_slug not in existing:
        return base_slug

    index = 2
    while f"{base_slug}-{index}" in existing:
        index += 1
    return f"{base_slug}-{index}"


def render_hub_index(catalog: list[dict[str, Any]], hub_title: str) -> str:
    sorted_catalog = sorted(catalog, key=lambda entry: str(entry.get("updated_at", "")), reverse=True)
    count = len(sorted_catalog)
    entries_html = "\n".join(render_library_item(entry) for entry in sorted_catalog)
    if not entries_html:
        entries_html = """
          <section class="empty-state">
            <h2>No study sheets yet</h2>
            <p>Publish the first HTML artifact with <code>publish_to_hub.py</code> to populate this library.</p>
          </section>
"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{escape(hub_title)}</title>
  <style>
    :root {{
      --bg: #f8f3ea;
      --fg: #17120e;
      --muted: #62564a;
      --line: #d2c3b1;
      --accent: #7b4a2d;
      --accent-soft: #e6d7c5;
      --sans: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      --serif: "Iowan Old Style", "Palatino Linotype", "Book Antiqua", Palatino, Georgia, serif;
      --mono: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
      --max: 78rem;
    }}

    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: var(--bg);
      color: var(--fg);
      font-family: var(--serif);
      line-height: 1.55;
    }}

    .page {{
      max-width: var(--max);
      margin: 0 auto;
      padding: 2rem 1.25rem 5rem;
    }}

    header {{
      border-bottom: 1px solid var(--line);
      margin-bottom: 2rem;
      padding-bottom: 1rem;
    }}

    .eyebrow,
    .meta,
    .tag,
    .library-item time {{
      font-family: var(--sans);
    }}

    .eyebrow {{
      color: var(--accent);
      letter-spacing: 0.06em;
      font-size: 0.78rem;
      text-transform: uppercase;
    }}

    h1, h2, h3 {{
      font-weight: 500;
      line-height: 1.1;
      margin: 0 0 0.75rem;
    }}

    h1 {{ font-size: 2.5rem; }}
    h2 {{ font-size: 1.35rem; margin-top: 0; }}
    p {{ margin: 0 0 1rem; }}
    .meta {{ color: var(--muted); }}

    .summary {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(11rem, 1fr));
      gap: 0.85rem;
      margin-top: 1.5rem;
    }}

    .summary-card {{
      border: 1px solid var(--line);
      background: #fdf9f2;
      padding: 0.9rem 1rem;
    }}

    .summary-card strong {{
      display: block;
      font-family: var(--sans);
      font-size: 0.8rem;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: var(--muted);
      margin-bottom: 0.4rem;
    }}

    .library {{
      display: grid;
      gap: 1rem;
    }}

    .library-item {{
      border: 1px solid var(--line);
      background: #fdf9f2;
      padding: 1.1rem 1.2rem;
    }}

    .library-item h2 a {{
      color: inherit;
      text-decoration: none;
    }}

    .library-item h2 a:hover {{
      color: var(--accent);
    }}

    .item-meta {{
      color: var(--muted);
      display: flex;
      flex-wrap: wrap;
      gap: 0.7rem;
      margin-bottom: 0.75rem;
      font-size: 0.95rem;
    }}

    .tags {{
      display: flex;
      flex-wrap: wrap;
      gap: 0.45rem;
      margin-top: 0.8rem;
    }}

    .tag {{
      border: 1px solid var(--line);
      border-radius: 999px;
      padding: 0.22rem 0.6rem;
      background: var(--accent-soft);
      font-size: 0.82rem;
    }}

    code {{
      font-family: var(--mono);
      background: #eee3d4;
      border: 1px solid #dccab5;
      border-radius: 0.2rem;
      padding: 0.08rem 0.28rem;
    }}

    .empty-state {{
      border: 1px dashed var(--line);
      padding: 1.25rem;
      background: rgba(255, 255, 255, 0.42);
    }}

    @media (max-width: 720px) {{
      .page {{ padding: 1.5rem 1rem 4rem; }}
      h1 {{ font-size: 2rem; }}
    }}
  </style>
</head>
<body>
  <div class="page">
    <header>
      <p class="eyebrow">Private Study Hub</p>
      <h1>{escape(hub_title)}</h1>
      <p class="meta">A self-contained library of HTML learning sheets published from <code>txt-to-html-srs</code>.</p>
      <div class="summary">
        <section class="summary-card">
          <strong>Sheets</strong>
          <span>{count}</span>
        </section>
        <section class="summary-card">
          <strong>Source of truth</strong>
          <span><code>library/catalog.json</code></span>
        </section>
        <section class="summary-card">
          <strong>Layout</strong>
          <span><code>index.html</code> + <code>library/</code></span>
        </section>
      </div>
    </header>

    <main class="library">
{entries_html}
    </main>
  </div>
</body>
</html>
"""


def render_library_item(entry: dict[str, Any]) -> str:
    title = escape(str(entry.get("title", "Untitled study sheet")))
    path = escape(str(entry.get("path", "")))
    summary = escape(str(entry.get("summary", "")))
    updated_at = escape(str(entry.get("updated_at", "")))
    source_kind = escape(str(entry.get("source_kind", "html")))
    tags = entry.get("tags") if isinstance(entry.get("tags"), list) else []
    tags_html = "".join(f'<span class="tag">{escape(str(tag))}</span>' for tag in tags if str(tag).strip())
    return f"""      <article class="library-item">
        <h2><a href="{path}">{title}</a></h2>
        <div class="item-meta">
          <time datetime="{updated_at}">Updated {updated_at}</time>
          <span>Source: {source_kind}</span>
        </div>
        <p>{summary}</p>
        <div class="tags">{tags_html}</div>
      </article>"""


def write_catalog(catalog_path: Path, catalog: list[dict[str, Any]]) -> None:
    catalog_path.write_text(json.dumps(catalog, indent=2) + "\n", encoding="utf-8")


def git_run(hub_dir: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], cwd=hub_dir, check=True, text=True, capture_output=True)


def publish_to_hub(
    *,
    hub_dir: Path,
    html_path: Path,
    title: str | None = None,
    summary: str | None = None,
    tags: list[str] | None = None,
    source_kind: str | None = None,
    commit: bool = False,
    push: bool = False,
) -> dict[str, Any]:
    validated = validate_hub_dir(hub_dir)
    html_text = html_path.read_text(encoding="utf-8")
    metadata = extract_metadata_from_html(html_text, html_path)
    if title:
        metadata["title"] = title.strip()
    if summary:
        metadata["summary"] = summary.strip()
    if tags is not None and tags:
        metadata["tags"] = [tag.strip() for tag in tags if tag.strip()]
    if source_kind:
        metadata["source_kind"] = source_kind.strip()

    slug = unique_slug(slugify(metadata["title"]), validated["catalog"])
    published_path = validated["library_dir"] / f"{slug}.html"
    shutil.copyfile(html_path, published_path)

    timestamp = now_utc()
    relative_path = published_path.relative_to(hub_dir).as_posix()
    entry = {
        "slug": slug,
        "title": metadata["title"],
        "summary": metadata["summary"],
        "tags": metadata["tags"],
        "created_at": timestamp,
        "updated_at": timestamp,
        "path": relative_path,
        "source_kind": metadata["source_kind"],
    }
    catalog = [*validated["catalog"], entry]
    write_catalog(validated["catalog_path"], catalog)
    validated["index_path"].write_text(render_hub_index(catalog, validated["hub_title"]), encoding="utf-8")

    commit_message = ""
    if push:
        commit = True
    if commit:
        git_run(hub_dir, "add", relative_path, validated["catalog_path"].relative_to(hub_dir).as_posix(), validated["index_path"].relative_to(hub_dir).as_posix())
        commit_message = f"Add study sheet: {metadata['title']}"
        git_run(hub_dir, "commit", "-m", commit_message)
    if push:
        git_run(hub_dir, "push")

    return {
        "slug": slug,
        "published_path": str(published_path),
        "catalog_path": str(validated["catalog_path"]),
        "index_path": str(validated["index_path"]),
        "commit_message": commit_message,
    }


def main() -> int:
    args = parse_args()
    result = publish_to_hub(
        hub_dir=Path(args.hub_dir).expanduser().resolve(),
        html_path=Path(args.html).expanduser().resolve(),
        title=args.title,
        summary=args.summary,
        tags=args.tag,
        source_kind=args.source_kind,
        commit=args.commit,
        push=args.push,
    )
    json.dump(result, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
