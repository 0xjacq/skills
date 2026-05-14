from __future__ import annotations

from html import escape
from pathlib import Path

from prebuild_engine.models import BuildOrNotResult, FindToolsResult


def render_build_or_not_canonical_report(result: BuildOrNotResult) -> str:
    lines = [
        f"# Build-or-Not Report: {result.capability}",
        "",
        f"- Run ID: `{result.run_id}`",
        f"- Generated at: `{result.generated_at}`",
        f"- Verdict: `{result.verdict}`",
        f"- Confidence: `{result.confidence}`",
        "",
        "## Decision",
        "",
        result.verdict_rationale,
        "",
        f"Recommended action: {result.recommended_action}",
        "",
        "## Evidence Policy",
        "",
        result.evidence_policy,
        "",
        "## Query Plan",
        "",
    ]
    for name, value in result.query_plan.facets.items():
        lines.append(f"- {name}: {value}")
    lines.extend(["", "## Leading Candidates", ""])
    if not result.leading_candidates:
        lines.append("- No corroborated candidate surfaced from Exa plus structured sources.")
    for candidate in result.leading_candidates:
        lines.extend(_candidate_section_lines(candidate))
    lines.extend(_artifact_section_lines(result))
    if result.warnings:
        lines.extend(["## Warnings", ""])
        lines.extend(f"- {warning}" for warning in result.warnings)
        lines.append("")
    return "\n".join(lines)


def render_find_tools_canonical_report(result: FindToolsResult) -> str:
    lines = [
        f"# Find-Tools Report: {result.query}",
        "",
        f"- Run ID: `{result.run_id}`",
        f"- Generated at: `{result.generated_at}`",
        f"- Decision: `{result.decision}`",
        f"- Confidence: `{result.confidence}`",
        "",
        "## Selection",
        "",
        result.selection_rationale,
        "",
    ]
    if result.recommended_artifact_type:
        lines.append(f"Recommended artifact type: `{result.recommended_artifact_type}`")
        lines.append("")
    lines.extend(["## Query Plan", ""])
    for name, value in result.query_plan.facets.items():
        lines.append(f"- {name}: {value}")
    lines.extend(["", "## Best Fit", ""])
    if result.best_fit is None:
        lines.append("- No single best fit met the confidence threshold.")
    else:
        lines.extend(_candidate_section_lines(result.best_fit))
    lines.extend(["## Alternatives", ""])
    if not result.alternatives:
        lines.append("- No strong alternatives were surfaced.")
    for candidate in result.alternatives:
        lines.extend(_candidate_section_lines(candidate))
    lines.extend(["## Near Misses", ""])
    if not result.near_misses:
        lines.append("- No near misses were recorded.")
    for candidate in result.near_misses:
        lines.extend(_candidate_section_lines(candidate))
    lines.extend(_artifact_section_lines(result))
    if result.warnings:
        lines.extend(["## Warnings", ""])
        lines.extend(f"- {warning}" for warning in result.warnings)
        lines.append("")
    return "\n".join(lines)


def render_build_or_not_html_report(result: BuildOrNotResult) -> str:
    candidate_rows = "".join(_candidate_row(candidate) for candidate in result.leading_candidates)
    if not candidate_rows:
        candidate_rows = "<tr><td colspan='5'>No corroborated candidate surfaced.</td></tr>"
    exa_items = _exa_items(result.exa_hits)
    warning_items = _warning_items(result.warnings)
    return _wrap_html(
        title="Build-or-Not Report",
        eyebrow="Build-or-Not runtime report",
        heading=result.capability,
        subtitle=result.verdict_rationale,
        deck_items=[
            ("Verdict", result.verdict),
            ("Confidence", result.confidence),
            ("Run ID", result.run_id),
            ("Generated", result.generated_at),
        ],
        main_sections="""
        <section class="panel">
          <h2>Recommended Action</h2>
          <p>{recommended_action}</p>
          <p><strong>Evidence policy:</strong> {evidence_policy}</p>
        </section>
        <section>
          <h2>Leading Candidates</h2>
          {candidate_table}
        </section>
        <section class="panel">
          <h2>Exa Evidence</h2>
          <ul>{exa_items}</ul>
        </section>
        """.format(
            recommended_action=escape(result.recommended_action),
            evidence_policy=escape(result.evidence_policy),
            candidate_table=_candidate_table(candidate_rows),
            exa_items=exa_items,
        ),
        rail_sections=_artifact_rail(result) + _warning_rail(warning_items),
    )


