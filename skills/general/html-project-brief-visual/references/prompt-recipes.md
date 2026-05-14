# Prompt Recipes

Use `imagegen` for raster generation. Stay on the built-in `image_gen` path by default.

All prompts for this skill should bias toward:

- editorial explainer composition
- clean negative space for HTML overlays
- restrained palette
- calm, credible mood
- no embedded text unless absolutely necessary

## Hero image

Use when the image needs to answer "what is this project and why does it matter?"

Prompt shape:

```text
Use case: stylized-concept
Asset type: onboarding brief hero image
Primary request: a visual introduction to the project's purpose and main operating context
Scene/backdrop: an editorial explainer scene with enough negative space for surrounding HTML copy
Subject: the project's main domain, workflow, or user outcome
Style/medium: polished illustration or stylized 3D editorial artwork
Composition/framing: cinematic but restrained, wide composition, clear focal point
Lighting/mood: calm, credible, intelligent
Color palette: restrained neutrals with one accent color family
Constraints: no embedded UI chrome unless source-grounded; no watermark; no logo invention
Avoid: generic SaaS dashboard art, clutter, text baked into the image
```

## Mental-model image

Use when the image needs to make the system concept memorable without pretending to be a literal diagram.

Prompt shape:

```text
Use case: stylized-concept
Asset type: system mental-model visual
Primary request: a conceptual image that helps a reader remember the system's core moving parts
Scene/backdrop: uncluttered editorial scene with room for HTML callouts
Subject: the project's main actors or layers represented metaphorically but grounded in the repo's actual responsibilities
Style/medium: educational editorial illustration
Composition/framing: simple depth, clearly separated elements, easy to annotate externally
Lighting/mood: calm, precise, thoughtful
Constraints: keep relationships visually distinct; no embedded labels; no watermark
Avoid: fake architecture diagrams, dense infographic text, busy backgrounds
```

## Architecture or subsystem image

Use when the image needs to support the main technical explanation for onboarding or architecture mode.

Prompt shape:

```text
Use case: stylized-concept
Asset type: architecture section visual
Primary request: a visual anchor for the system boundary or subsystem under discussion
Scene/backdrop: minimal editorial environment with room for SVG overlays
Subject: the subsystem, boundary, or flow being explained
Style/medium: crisp illustrative render with clean forms and limited textures
Composition/framing: horizontal composition, stable geometry, separated zones for overlay labels
Lighting/mood: neutral and analytical
Constraints: keep the image text-free; preserve generous negative space; no watermark
Avoid: detailed pseudo-diagram labels, noisy texture, dramatic effects that obscure structure
```

## Optional fourth image

Use only when it teaches something distinct.

Good uses:
- a usage scene that grounds the brief in a real workflow
- a risk or failure-mode visual that makes caveats memorable
- a read-next bridge visual for a large repo

Bad uses:
- repeating the same concept as the hero
- filling space
- decorative mood art with no comprehension value
