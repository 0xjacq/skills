#!/usr/bin/env python3
"""Fetch a YouTube transcript and save it as a raw Agenpedia source."""

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import parse_qs, urlparse


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run yt2txt.sh, save the raw transcript in raw/, and print the created file path."
    )
    parser.add_argument("url", help="Single YouTube video URL to transcribe")
    parser.add_argument(
        "--raw-dir",
        default="raw",
        help="Destination raw directory relative to the repo root (default: %(default)s)",
    )
    parser.add_argument(
        "--cli-path",
        default=os.environ.get("YT2TXT_CLI", "yt2txt.sh"),
        help="Path to yt2txt.sh or command name on PATH (default: %(default)s)",
    )
    parser.add_argument(
        "--keep-temp",
        action="store_true",
        help="Keep the temporary transcription directory for debugging",
    )
    return parser.parse_args()


def resolve_cli(cli_path: str) -> str:
    if os.path.sep in cli_path:
        expanded = Path(cli_path).expanduser()
        if not expanded.is_file():
            raise FileNotFoundError(f"yt2txt.sh not found: {expanded}")
        if not os.access(expanded, os.X_OK):
            raise PermissionError(f"yt2txt.sh is not executable: {expanded}")
        return str(expanded)

    resolved = shutil.which(cli_path)
    if not resolved:
        raise FileNotFoundError(
            f"yt2txt.sh not found on PATH: {cli_path}. Install it or set YT2TXT_CLI."
        )
    return resolved


def run_yt2txt(cli: str, url: str, output_dir: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [cli, url, "--output", str(output_dir)],
        input="n\n",
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def find_transcript(output_dir: Path) -> Path:
    output_files = sorted(output_dir.rglob("output.txt"))
    if len(output_files) == 1:
        return output_files[0]
    if len(output_files) > 1:
        raise RuntimeError(
            f"Expected one output.txt file, found {len(output_files)} under {output_dir}"
        )

    transcript_files = sorted(output_dir.rglob("*_transcription.txt"))
    if len(transcript_files) == 1:
        return transcript_files[0]
    if not transcript_files:
        raise RuntimeError(f"No transcript file found under {output_dir}")
    raise RuntimeError(
        f"Expected one transcript file, found {len(transcript_files)} under {output_dir}"
    )


def extract_video_id(url: str) -> str:
    parsed = urlparse(url)
    host = parsed.netloc.lower()

    if host.endswith("youtu.be"):
        candidate = parsed.path.strip("/").split("/")[0]
        if candidate:
            return candidate

    query_video_id = parse_qs(parsed.query).get("v", [])
    if query_video_id:
        return query_video_id[0]

    path_parts = [part for part in parsed.path.split("/") if part]
    if "shorts" in path_parts:
        index = path_parts.index("shorts")
        if index + 1 < len(path_parts):
            return path_parts[index + 1]

    return "video"


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "video"


def choose_output_path(raw_dir: Path, video_id: str) -> Path:
    base_name = f"youtube-{slugify(video_id)}"
    candidate = raw_dir / f"{base_name}.md"
    if not candidate.exists():
        return candidate

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    return raw_dir / f"{base_name}-{timestamp}.md"


def build_markdown(url: str, transcript: str) -> str:
    fetched_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")
    return (
        "# YouTube Transcript\n\n"
        f"- Source URL: {url}\n"
        f"- Fetched At: {fetched_at}\n"
        "- Source Type: YouTube video transcript\n\n"
        "## Raw Transcript\n\n"
        f"{transcript.rstrip()}\n"
    )


def get_repo_root() -> Path:
    return Path(__file__).resolve().parents[4]


def resolve_raw_dir(raw_dir_value: str, repo_root: Path) -> Path:
    raw_dir = Path(raw_dir_value).expanduser()
    if raw_dir.is_absolute():
        return raw_dir
    return repo_root / raw_dir


def render_output_path(output_path: Path, repo_root: Path) -> str:
    try:
        return output_path.relative_to(repo_root).as_posix()
    except ValueError:
        return output_path.as_posix()


def main() -> int:
    args = parse_args()
    repo_root = get_repo_root()

    try:
        cli = resolve_cli(args.cli_path)
    except (FileNotFoundError, PermissionError) as exc:
        print(str(exc), file=sys.stderr)
        return 1

    raw_dir = resolve_raw_dir(args.raw_dir, repo_root)
    raw_dir.mkdir(parents=True, exist_ok=True)

    temp_dir = Path(tempfile.mkdtemp(prefix="ingest-youtube-"))
    cleanup_dir = True

    try:
        result = run_yt2txt(cli, args.url, temp_dir)
        if result.returncode != 0:
            if result.stdout:
                print(result.stdout, file=sys.stderr, end="" if result.stdout.endswith("\n") else "\n")
            if result.stderr:
                print(result.stderr, file=sys.stderr, end="" if result.stderr.endswith("\n") else "\n")
            return result.returncode

        transcript_path = find_transcript(temp_dir)
        transcript = transcript_path.read_text(encoding="utf-8").strip()
        if not transcript:
            print(f"Transcript file is empty: {transcript_path}", file=sys.stderr)
            return 1

        output_path = choose_output_path(raw_dir, extract_video_id(args.url))
        output_path.write_text(build_markdown(args.url, transcript), encoding="utf-8")
        print(render_output_path(output_path, repo_root))

        if args.keep_temp:
            print(f"Temporary output kept at: {temp_dir}", file=sys.stderr)
            cleanup_dir = False

        return 0
    finally:
        if cleanup_dir and temp_dir.exists():
            shutil.rmtree(temp_dir)


if __name__ == "__main__":
    raise SystemExit(main())
