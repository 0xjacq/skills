from __future__ import annotations

import argparse
import importlib.util
import re
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_FILES = sorted(REPO_ROOT.glob("skills/*/*/SKILL.md"))
INGEST_SKILL = REPO_ROOT / "skills" / "agenpedia" / "ingest" / "SKILL.md"
INGEST_BATCH_SKILL = REPO_ROOT / "skills" / "agenpedia" / "ingest-batch" / "SKILL.md"
INGEST_YOUTUBE_SKILL = REPO_ROOT / "skills" / "agenpedia" / "ingest-youtube" / "SKILL.md"
QUERY_SKILL = REPO_ROOT / "skills" / "agenpedia" / "query" / "SKILL.md"
LINT_SKILL = REPO_ROOT / "skills" / "agenpedia" / "lint" / "SKILL.md"
INGEST_YOUTUBE_SCRIPT = (
    REPO_ROOT
    / "skills"
    / "agenpedia"
    / "ingest-youtube"
    / "scripts"
    / "fetch_youtube_transcript.py"
)


def read_frontmatter(skill_path: Path) -> dict[str, str]:
    text = skill_path.read_text(encoding="utf-8")
    match = re.match(r"---\n(.*?)\n---\n", text, re.DOTALL)
    assert match is not None, f"{skill_path} is missing YAML frontmatter"

    fields: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if not line.strip():
            continue
        key, separator, value = line.partition(":")
        assert separator == ":", f"{skill_path} has malformed frontmatter line: {line!r}"
        fields[key.strip()] = value.strip().strip('"')
    return fields


def read_openai_yaml(metadata_path: Path) -> dict[str, dict[str, str]]:
    sections: dict[str, dict[str, str]] = {}
    current_section: str | None = None

    for raw_line in metadata_path.read_text(encoding="utf-8").splitlines():
        if not raw_line.strip():
            continue
        if not raw_line.startswith(" "):
            key = raw_line.rstrip(":").strip()
            sections[key] = {}
            current_section = key
            continue

        assert current_section is not None, f"{metadata_path} contains nested data before a section header"
        key, separator, value = raw_line.strip().partition(":")
        assert separator == ":", f"{metadata_path} has malformed YAML line: {raw_line!r}"
        sections[current_section][key.strip()] = value.strip().strip('"')

    return sections


