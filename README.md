# 0xjacq/skills

Open collection of agent skills by [0xjacq](https://github.com/0xjacq).

Built on the [`npx skills`](https://github.com/vercel-labs/skills) standard — compatible with Claude Code, Gemini CLI, OpenCode, Kilo Code, Pi, Codex, and 50+ other coding agents.

## Categories

| Category | Skills | Description |
|----------|--------|-------------|
| [`agenpedia`](./skills/agenpedia/) | `ingest`, `ingest-batch`, `query`, `lint` | Markdown wiki knowledge base workflows |

## Install

### Install a category

```bash
# Install all agenpedia skills (auto-detects your installed coding agents)
npx skills add https://github.com/0xjacq/skills/tree/main/skills/agenpedia --all

# Install to a specific agent
npx skills add https://github.com/0xjacq/skills/tree/main/skills/agenpedia -a claude-code
npx skills add https://github.com/0xjacq/skills/tree/main/skills/agenpedia -a gemini-cli
npx skills add https://github.com/0xjacq/skills/tree/main/skills/agenpedia -a opencode
npx skills add https://github.com/0xjacq/skills/tree/main/skills/agenpedia -a kilo
npx skills add https://github.com/0xjacq/skills/tree/main/skills/agenpedia -a pi
npx skills add https://github.com/0xjacq/skills/tree/main/skills/agenpedia -a codex
```

### Update

```bash
npx skills update
```

## Agenpedia Skills

These skills power the [Agenpedia](https://github.com/0xjacq/Agenpedia) wiki template. They can also be used standalone in any markdown wiki project that follows the Agenpedia schema.

| Skill | Description |
|-------|-------------|
| `ingest` | Ingest a source (file, URL, text, or topic) into the wiki |
| `ingest-batch` | Triage and batch-ingest multiple sources |
| `query` | Query the wiki with a natural language question |
| `lint` | Check wiki health and fix structural issues |

## License

MIT
