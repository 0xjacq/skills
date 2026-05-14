# Changelog

All notable changes to this skills collection are documented here.

Format: [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
Versioning: [Semantic Versioning](https://semver.org/spec/v2.0.0.html)

## [Unreleased]

### Added
- `general/grill-me` — interactive plan and design grilling workflow
- `general/html-project-brief` — self-contained HTML briefing workflow for repos, diffs, and docs
- `agenpedia/ingest-youtube` — YouTube transcript adapter that feeds Agenpedia ingest
- `general/grill-me-light` — concise grilling mode that asks only the highest-leverage design questions before summarizing
- `tools/build-or-not` — runtime-backed build-vs-reuse diligence skill
- `tools/find-tools` — runtime-backed tool recommendation and prior-art search skill

### Changed
- aligned skill metadata, invocation policy, and Codex UI metadata files with current OpenAI Codex and Anthropic skill-authoring guidance
- expanded the top-level and tools-specific documentation for runtime-backed skills and cross-agent metadata expectations

### Fixed
- `agenpedia/ingest-youtube` now resolves repo-relative output paths from the repository root instead of the caller's working directory

## [1.0.0] — 2026-05-01

### Added
- `agenpedia/ingest` — full ingest workflow with source acquisition, classification, confrontation, Popper filter, and wiki page creation
- `agenpedia/ingest-batch` — batch triage and sequential ingest
- `agenpedia/query` — wiki query with optional synthesis filing
- `agenpedia/lint` — wiki health checks (wikilinks, orphans, coverage gaps, contradictions)
