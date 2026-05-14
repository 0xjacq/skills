# Mode Recipes

Choose one dominant mode before writing. This skill is optimized for `onboarding` and `architecture`.

## `onboarding`

Use when the reader is new to the project.

Required structural views:
- one simple system map
- one end-to-end main flow

Visual guidance:
- assume a mixed PM plus dev audience unless the user says otherwise
- use 2 complementary generated explainers by default
- let the first image explain the product before the reader dives into the diagrams
- let the second image explain ownership boundaries and runtime shape before the reader studies the system map
- keep the hero optional and compact

Suggested structure:
1. What this project is
2. Why it exists
3. System map
4. Main flow
5. Key files and modules
6. How to run or use it
7. Risks and open questions
8. Read next

## `architecture`

Use when the reader needs internal structure more than orientation.

Required structural views:
- one system map showing boundaries and responsibilities
- one main flow showing the primary data or control path

Visual guidance:
- keep generated imagery secondary
- for mixed audiences, default to one product operating picture plus one technical operating picture
- if the audience is explicitly engineering-only, the technical operating picture may stand alone
- use the pair to support the system map and the main flow, not to replace either
- avoid a dominant hero unless the domain truly needs context

Suggested structure:
1. System overview
2. System map
3. Main flow
4. Integration points
5. Key invariants
6. Failure modes
7. Read next

## `usage`

Use when operational understanding matters most.

Visual guidance:
- generated imagery is optional
- commands, setup, and workflows dominate
- add a system map or flow only if they materially clarify usage

## `code-explainer`

Use when one subsystem needs explanation.

Visual guidance:
- prefer one precise flow and annotated excerpts
- generated imagery, if any, should support the subsystem explanation rather than abstract it

## `change-brief`

Use when summarizing branch or agent work.

Visual guidance:
- prefer before-and-after HTML or SVG structure
- use generated imagery only when it genuinely improves orientation

## `research-brief`

Use when synthesizing findings, options, or hypotheses.

Visual guidance:
- keep images subordinate to evidence
- structure, tables, and comparisons should carry the core argument
