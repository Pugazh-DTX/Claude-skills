---
name: codedtx-post
description: Use when creating, reviewing, or rebuilding a CodeDTX LinkedIn carousel post. Drafts a Problem->Insight->Solution->Result post from a topic, picks one of 12 brand-correct SVG templates, fills it, runs it through an independent review agent, and renders the final 7-slide PDF.
---

# CodeDTX Post Skill

## Content strategy rules (apply to every topic, no exceptions)

1. Structure every post as **Problem → Insight → Solution → Result**. Never draft without a real, specific problem and a practical, specific solution.
2. Content must be useful, clear, concise, based on verified information. No unnecessary claims, no exaggeration, no generic marketing language ("revolutionary", "game-changing", etc. are banned words).
3. Title rules: catchy, creates curiosity, states a concrete value/outcome, no misleading claims. ("How we made a 2017 model TV perform the same as a 2026 model TV" is the reference bar — specific subject, concrete before/after, no unsupported hype.)
4. One clear idea per slide. Short sentences. No paragraph over 3 lines. No slide overloaded with multiple points.

## Workflow (three phases)

### Phase 1 — Content Agent (this thread)
1. Research the topic. Verify any claim/number you plan to use; if you cannot verify it, mark it for the `VERIFY`/cut decision later rather than inventing a source.
2. Identify the real Problem, the Insight, the Solution, the Result.
3. Draft 2-3 title options against the Title rules above.
4. Open `reference/template-selection-guide.md`, apply the decision table to the drafted problem, choose one `templates/NN-name/` folder (7 SVG files).
5. Fill each of the 7 SVGs' labeled text fields (see each template's field comment block) with the drafted copy. Every slide MUST have its `visual` field/element filled — no exceptions (see `reference/brand-tokens.md` "No Empty Slide Rule").
6. Save the filled set to `output/<topic-slug>/slide-1..7.svg`.

### Phase 2 — Review Agent (dispatch as a FRESH subagent, not this thread)
1. Render the 7 filled SVGs to PNG.
2. Dispatch a subagent with `review-agent.md` pasted in full as its instructions, plus the filled copy and the 7 rendered PNGs. Do NOT give it Phase 1's research notes or reasoning — cold read only.
3. Read its scorecard. Apply the gate logic in `review-agent.md`.
4. If `NEEDS REVISION`: patch only the flagged fields in the SVGs, then repeat Phase 2 with a NEW fresh subagent. Max 2 loops.
5. If `REJECTED` (fact accuracy failure): stop, report exactly what needs re-verification, do not patch blindly.
6. If still not `APPROVED` after 2 loops: stop, show the user the unresolved issues instead of looping further.

### Phase 3 — Render (only after APPROVED)
1. Re-render the 7 approved SVGs to PNG (if not already fresh).
2. Combine the 7 PNGs into a single PDF, slide order 1-7, via `render/render.md`.
3. Output path: `output/<topic-slug>/<topic-slug>.pdf`.

## Final output contract

When done, present to the user:
- The 2-3 title options considered and which was chosen (and why, against the Title rules).
- The template folder chosen and why (per the selection guide).
- The Review Agent's full scorecard.
- The rendered PDF (send it, don't just describe it).
