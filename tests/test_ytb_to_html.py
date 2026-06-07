from __future__ import annotations

import argparse
import importlib.util
import subprocess
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
YTB_TO_HTML_SCRIPT = (
    REPO_ROOT
    / "skills"
    / "general"
    / "ytb-to-html"
    / "scripts"
    / "fetch_youtube_transcript.py"
)


def load_ytb_to_html_module():
    spec = importlib.util.spec_from_file_location("test_ytb_to_html", YTB_TO_HTML_SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize(
    ("url", "expected"),
    [
        ("https://www.youtube.com/watch?v=Video123", "Video123"),
        ("https://www.youtube.com/watch?v=Video123&list=PLabc", "Video123"),
        ("https://youtu.be/AbC123xyz89", "AbC123xyz89"),
        ("https://www.youtube.com/shorts/Short123", "Short123"),
    ],
)
def test_extract_video_id_supports_common_single_video_urls(url, expected):
    module = load_ytb_to_html_module()
    assert module.extract_video_id(url) == expected


@pytest.mark.parametrize(
    "url",
    [
        "https://www.youtube.com/playlist?list=PLabc",
        "https://www.youtube.com/@openai",
        "https://www.example.com/watch?v=Video123",
    ],
)
def test_extract_video_id_rejects_non_video_urls(url):
    module = load_ytb_to_html_module()
    with pytest.raises(ValueError, match="single YouTube video URL"):
        module.extract_video_id(url)


def test_ytb_to_html_run_yt2txt_forwards_markers_flag(monkeypatch, tmp_path):
    module = load_ytb_to_html_module()
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
        "--markers",
    ]
    assert captured["kwargs"]["input"] == "n\n"


