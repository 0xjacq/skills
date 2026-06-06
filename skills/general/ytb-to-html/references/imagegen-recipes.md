# `imagegen` Recipes

Use `imagegen` only when a raster visual teaches faster than prose or a
code-native figure. Keep the default budget at `0-2` visuals.

Read the `imagegen` skill rules first. Stay on the built-in
`image_gen` path by default.

## Good uses

- conceptual mental model of a long-running harness
- source-grounded support visual for generator/evaluator collaboration
- one-glance editorial visual that makes the workflow memorable without
  pretending to be the exact diagram

## Bad uses

- precise timelines
- exact agent loops
- architecture topology
- code excerpts
- anything where specific wording or labels must be exact

## Prompt recipe: harness mental model

```text
Use case: stylized-concept
Asset type: conceptual support visual for a technical HTML brief
Primary request: a calm educational visual that helps a reader picture a long-running coding harness with planning, execution, evaluation, and persistent state
Scene/backdrop: restrained editorial explainer with 3 to 4 clearly separated zones
Subject: planner, worker loop, evaluator, and persistent state as conceptual areas only
Style/medium: polished editorial illustration
Composition/framing: landscape, clean negative space, easy to pair with adjacent HTML labels
Lighting/mood: credible, calm, diagram-friendly
Constraints: no fake architecture labels, no tiny text, no watermark
Avoid: marketing hero art, clutter, decorative symbolism, pretending to be the exact system diagram
```

## Prompt recipe: generator/evaluator operating picture

```text
Use case: infographic-diagram
Asset type: conceptual operating picture for a transcript synthesis
Primary request: a single visual that helps a technical reader understand the roles of a generator agent and evaluator agent, with persistent artifacts between them
Scene/backdrop: clean explainer composition with distinct zones and quiet background
Subject: builder role, evaluator role, shared artifact trail, and feedback loop as conceptual blocks
Style/medium: high-clarity editorial infographic
Composition/framing: landscape poster, large simple zones, negative space for HTML overlays
Lighting/mood: crisp, analytical, calm
Constraints: no invented services, no tiny labels, no watermark
Avoid: exact topology, pseudo-code in the image, busy arrows, decorative filler
```

## Caption rule

Every generated image should ship with:
- a short caption saying what the image teaches
- a provenance line such as `Conceptual visual` or
  `Source-grounded composite`
- nearby HTML or SVG that carries the exact technical meaning