def render_find_tools_html_report(result: FindToolsResult) -> str:
    best_fit_block = (
        _candidate_table(_candidate_row(result.best_fit))
        if result.best_fit is not None
        else "<p>No single best fit met the confidence threshold.</p>"
    )
    alternative_rows = "".join(_candidate_row(candidate) for candidate in result.alternatives)
    near_miss_rows = "".join(_candidate_row(candidate) for candidate in result.near_misses)
    exa_items = _exa_items(result.exa_hits)
    warning_items = _warning_items(result.warnings)
    return _wrap_html(
        title="Find-Tools Report",
        eyebrow="Find-Tools runtime report",
        heading=result.query,
        subtitle=result.selection_rationale,
        deck_items=[
            ("Decision", result.decision),
            ("Confidence", result.confidence),
            ("Run ID", result.run_id),
            ("Recommended type", result.recommended_artifact_type or "none"),
        ],
        main_sections="""
        <section class="panel">
          <h2>Best Fit</h2>
          {best_fit_block}
        </section>
        <section>
          <h2>Alternatives</h2>
          {alternatives_block}
        </section>
        <section class="panel">
          <h2>Near Misses</h2>
          {near_misses_block}
        </section>
        <section class="panel">
          <h2>Exa Evidence</h2>
          <ul>{exa_items}</ul>
        </section>
        """.format(
            best_fit_block=best_fit_block,
            alternatives_block=_candidate_table(alternative_rows)
            if alternative_rows
            else "<p>No strong alternatives were surfaced.</p>",
            near_misses_block=_candidate_table(near_miss_rows)
            if near_miss_rows
            else "<p>No near misses were recorded.</p>",
            exa_items=exa_items,
        ),
        rail_sections=_artifact_rail(result) + _warning_rail(warning_items),
    )


def _candidate_section_lines(candidate) -> list[str]:
    return [
        f"### {candidate.name}",
        "",
        f"- Type: `{candidate.artifact_type}`",
        f"- URL: {candidate.url}",
        f"- Confidence: `{candidate.confidence}`",
        (
            "- Corroboration: "
            f"primary={candidate.corroboration.primary_count}, "
            f"secondary={candidate.corroboration.secondary_count}, "
            f"discussion={candidate.corroboration.discussion_count}, "
            f"structured={','.join(candidate.corroboration.structured_sources) or 'none'}"
        ),
        f"- Rationale: {candidate.rationale}",
        "",
        candidate.summary or "No summary available.",
        "",
    ]


def _artifact_section_lines(result) -> list[str]:
    return [
        "## Artifacts",
        "",
        f"- Result JSON: `{result.artifacts.result_json}`",
        f"- Canonical report: `{result.artifacts.canonical_report}`",
        f"- HTML report: `{result.artifacts.html_report}`",
        f"- Audit bundle: `{result.artifacts.audit_bundle}`",
        "",
    ]


def _candidate_row(candidate) -> str:
    corroboration = (
        f"primary={candidate.corroboration.primary_count}, "
        f"secondary={candidate.corroboration.secondary_count}, "
        f"discussion={candidate.corroboration.discussion_count}, "
        f"structured={','.join(candidate.corroboration.structured_sources) or 'none'}"
    )
    return (
        "<tr>"
        f"<td><a href='{escape(candidate.url)}'>{escape(candidate.name)}</a><div>{escape(candidate.summary)}</div></td>"
        f"<td><code>{escape(candidate.artifact_type)}</code></td>"
        f"<td><code>{escape(candidate.confidence)}</code></td>"
        f"<td>{escape(corroboration)}</td>"
        f"<td>{escape(candidate.rationale)}</td>"
        "</tr>"
    )


def _candidate_table(rows: str) -> str:
    return (
        "<table><thead><tr><th>Candidate</th><th>Type</th><th>Confidence</th>"
        "<th>Corroboration</th><th>Rationale</th></tr></thead><tbody>"
        f"{rows}</tbody></table>"
    )


def _exa_items(exa_hits) -> str:
    return "".join(
        (
            "<li>"
            f"<strong>{escape(hit.title)}</strong> "
            f"({escape(hit.evidence_kind)}) "
            f"<a href='{escape(hit.url)}'>{escape(hit.url)}</a>"
            f"<div>{escape(hit.summary or 'No highlight available.')}</div>"
            "</li>"
        )
        for hit in exa_hits[:12]
    ) or "<li>No Exa hits captured.</li>"


