---
name: "html-project-brief-visual"
description: "Create or refresh a self-contained HTML project brief that explains a repo through repo-derived system maps, main-flow diagrams, and complementary generated product and technical explainer visuals for mixed product and engineering audiences."
argument-hint: "[optional brief request]"
disable-model-invocation: true
user-invocable: true
---

# HTML Project Brief Visual

Create a single self-contained HTML artifact that helps a human understand a project quickly through structure-first visual explanation.

Treat the output as a living comprehension surface, not as a website, dashboard, or product UI.

This skill is the architecture-first sibling of `html-project-brief`. It should coexist with the standard brief, not overwrite it by default.

## Core contract

Produce one portable HTML file by default.

Keep the artifact:
- self-contained
- locally viewable without a build step
- readable on desktop and mobile
- source-grounded
- optimized for fast scanning first and deeper reading second
- more visually structured than the standard brief without becoming decorative

Use inline CSS and only lightweight JavaScript.

Embed the final selected images directly into the HTML artifact so the default output remains a single file.

## Start with the dominant mode

Choose one dominant mode before drafting structure:

- `onboarding`
- `architecture`
- `usage`
- `code-explainer`
- `change-brief`
- `research-brief`

This skill is optimized first for `onboarding` and `architecture`.

Support the other modes, but keep `imagegen` secondary unless a generated visual materially improves understanding.

Read [references/mode-recipes.md](references/mode-recipes.md) when the mode choice materially affects the page shape.

## Functional contract

For a normal zero-prompt brief, always produce:

- 1 repo-derived system map showing modules, layers, or responsibilities
- 1 repo-derived main flow showing a key data or control path

These two views are mandatory.

Generated images are not mandatory architecture artifacts. They are optional explanation assets that should help a developer, product engineer, or product manager understand the product or tool faster.

Do not use `imagegen` to invent the system structure.

For `onboarding` and `architecture`, assume a mixed PM plus dev audience unless the user says otherwise.

## Answer the comprehension questions first

Design the page to answer most of these quickly:

- What is this project?
- Why does it exist?
- How is it structured?
- How does data or control move through it?
- What are the key modules or files?
- How do I run or use it?
- What changed recently?
- What should I read next?
- What is still risky or uncertain?

Do not start by styling. Start by extracting the structure that the page must explain.

## Structure first, visuals second

Use this sequence:

1. inspect the repo
2. identify modules, entrypoints, and responsibilities
3. derive the system map
4. derive the main flow
5. decide whether the default complementary PM plus dev visual pair is warranted, or whether a truthful single-image variant is better

Never reverse this order.

If the diagrams are weak, adding imagery will not fix the brief.

## Visual budget

Default generated image budget for a normal zero-prompt brief:

- 2 complementary generated explainer visuals by default for `onboarding` and `architecture`
- 1 generated explainer visual only when the audience is clearly narrower than mixed PM plus dev, or when the repo is too thin to support a truthful second visual

Do not exceed 2 generated images unless the user explicitly asks for a more image-heavy artifact.

The default complementary pair should be:

- a one-glance operating picture that helps a reader grasp the product, user surfaces, core pipeline, and backend edges in one frame
- a one-glance technical operating picture that helps a reader grasp runtime boundaries, shared ownership, service clusters, persistence edges, and integration handoffs in one frame

The first generated visual should not be abstract decoration.

When the brief needs to serve both product and engineering audiences:

- let the first image explain the product or tool in one glance
- let the second image explain the technical operating model in one glance
- do not let the second image merely redraw the first with denser labels

The pair must answer different questions:

- product operating picture: what the tool is, what surfaces users touch, what the core loop does, and where the main edges sit
- technical operating picture: where the code lives, what runtime boundaries exist, which layers own behavior, and where storage, routing, or sync handoffs occur

The hero is optional and compact. If it does not add useful context, omit it and start the page with the system map.

Read [references/visual-guidelines.md](references/visual-guidelines.md) before finalizing layout or captions.

## Keep trust high

Make the artifact trustworthy.

Always:
- date time-sensitive observations
- distinguish confirmed facts from inference
- identify the source of claims when possible
- say when context is partial
- keep technical labels and exact callouts in HTML or SVG
- keep the structure diagram repo-derived
- pair every generated image with a caption, provenance note, and pedagogical thesis

The pedagogical thesis should state exactly what the image helps the reader understand.

If you cannot state that clearly in one sentence, skip the image.

## Use images and diagrams for different jobs

Use HTML and SVG for:
- topology diagrams
- sequence diagrams
- exact request or data flows
- module maps
- boundaries and interfaces
- code annotation
- tables
- legends
- comparison matrices

Use generated raster visuals for:
- a one-glance product operating picture
- a one-glance technical operating picture
- a source-informed backdrop behind a system map
- a subsystem vignette that gives shape to a section
- a flow-support image that reinforces the adjacent sequence or path
- a compact context visual when the project domain is hard to picture from text alone

Generated images must either:

- help the reader understand the product or tool in one glance
- improve the readability of an existing diagram

If they do neither, skip them.

## Use `imagegen` deliberately

Use the `imagegen` skill for raster generation when it is available.

Image generation policy:
- use the built-in `image_gen` path by default
- do not switch to CLI fallback unless the user explicitly asks for it or the `imagegen` skill requires explicit confirmation for a fallback path
- keep prompts source-informed, restrained, and overlay-friendly
- allow a small amount of large, high-value text when it materially improves one-glance comprehension
- do not ask for metaphorical, imaginary, or purely atmospheric architecture scenes

Read [references/prompt-recipes.md](references/prompt-recipes.md) before drafting prompts.

