---
name: codedtx-render
description: Steps to convert 7 filled SVG slides into the final carousel PDF.
---

# Render Pipeline

1. For each of the 7 filled SVGs (`output/<topic-slug>/slide-N.svg`), rasterize to PNG at 1080x1350 (2x scale for crispness = 2160x2700 render, downscale to 1080x1350 on save). Use the Browser pane (open the SVG as a `file://` URL, screenshot at the exact canvas size) — this renders gradients, fonts and filters exactly as a real browser/LinkedIn preview would, which matters because the templates use CSS-style gradients.
2. Save PNGs as `output/<topic-slug>/slide-1.png` ... `slide-7.png`.
3. Combine the 7 PNGs into one PDF, in slide order, one PNG per page, via `img2pdf` (Python, already available in this environment):
   ```python
   import img2pdf
   pages = [f"output/<topic-slug>/slide-{i}.png" for i in range(1, 8)]
   with open(f"output/<topic-slug>/<topic-slug>.pdf", "wb") as f:
       f.write(img2pdf.convert(pages))
   ```
4. Verify the PDF has exactly 7 pages before handing it back (`pdfplumber` page count check) — a wrong page count means a slide failed to render and must be fixed, not silently dropped.
