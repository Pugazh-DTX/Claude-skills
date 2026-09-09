# Template selection

The builder picks the visual template automatically from the topic. Read the keyword table below before generating a carousel. Always state which template was selected and why.

## Auto-selection rule

Scan the topic, subtitle, and any supporting context for the keywords below. Use the first match. If no keywords match, use `codedtx-locked`.

| Template | Select when the topic contains |
|---|---|
| `ai-engineering` | ai, ml, engineering, developer, development, code, pipeline, api, backend, llm, model, algorithm, devops, machine learning, technical, software, cloud, data science |
| `design-impact` | design, ux, ui, creative, visual, figma, brand, typography, prototype, wireframe, designer, illustration, motion, graphic |
| `ott-insight` | platform, saas, growth, business, strategy, launch, revenue, product, market, startup, ott, streaming, pricing, failure, b2b, sales, funnel, retention, churn |
| `codedtx-dark` | framework, architecture, guardrails, review, testing, ownership, production-first, quality |
| `codedtx-locked` | (default — everything else, or general CodeDTX brand content) |

## Override

Pass `--template <name>` to the builder to force a specific template. Valid names: `ai-engineering`, `ott-insight`, `design-impact`, `codedtx-dark`, `codedtx-locked`.

## Template descriptions

### ai-engineering
Dark navy gradient cover. "MORE ABOUT" label sits clearly above the two-line title (white line 1, orange line 2). Content slides: light gray background, slide number circle top-left, CodeDTX logo top-right, two-colour bold headline, illustration placeholder left column, orange checkmark bullets right column, optional dark navy quote strip at bottom. CTA: dark navy with orange button.

### ott-insight
Dark navy cover with corner yellow accent triangle and centered circle photo frame (orange-to-red gradient border). Content slides: light gray background, compact slide number badge top-left, photo frame with gradient border, diamond gem bullets, optional quote callout, rounded pill footer bar. CTA: navy with gradient pill button and clickable link.

### design-impact
Dark, textured, moody background (soft grain and glow, no flat color blocks) used consistently across cover, content, and CTA. Header and footer are a single pill outline split by a vertical divider — logo mark on the left, a short tag ("5 KEY INSIGHTS", "INSIGHT 01", "LET'S TALK") on the right. Cover: a huge ghosted numeral with a soft glow behind it, condensed headline with one phrase called out in a solid orange highlight box. Content: condensed headline, three bullets each with a title and one-line description, a small rounded illustration card with a soft drop shadow, an orange-to-red gradient result bar. CTA: same highlight-box headline treatment, gradient "CONTACT US" button linked to `https://www.codedtx.com/`.

### codedtx-dark
Dark Navy background (`#0B172A`), CodeDTX logo, eyebrow `ENGINEERING PERSPECTIVE`, giant white/orange stacked title `AI IS CHANGING HOW SOFTWARE IS BUILT`, 4 structured framework card boxes (01 Context, 02 Review, 03 Tests, 04 Ownership), vibrant orange takeaway box, clickable CTA button linked to `https://www.codedtx.com/`.

### codedtx-locked
Uses the master SVGs in `assets/template-codedtx-locked/`. Light off-white grid theme, large headline, structured stat rows, takeaway card, and dynamic 7-page slide numbering.

## Stating the selection

When delivering a carousel, always include a line in the quality check:

> Template selected: `ai-engineering` — topic contains "AI pipelines" and "engineering".

If the user asks for a different template, re-run with `--template <name>`.
