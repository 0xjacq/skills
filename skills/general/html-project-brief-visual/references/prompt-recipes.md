# Prompt Recipes

Use `imagegen` for raster generation. Stay on the built-in `image_gen` path by default.

All prompts for this skill should bias toward:

- stable composition
- quiet backgrounds
- clear layer separation
- distinct zones that match the adjacent diagram
- no embedded text unless it materially improves one-glance comprehension

Every prompt should assume that HTML or SVG provides the exact architecture, labels, and flow details.

Do not ask the model to invent the architecture.

## Complementary pair contract

When the audience is mixed PM plus dev, treat the two visuals as a linked pair:

- visual 1 explains product surfaces, the user-visible loop, and the major system edges
- visual 2 explains runtime boundaries, shared ownership, service clusters, persistence, and handoffs

Keep the pair visually related through aspect ratio, palette family, and reading direction, but do not let the second prompt repeat the first prompt's information structure.

## One-glance operating picture

Use when the image should help a developer, product engineer, or product manager understand the tool or product in one frame.

Prompt shape:

```text
Use case: infographic-diagram
Asset type: one-glance product or system explainer
Primary request: a single visual that helps a technical or product reader understand what the product is, what surfaces users touch, what the core engine does, and where the main data or backend edges sit
Scene/backdrop: clean product architecture poster with 3 to 5 clear zones
Subject: only the confirmed product surfaces, core pipeline stages, and backend or persistence edges already established from the repo
Style/medium: high-clarity editorial infographic, polished product explainer
Composition/framing: landscape poster, easy to scan in one glance, stable zones, strong hierarchy
Lighting/mood: crisp, informative, calm
Text (verbatim): "Capture", "Understand", "Study", "Store" (optional; use only if the model can render a few large headings clearly)
Constraints: show real product surfaces or system stages, not abstract blocks alone; no invented services or flows; no tiny labels; no watermark
Avoid: vague shapes, pure atmosphere, mood board energy, unexplained architecture symbolism, service inventory overload
```

## One-glance technical operating picture

Use when the audience includes developers, technical product engineers, or architecture reviewers who need more implementation signal than a product explainer provides.

Prompt shape:

```text
Use case: infographic-diagram
Asset type: one-glance technical operating picture
Primary request: a single visual that helps a technical reader understand runtime boundaries, shared core ownership, backend routing, persistence edges, and the main service clusters in one frame
Scene/backdrop: clean engineering systems poster with 4 to 6 clearly separated zones
Subject: only the confirmed shells, shared core, service clusters, persistence layers, local data stores, routing logic, and backend or sync edges already established from the repo
Style/medium: high-clarity technical infographic, polished systems explainer
Composition/framing: landscape poster, easy to scan in one glance, stronger structural hierarchy than product marketing, a few large headings and arrows only
Lighting/mood: crisp, analytical, credible
Text (verbatim): "Shells", "Shared Core", "Services", "Persistence", "AI Routing", "Sync" (optional; use only if the model can render a few large headings clearly)
Constraints: make the technical boundaries legible; no invented services; no fake low-level code; no tiny labels; no watermark
Avoid: product-marketing emphasis, vague blocks, abstract geometry without ownership meaning, decorative filler, repeating the product operating picture's stage model
```

## System-map support plate

Use when a system map would benefit from a restrained source-informed backdrop.

Prompt shape:

```text
Use case: stylized-concept
Asset type: system-map support plate
Primary request: a restrained architectural support visual that helps the adjacent repo-derived system map feel more legible and memorable
Scene/backdrop: minimal structured backdrop with clearly separated zones that align with the module groups already identified from the repo
Subject: only the confirmed module families, layers, or responsibility groups described in the adjacent HTML or SVG
Style/medium: crisp editorial illustration with simple forms
Composition/framing: orthographic or near-orthographic feel, stable geometry, generous quiet space for overlays
Lighting/mood: calm, analytical, low-drama
Constraints: do not invent extra services, actors, or infrastructure; do not embed labels; do not pretend to be the actual diagram; no watermark
Avoid: metaphor, mood board energy, atmospheric background art, decorative clutter
```

## Flow support visual

Use when the main flow section needs one supportive image to reinforce the adjacent sequence or path.

Prompt shape:

```text
Use case: stylized-concept
Asset type: main-flow support visual
Primary request: a simple support visual for the adjacent repo-derived flow diagram
Scene/backdrop: uncluttered composition showing only the confirmed stages or actors that participate in the main path
Subject: the main actors, handoffs, or layers from the adjacent flow
Style/medium: restrained editorial render or illustration
Composition/framing: horizontal sequence-friendly layout, clear separation of stages, negative space for SVG arrows and notes
Lighting/mood: neutral and precise
Constraints: no fake arrows, no embedded labels, no invented hops, no watermark
Avoid: cinematic effects, complex perspective, pseudo-diagram text, unexplained components
```

## Subsystem vignette

Use when a specific subsystem section needs shape or texture without replacing the adjacent structure.

Prompt shape:

```text
Use case: stylized-concept
Asset type: subsystem support vignette
Primary request: a compact support visual that helps a reader picture the subsystem already explained by the surrounding HTML or SVG
Scene/backdrop: minimal environment linked to the subsystem's real responsibilities
Subject: only the confirmed subsystem concerns, tools, or surfaces already present in the repo explanation
Style/medium: polished but restrained illustration
Composition/framing: compact panel, stable geometry, uncluttered focal zones
Lighting/mood: credible, quiet, technical
Constraints: no invented modules, no metaphorical stand-ins, no embedded labels, no watermark
Avoid: pure atmosphere, abstract symbolism, dashboard art, busy collage
```

## Optional compact hero or context visual

Use only when the project domain is hard to picture from structure alone.

Prompt shape:

```text
Use case: stylized-concept
Asset type: compact context visual
Primary request: a small contextual visual that helps orient the reader before the system map
Scene/backdrop: focused scene tied to the project's real domain or usage context
Subject: the real operating context or user outcome already described in the brief
Style/medium: restrained editorial illustration
Composition/framing: compact, secondary, non-dominant
Lighting/mood: calm, informative
Constraints: the visual must remain subordinate to the system map; no fake UI or architecture; no watermark
Avoid: hero-banner spectacle, vague ambiance, decorative filler
```

## Hard rules

- The strongest default image is a one-glance operating picture, not an abstract support plate.
- When the audience is mixed product plus engineering, the default pair is product operating picture plus technical operating picture.
- The two prompts in that pair must answer different questions and should not share the same box model.
- No prompt should ask for a conceptual mental-model scene.
- No prompt should ask for an architecture mood board.
- No prompt should ask for metaphorical infrastructure or imaginary components.
- No prompt should produce generic rounded blocks with no product meaning.
- If the adjacent diagram cannot name the element, the image should not introduce it.
- If a generated image has no explicit pedagogical thesis, skip it.
