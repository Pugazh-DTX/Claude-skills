---
name: codedtx-template-selection-guide
description: Decision table mapping a drafted topic/problem to one of the 12 carousel templates, plus CTA-style rule.
---

# Template Selection Guide

Run this AFTER the Problem/Insight/Solution/Result brief is drafted (Phase 1), not before — template choice depends on the shape of the content, not the raw topic string.

## Decision table

| Signal in topic/problem | Template folder |
|---|---|
| "improved X to match Y", "before/after", "old vs new", "made X perform like Y" | `templates/02-before-after/` |
| "myth", "misconception", "people think... actually" | `templates/05-myth-reality/` |
| Heavy on %, counts, benchmarks, but little process | `templates/06-data-statistics/` |
| "X vs Y", tool/tech comparison | `templates/07-technology-comparison/` |
| "how it works", "architecture", "pipeline", process-heavy but light on numbers | `templates/08-how-it-works/` |
| "case study", "we helped", named client outcome | `templates/03-case-study/` |
| "steps", "framework", "phases", "our process" | `templates/04-step-by-step/` |
| "industry shift", "trend", "market" | `templates/09-industry-insight/` |
| "feature", "capability", "product update" | `templates/10-feature-product-explainer/` |
| Short, punchy, narrative/hook-driven, low data | `templates/11-full-bleed-story/` |
| No strong signal | `templates/01-problem-solution/` (default) |

## Tie-break rule

If a topic matches BOTH a data-heavy signal AND a process/how-it-works signal (common for engineering topics), prefer `templates/12-doodle-infographic/` — it structurally supports diagram + stat pills in one slide. Fall back to `06-data-statistics` or `08-how-it-works` only if the topic is single-dimension.

## CTA-style rule (applies to slide 7 in every template)

- **Lead-gen topics** (client capability, product, case study, comparison, "we can build this for you"): CTA text = `"Start Your Project"` or `"Contact Us"` — matches codedtx.com's actual site CTA copy.
- **Awareness topics** (industry insight, myth-reality, story, opinion/insight-only posts): CTA text = `"Follow CodeDTX"` or a discussion prompt ("Comment your experience below").

## Worked example

Topic: "How we made a 2017 model TV perform the same as a 2026 model TV."
- Signal: "made X perform like Y" → **`templates/02-before-after/`**.
- Funnel stage: this demonstrates CodeDTX engineering capability on a concrete before/after → lead-gen → CTA = `"Start Your Project"`.
