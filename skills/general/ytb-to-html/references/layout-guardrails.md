# Layout Guardrails

Use these rules when `ytb-to-html` turns transcript ideas into figures.

## Goal

Prefer structures that remain legible when transcript wording is longer
than expected. Optimize for calm scanning, not maximum compression.

## Safe defaults

- Put exact language in HTML whenever possible.
- Use SVG only when the geometry itself teaches something.
- Let captions and nearby prose carry the nuance that would otherwise
  overcrowd a figure.
- Prefer multiple short cards or rows over one crowded horizontal band.

## Banned patterns

- single-row timelines with many fixed `x/y` text labels
- SVG labels that assume a fixed string length
- diagrams that require reading dense sentence fragments inside shapes
- large `pre` blocks used as pseudo-diagrams when a list or grid would
  scan better

## Responsive figure heuristics

- If a label is longer than a short clause, move it outside the shape.
- If there are more than four milestones, use stacked cards, a table,
  or multiple SVG rows.
- If a loop has more than five steps, use HTML cards or an ordered list
  before considering a drawn diagram.
- If the exact order matters more than the shape, use HTML sequence
  markup rather than SVG.

## Prompt-time self-check

Before finalizing:
- scan for overlap
- scan for clipping
- check whether every figure label can be read without zooming
- check whether a caption or table would communicate better than the
  current figure

If any answer is no, simplify the figure instead of shrinking the text.
