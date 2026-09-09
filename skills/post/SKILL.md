---
name: post
description: Create evidence-grounded LinkedIn posts with finished editable carousel slides and rendered PNG previews. Auto-selects one of five visual templates based on the topic — ai-engineering, ott-insight, design-impact, codedtx-dark, or codedtx-locked — and builds both the post copy and the carousel in the same turn. Use when the user asks to create, rewrite, review, humanise, simplify, or plan a LinkedIn post, founder post, technical post, buyer post, visual explainer, poster, or carousel. Also use to check claims, confidentiality, repetition, and publishing readiness. Produce both the post and carousel by default unless the user explicitly asks for text only.
---

# LinkedIn Post Manager

Turn real work, lessons, evidence, or user-supplied material into credible LinkedIn content with a matching visual carousel. Educate first. Create commercial relevance naturally. Never publish without explicit user approval.

Read [references/editorial-rules.md](references/editorial-rules.md) before drafting any public copy.

Read [references/template-selection.md](references/template-selection.md) to choose the correct carousel template before building slides.

Read [references/carousel-workflow.md](references/carousel-workflow.md) for the full build and render steps.

## Establish context

Use the current project as the source of truth when one exists.

1. Read project instructions such as `AGENTS.md`, `CLAUDE.md`, and `README.md` when present.
2. Check repository status without changing files.
3. Inspect relevant task records, recent work logs, documentation, code, tests, review notes, and history as needed.
4. Read the relevant product or component overview before relying on implementation details.
5. Inspect any existing content calendar or published topic log to avoid repetition.
6. Treat user-supplied notes, documents, links, and visuals as source material, not automatic proof.

If there is no project evidence, use only material the user supplied or facts that can be verified safely. Ask for a missing fact only when it materially changes the post. Otherwise write conservatively.

## Select the story

For a broad request such as "create today's post":

1. Identify two or three credible candidate stories.
2. Prefer meaningful work that has not already been covered.
3. Select the strongest story and briefly explain why.
4. Label its status accurately as planned, in progress, in review, completed, or deployed.

If no project update is suitable, create buyer education from an established lesson. Never manufacture news.

## Protect truth and confidentiality

Never invent or imply metrics, clients, testimonials, outcomes, approvals, partnerships, deployments, availability, or capabilities.

Remove secrets, credentials, email addresses, private URLs, internal endpoints, confidential commercial details, private source code, security weaknesses, and unapproved names.

Do not present planned work as completed. Do not say a system is live, production ready, approved, or public unless the evidence confirms it.

Keep repository paths and private citations out of public copy. List supporting sources only in the private quality check.

## Draft the post

Use 130 to 250 words unless the user requests another length.

Choose a structure that fits the story. A useful default is:

1. Hook
2. Real problem or context
3. Decision or insight
4. Practical lesson
5. Subtle relevance to the author or company
6. One low-pressure question or invitation

Write one complete post by default. Give alternatives only when requested or when several hooks would materially help.

## Select and build the carousel

Read [references/template-selection.md](references/template-selection.md) first to understand the five templates and their keyword rules. Do NOT pass `--template` to the builder unless the user explicitly requests a specific template — the builder auto-selects by scanning the topic, subtitle, and slide content. After the build runs, report which template the builder selected and why (from its printed output line "Template selected: …").

**Five templates — one skill, one builder:**

| Template | Best for |
|---|---|
| `ai-engineering` | AI, ML, engineering, backend, pipelines, developer tools |
| `ott-insight` | Platforms, SaaS, growth, business strategy, OTT, B2B |
| `design-impact` | Design, UX/UI, creative tools, visual workflows |
| `codedtx-dark` | Dark engineering framework, software architecture, guardrails |
| `codedtx-locked` | General CodeDTX brand content, any topic not covered above |

### CodeDTX master rules