def load_ingest_youtube_module():
    spec = importlib.util.spec_from_file_location("test_fetch_youtube_transcript", INGEST_YOUTUBE_SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_skills_ship_required_metadata_and_policy_alignment():
    assert SKILL_FILES, "expected repo skills to exist"

    for skill_path in SKILL_FILES:
        frontmatter = read_frontmatter(skill_path)
        assert {"name", "description", "disable-model-invocation", "user-invocable"} <= frontmatter.keys()
        assert frontmatter["name"]
        assert frontmatter["description"]
        assert len(skill_path.read_text(encoding="utf-8").splitlines()) <= 500

        metadata_path = skill_path.parent / "agents" / "openai.yaml"
        assert metadata_path.is_file(), f"{skill_path} is missing agents/openai.yaml"

        metadata = read_openai_yaml(metadata_path)
        assert metadata["interface"]["display_name"]
        assert metadata["interface"]["short_description"]

        allow_implicit = metadata["policy"]["allow_implicit_invocation"].lower() == "true"
        disable_model_invocation = frontmatter["disable-model-invocation"].lower() == "true"
        assert allow_implicit == (not disable_model_invocation)


def test_ingest_skill_documents_anti_overcompression_rules():
    text = INGEST_SKILL.read_text(encoding="utf-8")
    lowered = text.lower()

    assert "## Step 2b: Assess Source Density and Compression Strategy" in text
    assert "low repetition" in lowered
    assert "high ratio of mechanisms, arguments, or frameworks to filler" in lowered
    assert "reusable lists, checklists, matrices, or distinctions" in lowered
    assert "examples that explain mechanism rather than merely illustrate it" in lowered
    assert "section structure that is already operationally useful" in lowered
    assert "high-fidelity synthesis" in lowered
    assert "do not choose page length by matching prior wiki averages" in lowered
    assert "repo-local" in lowered
    assert "instructions still win" in lowered


def test_agenpedia_follow_on_skills_propagate_anti_overcompression_rules():
    batch_text = " ".join(INGEST_BATCH_SKILL.read_text(encoding="utf-8").lower().split())
    youtube_text = " ".join(INGEST_YOUTUBE_SKILL.read_text(encoding="utf-8").lower().split())
    query_text = " ".join(QUERY_SKILL.read_text(encoding="utf-8").lower().split())
    lint_text = " ".join(LINT_SKILL.read_text(encoding="utf-8").lower().split())

    assert "do not normalize batch" in batch_text
    assert "likely high-fidelity" in batch_text

    assert "step 2b source-density check and compression mode" in youtube_text
    assert "do not pre-compress long transcripts at this adapter layer" in youtube_text
    assert "thin summary" in youtube_text

    assert "high-fidelity synthesis" in query_text
    assert "do not collapse a rich cross-page answer into a thin executive summary" in query_text

    assert "### 6. undercompressed syntheses" in lint_text
    assert "thin executive summaries" in lint_text
    assert "auto-fix in auto-maintenance mode only when the missing structure is explicit and source-grounded" in lint_text


def test_ingest_youtube_default_output_targets_repo_root_raw(tmp_path, monkeypatch, capsys):
    module = load_ingest_youtube_module()
    fake_script = tmp_path / "repo" / "skills" / "agenpedia" / "ingest-youtube" / "scripts" / "fetch_youtube_transcript.py"
    fake_script.parent.mkdir(parents=True, exist_ok=True)
    module.__file__ = str(fake_script)

    temp_dir = tmp_path / "yt2txt-output"
    temp_dir.mkdir()
    transcript_path = temp_dir / "output.txt"
    transcript_path.write_text("Transcript body\n", encoding="utf-8")

    monkeypatch.setattr(
        module,
        "parse_args",
        lambda: argparse.Namespace(
            url="https://youtu.be/AbC123xyz89",
            raw_dir="raw",
            cli_path="yt2txt.sh",
            keep_temp=False,
        ),
    )
    monkeypatch.setattr(module, "resolve_cli", lambda _cli_path: "/bin/echo")
    monkeypatch.setattr(
        module,
        "run_yt2txt",
        lambda cli, url, output_dir: subprocess.CompletedProcess([cli, url], 0, "", ""),
    )
    monkeypatch.setattr(module, "find_transcript", lambda _output_dir: transcript_path)
    monkeypatch.setattr(module.tempfile, "mkdtemp", lambda prefix: str(temp_dir))

    assert module.main() == 0

    created_path = tmp_path / "repo" / "raw" / "youtube-abc123xyz89.md"
    assert created_path.is_file()
    assert capsys.readouterr().out.strip() == "raw/youtube-abc123xyz89.md"


def test_ingest_youtube_relative_raw_dir_resolves_from_repo_root(tmp_path, monkeypatch, capsys):
    module = load_ingest_youtube_module()
    fake_script = tmp_path / "repo" / "skills" / "agenpedia" / "ingest-youtube" / "scripts" / "fetch_youtube_transcript.py"
    fake_script.parent.mkdir(parents=True, exist_ok=True)
    module.__file__ = str(fake_script)

    temp_dir = tmp_path / "yt2txt-output"
    temp_dir.mkdir()
    transcript_path = temp_dir / "output.txt"
    transcript_path.write_text("Transcript body\n", encoding="utf-8")

    monkeypatch.setattr(
        module,
        "parse_args",
        lambda: argparse.Namespace(
            url="https://www.youtube.com/watch?v=Video123",
            raw_dir="raw/custom",
            cli_path="yt2txt.sh",
            keep_temp=False,
        ),
    )
    monkeypatch.setattr(module, "resolve_cli", lambda _cli_path: "/bin/echo")
    monkeypatch.setattr(
        module,
        "run_yt2txt",
        lambda cli, url, output_dir: subprocess.CompletedProcess([cli, url], 0, "", ""),
    )
    monkeypatch.setattr(module, "find_transcript", lambda _output_dir: transcript_path)
    monkeypatch.setattr(module.tempfile, "mkdtemp", lambda prefix: str(temp_dir))

    assert module.main() == 0

    created_path = tmp_path / "repo" / "raw" / "custom" / "youtube-video123.md"
    assert created_path.is_file()
    assert capsys.readouterr().out.strip() == "raw/custom/youtube-video123.md"


def test_ingest_youtube_run_yt2txt_relies_on_backend_defaults(monkeypatch, tmp_path):
    module = load_ingest_youtube_module()
    captured: dict[str, object] = {}

    def fake_run(*args, **kwargs):
        captured["args"] = args[0]
        captured["kwargs"] = kwargs
        return subprocess.CompletedProcess(args[0], 0, "", "")

    monkeypatch.setattr(module.subprocess, "run", fake_run)

    output_dir = tmp_path / "yt2txt-output"
    result = module.run_yt2txt("/usr/local/bin/yt2txt.sh", "https://youtu.be/AbC123xyz89", output_dir)

    assert result.returncode == 0
    assert captured["args"] == [
        "/usr/local/bin/yt2txt.sh",
        "https://youtu.be/AbC123xyz89",
        "--output",
        str(output_dir),
    ]
    assert "--markers" not in captured["args"]
