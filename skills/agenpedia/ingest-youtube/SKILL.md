---
name: "ingest-youtube"
description: "Transcribe a single YouTube video with a local `yt2txt.sh` CLI, save the raw transcript as a markdown source in `raw/`, then hand that file to the Agenpedia `ingest` workflow. Use when the user gives a YouTube video URL and wants it added to the wiki knowledge base."
argument-hint: "<youtube-video-url>"
disable-model-invocation: false
user-invocable: true
---

# YouTube Ingest

Turn one YouTube video URL into a raw source file in `raw/`, then continue with the standard Agenpedia `ingest` flow on that file.

## Context

Read `AGENTS.md` at the project root for wiki conventions, naming rules,
configured tools, and the expected `raw/` and `wiki/` workflow.

This skill is a thin adapter around the existing `ingest` skill. Do not
duplicate the ingest logic here.

## Prerequisites

- Require a local `yt2txt.sh` executable available on `PATH`, or set
  `YT2TXT_CLI` to its absolute path before running the helper script.
- Require a writable `raw/` directory at the project root.

If either prerequisite is missing, stop and tell the user exactly what
is missing.

## Workflow

1. Confirm the argument is a single YouTube video URL. If the user gives
   a playlist or channel URL, stop and ask for a single video URL unless
   they explicitly want batch processing.
2. Run:

   ```bash
   python3 skills/agenpedia/ingest-youtube/scripts/fetch_youtube_transcript.py "<youtube-url>"
   ```

3. The script writes a markdown source file under `raw/` and prints the
   relative file path on stdout, for example `raw/youtube-abc123xyz89.md`.
4. Verify that the printed file exists and contains the raw transcript.
   Do not summarize, translate, or clean the transcript unless the user
   asked for that separately.
5. Immediately continue by invoking the `ingest` skill with the emitted
   file path as its argument.

## Failure Handling

- If `yt2txt.sh` exits non-zero, surface the error output and stop.
- If the helper cannot find exactly one transcript output, stop.
- If the transcript file is empty, stop.
- If the helper succeeds but `ingest` is unavailable, return the created
  `raw/...` file path and state that it is ready for `/ingest`.

## Script

`skills/agenpedia/ingest-youtube/scripts/fetch_youtube_transcript.py`
does the deterministic work:

- runs `yt2txt.sh` non-interactively
- reads the generated transcript
- writes a markdown source file into `raw/`
- prints the relative `raw/...` file path for the next `ingest` step
