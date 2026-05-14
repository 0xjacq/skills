# Tools Skills

Runtime-backed skills that orchestrate external engines and return structured artifacts.

## Skills

- `build-or-not`: conservative prior-art and reuse check before recommending a greenfield build
- `find-tools`: recommend the strongest existing tool for a capability, with alternatives and near misses

## Runtime Layout

- Canonical Python sources live in `skills/tools/_internal/python_runtime/`.
- Each public skill ships a copied runtime in its local `scripts/` directory so the skill stays self-contained when installed elsewhere.
- `skills/tools/_internal/sync_runtime.py` is the sync script that refreshes those copied runtimes.

## Prerequisites

- Python 3.11+
- `uv` recommended for dependency resolution during local runs and tests
- `EXA_API_KEY` for live Exa-backed discovery; without it, the runtimes degrade to `needs_manual_review` instead of making overconfident recommendations

## Local Usage

Run the wrappers from a workspace where you want artifacts written:

```bash
python skills/tools/build-or-not/scripts/run.py "<capability or idea>"
python skills/tools/find-tools/scripts/run.py "<tool query>"
```

Both wrappers can also emit raw JSON with `--json`.

Artifacts land under:

```text
.cache/skills-tools/build-or-not/<run_id>/
.cache/skills-tools/find-tools/<run_id>/
```

Each run writes:

- `result.json`
- canonical markdown report
- reference HTML report
- audit bundle with raw evidence artifacts

## Maintenance

After editing the canonical runtime under `_internal/python_runtime`, resync the copied skill runtimes:

```bash
python skills/tools/_internal/sync_runtime.py
```

The test suite checks that the copied runtimes still match the canonical source tree, including nested packages.

## Tests

Run the local validation suite with:

```bash
uv run --with pytest pytest -q
```

The suite covers:

- runtime wrapper help output
- artifact generation and renderer snapshots
- sync integrity between canonical and copied runtimes
- repo-wide skill metadata and invocation policy compliance
