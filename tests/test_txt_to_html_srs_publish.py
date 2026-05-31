from __future__ import annotations

import importlib.util
import json
import subprocess
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
PUBLISH_SCRIPT = (
    REPO_ROOT
    / "skills"
    / "general"
    / "txt-to-html-srs"
    / "scripts"
    / "publish_to_hub.py"
)
HUB_TEMPLATE_ROOT = (
    REPO_ROOT
    / "skills"
    / "general"
    / "txt-to-html-srs"
    / "assets"
    / "study-hub-template"
)


def load_publish_module():
    spec = importlib.util.spec_from_file_location("test_publish_to_hub", PUBLISH_SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sample_study_sheet(title: str, summary: str, *, tags: list[str] | None = None) -> str:
    payload = {
        "document": {
            "title": title,
            "summary": summary,
            "tags": tags or ["memory", "fundamentals"],
            "source_kind": "markdown",
        },
        "flashcards": [
            {"front": "What matters?", "back": "Recall over recognition."},
        ],
    }
    return f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="utf-8" /><title>{title}</title></head>
<body>
  <article>
    <h1>{title}</h1>
    <p>{summary}</p>
  </article>
  <script id="study-sheet-data" type="application/json">{json.dumps(payload)}</script>
</body>
</html>
"""


def init_hub_repo(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "init"], cwd=path, check=True, capture_output=True, text=True)
    subprocess.run(["git", "config", "user.name", "Codex Tests"], cwd=path, check=True)
    subprocess.run(["git", "config", "user.email", "codex@example.com"], cwd=path, check=True)
    (path / ".study-hub.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "hub_title": "Study Hub",
                "library_dir": "library",
                "catalog_path": "library/catalog.json",
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    library_dir = path / "library"
    library_dir.mkdir()
    (library_dir / "catalog.json").write_text("[]\n", encoding="utf-8")
    (path / "index.html").write_text("<!DOCTYPE html><title>Empty</title>\n", encoding="utf-8")


def test_hub_template_assets_ship_required_files():
    assert HUB_TEMPLATE_ROOT.is_dir()
    assert (HUB_TEMPLATE_ROOT / ".study-hub.json").is_file()
    assert (HUB_TEMPLATE_ROOT / "index.html").is_file()
    assert (HUB_TEMPLATE_ROOT / "library").is_dir()
    assert (HUB_TEMPLATE_ROOT / "library" / "catalog.json").is_file()


def test_publish_to_hub_writes_html_updates_catalog_and_index(tmp_path):
    module = load_publish_module()
    hub_dir = tmp_path / "hub"
    init_hub_repo(hub_dir)

    html_path = tmp_path / "retrieval-practice.html"
    html_path.write_text(
        sample_study_sheet(
            "Retrieval Practice",
            "Active recall strengthens durable learning.",
            tags=["learning", "recall"],
        ),
        encoding="utf-8",
    )

    result = module.publish_to_hub(hub_dir=hub_dir, html_path=html_path)

    published_path = hub_dir / "library" / "retrieval-practice.html"
    assert published_path.is_file()
    assert result["slug"] == "retrieval-practice"
    assert result["published_path"] == str(published_path)

    catalog = json.loads((hub_dir / "library" / "catalog.json").read_text(encoding="utf-8"))
    assert [entry["slug"] for entry in catalog] == ["retrieval-practice"]
    assert catalog[0]["summary"] == "Active recall strengthens durable learning."
    assert catalog[0]["tags"] == ["learning", "recall"]

    index_html = (hub_dir / "index.html").read_text(encoding="utf-8")
    assert "Retrieval Practice" in index_html
    assert "library/retrieval-practice.html" in index_html
    assert "Active recall strengthens durable learning." in index_html


def test_publish_to_hub_disambiguates_slug_collisions(tmp_path):
    module = load_publish_module()
    hub_dir = tmp_path / "hub"
    init_hub_repo(hub_dir)

    first_html = tmp_path / "first.html"
    first_html.write_text(
        sample_study_sheet("Learning Loops", "First summary."),
        encoding="utf-8",
    )
    second_html = tmp_path / "second.html"
    second_html.write_text(
        sample_study_sheet("Learning Loops", "Second summary."),
        encoding="utf-8",
    )

    first_result = module.publish_to_hub(hub_dir=hub_dir, html_path=first_html)
    second_result = module.publish_to_hub(hub_dir=hub_dir, html_path=second_html)

    assert first_result["slug"] == "learning-loops"
    assert second_result["slug"] == "learning-loops-2"

    catalog = json.loads((hub_dir / "library" / "catalog.json").read_text(encoding="utf-8"))
    assert [entry["slug"] for entry in catalog] == ["learning-loops", "learning-loops-2"]


def test_publish_to_hub_rejects_missing_sentinel(tmp_path):
    module = load_publish_module()
    hub_dir = tmp_path / "hub"
    hub_dir.mkdir()
    html_path = tmp_path / "sheet.html"
    html_path.write_text(sample_study_sheet("Signal", "Noise"), encoding="utf-8")

    with pytest.raises(module.HubValidationError, match="\\.study-hub\\.json"):
        module.publish_to_hub(hub_dir=hub_dir, html_path=html_path)


def test_publish_to_hub_rejects_incompatible_schema(tmp_path):
    module = load_publish_module()
    hub_dir = tmp_path / "hub"
    init_hub_repo(hub_dir)
    (hub_dir / ".study-hub.json").write_text(
        json.dumps({"schema_version": 99}, indent=2) + "\n",
        encoding="utf-8",
    )
    html_path = tmp_path / "sheet.html"
    html_path.write_text(sample_study_sheet("Signal", "Noise"), encoding="utf-8")

    with pytest.raises(module.HubValidationError, match="schema"):
        module.publish_to_hub(hub_dir=hub_dir, html_path=html_path)


def test_publish_to_hub_can_commit_changes(tmp_path):
    module = load_publish_module()
    hub_dir = tmp_path / "hub"
    init_hub_repo(hub_dir)
    html_path = tmp_path / "sheet.html"
    html_path.write_text(
        sample_study_sheet("Chunking", "Grouping reduces cognitive load."),
        encoding="utf-8",
    )

    result = module.publish_to_hub(hub_dir=hub_dir, html_path=html_path, commit=True)

    log = subprocess.run(
        ["git", "log", "-1", "--pretty=%s"],
        cwd=hub_dir,
        check=True,
        capture_output=True,
        text=True,
    )
    assert log.stdout.strip() == "Add study sheet: Chunking"
    assert result["commit_message"] == "Add study sheet: Chunking"