When prompting visuals for this skill, bias toward:
- stable composition
- clear layer separation
- quiet backgrounds
- recognizable product surfaces or system stages
- zones that match the adjacent diagram
- visual choices that stay aligned with known repo facts

Avoid:
- architecture mood boards
- conceptual mental-model scenes
- cinematic spectacle
- decorative collage clutter
- abstract block art with no product meaning
- fake architecture implied by unexplained imagery

## Build the right page shape

A strong default page usually includes:

- title
- one-sentence purpose
- short summary deck
- overview
- system map
- main flow
- key files or modules
- usage or navigation guidance
- risks or open questions
- suggested next reading

Optional additions:
- one-glance operating picture
- one-glance technical operating picture
- compact hero or context visual
- one support visual beside the system map
- one support visual beside a subsystem or flow section

Keep interactivity light.

Allowed patterns:
- tabs for alternate views
- collapsible dense sections
- glossary toggles
- copy buttons for commands or snippets
- reveal panels for metadata, sources, or commit context

Do not turn the brief into an editor, simulator, or workflow app.

## Default template

Use the architecture-first visual template in [assets/editorial-visual-brief.html](assets/editorial-visual-brief.html) unless the repository already has a stronger visual language that should be preserved.

The default visual language should feel:
- clear
- structured
- restrained
- diagram-led
- readable on mobile

The page should read as:

- `overview`
- `operating picture` for mixed PM plus dev audiences
- `technical operating picture` for mixed PM plus dev audiences
- `system map`
- `main flow`
- `key areas`
- `usage`
- `risks`

Do not let the hero or support imagery outrank the diagrams.

## Follow this workflow

1. Determine the dominant mode.
2. Read only the files and artifacts relevant to that mode.
3. Identify the core comprehension questions.
4. Extract repo facts: entrypoints, key modules, ownership boundaries, and main path.
5. Build the system map in HTML or SVG.
6. Build the main flow in HTML or SVG.
7. Unless the user or repo strongly indicates otherwise, assume a mixed PM plus dev audience for `onboarding` or `architecture`.
8. Generate a one-glance operating picture for product understanding.
9. Generate a one-glance technical operating picture for engineering understanding.
10. Generate only the visuals that have a clear pedagogical thesis.
11. Place the operating picture before the system map, and place the technical operating picture immediately before the system map or main flow.
12. Caption every visual with what it shows, why it exists, and how grounded it is.
13. Keep the file self-contained.
14. Check desktop and mobile readability.
15. Verify that the artifact is easier to understand than the source material.

## Zero-prompt behavior

Support explicit zero-prompt invocation when the user names only `$html-project-brief-visual` and provides no other task detail.

Treat that invocation as:

- "create or refresh the best default visual project brief for the current workspace"

### Canonical artifact

Use one canonical filename for zero-prompt operation:

- `project-brief-visual.html`

If the user explicitly asks for another filename or output path, follow the user's instruction instead.

### Bootstrap mode

If `project-brief-visual.html` does not exist, enter bootstrap mode.

In bootstrap mode:
- create the first baseline visual brief
- default to an `onboarding`-led structure
- include `architecture` and `usage` sections when the repo supports them
- include `recent changes` only as a secondary section
- always produce a system map plus a main flow
- default to the complementary PM plus dev visual pair for `onboarding` or `architecture`
- collapse to 1 generated explainer visual only when a second image would be repetitive or weak

Prioritize these questions:
- what is this project
- why does it exist
- how is it organized
- how does the main path work
- how do I use or navigate it
- what should I read next

### Refresh mode

If `project-brief-visual.html` already exists, enter refresh mode.

In refresh mode:
- treat the existing visual brief as a maintained artifact
- update it rather than replacing it blindly
- preserve still-accurate structure and diagrams when they remain useful
- replace support visuals when the diagram, emphasis, or explanation has changed
- increase emphasis on changes since the last pass

In refresh mode, read:
- the existing `project-brief-visual.html`
- the current repo structure
- the main entrypoints
- key configs or package files
- modified and untracked files when relevant

Use current code and docs as the source of truth when they conflict with the existing brief.

## Mode-specific defaults

For `onboarding`:
- always show a simple system map plus one end-to-end flow
- keep the diagrams approachable
- default to a complementary pair: one operating picture plus one technical operating picture
- collapse to a single visual only when the audience is clearly non-technical or the repo does not support a truthful technical picture

For `architecture`:
- always show boundaries, responsibilities, integrations, and the main path
- keep the hero absent or very restrained
- let HTML or SVG carry exact boundaries, invariants, and interfaces
- default to a complementary pair when the audience includes both product and engineering readers
- keep the technical operating picture closer to the system map than the product operating picture

For `usage`, `code-explainer`, `change-brief`, and `research-brief`:
- keep the system map and flow only when they are relevant to the brief goal
- limit `imagegen` to a secondary role
- prefer structure, evidence, and annotation over atmosphere

## Ambiguous repos

If the repo is ambiguous, incomplete, or documentation-light:
- derive a responsibility map from the strongest available evidence, such as folders, entrypoints, config, and package files
- choose the most demonstrable main flow from code, docs, or commands
- clearly label where the flow is inferred rather than directly documented

Do not invent architecture just to make the page look complete.

## Use bundled references progressively

Read bundled reference files only when needed.

Recommended references:
- [references/visual-guidelines.md](references/visual-guidelines.md)
- [references/mode-recipes.md](references/mode-recipes.md)
- [references/prompt-recipes.md](references/prompt-recipes.md)

Do not load every reference by default.

## Aim for this standard

A good artifact produced with this skill should:
- explain architecture before atmosphere
- make the main path obvious
- make the product legible in one visual and the implementation shape legible in a second visual when the audience is mixed PM plus dev
- use images only when they teach
- keep diagrams repo-derived
- remain useful when refreshed later