def _artifact_rail(result) -> str:
    return """
        <section>
          <h2>Artifacts</h2>
          <ul>
            <li><code>{result_json}</code></li>
            <li><code>{canonical_report}</code></li>
            <li><code>{html_report}</code></li>
            <li><code>{audit_bundle}</code></li>
          </ul>
        </section>
    """.format(
        result_json=escape(result.artifacts.result_json),
        canonical_report=escape(result.artifacts.canonical_report),
        html_report=escape(result.artifacts.html_report),
        audit_bundle=escape(result.artifacts.audit_bundle),
    )


def _warning_items(warnings: list[str]) -> str:
    return "".join(f"<li>{escape(item)}</li>" for item in warnings) or "<li>None</li>"


def _warning_rail(warning_items: str) -> str:
    return f"""
        <section>
          <h2>Warnings</h2>
          <ul>{warning_items}</ul>
        </section>
    """


def _wrap_html(
    *,
    title: str,
    eyebrow: str,
    heading: str,
    subtitle: str,
    deck_items: list[tuple[str, str]],
    main_sections: str,
    rail_sections: str,
) -> str:
    deck_html = "".join(
        f"<div class='card'><div class='label'>{escape(label)}</div><div class='value'><code>{escape(value)}</code></div></div>"
        for label, value in deck_items
    )
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{escape(title)}</title>
  <style>
    :root {{
      --bg: #f7f4ec;
      --fg: #1d1a17;
      --muted: #655c52;
      --line: #d7cbb8;
      --accent: #7e3b12;
      --card: #fffdf8;
      --mono: ui-monospace, SFMono-Regular, Menlo, monospace;
      --sans: "Avenir Next", "Segoe UI", sans-serif;
      --serif: "Iowan Old Style", Georgia, serif;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      padding: 0;
      background: linear-gradient(180deg, #f4efe4 0%, #fbfaf6 28%, #f7f4ec 100%);
      color: var(--fg);
      font-family: var(--serif);
      line-height: 1.55;
    }}
    .page {{
      max-width: 72rem;
      margin: 0 auto;
      padding: 2rem 1.25rem 4rem;
    }}
    header {{
      padding-bottom: 1rem;
      border-bottom: 1px solid var(--line);
      margin-bottom: 1.5rem;
    }}
    h1, h2 {{
      font-weight: 600;
      line-height: 1.1;
    }}
    h1 {{ margin: 0 0 0.5rem; font-size: 2.3rem; }}
    h2 {{ margin-top: 2rem; font-size: 1.35rem; }}
    .deck {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(10rem, 1fr));
      gap: 0.75rem;
      margin: 1rem 0 0;
    }}
    .card {{
      background: var(--card);
      border: 1px solid var(--line);
      padding: 0.9rem;
    }}
    .label {{
      font-family: var(--sans);
      color: var(--muted);
      font-size: 0.85rem;
      text-transform: uppercase;
      letter-spacing: 0.04em;
    }}
    .value {{
      font-size: 1.05rem;
      margin-top: 0.25rem;
    }}
    .layout {{
      display: grid;
      grid-template-columns: minmax(0, 2fr) minmax(16rem, 1fr);
      gap: 1.5rem;
    }}
    .rail {{
      background: rgba(255, 253, 248, 0.78);
      border: 1px solid var(--line);
      padding: 1rem;
      align-self: start;
      position: sticky;
      top: 1rem;
    }}
    .panel {{
      background: rgba(255, 253, 248, 0.88);
      border: 1px solid var(--line);
      padding: 1rem;
      margin-bottom: 1rem;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      background: var(--card);
      border: 1px solid var(--line);
    }}
    th, td {{
      text-align: left;
      padding: 0.7rem 0.6rem;
      border-bottom: 1px solid var(--line);
      vertical-align: top;
    }}
    th {{
      font-family: var(--sans);
      font-size: 0.9rem;
      color: var(--muted);
    }}
    code {{
      font-family: var(--mono);
      font-size: 0.92rem;
    }}
    a {{ color: var(--accent); }}
    ul {{ padding-left: 1.25rem; }}
    @media (max-width: 920px) {{
      .layout {{ grid-template-columns: 1fr; }}
      .rail {{ position: static; }}
    }}
  </style>
</head>
<body>
  <div class="page">
    <header>
      <div class="label">{escape(eyebrow)}</div>
      <h1>{escape(heading)}</h1>
      <p>{escape(subtitle)}</p>
      <div class="deck">{deck_html}</div>
    </header>
    <div class="layout">
      <main>{main_sections}</main>
      <aside class="rail">{rail_sections}</aside>
    </div>
  </div>
</body>
</html>
"""


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
