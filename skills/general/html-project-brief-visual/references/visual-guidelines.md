# Visual Guidelines

Default visual language: `Architecture-First Editorial`

## Goals

- explain the repo structure before adding atmosphere
- make the system map and main flow immediately readable
- make the product or tool understandable in one generated visual when imagery is used
- use generated imagery only when it teaches faster than text alone
- keep the page credible and calm

## Mandatory structural views

For a normal zero-prompt brief:

- one repo-derived system map
- one repo-derived main flow

These views are primary. Generated images are secondary.

## Default image budget

For a normal zero-prompt brief:

- two complementary generated explainer visuals by default for `onboarding` and `architecture`
- one generated explainer visual only when the audience is clearly narrower than mixed PM plus dev, or when the repo cannot support a truthful second visual

Do not exceed 2 generated images unless the user explicitly asks for a more image-heavy artifact.

## Complementarity rule

For mixed product and engineering audiences, the two visuals must do different jobs:

- visual 1 explains the product or tool operating model
- visual 2 explains the technical operating model

They should share a visual family, but they should not repeat the same boxes with only cosmetic differences.

If the second visual merely restates the first with denser labels, it failed.

## Pedagogical thesis rule

No generated image is allowed without a one-sentence pedagogical thesis.

Examples:

- `This visual helps the reader distinguish the ingestion, processing, and output layers before reading the system map labels.`
- `This visual helps the reader remember the main handoff points in the request path shown in the adjacent flow diagram.`

If you cannot write that sentence, skip the image.

## Preferred first image

The strongest default generated image is a one-glance operating picture.

It should help a technical or product reader understand:

- what the user touches
- what the product does in the middle
- what the core intelligence or service layer does
- where storage, sync, or backend edges sit

If the image only looks “structured” but does not answer those questions, it is not good enough.

For mixed product and engineering audiences, the default two-image pairing is:

- one product or tool operating picture
- one technical operating picture

## Layout rules

- The page should begin with understanding, not spectacle.
- The hero is optional and compact.
- When no useful hero exists, start directly with the overview and system map.
- For mixed audiences, place the product operating picture first and the technical operating picture second, both before the system map.
- If a useful operating picture exists, place it near the top of the story as an explainer panel, not a decorative banner.
- Give the system map the widest, most visually dominant slot.
- Give the main flow its own dedicated section rather than burying it inside tabs.
- Place support imagery beside the section it reinforces, never above the whole story as decoration.

## Caption and provenance rules

Every generated image needs:

- a short caption describing what the image teaches
- a provenance line indicating how tightly it is grounded in the repo
- supporting nearby text that states the pedagogical thesis explicitly

Suggested provenance labels:

- `Source-informed support visual`
- `Diagram-adjacent support visual`
- `Explanatory support visual`

## Label strategy

- Put technical labels, arrows, component names, legends, invariants, and interfaces in HTML or SVG.
- Keep generated images mostly text-free.
- If an image includes display text, restate it in HTML and do not depend on it for correctness.

## Avoid

- decorative hero art
- abstract block art with no product meaning
- conceptual mental-model scenes
- architecture mood boards
- more than one dominant visual before the system map
- two visuals that teach the same thing at different prettiness levels
- images that imply exact structure without adjacent proof
