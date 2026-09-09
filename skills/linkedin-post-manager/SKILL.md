---
name: linkedin-post-manager
description: "Use when the user asks to create/generate a LinkedIn (or Instagram) carousel post, image post, or content pack on a topic — produces a 3-page Cover/Content/CTA design from the saved template."
---

# LinkedIn Post Manager

Generates a 3-page LinkedIn/Instagram carousel (**Cover → Content → CTA**) for any topic, using one fixed visual design system and content that is derived dynamically from the topic. This skill owns the *design pattern and theme*; only the words change per topic.

## When to use this

The user asks for a LinkedIn carousel, a LinkedIn image post, a "content pack," or similar, and gives (or can give) a topic — e.g. "make a LinkedIn carousel about X," "turn this into a LinkedIn post," "generate the next post in my series."

If the user hasn't given a topic yet, ask for one (topic/title + optionally 3–5 sub-points). If they give a topic with no sub-points, derive 3 stat-row items, 5 badge/card items, and a callout from the topic yourself — don't block on it.

## Design system (fixed — do not change without the user asking)

- Canvas: 1080×1350 (IG/LinkedIn portrait carousel ratio)
- Background: navy `#0D1B2A` + a subtle dot-grid pattern (`#6A809A` dots, ~16% opacity, 26px pitch)
- Top accent bar: solid `#FF5A00`, full width, 10px tall, at y=0
- Divider line under the top zone: `#1E3048`
- Primary gradient (used for CTA buttons/callout bars): `#FF0063 → #FF7600 (48%) → #FFA200`, left-to-right
- Accent palette used for badges/cards/stat bars, cycled per item: orange `#FF5A00`, cyan `#22D3EE`, green `#3DDB7C`, purple `#A78BFA`, gold `#FFB800`
- Text: headlines white `#FFFFFF`, body/secondary `#9FB4CC` / `#8FA6C0`, panel/card background `#12233A` with `#22384f` border
- Font: Arial/Helvetica, bold weights (700–800) for headlines
- Every page carries a small logo watermark near the bottom and a 3-dot page-position footer

## Page structure (fixed sections, dynamic content)

**Page 1 — Cover**: kicker label, multi-line title, subtitle, a decorative illustration block, a 5-item badge row (2 per row) drawn from the topic's key sub-points.

**Page 2 — Content** (explicitly required to always contain these three sections, in this order):
1. **Stats row** — 3 cards, each a short value (e.g. an acronym, number, or key term) + one-line label, left-bordered in a rotating accent color.
2. **Illustration zone** — a labeled decorative graphic block with a one-line caption underneath, summarizing the visual/technical idea.
3. **Callout bar** — a full-width gradient bar at the bottom with a bold title and 1–2 lines of supporting text (the single most important takeaway).

**Page 3 — CTA**: decorative illustration, a large 1–2 line bold headline, a 5-card feature/recap row (same 5 topics as the cover badges, restated as cards), and a full-width gradient pill button with the CTA text (e.g. "Save This Guide", "Follow for Part 2").

## How to generate a post

1. Map the topic into this content model:
   ```js
   {
     kicker, coverTitle, coverSubtitle,        // cover
     badges: [5x {label, color}],               // cover badge row
     contentHeading,
     stats: [3x {value, label}],                 // content stats row
     illoCaption,                                 // content illustration zone
     calloutTitle, calloutText,                   // content callout bar
     ctaHeadline,
     ctaCards: [5x {label, color}],               // usually same as badges
     ctaButton
   }
   ```
2. Write a new self-contained HTML file (e.g. `<topic-slug>-carousel.html`) in the working directory, using the **reference implementation below** as the starting point verbatim — it is already validated (renders 3 SVGs with no console errors, PNG export confirmed not to hit the canvas-tainting bug). Only change the `defaultBadges` / `defaultBadgeColors` / `defaultStats` / `defaultCtaCards` arrays and the default `value="..."` content in the form fields to match the new topic — do not restructure the render functions.
3. Verify before delivering: run it headless (Playwright, `executablePath: '/opt/pw-browsers/chromium'`), confirm `document.querySelectorAll('#stage svg').length === 3`, zero `pageerror`/console errors, and that `canvas.toBlob` succeeds for at least one page (catches any re-introduced `<foreignObject>` that would taint PNG export — always wrap dynamic text with the included `wrapTextByWidth()` helper instead of foreignObject).
4. Deliver with SendUserFile. Mention once, briefly, that headline/illustration/logo are rebuilt in the established style (real editable `<text>` + generated shapes) rather than pixel-traced from any original design file, since no original asset files are stored by this skill.

## Reference implementation (validated — copy as the base for every new topic)

The full working generator lives at `/home/claude/ig-carousel-generator.html` in past sessions; recreate it fresh each time from this spec since prior session files don't persist. Structure to reproduce:

- A left form panel with fields for: kicker, cover title (`\n` = line break), cover subtitle, 5 badges (text + accent-color dropdown), content heading, 3 stats (value + label), illustration caption, callout title/text, CTA headline (`\n` = line break), 5 CTA cards (label + color), CTA button text.
- A right `#stage` area rendering three live SVG previews (Cover/Content/CTA) with per-page SVG and PNG download buttons.
- Shared JS builder functions: `defsBlock(id)` (dot-grid pattern + primary gradient defs, unique per-page id to avoid collisions), `bgBlock(id)` (navy fill + dot overlay + top bar + divider), `logoWatermark(y)`, `pageFooter(pageNum)` (3-dot indicator), `star(cx,cy,scale,color)` (sparkle accent), `illustrationCluster(x,y,w,h,id,accent)` (abstract dashboard-mockup graphic from primitive shapes — panel, trend line, dots, progress bars, two ring gauges), `badgePill(cx,y,w,label,accent)`, `multilineText(x,y,lines,size,weight,fill,lh,anchor)`, and **`wrapTextByWidth(text,maxWidth,fontSize,fontWeight)`** — measures with an offscreen canvas context and greedily wraps words; this is the only safe way to fit dynamic body text into a card without `<foreignObject>` (foreignObject taints the canvas and silently breaks PNG export — confirmed via `Failed to execute 'toBlob' ... Tainted canvases may not be exported`).
- `buildCover(d)`, `buildContent(d)`, `buildCta(d)` each return a full `<svg viewBox="0 0 1080 1350">` string assembled from the blocks above plus the per-topic content in `d`.
- `gatherState()` reads all form fields into the content-model object; `renderAll()` rebuilds all 3 SVGs and re-injects them into the DOM; the panel has a debounced (`250ms`) `input` listener so edits re-render live.
- `downloadSVG(page)` blobs the cached SVG string directly. `downloadPNG(page)` blobs the SVG, loads it into an `Image`, draws it to a 2×-scaled `<canvas>`, and exports via `canvas.toBlob` — only safe because no `<foreignObject>` is used anywhere in the SVG strings.

When asked for just one static set of images (not the editable tool), it's fine to render the three `buildCover/buildContent/buildCta` SVG strings directly to `.svg` files (and rasterize to `.png` via the same canvas approach in a headless browser) instead of shipping the whole editor page — use judgment on which the user wants.