def test_ytb_to_html_default_output_targets_current_workspace(tmp_path, monkeypatch, capsys):
    module = load_ytb_to_html_module()
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    monkeypatch.chdir(workspace)

    temp_dir = tmp_path / "yt2txt-output"
    temp_dir.mkdir()
    transcript_path = temp_dir / "output.txt"
    transcript_path.write_text("Transcript body\n", encoding="utf-8")

    monkeypatch.setattr(
        module,
        "parse_args",
        lambda: argparse.Namespace(
            url="https://youtu.be/AbC123xyz89",
            output_dir=".",
            output_path=None,
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

    created_path = workspace / "youtube-abc123xyz89.md"
    assert created_path.is_file()
    assert "## Raw Transcript" in created_path.read_text(encoding="utf-8")
    assert capsys.readouterr().out.strip() == "youtube-abc123xyz89.md"


def test_ytb_to_html_relative_output_dir_resolves_from_current_workspace(tmp_path, monkeypatch, capsys):
    module = load_ytb_to_html_module()
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    monkeypatch.chdir(workspace)

    temp_dir = tmp_path / "yt2txt-output"
    temp_dir.mkdir()
    transcript_path = temp_dir / "output.txt"
    transcript_path.write_text("Transcript body\n", encoding="utf-8")

    monkeypatch.setattr(
        module,
        "parse_args",
        lambda: argparse.Namespace(
            url="https://www.youtube.com/watch?v=Video123",
            output_dir="artifacts/youtube",
            output_path=None,
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

    created_path = workspace / "artifacts" / "youtube" / "youtube-video123.md"
    assert created_path.is_file()
    assert capsys.readouterr().out.strip() == "artifacts/youtube/youtube-video123.md"


def test_ytb_to_html_explicit_output_path_is_honored(tmp_path, monkeypatch, capsys):
    module = load_ytb_to_html_module()
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    monkeypatch.chdir(workspace)

    temp_dir = tmp_path / "yt2txt-output"
    temp_dir.mkdir()
    transcript_path = temp_dir / "output.txt"
    transcript_path.write_text("Transcript body\n", encoding="utf-8")

    monkeypatch.setattr(
        module,
        "parse_args",
        lambda: argparse.Namespace(
            url="https://www.youtube.com/shorts/Short123",
            output_dir=".",
            output_path="notes/final-transcript.md",
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

    created_path = workspace / "notes" / "final-transcript.md"
    assert created_path.is_file()
    assert capsys.readouterr().out.strip() == "notes/final-transcript.md"


def test_ytb_to_html_adds_collision_suffix_for_default_output(tmp_path):
    module = load_ytb_to_html_module()
    output_dir = tmp_path / "workspace"
    output_dir.mkdir()
    (output_dir / "youtube-abc123xyz89.md").write_text("existing\n", encoding="utf-8")

    result = module.choose_output_path(output_dir, "AbC123xyz89")

    assert result.name.startswith("youtube-abc123xyz89-")
    assert result.suffix == ".md"


def test_ytb_to_html_missing_cli_returns_error(tmp_path, monkeypatch, capsys):
    module = load_ytb_to_html_module()
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    monkeypatch.chdir(workspace)

    monkeypatch.setattr(
        module,
        "parse_args",
        lambda: argparse.Namespace(
            url="https://youtu.be/AbC123xyz89",
            output_dir=".",
            output_path=None,
            cli_path="yt2txt.sh",
            keep_temp=False,
        ),
    )
    monkeypatch.setattr(module.shutil, "which", lambda _name: None)

    assert module.main() == 1
    assert "yt2txt.sh not found on PATH" in capsys.readouterr().err


def test_ytb_to_html_non_zero_backend_exit_surfaces_output(tmp_path, monkeypatch, capsys):
    module = load_ytb_to_html_module()
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    monkeypatch.chdir(workspace)

    temp_dir = tmp_path / "yt2txt-output"
    temp_dir.mkdir()

    monkeypatch.setattr(
        module,
        "parse_args",
        lambda: argparse.Namespace(
            url="https://youtu.be/AbC123xyz89",
            output_dir=".",
            output_path=None,
            cli_path="yt2txt.sh",
            keep_temp=False,
        ),
    )
    monkeypatch.setattr(module, "resolve_cli", lambda _cli_path: "/bin/echo")
    monkeypatch.setattr(
        module,
        "run_yt2txt",
        lambda cli, url, output_dir: subprocess.CompletedProcess(
            [cli, url],
            2,
            "backend stdout\n",
            "backend stderr\n",
        ),
    )
    monkeypatch.setattr(module.tempfile, "mkdtemp", lambda prefix: str(temp_dir))

    assert module.main() == 2

    stderr = capsys.readouterr().err
    assert "backend stdout" in stderr
    assert "backend stderr" in stderr


def test_ytb_to_html_missing_transcript_file_returns_error(tmp_path, monkeypatch, capsys):
    module = load_ytb_to_html_module()
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    monkeypatch.chdir(workspace)

    temp_dir = tmp_path / "yt2txt-output"
    temp_dir.mkdir()

    monkeypatch.setattr(
        module,
        "parse_args",
        lambda: argparse.Namespace(
            url="https://youtu.be/AbC123xyz89",
            output_dir=".",
            output_path=None,
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
    monkeypatch.setattr(
        module,
        "find_transcript",
        lambda _output_dir: (_ for _ in ()).throw(RuntimeError("No transcript file found")),
    )
    monkeypatch.setattr(module.tempfile, "mkdtemp", lambda prefix: str(temp_dir))

    assert module.main() == 1
    assert "No transcript file found" in capsys.readouterr().err


def test_ytb_to_html_empty_transcript_returns_error(tmp_path, monkeypatch, capsys):
    module = load_ytb_to_html_module()
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    monkeypatch.chdir(workspace)

    temp_dir = tmp_path / "yt2txt-output"
    temp_dir.mkdir()
    transcript_path = temp_dir / "output.txt"
    transcript_path.write_text("", encoding="utf-8")

    monkeypatch.setattr(
        module,
        "parse_args",
        lambda: argparse.Namespace(
            url="https://youtu.be/AbC123xyz89",
            output_dir=".",
            output_path=None,
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

    assert module.main() == 1
    assert "Transcript file is empty" in capsys.readouterr().err
