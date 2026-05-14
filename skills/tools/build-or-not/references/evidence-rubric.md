# Evidence Rubric

## Verdicts

- `reuse_existing`: a credible existing solution already covers enough of the request that greenfield work should not be the default.
- `adapt_existing`: meaningful prior art exists, but some integration or gap-closing work is still likely.
- `build_new`: no credible solution was corroborated after broad discovery plus structured checks.
- `needs_manual_review`: evidence is incomplete or degraded, so a confident build decision would be premature.

## Evidence hierarchy

- `primary`: official product pages, package registries, docs, repos, or clearly first-party material
- `secondary`: directories, catalogs, launch listings, or third-party summaries
- `discussion`: forums, Hacker News, Reddit, and similar discussion signals

## Rules

- Important claims should cite primary evidence when available.
- Prefer two corroborating signals when possible.
- Freshness should influence confidence.
- `build_new` should be rare when strong products or reusable components already exist.
