# Carousel workflow

Use this workflow whenever the user asks for a LinkedIn post unless they explicitly ask for text only.

## Default result

Create both:

1. A copy-ready LinkedIn post
2. A finished carousel: 7 slides (cover + 5 content + CTA), SVG/HTML files, PNG previews, and a single `carousel.pdf`

### Slide structure (always 7 pages)

| Page | Type    | Notes |
|------|---------|-------|
| 1    | Cover   | Topic title, subtitle, template-matched visual |
| 2–6  | Content | 5 content slides, each with generated illustration |
| 7    | CTA     | Closing question, follow prompt |

If the brief has fewer than 5 content slides the builder auto-pads; if more it uses the first 5.

## Step 1 — Select the template

Read [template-selection.md](template-selection.md) and pick from the five options:

| Template | Asset folder | Auto-selected when topic contains |
|---|---|---|
| `ai-engineering` | `assets/template-ai-engineering/` | AI, ML, code, engineering, pipeline, backend, LLM |
| `ott-insight` | `assets/template-ott-insight/` | Platform, SaaS, growth, OTT, business strategy |
| `design-impact` | `assets/template-design-impact/` | Design, UX, UI, creative, Figma, visual, brand |
| `codedtx-dark` | `assets/template-codedtx-dark/` | Framework, architecture, guardrails, review, testing, ownership |
| `codedtx-locked` | `assets/template-codedtx-locked/` | Everything else / general CodeDTX branded content |

State the selected template in the delivery so the user can request a different one.

## Step 2 — Prepare the input JSON

Write a brief JSON file with this shape. Omit fields that do not apply to the chosen template.

```json
{
  "topic": "Topic string that drives auto-selection",
  "subtitle": "One sentence under 15 words",
  "slides": [
    {
      "number": 1,
      "headline": "Short slide headline",
      "points": ["Point one", "Point two", "Point three"],
      "image_label": "Illustration description",
      "section_label": "CHALLENGE",
      "dark_slide": false,
      "spotlight": "3X FASTER",
      "quote": "Optional pull quote",
      "quote_author": "Source or name"
    }
  ],
  "cta": {
    "headline": "Low-pressure closing",
    "body": "One clear next step.",
    "action": "CONTACT US"
  }
}
```

Provide exactly 5 content slides. Fewer than 5 are auto-padded with generic filler content (visibly weaker than real content — avoid relying on this); more than 5 are truncated to the first 5.

### Field guide by template

| Field | ai-engineering | ott-insight | design-impact | codedtx-locked |
|---|---|---|---|---|
| `headline` | Use OR use `headline_black` / `headline_orange` / `headline_red` | Short, plain | Short, plain | Short, plain |
| `image_label` | Required — describes left illustration | Use `photo_label` | Not used | Not used |
| `section_label` | Not used | Not used | Required — ALL-CAPS label inside strip | Not used |
| `dark_slide` | Not used | Not used | Optional — flip slide to navy bg | Not used |
| `spotlight` | Not used | Not used | Optional — ALL-CAPS stat, max 20 chars | Not used |
| `quote` | Optional — fills navy strip at bottom | Optional — fills quote callout | Not used | Optional |

## Step 3 — Build

Choose an output directory. Prefer `outputs/linkedin/<slug>/`.

```bash
python3 <skill-path>/scripts/build_carousel.py \
  --input brief.json \
  --output outputs/linkedin/<slug>/
```

To force a specific template:

```bash
python3 <skill-path>/scripts/build_carousel.py \
  --input brief.json \
  --output outputs/linkedin/<slug>/ \
  --template design-impact
```

## Step 4 — Render and compile PDF

The builder renders each `slide-N.html` to `previews/slide-N.png` at 1080×1350 using Playwright automatically, then compiles all 7 PNGs into `carousel.pdf` (one slide per page) using `img2pdf` or `Pillow`.

If Playwright is unavailable, the builder says so and delivers the HTML files. Install with: `pip install playwright && playwright install chromium`

To skip PDF: `--no-pdf`

## Step 5 — Inspect

Open every rendered slide. Check:

- Text overflow — no text runs past the slide edge or into another element
- Collisions — headlines, labels, bullets, and logos do not overlap
- Contrast — all text readable against its background
- Slide numbering — sequential and correct
- Factual accuracy — every visible claim is true and verifiable
- Mobile readability — no text below 22px, no element smaller than a finger-tap width

Fix any failed slide and re-render before delivery.

## Template locks (all five families)

SVG masters live in `assets/template-<name>/` — `template-codedtx-locked/`, `template-codedtx-dark/`, `template-ai-engineering/`, `template-ott-insight/`, `template-design-impact/` — each with `template-cover.svg`, `template-content.svg`, `template-cta.svg`.

These master files intentionally contain **no `{{ }}` token syntax** — they're meant to open cleanly as finished designs in a browser, Figma, or Illustrator, not as code templates. The builder fills them by matching known literal placeholder text (e.g. replacing the sample headline text with the real one) and, for illustrations, by matching the static placeholder icon markup and swapping in a generated SVG graphic — the same substitution idea as a token, just without the visible `{{ }}` syntax in the raw file.

**Known gap:** on the cover and CTA slides, `topic`, `subtitle`, `headline`, and `cta.headline`/`cta.body` reliably flow through on every template. On content slides, `headline` and `image_label` flow through on every template; `points` (the bullet list) currently does **not** — the bullet text you see in the master files is what ships. If a user needs the bullets themselves to vary per post, that requires wiring bullet text the same way images were wired (matching the static bullet markup and replacing it), which hasn't been done yet — flag this rather than silently shipping generic bullets as if they were the user's real content.

Never change theme, colours, gradients, font family, font sizes, font weights, geometry, spacing, logo, embedded assets, component layout, or footer styling by hand when filling content. If content overflows, shorten the copy rather than resizing the design.

## Deliver

Provide the output folder path, all SVG and HTML files, all PNG previews, slide count, the template name and selection reason, and the LinkedIn post copy.

If preview rendering was unavailable, deliver the SVG slides and state the limitation. Do not silently return only an outline.
