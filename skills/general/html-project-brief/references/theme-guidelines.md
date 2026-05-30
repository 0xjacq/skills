# Theme Guidelines

Default house style: `Tufte Brief`

This theme is Tufte-inspired, not a strict copy.

## Goals

- optimize for reading
- keep signal high and noise low
- place figures near the text they explain
- use side rails sparingly and only when they clarify the reading flow
- keep the page credible and calm

## Typography

- Use serif for the main reading column.
- Use restrained sans-serif for UI chrome such as tabs, pills, labels, and metadata.
- Keep line length narrow enough for sustained reading.
- Prefer 2 heading levels, with a third only when truly needed.

## Color

- Use an off-white page background and near-black text.
- Reserve saturated color for meaning:
  - severity
  - recency
  - change type
  - status
- Do not use color as decoration.

## Layout

- Use one main reading column.
- Use a compact left contents rail on wide screens.
- Use a right context rail only when there are real notes, provenance, or "read next" hints worth surfacing.
- Keep the navigation rail visually subordinate. It should not exceed roughly 15% of the useful page width.
- Use full-width sections only for:
  - architecture diagrams
  - timelines
  - large comparison tables
  - diff overviews
- On medium screens, keep the contents rail and move the context rail below the main column when needed.
- On narrow screens, collapse the layout to one column in this order:
  1. contents
  2. main content
  3. context
- Collapse context-rail content into inline callouts or toggles on narrow screens.

## Components

Preferred components:
- summary deck with 2 to 4 key facts
- sticky table of contents in the left rail
- figure with caption
- inline note or contextual right-rail note
- callout for caveat or invariant
- code excerpt with short annotation
- change badge
- metadata row

Avoid:
- card-grid overload
- dashboard chrome
- bright hero banners
- heavy shadows
- decorative gradients
- large empty whitespace that reduces density without aiding readability

## Writing Style

- Write short, high-information sections.
- Prefer synthesis over restating file contents.
- Put the most important interpretation in the main column.
- Put secondary detail in notes or collapsible sections.
