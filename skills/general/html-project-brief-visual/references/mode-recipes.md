# Mode Recipes

Choose one dominant mode before writing. This skill is optimized for `onboarding` and `architecture`.

## `onboarding`

Use when the reader is new to the project.

Default visual plan:
- hero image for project purpose
- mental-model visual for the core system idea
- architecture visual for the main moving parts
- optional fourth image for usage or read-next if the repo supports it

Suggested structure:
1. What this project is
2. Why it exists
3. System picture
4. Key files and modules
5. How to run or use it
6. Risks and open questions
7. Read next

## `architecture`

Use when the reader needs internal structure more than orientation.

Default visual plan:
- restrained hero or section opener
- one strong subsystem or flow visual
- optional supporting mental-model visual

Suggested structure:
1. System overview
2. Main components
3. Data or control flow
4. Integration points
5. Key invariants
6. Failure modes
7. Read next

## `usage`

Use when operational understanding matters most.

Visual guidance:
- usually 1 or 2 images
- prioritize one opener and one workflow-supporting visual if needed
- let commands, steps, and config details dominate

## `code-explainer`

Use when one subsystem needs explanation.

Visual guidance:
- usually 1 or 2 images
- pair one conceptual image with 3 to 5 annotated code excerpts
- let SVG or HTML carry the precise flow

## `change-brief`

Use when summarizing branch or agent work.

Visual guidance:
- use imagery sparingly
- prefer before-and-after HTML or SVG structure
- add a generated image only when it genuinely improves orientation

## `research-brief`

Use when synthesizing findings, options, or hypotheses.

Visual guidance:
- keep images subordinate to evidence
- use at most 1 or 2 visuals unless the user explicitly asks for a richer narrative
- let tables and comparison structure carry the core argument
