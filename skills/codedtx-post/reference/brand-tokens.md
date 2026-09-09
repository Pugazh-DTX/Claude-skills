---
name: codedtx-brand-tokens
description: The 12 distinct visual themes used by the 12 carousel templates — real extracted tokens, not one reused palette.
---

# CodeDTX Brand Tokens — Multi-Theme System

Each of the 12 templates in `templates/` has its OWN theme (background, text, accent, card colors, decorative motif). Never reuse one theme's palette across multiple templates — that was tried once and was wrong. Five of these themes were extracted directly from real pre-built assets at `C:\Users\HP\Documents\post\post\assets\template-*` (the source of truth for those five); the rest were designed to the same convention to cover the remaining content-structure types.

## Theme registry

| Template folder | Theme name | Mood | bg | text | accent | accent2 | motif |
|---|---|---|---|---|---|---|---|
| 01-problem-solution | codedtx-locked | clean corporate | #F9FAFB | #0B172A | #FF6B00 | #FF6B00 | grid |
| 02-before-after | gradient | bold tech | #00070F | #FFFFFF | #FF7600 | #FE004B | dotgrid |
| 03-case-study | ai-engineering | deep dive | #0A1128 | #FFFFFF | #FF6B00 | #FF2A55 | wave |
| 04-step-by-step | codedtx-dark | minimal | #0B172A | #FFFFFF | #FF6B00 | #FF6B00 | grid |
| 05-myth-reality | myth-contrast | dramatic | #1A0E0E | #FFFFFF | #FF3B3B | #FF6B00 | split |
| 06-data-statistics | ott-insight | bold stat | #0B172A | #FFFFFF | #FF6B00 | #FF3D1F | triangle |
| 07-technology-comparison | tech-teal | technical | #06141B | #FFFFFF | #00D4B4 | #0091FF | circuit |
| 08-how-it-works | violet-flow | systems | #120E1F | #FFFFFF | #8B5CF6 | #EC4899 | nodes |
| 09-industry-insight | design-impact | editorial | #181410 | #FFFFFF | #FF6B00 | #FF3D1F | pillbar |
| 10-feature-product-explainer | emerald-feature | light/product | #F4FBF7 | #0B2A1B | #00A870 | #00C48C | grid-light |
| 11-full-bleed-story | mono-story | cinematic | #0A0A0A | #FFFFFF | #FFFFFF | #FF6B00 | none (full-bleed photo) |
| 12-doodle-infographic | doodle-pastel | warm explainer | #FFF8F0 | #2B2118 | #FF6B00 | #FFB020 | paper |

Full token sets (muted text, card colors, dividers) are in `.claude/skills/codedtx-post/../../../_gen/themes.py` at build time — treat the values above as the ones that matter for a human reviewing a slide.

## Typography

All 12 themes use **Poppins** (weights 400–900), matching the real assets exactly. Headline weight 900, body 400, labels/eyebrows 700 with 2px letter-spacing.

## Structure (per template)

Each template folder has **7 slides**, not 3 — this extends the real assets' cover/content/cta pattern into the full Problem→Insight→Solution→Result flow validated on `02-before-after`:
```
slide-1-cover.svg       -- hook headline + theme's signature visual
slide-2-problem.svg     -- eyebrow + headline + body + stat rows or callout
slide-3-insight.svg     -- eyebrow + headline + body + diagram/steps
slide-4-solution.svg    -- eyebrow + headline + body + steps/callout/comparison
slide-5-result.svg      -- eyebrow + headline + body + stat hero/metric row
slide-6-takeaway.svg    -- eyebrow + headline + body + gradient/dark callout
slide-7-cta.svg         -- headline + CTA button + trust points, no swipe arrow
```
`11-full-bleed-story` is the one exception — it uses minimal chrome (full-bleed photo + one overlay line per slide), matching its cinematic reference.

## Vertical rhythm (unchanged from validation on 02-before-after)

```
y=70   logo
y=126  eyebrow
y=260  headline block starts (2-line, tight coupling, accent on line 2, rule underneath)
y=hy   body text starts (hy = value returned by the headline() helper — do not hardcode an offset)
y=hy+~100-160  main visual anchor starts, sized to reach within ~150-250px of the footer
y=1230 footer divider
y=1272 footer content (page counter left, gradient chevron-circle right, omitted on slide 7)
```

## Hard rules (all caused real bugs during generation — keep these)

1. **No Empty Slide / No Empty Bottom:** every slide needs a real visual anchor reaching near the footer. Enlarging a container is not enough — fill it with a second real content element (description line, sub-stat, divider), not padding around one small centered element.
2. **XML escaping:** any literal `&` in slide copy MUST be written `&amp;` — this broke rendering once already (a "DATA & STATISTICS" eyebrow).
3. **Spacing math:** never hardcode an offset like `y=hy-40` against a helper's returned position — use the returned value directly. An erroneous `-40` once caused the accent rule to strike through the body text.
4. **Character budgets:** headline ~20-24 chars/line, body ~50-58 chars/line, stat/step body ~58-68 chars/line, callout body ~24-30 chars/line. Split to a new line rather than overflow past x=1000.
