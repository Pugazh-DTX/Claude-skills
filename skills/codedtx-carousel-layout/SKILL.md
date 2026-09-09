---
name: codedtx-carousel-layout
description: "Build perfectly aligned dark-premium LinkedIn carousel slides for CodeDTX — enforces fixed zone constants, centered illustrations, consistent gaps between every element, and Poppins font across all 8 slides."
---

# CodeDTX Carousel Layout Skill

## Canvas & grid
- Size: **1080 × 1350 px** (LinkedIn portrait)
- Left/right margin `PAD = 72`; usable width `CW = 936`; centre `MX = 540`

## Fixed vertical zones — every content slide MUST honour these

| Constant | Y | Purpose |
|---|---|---|
| `Y_HDR_BOT` | 120 | Header band bottom / divider |
| `Y_LBL` | 148 | Section label (THE PROBLEM) |
| `Y_HEAD` | 215 | Headline line-1 baseline |
| `Y_BODY` | 322 | Body copy top |
| `Y_STAT` | 468 | Stats row baseline |
| `Y_ILL_TOP` | 536 | Illustration zone top |
| `Y_ILL_BOT` | 974 | Illustration zone bottom |
| `Y_CALL` | 988 | Callout bar top (height 60) |
| `Y_FTR` | 1082 | Footer divider |

**Nothing may cross `Y_CALL = 988`.** All illustration content must end by y ≈ 982.

## Centering rules

### Horizontal centering
- Single element centred on slide: `x = MX`, `text-anchor="middle"`
- Two-column layout: left column at `PAD`, right column at `PAD + CW//2 + 30`
- A row of N items: `x0 = (W - N*item_w - (N-1)*gap) // 2`, then `xi = x0 + i*(item_w+gap)`
- Zone labels (BEFORE / AFTER): centre on their column mid-point, not on PAD

### Vertical centering within a zone
- Available zone height: `zone_h = Y_CALL - Y_ILL_TOP = 452`
- For a block of total height `content_h`: start at `Y_ILL_TOP + (452 - content_h) // 2`
- Minimum top padding inside illustration zone: **24 px**
- Minimum bottom clearance before `Y_CALL`: **14 px**

### Text-to-element gaps
- Label above diagram: **16 px** between label baseline and diagram top
- Caption below diagram: **14 px** between diagram bottom and caption baseline
- Section divider (`horiz_div`): **12 px** breathing room above and below
- Between two stacked diagrams: **20 px** divider + 16 px padding each side

## Illustration layout patterns

### Side-by-side BEFORE / AFTER
```
zone_mid_x = MX
left_cx  = PAD + left_w // 2        # centre of left panel
right_cx = W - PAD - right_w // 2   # centre of right panel
arrow_x1 = PAD + left_w + 20
arrow_x2 = W - PAD - right_w - 20
arrow_y  = Y_ILL_TOP + zone_h // 2  # vertically centred in zone
```
- BEFORE label centred at `left_cx`, `Y_ILL_TOP + 14`
- AFTER label centred at `right_cx`, `Y_ILL_TOP + 14`
- Diagram tops at `Y_ILL_TOP + 36`
- Arrow centred vertically between diagram tops and bottoms

### Single centred diagram + stats
```
diagram_top = Y_ILL_TOP + 24
diagram_cx  = MX
stat_y      = diagram_bottom + 20   # but must be ≤ Y_CALL - 60
```

### Stacked rows (2-section layout)
```
section1_top = Y_ILL_TOP + 24
section1_bot = section1_top + section1_h
divider_y    = section1_bot + 14
section2_top = divider_y + 16
section2_bot = section2_top + section2_h   # must be ≤ Y_CALL - 14
```
If `section2_bot > Y_CALL - 14`: remove or compress section 2 rather than overflow.

### Three-column stat cards
```
card_gap = 14
card_w   = (CW - 2*card_gap) // 3   # ≈ 302
x0 = PAD
for i in range(3):
    cx = x0 + i*(card_w+card_gap)
```

### Five-column metric cards
```
card_w, gap = 170, 12
total = 5*card_w + 4*gap
x0 = (W - total) // 2
```

## Spacing checklist — run before rendering every slide

- [ ] No element baseline or rect-bottom crosses y = 988
- [ ] Headline line-1 baseline ≥ 215 (below label cap-height)
- [ ] Body copy starts ≥ Y_BODY = 322
- [ ] Illustration content has ≥ 24 px top padding from Y_ILL_TOP
- [ ] BEFORE / AFTER zone labels are centred on their column, not flush-left
- [ ] Arrow is vertically centred between paired diagrams
- [ ] All caption text below diagrams has ≥ 14 px clearance to bottom
- [ ] Section dividers have 12 px breathing room on both sides
- [ ] Callout bar text at `Y_CALL + 37` (vertically centred in 60 px bar)
- [ ] Footer logo centred at `MX` horizontally

## Font rules (Poppins — single family, four weights)
```python
# SVG attribute — no inner quotes
font-family="Poppins"
font-weight="700"   # Bold: headlines, stat values, badge text
font-weight="600"   # SemiBold: section sub-titles, card labels
font-weight="500"   # Medium: section labels (THE PROBLEM), callout text
font-weight="400"   # Regular: captions, website URL
font-weight="300"   # Light: body copy, dim annotations
```
Typical sizes: headline 54 px, stat value 68–72 px, body 22 px, label 13 px, caption 14–16 px.

## Palette
```python
bg      = "#0D1B2A"   # slide background
panel   = "#132030"   # card / panel fill
card    = "#1A2D44"   # elevated card
accent  = "#FF5A00"   # orange — primary brand
gold    = "#FFB800"   # highlights / arrows
white   = "#FFFFFF"
text    = "#DCE8F4"   # body copy
dim     = "#6A809A"   # secondary / captions
green   = "#3DDB7C"   # positive / AFTER
red     = "#FF5C5C"   # negative / BEFORE
purple  = "#A78BFA"
cyan    = "#22D3EE"
div     = "#1E3048"   # divider lines
```

## Rendering
- Build as HTML with embedded base64 woff2 Poppins (Light/Regular/Medium/Bold)
- SVG element gets `font-family="Poppins,sans-serif"` as default
- Render with Playwright/Chromium headless at `--window-size=1080,1350`
- Output: PNG per slide