SVG master files live in `assets/template-codedtx-locked/` (`codedtx-locked`), `assets/template-codedtx-dark/` (`codedtx-dark`), `assets/template-ai-engineering/`, `assets/template-ott-insight/`, and `assets/template-design-impact/`. Copy them to the output folder, then fill replacement text. Never change theme, colours, gradients, font family, font sizes, font weights, geometry, spacing, logo, embedded assets, component layout, or footer styling. If content overflows, shorten the copy.

Page numbering style varies by template — some show a running `N / 7` count, others use a static page marker or none at all; this is intentional per-template design, not a bug. The CTA button on page 7 is a real clickable link in the finished PDF (a link annotation is stamped onto it after rendering, since the PDF is otherwise flat images) and points to `https://www.codedtx.com/`. Footer links on the other 6 pages are clickable only in the HTML output, not in the PDF.

### Template rules

For `design-impact`, set `dark_slide: true` on slides that should use the navy background variant. Set `spotlight` only when the slide has a single real metric in ALL-CAPS under 20 characters.

Keep content within the text areas defined in the SVG. If copy overflows, shorten it — do not adjust the design.

### Build command

```bash
python3 <skill-path>/scripts/build_carousel.py \
  --input brief.json \
  --output outputs/linkedin/<slug>/
```

To force a template: `--template ai-engineering`

Add `--no-pdf` to skip PDF compilation (HTML and PNG only).

### Input JSON shape (all templates)

```json
{
  "topic": "Topic that drives auto-selection",
  "subtitle": "One sentence under 15 words",
  "slides": [
    {
      "number": 1,
      "headline": "Short headline for the slide",
      "points": ["Point one", "Point two", "Point three"],
      "image_label": "What the image shows",
      "section_label": "CHALLENGE",
      "dark_slide": false,
      "spotlight": "3X FASTER",
      "quote": "Optional pull quote",
      "quote_author": "Source name"
    }
  ],
  "cta": {
    "headline": "Low-pressure closing question",
    "body": "One clear next step.",
    "action": "FOLLOW"
  }
}
```

Provide exactly **5 content slides** (cover + 5 content + CTA = 7 pages total). If fewer than 5 are given the builder auto-pads with defaults. If more than 5 are given the builder uses the first 5.

Omit fields that do not apply to the chosen template.

## Render and inspect

Render every `slide-N.html` at 1080 by 1350 with Playwright. Save each preview as `slide-N.png` in a `previews/` folder. After rendering, the builder compiles all 7 PNGs into a single `carousel.pdf` (one slide per page) using `img2pdf` or `Pillow`.

Open every rendered slide. Check text overflow, collisions, contrast, numbering, factual accuracy, and mobile readability. Fix and re-render any failed slide.

If PNG rendering is unavailable, deliver the SVG and HTML slides and state the limitation clearly.

## Verify before delivery

1. Trace every factual claim to a source.
2. Confirm work status and remove confidential details.
3. Search all public copy for hyphens, en dashes, and em dashes. Rewrite every match.
4. Read the post and carousel copy aloud. Rewrite formal, mechanical, crowded, or breathless lines.
5. Confirm the hook creates honest curiosity without clickbait.
6. Check that jargon is removed or explained.
7. For visuals, check overflow, collisions, contrast, numbering, asset loading, and mobile readability.

## Deliver

Return all of the following in one response:

### Selected story

Source work, current status, why it matters, and intended reader.

### LinkedIn post

Copy-ready public post.

### Carousel

Finished carousel files, rendered previews, slide count, headline, template used, and why it was selected.

### Quality check

Claims verified, confidential information removed, planned work labelled, repetition checked, dash check passed, template selected with reason, and three to five hashtags. Always include `#CodeDTX` as the first hashtag, followed by two to four topic-relevant hashtags (e.g. `#AI` `#OTTStreaming` `#ProductDesign`).

### Alternative hooks

Three short options.

End by stating that nothing was published. Never post, message, commit, push, deploy, or change production systems unless the user explicitly requests and authorises that separate action.

Update an editorial history only after the user approves the draft and only when the project already uses one or the user asks to create one.
