---
title: Tufte Renderer Showcase
subtitle: Hybrid reference fixture
author: Codex
date: 2026-05-14
---

<section>

<p><span class="newthought">This fixture</span> starts with a standard markdown footnote.[^sidenote] It also includes an explicit margin note <label for="mn-fixture" class="margin-toggle">⊕</label><input type="checkbox" id="mn-fixture" class="margin-toggle"/><span class="marginnote">Explicit margin notes stay source-driven and are never invented.</span> and a <span class="sans">sans-serif aside</span>.</p>

</section>

## Epigraph

<div class="epigraph">
<blockquote>
<p>Well-designed evidence is quiet.</p>
<footer>Reference fixture</footer>
</blockquote>
</div>

## Media

<figure class="fullwidth">
  <svg viewBox="0 0 1200 240" width="100%" role="img" aria-label="Full-width fixture figure">
    <rect x="0" y="0" width="1200" height="240" fill="#e6d7c5"></rect>
    <rect x="80" y="52" width="220" height="136" fill="#f8f3ea" stroke="#7b4a2d" stroke-width="4"></rect>
    <rect x="370" y="52" width="460" height="136" fill="#f8f3ea" stroke="#7b4a2d" stroke-width="4"></rect>
    <rect x="900" y="52" width="220" height="136" fill="#f8f3ea" stroke="#7b4a2d" stroke-width="4"></rect>
    <text x="190" y="130" font-family="Georgia, serif" font-size="28" fill="#17120e" text-anchor="middle">Main Column</text>
    <text x="600" y="130" font-family="Georgia, serif" font-size="28" fill="#17120e" text-anchor="middle">Full-width Figure</text>
    <text x="1010" y="130" font-family="Georgia, serif" font-size="28" fill="#17120e" text-anchor="middle">Margin Space</text>
  </svg>
  <figcaption>Full-width figures extend beyond the reading column.</figcaption>
</figure>

<figure class="iframe-wrapper">
  <iframe title="Embedded media placeholder" srcdoc="<!doctype html><html><body style='margin:0;display:grid;place-items:center;height:100vh;background:#f3ece2;color:#17120e;font-family:Georgia,serif;'>Embedded media placeholder</body></html>"></iframe>
</figure>

## Code

```html
<figure class="iframe-wrapper">
  <iframe title="Embedded media placeholder"></iframe>
</figure>
```

[^sidenote]: Standard markdown footnotes should map to Tufte-style sidenotes.
