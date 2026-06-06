# 0xjacq/skills

Open collection of agent skills by [0xjacq](https://github.com/0xjacq).

Built on the [`npx skills`](https://github.com/vercel-labs/skills) standard — compatible with Claude Code, Gemini CLI, OpenCode, Kilo Code, Pi, Codex, and 50+ other coding agents.

Each skill keeps reusable workflow instructions in `SKILL.md`, pushes heavy reference material into `references/` or `scripts/`, and now ships Codex-specific UI and invocation metadata in `agents/openai.yaml`. The collection is tuned against current OpenAI Codex and Anthropic skill-authoring guidance while remaining portable across agent runtimes.

## Categories

| Category | Skills | Description |
|----------|--------|-------------|
| [`agenpedia`](./skills/agenpedia/) | `ingest`, `ingest-youtube`, `ingest-batch`, `query`, `lint` | Markdown wiki knowledge base workflows |
| [`general`](./skills/general/) | `grill-me`, `grill-me-light`, `html-project-brief`, `html-project-brief-visual`, `markdown-to-tufte-html`, `txt-to-html-srs`, `ytb-to-html` | Cross-project planning, design review, and HTML-based artifact generation |
| [`tools`](./skills/tools/) | `build-or-not`, `find-tools` | Tooling and pre-build diligence orchestration skills |

## Install

Install any category URL with `npx skills`:

```bash
# Install one category for all detected agents
npx skills add https://github.com/0xjacq/skills/tree/main/skills/<category> --all

# Install one category for a specific agent
npx skills add https://github.com/0xjacq/skills/tree/main/skills/<category> -a <agent>
```

Valid categories: `agenpedia`, `general`, `tools`

Common agents: `claude-code`, `gemini-cli`, `opencode`, `kilo`, `pi`, `codex`

### Update

```bash
npx skills update
```

For the runtime-backed `tools` category, see [skills/tools/README.md](./skills/tools/README.md) for prerequisites, local testing, and sync workflow details.

## Agenpedia Skills

These skills power the [Agenpedia](https://github.com/0xjacq/Agenpedia) wiki template. They can also be used standalone in any markdown wiki project that follows the Agenpedia schema.

| Skill | Description |
|-------|-------------|
| `ingest` | Ingest a source (file, URL, text, or topic) into the wiki |
| `ingest-youtube` | Transcribe a YouTube video into `raw/`, then hand it to `ingest` |
| `ingest-batch` | Triage and batch-ingest multiple sources |
| `query` | Query the wiki with a natural language question |
| `lint` | Check wiki health and fix structural issues |

## General Skills

Reusable skills that are not tied to a specific product or schema.

| Skill | Description |
|-------|-------------|
| `grill-me` | Stress-test a plan or design one decision at a time |
| `grill-me-light` | Run a short, high-leverage stress-test of a plan or design |
| `html-project-brief` | Turn repos, docs, and diffs into self-contained HTML project briefings |
| `html-project-brief-visual` | Turn repos, docs, and diffs into visual-first self-contained HTML project briefings |
| `markdown-to-tufte-html` | Render markdown into a self-contained Tufte-style HTML document without rewriting it |
| `txt-to-html-srs` | Turn source text into a Tufte-style study sheet with flashcards and optional publishing |
| `ytb-to-html` | Transcribe one YouTube video into markdown and synthesize a self-contained HTML brief |

## Tools Skills

Runtime-backed skills that orchestrate external engines and return structured artifacts.

| Skill | Description |
|-------|-------------|
| `build-or-not` | Run a conservative prior-art and reuse check before recommending a greenfield build |
| `find-tools` | Find the current best-fit tool, package, framework, repo, or product for a capability |

## License

MIT
