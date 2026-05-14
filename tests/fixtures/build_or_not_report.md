# Build-or-Not Report: agent marketplace for software bounties

- Run ID: `build-or-not-test-1234`
- Generated at: `2026-05-14T10:00:00+00:00`
- Verdict: `reuse_existing`
- Confidence: `high`

## Decision

A credible existing solution surfaced with corroboration across web discovery and structured sources.

Recommended action: Default to the top existing candidate first. Only build new capability around gaps that remain after evaluation.

## Evidence Policy

Important claims should cite primary evidence when available, prefer two corroborating signals when possible, and fold freshness into confidence.

## Query Plan

- functional: agent marketplace
- technical: agent skill mcp
- market: software bounty marketplace
- research: agent marketplace

## Leading Candidates

### acme/agent-market

- Type: `repo`
- URL: https://github.com/acme/agent-market
- Confidence: `high`
- Corroboration: primary=2, secondary=1, discussion=0, structured=github,repo_posts
- Rationale: 1 Exa corroboration hit(s); structured sources: github, repo_posts; fit labels: marketplace, agent_platform

Open source marketplace for autonomous agent bidding.

## Artifacts

- Result JSON: `/tmp/build-or-not-test-1234/result.json`
- Canonical report: `/tmp/build-or-not-test-1234/canonical-report.md`
- HTML report: `/tmp/build-or-not-test-1234/report.html`
- Audit bundle: `/tmp/build-or-not-test-1234/audit`

## Warnings

- Directory seed search timed out.
