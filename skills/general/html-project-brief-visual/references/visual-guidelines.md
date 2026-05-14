# Visual Guidelines

Default visual language: `Editorial Explainer`

## Goals

- teach quickly through a small number of strong images
- keep the page credible and calm
- make technical sections memorable without pretending the images are exact diagrams
- reserve precision for HTML and SVG overlays

## Default image budget

For a normal zero-prompt brief:

- hero image
- system mental-model image
- architecture or key-flow image
- optional fourth image for usage, risks, or read-next

Do not exceed 4 generated images unless the user explicitly asks for a more image-heavy artifact.

## Layout rules

- Lead with one dominant hero visual rather than a grid of equally weighted cards.
- Keep a strong reading column and let visuals punctuate the story.
- Place each image near the section it teaches.
- On desktop, allow wider figure spans. On mobile, stack images above their overlays and notes.
- Preserve generous padding around images when you expect HTML labels, legends, or captions nearby.

## Caption and provenance rules

Every generated image needs:

- a short caption describing what the image teaches
- a provenance line indicating whether it is conceptual, source-grounded, or interpretive
- supporting nearby text that makes the technical point explicit

Suggested provenance labels:

- `Conceptual visual`
- `Source-grounded composite`
- `Interpretive summary`

## Label strategy

- Put technical labels, arrows, component names, legends, and invariants in HTML or SVG.
- Keep generated images mostly text-free.
- If an image includes display text, restate it in HTML and do not depend on it for correctness.

## Avoid

- generic dashboard hero art
- bright marketing gradients
- collage overload
- more than one large image competing for attention in the same section
- images that imply exact architecture when they are only conceptual
