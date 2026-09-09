#!/usr/bin/env python3
"""
LinkedIn carousel builder — CodeDTX multi-template edition.

Four templates, auto-selected from the topic keyword, or set explicitly:
  ai-engineering   Dark navy cover, checkmark bullets, navy quote block.
  ott-insight      Diagonal split cover, gem bullets, gradient photo frame.
  design-impact    Beige/navy split cover, wave divider, ALL-CAPS spotlight.
  codedtx-locked   Locked CodeDTX master SVGs (existing brand template).

Output: 7 HTML slide files + 7 PNG previews + single carousel.pdf

Usage:
  python3 build_carousel.py --input brief.json --output outputs/linkedin/my-post/
  python3 build_carousel.py --input brief.json --output out/ --template ott-insight
"""

import argparse, base64, json, os, re, sys, textwrap, urllib.request, urllib.parse

W, H             = 1080, 1350
SLIDES_REQUIRED  = 7  # cover (1) + content (5) + cta (1)
CONTENT_SLIDES   = 5
DASHES           = {"-", "–", "—"}

# Template priority — first full-word match wins.
# Order: ai-engineering first so specific tech terms beat generic business words.
TEMPLATE_KEYWORDS = [
    ("ai-engineering", ["ai", "ml", "llm", "gpt", "artificial intelligence",
                        "machine learning", "data science",
                        "engineering", "developer", "development", "pipeline",
                        "backend", "algorithm", "devops", "coding",
                        "software", "cloud", "api"]),
    ("design-impact",  ["design", "ux", "ui", "creative", "visual", "figma",
                        "brand", "typography", "prototype", "wireframe",
                        "designer", "illustration", "motion", "graphic"]),
    ("ott-insight",    ["platform", "saas", "business strategy", "go-to-market",
                        "launch", "revenue", "startup",
                        "ott", "streaming", "pricing", "b2b",
                        "sales funnel", "retention", "churn"]),
    ("codedtx-dark",   ["framework", "architecture", "guardrails", "review",
                        "testing", "ownership", "production-first", "quality"]),
]
_AI_WORDS: set = set()  # now handled in TEMPLATE_KEYWORDS above


# ── utilities ─────────────────────────────────────────────────────────────────

def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def wrap(text, width, maxlines=2):
    return textwrap.wrap(str(text), width)[:maxlines]


def pl(text, width=20):
    lines = wrap(text, width, 2)
    return (lines[0] if len(lines) > 0 else "",
            lines[1] if len(lines) > 1 else "")


def check_dashes(data):
    def recurse(obj):
        if isinstance(obj, str):
            for ch in DASHES:
                if ch in obj:
                    return ch, obj
        elif isinstance(obj, dict):
            for v in obj.values():
                r = recurse(v)
                if r:
                    return r
        elif isinstance(obj, list):
            for v in obj:
                r = recurse(v)
                if r:
                    return r
        return None
    return recurse(data)


def _word_match(keyword, text):
    return bool(re.search(r"\b" + re.escape(keyword) + r"\b", text))


def select_template(topic, override=None, subtitle="", slides=None):
    """Auto-select template by scanning topic + subtitle first, then slide headlines.

    Scanning points is intentionally skipped — generic words like 'code review'
    or 'growth chart' inside bullet copy would cause false positives.
    """
    if override and override != "auto":
        return override
    # Topic + subtitle carry the clearest signal; headlines + section labels are secondary.
    parts = [topic or "", subtitle or ""]
    for sl in (slides or []):
        parts.append(sl.get("headline", ""))
        parts.append(sl.get("section_label", ""))
        parts.append(sl.get("image_label", ""))
        # points intentionally excluded — too noisy for auto-selection
    t = " ".join(parts).lower()
    for tmpl, keywords in TEMPLATE_KEYWORDS:
        if any(_word_match(kw, t) for kw in keywords):
            return tmpl
    if any(_word_match(kw, t) for kw in _AI_WORDS):
        return "ai-engineering"
    return "codedtx-locked"


def skill_dir():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_svg(asset_subpath):
    path = os.path.join(skill_dir(), "assets", asset_subpath)
    with open(path, encoding="utf-8") as f:
        return f.read()


NATURAL_TEXT_MAP = {
    "TITLE_LINE1": ["Headline line one", "Your Main Headline Goes Here", "AI IS CHANGING", "AI ENGINEERING", "THE IMPORTANCE OF"],
    "TITLE_LINE2": ["headline line two", "With Highlighted Action", "HOW SOFTWARE", "DEVELOPMENT", "AI IN DESIGN"],
    "COVER_BIG_L1": ["Headline line one", "Your Main Headline Goes Here", "AI IS CHANGING"],
    "COVER_BIG_L2": ["headline line two", "With Highlighted Action", "HOW SOFTWARE"],
    "SUBTITLE_LINE1": ["Body paragraph one, first line. Keep every line inside the", "Add a clear supporting description here for the topic.", "The tooling changed in eighteen months. The", "How production-grade AI agents, pipelines,", "How generative tools and intelligent systems"],
    "SUBTITLE_LINE2": ["952 px content width — SVG does not wrap.", "Explain the context in two clean lines of readable copy.", "way most teams build has not caught up yet.", "and automated workflows accelerate dev speed.", "elevate creative freedom and product velocity."],
    "COVER_P1": ["Body paragraph one, first line. Keep every line inside the", "Add a clear supporting description here for the topic.", "The tooling changed in eighteen months. The"],
    "COVER_P2": ["952 px content width — SVG does not wrap.", "Explain the context in two clean lines of readable copy.", "way most teams build has not caught up yet."],
    "COVER_SETUP": ["ENGINEERING PERSPECTIVE", "MORE ABOUT", "EYEBROW"],
    "SECTION_TAG": ["SECTION TAG", "THE FRAMEWORK", "THE INDUSTRY SHIFT", "ENGINEERING PERSPECTIVE", "PLATFORM & STRATEGY INSIGHT"],
    "HL1": ["Headline line one", "Where to put the", "Speed without structure", "AI IS HELPING DESIGNERS"],
    "HL2": ["headline line two", "guardrails", "only moves the bottleneck", "MAKE BETTER CHOICES"],
    "HEADLINE_L1": ["Headline line one", "Where to put the", "Speed without structure", "Your Main Headline Goes Here"],
    "HEADLINE_L2": ["headline line two", "guardrails", "only moves the bottleneck", "With Highlighted Action"],
    "BODY1_L1": ["Body paragraph one, first line. Keep every line inside the", "Give the model the same constraints", "Add a clear supporting description for the topic"],
    "BODY1_L2": ["952 px content width — SVG does not wrap.", "you would give a new engineer.", "here, written in two clean, scannable lines."],
    "BODY2_L1": ["Body paragraph two, first line. Use an inline tspan for", "Review effort scales with volume.", "Use a second paragraph to add context, an example,"],
    "BODY2_L2": ["emphasis: 16.7 ms or one thread.", "Budget for it deliberately.", "or a number worth remembering."],
    "CTA_HL1": ["Build Software That", "Let's build", "100-Day Modernization", "Ready to Scale Your", "THE FUTURE OF DESIGN"],
    "CTA_HL2": ["Holds Up Under Scale", "software that", "Framework Blueprint", "Platform Architecture?", "IS INTELLIGENT"],
    "CTA_B1": ["See how CodeDTX ships production grade software at codedtx.com.", "Visit codedtx.com for engineering", "UX/UI Redesign Blueprint", "Visit codedtx.com for weekly strategic insights", "AI is not replacing designers."],
    "CTA_B2": ["perspectives on building with AI, without", "Security & Performance Upgrade", "and production ready engineering blueprints.", "It's upgrading them."],
    "CTA_ACTION": ["CONTACT US", "Contact Us"],
    "CTA_ACTION_TEXT": ["CONTACT US"],
    "STAT1_LABEL": ["Key metric label one"],
    "STAT1_VAL":   ["42%"],
    "STAT2_LABEL": ["Key metric label two"],
    "STAT2_VAL":   ["3.2x"],
    "STAT3_LABEL": ["Key metric label three"],
    "STAT3_VAL":   ["18 days"],
    "LESSON_L1":   ["Write the lesson in one sentence, with the turn in"],
    "LESSON_L2":   ["orange emphasis."],
    "TAKEAWAY_TEXT": ["Ship what you can explain, test, and own"],
}


IMAGE_PLACEHOLDER_BLOCKS = {
    "ai-engineering-content": {
        "old": '<text x="195" y="260" font-family="\'Poppins\', sans-serif" font-weight="600" font-size="22px" fill="#9CA3AF" text-anchor="middle">Add your visual here</text>',
        "box": (0, 0, 390, 520, 16),
        "clip_id": "aieContentImgClip",
    },
    "ott-insight-content": {
        "old": ('<g transform="translate(208, 220)" opacity="0.6">\n'
                '      <circle cx="0" cy="-30" r="15" fill="#FACC15" />\n'
                '      <path d="M -110 55 L -38 -22 L 5 18 L 48 -32 L 110 55 Z" fill="#FF6B00" opacity="0.7" />\n'
                '      <path d="M -110 55 L -16 12 L 25 44 L 65 6 L 110 55 Z" fill="#0B172A" opacity="0.85" />\n'
                '    </g>\n'
                '    <text x="208" y="300" font-family="\'Poppins\', sans-serif" font-weight="600" font-size="20px" fill="#94A3B8" text-anchor="middle">Add your visual here</text>'),
        "box": (0, 0, 416, 494, 16),
        "clip_id": "ottContentImgClip",
    },
    "design-impact-content": {
        "old": ('<g transform="translate(170, 150)" opacity="0.65">\n'
                '      <circle cx="0" cy="-22" r="13" fill="#FACC15" />\n'
                '      <path d="M -90 48 L -32 -16 L 8 24 L 48 -32 L 90 48 Z" fill="#FF6B00" opacity="0.7" />\n'
                '      <path d="M -90 48 L -16 8 L 24 44 L 65 4 L 90 48 Z" fill="#1B2A4A" opacity="0.8" />\n'
                '    </g>\n'
                '    <text x="170" y="270" font-family="\'Poppins\', sans-serif" font-weight="600" font-size="16px" fill="#94A3B8" text-anchor="middle">Add your visual here</text>'),
        "box": (0, 0, 340, 300, 16),
        "clip_id": "diContentImgClip",
    },
    "codedtx-dark-content": {
        "old": ('<g transform="translate(220, 165)" opacity="0.6">\n'
                '      <circle cx="0" cy="-30" r="18" fill="#FF6B00" opacity="0.5"/>\n'
                '      <path d="M -120 60 L -42 -24 L 6 20 L 52 -36 L 120 60 Z" fill="#FF6B00" opacity="0.55" />\n'
                '      <path d="M -120 60 L -18 14 L 28 48 L 70 6 L 120 60 Z" fill="#0B172A" opacity="0.9" />\n'
                '    </g>\n'
                '    <text x="220" y="350" class="illus-label" text-anchor="middle">Add your visual here</text>'),
        "box": (0, 0, 440, 400, 16),
        "clip_id": "darkContentImgClip",
    },
}


def swap_image_placeholder(svg, key, img_uri):
    """Replace a template's static placeholder icon with a real generated
    illustration, matched by exact markup (same approach as NATURAL_TEXT_MAP)
    so the raw .svg file never needs {{ }} token syntax."""
    spec = IMAGE_PLACEHOLDER_BLOCKS[key]
    if spec["old"] not in svg or not img_uri:
        return svg
    x, y, w, h, rx = spec["box"]
    clip_id = spec["clip_id"]
    if clip_id not in svg:
        clip_def = f'<clipPath id="{clip_id}"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}"/></clipPath>'
        svg = svg.replace("<defs>", "<defs>" + clip_def, 1)
    image_tag = (f'<image href="{img_uri}" x="{x}" y="{y}" width="{w}" height="{h}" '
                 f'clip-path="url(#{clip_id})" preserveAspectRatio="xMidYMid slice" />')
    return svg.replace(spec["old"], image_tag)


def swap_bullets_ai_engineering(svg, points):
    """Match each bullet's exact markup and swap in real point text, keeping
    the original bold-first-word treatment."""
    slots = [
        ("Long", " sprint cycles"),
        ("Large", " engineering teams"),
        ("Slow", " testing &amp; deployments"),
        ("Unpredictable", " delivery timelines"),
    ]
    for word, rest in slots:
        if not points:
            break
        pt = points.pop(0).strip()
        if not pt:
            continue
        parts = pt.split(None, 1)
        new_word = esc(parts[0][:24])
        new_rest = esc((" " + parts[1])[:46]) if len(parts) > 1 else ""
        old = f'<tspan fill="#FF6B00" font-weight="800">{word}</tspan>{rest}'
        new = f'<tspan fill="#FF6B00" font-weight="800">{new_word}</tspan>{new_rest}'
        if old in svg:
            svg = svg.replace(old, new)
    return svg


def swap_bullets_ott_insight(svg, points):
    slots = [
        ("Code arrives faster than", "teams can review it."),
        ("Standards drift and", "ownership blurs over time."),
        ("Maintenance costs surface", "later in delivery."),
    ]
    for l1, l2 in slots:
        if not points:
            break
        pt = points.pop(0).strip()
        if not pt:
            continue
        nl1, nl2 = pl(pt, 22)
        old = (f'<text x="48" y="24" class="bullet-text">{l1}</text>\n'
               f'      <text x="48" y="58" class="bullet-text">{l2}</text>')
        new = (f'<text x="48" y="24" class="bullet-text">{esc(nl1)}</text>\n'
               f'      <text x="48" y="58" class="bullet-text">{esc(nl2)}</text>')
        if old in svg:
            svg = svg.replace(old, new)
    return svg


def swap_bullets_design_impact(svg, points):
    slots = [
        ("Faster Decisions", "Teams act on data instead of guesswork."),
        ("Smarter Product Choices", "AI surfaces patterns humans tend to miss."),
        ("Measurable UX Improvements", "Every change ties back to a real metric."),
    ]
    for title, desc in slots:
        if not points:
            break
        pt = points.pop(0).strip()
        if not pt:
            continue
        words = pt.split()
        new_title = esc(" ".join(words[:3]).title()[:30]) if words else title
        new_desc = esc(pt[:44])
        old = (f'<text x="52" y="16" class="bullet-title">{title}</text>\n'
               f'      <text x="52" y="44" class="bullet-desc">{desc}</text>')
        new = (f'<text x="52" y="16" class="bullet-title">{new_title}</text>\n'
               f'      <text x="52" y="44" class="bullet-desc">{new_desc}</text>')
        if old in svg:
            svg = svg.replace(old, new)
    return svg


def fill(svg, replacements):
    for key, value in replacements.items():
        if value is not None:
            val_str = esc(str(value))
            svg = svg.replace("{{" + key + "}}", val_str)
            if key in NATURAL_TEXT_MAP:
                for target_text in NATURAL_TEXT_MAP[key]:
                    if target_text and val_str:
                        svg = svg.replace(target_text, val_str)

    if "SLIDE_NUM" in replacements and "SLIDE_TOTAL" in replacements:
        num_str = str(replacements["SLIDE_NUM"])
        tot_str = str(replacements["SLIDE_TOTAL"])
        page_fmt = f"{num_str} / {tot_str}"
        svg = svg.replace(">PAGE<", f">{page_fmt}<")

    svg = re.sub(r"\{\{[A-Z0-9_]+\}\}", "", svg)
    return svg


def html_wrap(svg_content):
    return (
        "<!DOCTYPE html><html><head>"
        "<meta charset='utf-8'>"
        "<link rel='preconnect' href='https://fonts.googleapis.com'>"
        "<link rel='stylesheet' "
        "href='https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700;800;900&display=swap'>"
        "<style>*{margin:0;padding:0;box-sizing:border-box}"
        "body{width:" + str(W) + "px;height:" + str(H) + "px;overflow:hidden}"
        "svg{display:block;font-family:Poppins,Arial,sans-serif}</style>"
        "</head><body>" + svg_content + "</body></html>"
    )


def save_slide(html, out_dir, n):
    path = os.path.join(out_dir, f"slide-{n}.html")
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"  slide-{n}.html")
    return path


# ── illustration generator ────────────────────────────────────────────────────

def _svg_uri(svg_str):
    """Encode SVG string as a base64 data URI."""
    b64 = base64.b64encode(svg_str.encode("utf-8")).decode("ascii")
    return "data:image/svg+xml;base64," + b64


def _illus_pipeline(w, h):
    """4-step pipeline flow diagram on dark navy background."""
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">'
        '<defs>'
        '<linearGradient id="bg" x1="0" y1="0" x2="0" y2="1" gradientUnits="objectBoundingBox">'
        '<stop offset="0%" stop-color="#0d1a2e"/><stop offset="100%" stop-color="#1B2A4A"/>'
        '</linearGradient>'
        '<marker id="ar" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">'
        '<polygon points="0 0,10 3.5,0 7" fill="#FF6B00"/>'
        '</marker>'
        '</defs>'
        '<rect width="{w}" height="{h}" fill="url(#bg)"/>'
        # Decorative bg circles
        '<circle cx="320" cy="60" r="80" fill="#FF6B00" opacity="0.05"/>'
        '<circle cx="50" cy="{h2}" r="60" fill="#E8002D" opacity="0.05"/>'
        # Step 1
        '<circle cx="195" cy="90" r="48" fill="#1f3258" stroke="#FF6B00" stroke-width="2.5"/>'
        '<text x="195" y="84" font-family="Arial,sans-serif" font-size="22" fill="#FF6B00" text-anchor="middle" font-weight="900">01</text>'
        '<text x="195" y="106" font-family="Arial,sans-serif" font-size="14" fill="#8899bb" text-anchor="middle">INPUT</text>'
        # Arrow 1→2
        '<line x1="195" y1="142" x2="195" y2="170" stroke="#FF6B00" stroke-width="2.5" marker-end="url(#ar)"/>'
        # Step 2
        '<circle cx="195" cy="220" r="48" fill="#1f3258" stroke="#FF6B00" stroke-width="2.5"/>'
        '<text x="195" y="214" font-family="Arial,sans-serif" font-size="22" fill="#FF6B00" text-anchor="middle" font-weight="900">02</text>'
        '<text x="195" y="236" font-family="Arial,sans-serif" font-size="14" fill="#8899bb" text-anchor="middle">PROCESS</text>'
        # Arrow 2→3
        '<line x1="195" y1="272" x2="195" y2="300" stroke="#FF6B00" stroke-width="2.5" marker-end="url(#ar)"/>'
        # Step 3
        '<circle cx="195" cy="350" r="48" fill="#1f3258" stroke="#FF6B00" stroke-width="2.5"/>'
        '<text x="195" y="344" font-family="Arial,sans-serif" font-size="22" fill="#FF6B00" text-anchor="middle" font-weight="900">03</text>'
        '<text x="195" y="366" font-family="Arial,sans-serif" font-size="14" fill="#8899bb" text-anchor="middle">VALIDATE</text>'
        # Arrow 3→4
        '<line x1="195" y1="402" x2="195" y2="380" stroke="none"/>'
        '<line x1="195" y1="402" x2="195" y2="356" stroke="none"/>'
        # Step 4 output
        '<rect x="100" y="418" width="190" height="56" rx="28" fill="#FF6B00"/>'
        '<text x="195" y="451" font-family="Arial,sans-serif" font-size="18" fill="#FFFFFF" text-anchor="middle" font-weight="800">OUTPUT ✓</text>'
        '<line x1="195" y1="400" x2="195" y2="416" stroke="#FF6B00" stroke-width="2.5" marker-end="url(#ar)"/>'
        '</svg>'
    ).format(w=w, h=h, h2=h // 2)


def _illus_neural(w, h):
    """Neural network visualization on dark background."""
    cx = w // 2
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">'
        '<defs>'
        '<linearGradient id="bg" x1="0" y1="0" x2="0" y2="1" gradientUnits="objectBoundingBox">'
        '<stop offset="0%" stop-color="#0a1628"/><stop offset="100%" stop-color="#1B2A4A"/>'
        '</linearGradient>'
        '<linearGradient id="og" x1="0" y1="0" x2="1" y2="0" gradientUnits="objectBoundingBox">'
        '<stop offset="0%" stop-color="#FF6B00"/><stop offset="100%" stop-color="#E8002D"/>'
        '</linearGradient>'
        '</defs>'
        '<rect width="{w}" height="{h}" fill="url(#bg)"/>'
        # Input layer (x=60)
        '<circle cx="60" cy="130" r="22" fill="#243555" stroke="#FF6B00" stroke-width="1.5"/>'
        '<circle cx="60" cy="220" r="22" fill="#243555" stroke="#FF6B00" stroke-width="1.5"/>'
        '<circle cx="60" cy="310" r="22" fill="#243555" stroke="#FF6B00" stroke-width="1.5"/>'
        '<text x="60" y="390" font-family="Arial" font-size="11" fill="#556677" text-anchor="middle">INPUT</text>'
        # Hidden layer (x=195)
        '<circle cx="195" cy="95" r="24" fill="#2a3e62" stroke="#FF6B00" stroke-width="2"/>'
        '<circle cx="195" cy="180" r="24" fill="#2a3e62" stroke="#FF6B00" stroke-width="2"/>'
        '<circle cx="195" cy="265" r="24" fill="#2a3e62" stroke="#FF6B00" stroke-width="2"/>'
        '<circle cx="195" cy="350" r="24" fill="#2a3e62" stroke="#FF6B00" stroke-width="2"/>'
        '<text x="195" y="405" font-family="Arial" font-size="11" fill="#556677" text-anchor="middle">HIDDEN</text>'
        # Output layer (x=330)
        '<circle cx="330" cy="155" r="26" fill="url(#og)"/>'
        '<circle cx="330" cy="265" r="26" fill="url(#og)"/>'
        '<text x="330" y="405" font-family="Arial" font-size="11" fill="#556677" text-anchor="middle">OUTPUT</text>'
        # Connections input→hidden (orange, semi-transparent)
        '<g stroke="#FF6B00" stroke-width="1" opacity="0.25">'
        '<line x1="82" y1="130" x2="171" y2="95"/>'
        '<line x1="82" y1="130" x2="171" y2="180"/>'
        '<line x1="82" y1="130" x2="171" y2="265"/>'
        '<line x1="82" y1="130" x2="171" y2="350"/>'
        '<line x1="82" y1="220" x2="171" y2="95"/>'
        '<line x1="82" y1="220" x2="171" y2="180"/>'
        '<line x1="82" y1="220" x2="171" y2="265"/>'
        '<line x1="82" y1="220" x2="171" y2="350"/>'
        '<line x1="82" y1="310" x2="171" y2="95"/>'
        '<line x1="82" y1="310" x2="171" y2="180"/>'
        '<line x1="82" y1="310" x2="171" y2="265"/>'
        '<line x1="82" y1="310" x2="171" y2="350"/>'
        '</g>'
        # Connections hidden→output
        '<g stroke="#FF6B00" stroke-width="1.5" opacity="0.45">'
        '<line x1="219" y1="95" x2="304" y2="155"/>'
        '<line x1="219" y1="180" x2="304" y2="155"/>'
        '<line x1="219" y1="180" x2="304" y2="265"/>'
        '<line x1="219" y1="265" x2="304" y2="155"/>'
        '<line x1="219" y1="265" x2="304" y2="265"/>'
        '<line x1="219" y1="350" x2="304" y2="265"/>'
        '</g>'
        # Label
        '<text x="{cx}" y="440" font-family="Arial" font-size="15" fill="#FF6B00" text-anchor="middle" font-weight="700">NEURAL NETWORK</text>'
        '</svg>'
    ).format(w=w, h=h, cx=cx)


def _illus_chart(w, h):
    """Bar chart with trend line on light background."""
    bar_w = 38
    gap   = 20
    bars  = [0.45, 0.62, 0.55, 0.78, 0.91, 0.85]
    max_bar_h = h - 140
    base_y = h - 80
    start_x = (w - (len(bars) * (bar_w + gap) - gap)) // 2

    rects = ""
    trend_pts = []
    for i, ratio in enumerate(bars):
        x = start_x + i * (bar_w + gap)
        bh = int(ratio * max_bar_h * 0.6)
        y  = base_y - bh
        cx = x + bar_w // 2
        # Gradient rect
        rects += (
            '<defs><linearGradient id="b{i}" x1="0" y1="0" x2="0" y2="1" '
            'gradientUnits="objectBoundingBox">'
            '<stop offset="0%" stop-color="#FF6B00"/>'
            '<stop offset="100%" stop-color="#E8002D" stop-opacity="0.7"/>'
            '</linearGradient></defs>'
            '<rect x="{x}" y="{y}" width="{bw}" height="{bh}" rx="5" fill="url(#b{i})"/>'
        ).format(i=i, x=x, y=y, bw=bar_w, bh=bh)
        trend_pts.append(f"{cx},{y - 18}")

    trend_line = "<polyline points='" + " ".join(trend_pts) + "' fill='none' stroke='#1B2A4A' stroke-width='2.5' stroke-dasharray='6,4'/>"
    dots = ""
    for p in trend_pts:
        xy = p.split(",")
        dots += "<circle cx='" + xy[0] + "' cy='" + xy[1] + "' r='5' fill='#1B2A4A'/>"

    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">'
        '<rect width="{w}" height="{h}" fill="#F5F0E8" rx="16"/>'
        # Grid lines
        '<g stroke="#d0c8b8" stroke-width="1" opacity="0.8">'
        '<line x1="30" y1="80" x2="{w2}" y2="80"/>'
        '<line x1="30" y1="160" x2="{w2}" y2="160"/>'
        '<line x1="30" y1="240" x2="{w2}" y2="240"/>'
        '<line x1="30" y1="320" x2="{w2}" y2="320"/>'
        '</g>'
        '{rects}'
        '{trend_line}'
        '{dots}'
        '<text x="{cx}" y="{ty}" font-family="Arial" font-size="15" fill="#1B2A4A" text-anchor="middle" font-weight="700">PERFORMANCE GROWTH</text>'
        '</svg>'
    ).format(
        w=w, h=h, w2=w - 30,
        rects=rects, trend_line=trend_line, dots=dots,
        cx=w // 2, ty=h - 30
    )


def _illus_code(w, h):
    """Code editor visualization on dark background."""
    lines = [
        ("#FF6B00", 55, "def  transform(data):"),
        ("#8899bb", 42, "    results = []"),
        ("#8899bb", 58, "    for item in data:"),
        ("#FF6B00", 50, "        out = process(item)"),
        ("#8899bb", 45, "        results.append(out)"),
        ("#8899bb", 35, "    return results"),
        ("#556677", 30, ""),
        ("#FF6B00", 55, "# Deploy to production"),
        ("#8899bb", 48, "pipeline.run(transform)"),
    ]
    line_h = 44
    start_y = 110
    code_elements = ""
    for i, (color, opacity_pct, text) in enumerate(lines):
        y = start_y + i * line_h
        # line number
        code_elements += f'<text x="42" y="{y}" font-family="Courier,monospace" font-size="16" fill="#334466">{i+1:02d}</text>'
        if text:
            code_elements += f'<text x="80" y="{y}" font-family="Courier,monospace" font-size="16" fill="{color}">{esc(text)}</text>'

    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">'
        '<rect width="{w}" height="{h}" fill="#0d1628" rx="16"/>'
        # Editor chrome
        '<rect width="{w}" height="52" fill="#1a2640" rx="16"/>'
        '<rect x="0" y="36" width="{w}" height="16" fill="#1a2640"/>'
        # Traffic lights
        '<circle cx="28" cy="26" r="7" fill="#E8002D" opacity="0.8"/>'
        '<circle cx="50" cy="26" r="7" fill="#FF6B00" opacity="0.8"/>'
        '<circle cx="72" cy="26" r="7" fill="#2dba4e" opacity="0.8"/>'
        # File tab
        '<rect x="100" y="10" width="140" height="32" rx="6" fill="#243555"/>'
        '<text x="170" y="30" font-family="Courier,monospace" font-size="13" fill="#8899bb" text-anchor="middle">pipeline.py</text>'
        # Line number gutter
        '<rect x="0" y="52" width="64" height="{h2}" fill="#111e30"/>'
        # Cursor blink line
        '<rect x="80" y="152" width="2" height="20" fill="#FF6B00" opacity="0.9"/>'
        '{code}'
        # Status bar
        '<rect x="0" y="{sb}" width="{w}" height="32" fill="#FF6B00"/>'
        '<text x="20" y="{sbt}" font-family="Courier,monospace" font-size="13" fill="#FFFFFF" font-weight="700">Python  UTF-8  LF  Ready</text>'
        '</svg>'
    ).format(w=w, h=h, h2=h - 52, code=code_elements, sb=h - 32, sbt=h - 12)


def _illus_network(w, h):
    """Network topology — central hub with spokes on dark background."""
    cx = w // 2
    cy = (h - 60) // 2 + 30
    hub_r = 40
    sat_r = 24
    spoke_len = 110
    import math
    satellites = [
        (0,   "#FF6B00", "API"),
        (60,  "#E8002D", "DB"),
        (120, "#FF6B00", "CDN"),
        (180, "#E8002D", "Auth"),
        (240, "#FF6B00", "Cache"),
        (300, "#E8002D", "Queue"),
    ]
    lines = ""
    nodes = ""
    for deg, color, label in satellites:
        rad = deg * 3.14159 / 180
        sx = cx + int(spoke_len * math.cos(rad))
        sy = cy + int(spoke_len * math.sin(rad))
        lines += f'<line x1="{cx}" y1="{cy}" x2="{sx}" y2="{sy}" stroke="{color}" stroke-width="2" opacity="0.5"/>'
        nodes += (
            f'<circle cx="{sx}" cy="{sy}" r="{sat_r}" fill="#1f3258" stroke="{color}" stroke-width="2"/>'
            f'<text x="{sx}" y="{sy + 5}" font-family="Arial" font-size="11" fill="{color}" '
            f'text-anchor="middle" font-weight="700">{label}</text>'
        )

    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">'
        '<defs>'
        '<linearGradient id="bg" x1="0" y1="0" x2="0" y2="1" gradientUnits="objectBoundingBox">'
        '<stop offset="0%" stop-color="#0a1628"/><stop offset="100%" stop-color="#1B2A4A"/>'
        '</linearGradient>'
        '</defs>'
        '<rect width="{w}" height="{h}" fill="url(#bg)"/>'
        # Concentric pulse circles
        '<circle cx="{cx}" cy="{cy}" r="70" fill="none" stroke="#FF6B00" stroke-width="1" opacity="0.15"/>'
        '<circle cx="{cx}" cy="{cy}" r="100" fill="none" stroke="#FF6B00" stroke-width="1" opacity="0.1"/>'
        '<circle cx="{cx}" cy="{cy}" r="140" fill="none" stroke="#FF6B00" stroke-width="1" opacity="0.06"/>'
        '{lines}'
        '{nodes}'
        # Hub
        '<circle cx="{cx}" cy="{cy}" r="{hr}" fill="#FF6B00"/>'
        '<text x="{cx}" y="{cy}" font-family="Arial" font-size="13" fill="#FFFFFF" text-anchor="middle" dominant-baseline="middle" font-weight="900">CLOUD</text>'
        # Title
        '<text x="{cx}" y="{ty}" font-family="Arial" font-size="14" fill="#8899bb" text-anchor="middle">DISTRIBUTED ARCHITECTURE</text>'
        '</svg>'
    ).format(w=w, h=h, cx=cx, cy=cy, hr=hub_r, lines=lines, nodes=nodes, ty=h - 30)


def _illus_growth(w, h):
    """Upward trend chart with gradient area fill."""
    pts_raw = [
        (0.05, 0.75), (0.18, 0.65), (0.30, 0.58), (0.42, 0.48),
        (0.55, 0.38), (0.68, 0.28), (0.80, 0.20), (0.92, 0.12),
    ]
    chart_l, chart_r = 40, w - 30
    chart_t, chart_b = 60, h - 100
    chart_w = chart_r - chart_l
    chart_h = chart_b - chart_t

    def to_xy(rx, ry):
        return (int(chart_l + rx * chart_w), int(chart_t + ry * chart_h))

    pts = [to_xy(rx, ry) for rx, ry in pts_raw]
    # Line points
    line_pts = " ".join(f"{x},{y}" for x, y in pts)
    # Area polygon (line + back along bottom)
    area_pts = line_pts + f" {chart_r},{chart_b} {chart_l},{chart_b}"
    dots = "".join(f'<circle cx="{x}" cy="{y}" r="6" fill="#1B2A4A"/>' for x, y in pts)

    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">'
        '<defs>'
        '<linearGradient id="area" x1="0" y1="0" x2="0" y2="1" gradientUnits="objectBoundingBox">'
        '<stop offset="0%" stop-color="#FF6B00" stop-opacity="0.5"/>'
        '<stop offset="100%" stop-color="#FF6B00" stop-opacity="0.02"/>'
        '</linearGradient>'
        '</defs>'
        '<rect width="{w}" height="{h}" fill="#F5F0E8" rx="16"/>'
        # Grid
        '<g stroke="#d8d0c0" stroke-width="1">'
        '<line x1="{cl}" y1="{ct}" x2="{cr}" y2="{ct}"/>'
        '<line x1="{cl}" y1="{cm}" x2="{cr}" y2="{cm}"/>'
        '<line x1="{cl}" y1="{cb}" x2="{cr}" y2="{cb}"/>'
        '</g>'
        # Area fill
        '<polygon points="{area}" fill="url(#area)"/>'
        # Trend line
        '<polyline points="{line}" fill="none" stroke="#FF6B00" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>'
        '{dots}'
        # Arrow up-right at end
        '<text x="{arx}" y="{ary}" font-family="Arial" font-size="28" fill="#FF6B00" font-weight="900">↗</text>'
        # Labels
        '<text x="{cx}" y="{ty}" font-family="Arial" font-size="14" fill="#1B2A4A" text-anchor="middle" font-weight="700">GROWTH TRAJECTORY</text>'
        '<text x="{cl}" y="{yb}" font-family="Arial" font-size="12" fill="#888888">Q1</text>'
        '<text x="{cr}" y="{yb}" font-family="Arial" font-size="12" fill="#888888" text-anchor="end">Q4</text>'
        '</svg>'
    ).format(
        w=w, h=h,
        cl=chart_l, cr=chart_r, ct=chart_t,
        cm=(chart_t + chart_b) // 2, cb=chart_b,
        area=area_pts, line=line_pts, dots=dots,
        arx=pts[-1][0] - 10, ary=pts[-1][1] - 5,
        cx=w // 2, ty=h - 40, yb=chart_b + 30
    )


def _illus_design(w, h):
    """Bold geometric design composition — Bauhaus-inspired."""
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">'
        '<rect width="{w}" height="{h}" fill="#F5F0E8" rx="16"/>'
        # Large orange circle (top-right)
        '<circle cx="{cx}" cy="160" r="110" fill="#FF6B00"/>'
        # Navy rectangle (center-left)
        '<rect x="30" y="140" width="160" height="200" rx="12" fill="#1B2A4A"/>'
        # Small accent circle (orange outline)
        '<circle cx="70" cy="390" r="50" fill="none" stroke="#FF6B00" stroke-width="8"/>'
        # Triangle (bottom-right)
        '<polygon points="{w2},320 {wr},440 {w2},440" fill="#1B2A4A" opacity="0.7"/>'
        # White line accents
        '<line x1="30" y1="370" x2="200" y2="370" stroke="#FFFFFF" stroke-width="3" opacity="0.5"/>'
        '<line x1="30" y1="390" x2="150" y2="390" stroke="#FFFFFF" stroke-width="2" opacity="0.3"/>'
        # Label
        '<text x="{cx}" y="{ty}" font-family="Arial" font-size="14" fill="#1B2A4A" text-anchor="middle" font-weight="800">DESIGN THINKING</text>'
        '</svg>'
    ).format(w=w, h=h, cx=w // 2, w2=w - 80, wr=w - 20, ty=h - 30)


def _illus_abstract(w, h):
    """Abstract gradient circles on dark background — default."""
    cx = w // 2
    cy = (h - 80) // 2
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">'
        '<defs>'
        '<linearGradient id="bg" x1="0" y1="0" x2="0" y2="1" gradientUnits="objectBoundingBox">'
        '<stop offset="0%" stop-color="#0d1a2e"/><stop offset="100%" stop-color="#1B2A4A"/>'
        '</linearGradient>'
        '<radialGradient id="g1" cx="50%" cy="50%" r="50%">'
        '<stop offset="0%" stop-color="#FF6B00" stop-opacity="0.6"/>'
        '<stop offset="100%" stop-color="#FF6B00" stop-opacity="0"/>'
        '</radialGradient>'
        '<radialGradient id="g2" cx="50%" cy="50%" r="50%">'
        '<stop offset="0%" stop-color="#E8002D" stop-opacity="0.4"/>'
        '<stop offset="100%" stop-color="#E8002D" stop-opacity="0"/>'
        '</radialGradient>'
        '</defs>'
        '<rect width="{w}" height="{h}" fill="url(#bg)"/>'
        # Glowing orbs
        '<circle cx="{c1x}" cy="{c1y}" r="140" fill="url(#g1)"/>'
        '<circle cx="{c2x}" cy="{c2y}" r="110" fill="url(#g2)"/>'
        '<circle cx="{c3x}" cy="{c3y}" r="90" fill="url(#g1)" opacity="0.5"/>'
        # Grid lines
        '<g stroke="#FFFFFF" stroke-width="0.5" opacity="0.06">'
        '<line x1="0" y1="{l1}" x2="{w}" y2="{l1}"/>'
        '<line x1="0" y1="{l2}" x2="{w}" y2="{l2}"/>'
        '<line x1="{l3}" y1="0" x2="{l3}" y2="{h}"/>'
        '<line x1="{l4}" y1="0" x2="{l4}" y2="{h}"/>'
        '</g>'
        # Central ring
        '<circle cx="{cx}" cy="{cy}" r="68" fill="none" stroke="#FF6B00" stroke-width="2" opacity="0.6"/>'
        '<circle cx="{cx}" cy="{cy}" r="44" fill="#1f3360" stroke="#FF6B00" stroke-width="1.5"/>'
        '<text x="{cx}" y="{cy}" font-family="Arial" font-size="20" fill="#FF6B00" text-anchor="middle" dominant-baseline="middle" font-weight="900">DTX</text>'
        '</svg>'
    ).format(
        w=w, h=h, cx=cx, cy=cy,
        c1x=int(w * 0.3), c1y=int(h * 0.35),
        c2x=int(w * 0.72), c2y=int(h * 0.55),
        c3x=int(w * 0.55), c3y=int(h * 0.25),
        l1=int(h * 0.33), l2=int(h * 0.66),
        l3=int(w * 0.33), l4=int(w * 0.66),
    )


def _illus_audio(w, h):
    """Audio waveform on dark background — for TTS, speech, streaming, voice."""
    cx = w // 2
    cy = h // 2
    bars = [0.30, 0.50, 0.70, 0.88, 1.00, 0.92, 0.78, 0.60, 0.45,
            0.72, 0.88, 0.80, 0.60, 0.40, 0.28]
    bar_w = max(12, (w - 60) // (len(bars) * 2))
    gap   = bar_w // 2
    total_w = len(bars) * (bar_w + gap) - gap
    sx    = (w - total_w) // 2
    elems = ""
    for i, amp in enumerate(bars):
        x  = sx + i * (bar_w + gap)
        bh = int(amp * h * 0.42)
        y  = cy - bh // 2
        op = round(0.55 + amp * 0.45, 2)
        color = "#FF6B00" if i % 3 != 1 else "#E8002D"
        elems += (
            '<rect x="' + str(x) + '" y="' + str(y) + '" width="' + str(bar_w) +
            '" height="' + str(bh) + '" rx="' + str(bar_w // 2) +
            '" fill="' + color + '" opacity="' + str(op) + '"/>'
        )
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">'
        '<defs><linearGradient id="bg" x1="0" y1="0" x2="0" y2="1" gradientUnits="objectBoundingBox">'
        '<stop offset="0%" stop-color="#0a1628"/><stop offset="100%" stop-color="#1B2A4A"/>'
        '</linearGradient></defs>'
        '<rect width="{w}" height="{h}" fill="url(#bg)"/>'
        '<circle cx="{cx}" cy="{cy}" r="{cr}" fill="#FF6B00" opacity="0.07"/>'
        '{elems}'
        '<text x="{cx}" y="{ty}" font-family="Arial,sans-serif" font-size="13" '
        'fill="#8899bb" text-anchor="middle" letter-spacing="3">AUDIO STREAM</text>'
        '</svg>'
    ).format(w=w, h=h, cx=cx, cy=cy, cr=min(w, h) // 3, elems=elems, ty=h - 22)


def generate_illustration(label, width=390, height=440):
    """Return a base64 data URI of an SVG illustration for the given label."""
    lbl = (label or "").lower()
    if any(k in lbl for k in ["pipeline", "flow", "process", "workflow", "step"]):
        svg = _illus_pipeline(width, height)
    elif any(k in lbl for k in ["neural", "model", "learning", "llm", "gpt", "agent"]):
        svg = _illus_neural(width, height)
    elif any(k in lbl for k in ["data", "chart", "analytic", "metric", "stat", "report", "insight"]):
        svg = _illus_chart(width, height)
    elif any(k in lbl for k in ["code", "dev", "api", "software", "engineer", "backend", "stack"]):
        svg = _illus_code(width, height)
    elif any(k in lbl for k in ["platform", "cloud", "network", "connect", "architect", "system", "saas"]):
        svg = _illus_network(width, height)
    elif any(k in lbl for k in ["growth", "revenue", "trend", "scale", "launch", "startup", "market"]):
        svg = _illus_growth(width, height)
    elif any(k in lbl for k in ["design", "ui", "ux", "visual", "creative", "brand", "figma"]):
        svg = _illus_design(width, height)
    elif any(k in lbl for k in ["audio", "tts", "speech", "voice", "sound", "stream", "video", "watch", "play"]):
        svg = _illus_audio(width, height)
    else:
        svg = _illus_abstract(width, height)
    return _svg_uri(svg)


_IMAGE_CACHE = {}

def _img_to_data_uri(raw_bytes, content_type="image/jpeg"):
    return "data:{};base64,{}".format(content_type, base64.b64encode(raw_bytes).decode("ascii"))

def _openverse_search(keyword, pick_index=0):
    """Search OpenVerse (CC-licensed, no API key required) and return a data URI.
    pick_index lets each slide pick a different result from the same search pool."""
    try:
        url = "https://api.openverse.org/v1/images/?q={}&page_size=10&license_type=commercial,modification".format(
            urllib.parse.quote(keyword))
        req = urllib.request.Request(url, headers={"User-Agent": "CodeDTX-Carousel/1.0 (contact@codedtx.com)"})
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read())
        results = data.get("results", [])
        if not results:
            return None
        item = results[pick_index % len(results)]
        # prefer thumbnail (smaller, faster) then fall back to full url
        img_url = item.get("thumbnail") or item.get("url", "")
        if not img_url:
            return None
        with urllib.request.urlopen(img_url, timeout=12) as r:
            ct = r.headers.get("Content-Type", "image/jpeg").split(";")[0].strip() or "image/jpeg"
            return _img_to_data_uri(r.read(), ct)
    except Exception:
        return None

def fetch_stock_image(label, width=390, height=440, slide_index=0):
    """Fetch a unique open-licensed photo from OpenVerse for each slide.
    No API key or environment variables required.
    Falls back to a generated SVG illustration if the network is unavailable."""
    keyword = (label or "technology business").strip()
    cache_key = "{}-{}".format(keyword.lower(), slide_index)
    if cache_key in _IMAGE_CACHE:
        return _IMAGE_CACHE[cache_key]

    # Try the exact label first, then the first word only (broader), then a safe fallback
    result = (
        _openverse_search(keyword, slide_index) or
        _openverse_search(keyword.split()[0], slide_index) or
        _openverse_search("technology", slide_index) or
        generate_illustration(label, width, height)
    )
    _IMAGE_CACHE[cache_key] = result
    source = "OpenVerse photo" if result and not result.startswith("data:image/svg") else "generated SVG"
    print("  [image] slide {} — {} → {}".format(slide_index + 1, keyword, source))
    return result


# ── render + pdf ──────────────────────────────────────────────────────────────

def render_pngs(out_dir, total):
    """Render HTML slides to PNG via Playwright. Returns list of PNG paths."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("  [PNG skipped — playwright not installed: pip install playwright]")
        return []
    preview_dir = os.path.join(out_dir, "previews")
    os.makedirs(preview_dir, exist_ok=True)
    png_paths = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": W, "height": H})
        for i in range(1, total + 1):
            src = os.path.abspath(os.path.join(out_dir, f"slide-{i}.html"))
            page.goto("file://" + src)
            page.wait_for_timeout(800)
            dst = os.path.join(preview_dir, f"slide-{i}.png")
            page.screenshot(path=dst, full_page=False)
            png_paths.append(dst)
            print(f"  previews/slide-{i}.png")
        browser.close()
    return png_paths


# CTA button bounding box per template, in SVG pixel coords (top-left origin,
# 1080x1350 canvas) — used to stamp a real clickable link onto the final PDF,
# since a PNG-based PDF page carries no interactivity on its own.
CTA_BUTTON_RECTS = {
    "codedtx-locked": (90, 720, 900, 120),
    "ai-engineering": (240, 960, 600, 90),
    "ott-insight":    (240, 880, 600, 96),
    "design-impact":  (240, 840, 600, 92),
    "codedtx-dark":   (90, 880, 900, 120),
}


def add_cta_link(pdf_path, tmpl_name, url="https://www.codedtx.com/"):
    """Stamp a real clickable link annotation over the CTA button on the last
    page. img2pdf/Pillow output is flat raster — without this, the button is
    only visually a button and does nothing when clicked in a PDF viewer."""
    rect = CTA_BUTTON_RECTS.get(tmpl_name)
    if not rect:
        return
    try:
        import pikepdf
    except ImportError:
        print("  [CTA link skipped — install pikepdf: pip install pikepdf]")
        return

    x, y, w, h = rect
    with pikepdf.open(pdf_path, allow_overwriting_input=True) as pdf:
        page = pdf.pages[-1]
        mbox = page.MediaBox
        page_w, page_h = float(mbox[2]), float(mbox[3])
        scale = page_w / W  # W = 1080, the fixed SVG canvas width

        x0 = x * scale
        x1 = (x + w) * scale
        y0 = page_h - (y + h) * scale   # PDF origin is bottom-left
        y1 = page_h - y * scale

        annotation = pdf.make_indirect(pikepdf.Dictionary(
            Type=pikepdf.Name.Annot,
            Subtype=pikepdf.Name.Link,
            Rect=[x0, y0, x1, y1],
            Border=[0, 0, 0],
            A=pikepdf.Dictionary(
                Type=pikepdf.Name.Action,
                S=pikepdf.Name.URI,
                URI=url,
            ),
        ))
        page.Annots = pdf.make_indirect(pikepdf.Array([annotation]))
        pdf.save(pdf_path)
    print(f"  linked CTA button -> {url}")


def compile_pdf(out_dir, total, tmpl_name=None):
    """Compile all slide PNGs into a single multi-page PDF carousel.pdf."""
    preview_dir = os.path.join(out_dir, "previews")
    pdf_path    = os.path.join(out_dir, "carousel.pdf")
    png_files   = [os.path.join(preview_dir, f"slide-{i}.png") for i in range(1, total + 1)]
    existing    = [f for f in png_files if os.path.exists(f)]

    if not existing:
        print("  [PDF skipped — no PNG previews found]")
        return None

    made = False
    # Try img2pdf first (lossless, preserves exact pixel dimensions)
    try:
        import img2pdf
        with open(pdf_path, "wb") as fh:
            fh.write(img2pdf.convert(existing))
        print(f"  carousel.pdf ({len(existing)} pages)")
        made = True
    except ImportError:
        pass

    # Fall back to Pillow
    if not made:
        try:
            from PIL import Image
            imgs = [Image.open(f).convert("RGB") for f in existing]
            imgs[0].save(
                pdf_path,
                save_all=True,
                append_images=imgs[1:],
                resolution=96,
            )
            print(f"  carousel.pdf ({len(imgs)} pages) [Pillow]")
            made = True
        except ImportError:
            pass

    if not made:
        print("  [PDF skipped — install img2pdf or Pillow: pip install img2pdf]")
        return None

    if tmpl_name:
        add_cta_link(pdf_path, tmpl_name)
    return pdf_path


# ── bullet + key-insight helpers ──────────────────────────────────────────────

def key_insights_map(points, w1=22, w2=36):
    """Return KEY_INSIGHT / KEY_INSIGHT2 / KEY_INSIGHT3 from first 3 points."""
    def kl(idx, width):
        pt = (points[idx] if idx < len(points) else "").strip()
        return pl(pt, width) if pt else ("", "")
    l1a, l1b = kl(0, w1)
    l2a, l2b = kl(1, w2)
    l3a, l3b = kl(2, w2)
    return {
        "KEY_INSIGHT_L1":  l1a,
        "KEY_INSIGHT_L2":  l1b,
        "KEY_INSIGHT2_L1": l2a,
        "KEY_INSIGHT2_L2": l2b,
        "KEY_INSIGHT3_L1": l3a,
        "KEY_INSIGHT3_L2": l3b,
    }


def bullet_map(points, width=20):
    d = {}
    for i in range(1, 6):
        pt = (points[i - 1] if i <= len(points) else "").strip()
        l1, l2 = pl(pt, width) if pt else ("", "")
        d[f"P{i}L1"]      = l1
        d[f"P{i}L2"]      = l2
        d[f"P{i}_DISPLAY"] = "block" if pt else "none"
    return d


# ── ai-engineering ────────────────────────────────────────────────────────────

def aie_cover(data):
    tl = wrap(data.get("topic", "AI Engineering").upper(), 16, 2)
    sl = wrap(data.get("subtitle", "What you need to know"), 38, 2)
    return html_wrap(fill(load_svg("template-ai-engineering/template-cover.svg"), {
        "TITLE_LINE1":    tl[0] if tl else "",
        "TITLE_LINE2":    tl[1] if len(tl) > 1 else "",
        "SUBTITLE_LINE1": sl[0] if sl else "",
        "SUBTITLE_LINE2": sl[1] if len(sl) > 1 else "",
    }))


def aie_content(slide, num, total):
    if isinstance(slide.get("headline"), str):
        words = slide["headline"].split()
        mid   = max(1, len(words) // 2)
        black, orange, red = " ".join(words[:mid]), " ".join(words[mid:]), ""
    else:
        black  = slide.get("headline_black", "")
        orange = slide.get("headline_orange", "")
        red    = slide.get("headline_red", "")
    full    = (black + " " + orange + " " + red).strip()
    hl      = wrap(full, 24, 2)
    quote   = slide.get("quote", "")
    q_lines = wrap(quote, 48, 2) if quote else []
    img_uri = fetch_stock_image(slide.get("image_label", "abstract"), 390, 520, slide_index=num - 1)
    points  = slide.get("points", [])
    svg = fill(load_svg("template-ai-engineering/template-content.svg"), {
        "SLIDE_NUM":        "0" + str(num) if num < 10 else str(num),
        "SLIDE_FRACTION":   str(num) + "/" + str(total),
        "HL1_BLACK":        black  if len(hl) <= 1 else black,
        "HL1_ORANGE":       orange if len(hl) <= 1 else "",
        "HL1_RED":          red    if len(hl) <= 1 else "",
        "HL2_BLACK":        "" if len(hl) <= 1 else (orange + " " + red).strip(),
        "HL2_ORANGE":       "",
        **bullet_map(points, width=20),
        "QUOTE_DISPLAY":    "block" if quote else "none",
        "NO_QUOTE_DISPLAY": "none"  if quote else "block",
        "QUOTE_L1":         q_lines[0] if len(q_lines) > 0 else "",
        "QUOTE_L2":         q_lines[1] if len(q_lines) > 1 else "",
        "QUOTE_AUTHOR":     slide.get("quote_author", ""),
        **key_insights_map(points),
    })
    svg = swap_image_placeholder(svg, "ai-engineering-content", img_uri)
    svg = swap_bullets_ai_engineering(svg, list(points))
    return html_wrap(svg)


def aie_cta(data):
    cta = data.get("cta", {})
    hl  = wrap(cta.get("headline", "Build smarter"), 20, 2)
    bd  = wrap(cta.get("body", "See how we build with AI."), 38, 3)
    return html_wrap(fill(load_svg("template-ai-engineering/template-cta.svg"), {
        "CTA_HL1":    hl[0] if hl else "",
        "CTA_HL2":    hl[1] if len(hl) > 1 else "",
        "CTA_B1":     bd[0] if bd else "",
        "CTA_B2":     bd[1] if len(bd) > 1 else "",
        "CTA_B3":     bd[2] if len(bd) > 2 else "",
        "CTA_ACTION": cta.get("action", "CONTACT US"),
    }))


# ── ott-insight ───────────────────────────────────────────────────────────────

def ott_cover(data):
    tl      = wrap(data.get("topic", "Platform Insight").upper(), 18, 2)
    sl      = wrap(data.get("subtitle", "Key lessons from the field"), 38, 2)
    img_uri = fetch_stock_image(data.get("topic", "platform"), 420, 420, slide_index=0)
    return html_wrap(fill(load_svg("template-ott-insight/template-cover.svg"), {
        "TITLE_LINE1":    tl[0] if tl else "",
        "TITLE_LINE2":    tl[1] if len(tl) > 1 else "",
        "SUBTITLE_LINE1": sl[0] if sl else "",
        "SUBTITLE_LINE2": sl[1] if len(sl) > 1 else "",
        "IMAGE_DATA_URI": img_uri,
    }))


def ott_content(slide, num, total):
    hl      = wrap(slide.get("headline", "Key insight"), 22, 2)
    quote   = slide.get("quote", "")
    q_lines = wrap(quote, 44, 2) if quote else []
    img_uri = fetch_stock_image(
        slide.get("photo_label", slide.get("image_label", "abstract")), 416, 494,
        slide_index=num - 1
    )
    points  = slide.get("points", [])
    svg = fill(load_svg("template-ott-insight/template-content.svg"), {
        "SLIDE_NUM":        "0" + str(num) if num < 10 else str(num),
        "SLIDE_TOTAL":      str(total),
        "HL1":              hl[0] if hl else "",
        "HL2":              hl[1] if len(hl) > 1 else "",
        **bullet_map(points, width=18),
        "QUOTE_DISPLAY":    "block" if quote else "none",
        "NO_QUOTE_DISPLAY": "none"  if quote else "block",
        "QUOTE_L1":         q_lines[0] if len(q_lines) > 0 else "",
        "QUOTE_L2":         q_lines[1] if len(q_lines) > 1 else "",
        "QUOTE_AUTHOR":     slide.get("quote_author", ""),
        **key_insights_map(points),
    })
    svg = swap_image_placeholder(svg, "ott-insight-content", img_uri)
    svg = swap_bullets_ott_insight(svg, list(points))
    return html_wrap(svg)


def ott_cta(data):
    cta = data.get("cta", {})
    hl  = wrap(cta.get("headline", "Ready for more?"), 20, 2)
    bd  = wrap(cta.get("body", "See what's next for your platform."), 40, 2)
    return html_wrap(fill(load_svg("template-ott-insight/template-cta.svg"), {
        "CTA_HL1":    hl[0] if hl else "",
        "CTA_HL2":    hl[1] if len(hl) > 1 else "",
        "CTA_B1":     bd[0] if bd else "",
        "CTA_B2":     bd[1] if len(bd) > 1 else "",
        "CTA_ACTION": cta.get("action", "CONTACT US"),
    }))


# ── design-impact ─────────────────────────────────────────────────────────────

def di_cover(data):
    tl = wrap(data.get("topic", "Design Impact").upper(), 14, 2)
    sl = wrap(data.get("subtitle", "How AI is changing creative work"), 36, 2)
    return html_wrap(fill(load_svg("template-design-impact/template-cover.svg"), {
        "TITLE_LINE1":    tl[0] if tl else "",
        "TITLE_LINE2":    tl[1] if len(tl) > 1 else "",
        "SUBTITLE_LINE1": sl[0] if sl else "",
        "SUBTITLE_LINE2": sl[1] if len(sl) > 1 else "",
    }))


def di_content(slide, num, total):
    dark      = slide.get("dark_slide", False)
    hl        = wrap(slide.get("headline", "Key insight"), 22, 2)
    spotlight = slide.get("spotlight", "").upper()
    points    = slide.get("points", [])
    first_pt  = points[0] if points else ""
    ki = wrap(first_pt, 42, 2) if first_pt else []
    img_uri = fetch_stock_image(slide.get("image_label", "design"), 340, 300, slide_index=num - 1)
    svg = fill(load_svg("template-design-impact/template-content.svg"), {
        "SLIDE_NUM":       "0" + str(num) if num < 10 else str(num),
        "SLIDE_FRACTION":  str(num) + "/" + str(total),
        "SECTION_LABEL":   slide.get("section_label", "INSIGHT " + str(num)).upper(),
        "BG_COLOR":        "#1B2A4A" if dark else "#F5F0E8",
        "STRIP_COLOR":     "#243555" if dark else "#1B2A4A",
        "HL_COLOR":        "#FF6B00" if dark else "#1a1a2e",
        "TEXT_COLOR":      "#FFFFFF" if dark else "#1a1a2e",
        "UL_DISPLAY":      "none"   if dark else "block",
        "HL1":             hl[0] if hl else "",
        "HL2":             hl[1] if len(hl) > 1 else "",
        **bullet_map(points, width=28),
        "SPOT_DISPLAY":    "block" if spotlight else "none",
        "NO_SPOT_DISPLAY": "none"  if spotlight else "block",
        "SPOTLIGHT":       spotlight,
        **key_insights_map(points, w1=22, w2=38),
    })
    svg = swap_image_placeholder(svg, "design-impact-content", img_uri)
    svg = swap_bullets_design_impact(svg, list(points))
    return html_wrap(svg)


def di_cta(data):
    cta = data.get("cta", {})
    hl  = wrap(cta.get("headline", "Transform your workflow"), 20, 2)
    bd  = wrap(cta.get("body", "See the work at codedtx.com."), 40, 2)
    return html_wrap(fill(load_svg("template-design-impact/template-cta.svg"), {
        "CTA_HL1":    hl[0] if hl else "",
        "CTA_HL2":    hl[1] if len(hl) > 1 else "",
        "CTA_B1":     bd[0] if bd else "",
        "CTA_B2":     bd[1] if len(bd) > 1 else "",
        "CTA_ACTION": cta.get("action", "CONTACT US"),
    }))


# ── codedtx-locked ────────────────────────────────────────────────────────────

def locked_cover(data):
    topic    = data.get("topic", "CodeDTX Insight")
    subtitle = data.get("subtitle", "Swipe to learn more")
    slides   = data.get("slides", [])

    # Big headline — topic split across two lines
    tl = wrap(topic.upper(), 12, 2)

    # Pill text — short tagline from subtitle (first ~4 words)
    pill_words = subtitle.split()
    pill = " ".join(pill_words[:4]).rstrip(".,;:")

    # Promise lines — subtitle split across two lines (full)
    pl_lines = wrap(subtitle, 40, 2)

    # Proof card — draw from first slide's points if available
    first_pts = slides[0].get("points", []) if slides else []
    proof_label  = slides[0].get("section_label", "KEY INSIGHTS").upper() if slides else "KEY INSIGHTS"
    proof_slot   = first_pts[0][:60] if first_pts else ""
    budget_label = first_pts[1][:60] if len(first_pts) > 1 else ""
    proof_unit   = data.get("cta", {}).get("action", "FOLLOW")

    return html_wrap(fill(load_svg("template-codedtx-locked/template-cover.svg"), {
        "COVER_SETUP":   subtitle[:55],
        "COVER_BIG_L1":  tl[0] if tl else "",
        "COVER_BIG_L2":  tl[1] if len(tl) > 1 else "",
        "COVER_PILL":    pill,
        "COVER_P1":      pl_lines[0] if pl_lines else "",
        "COVER_P2":      pl_lines[1] if len(pl_lines) > 1 else "",
        "PROOF_LABEL":   proof_label,
        "PROOF_UNIT":    proof_unit,
        "PROOF_SLOT":    proof_slot,
        "BUDGET_LABEL":  budget_label,
    }))


def locked_content(slide, num, total):
    hl     = wrap(slide.get("headline", "Insight"), 24, 2)
    points = slide.get("points", [])

    # Body paragraphs from first two points
    b1 = wrap(points[0] if points else "", 42, 2)
    b2 = wrap(points[1] if len(points) > 1 else "", 42, 2)

    # Stat rows — expect "Label: Value" in points[2..4]; fall back gracefully
    def _stat(idx):
        raw = points[idx].strip() if idx < len(points) else ""
        if ": " in raw:
            label, val = raw.split(": ", 1)
        elif raw:
            label, val = raw[:20], ""
        else:
            label, val = "", ""
        return label[:22], val[:16]

    st1l, st1v = _stat(2)
    st2l, st2v = _stat(3)
    st3l, st3v = _stat(4)

    # Lesson — first point at narrow width
    lesson = wrap(points[0] if points else "", 30, 2)

    section = slide.get("section_label", f"INSIGHT {num}").upper()

    return html_wrap(fill(load_svg("template-codedtx-locked/template-content.svg"), {
        "SLIDE_NUM":    str(num),
        "SLIDE_TOTAL":  str(total),
        "SECTION_TAG":  section,
        "EYEBROW":      section,
        "HEADLINE_L1":  hl[0] if hl else "",
        "HEADLINE_L2":  hl[1] if len(hl) > 1 else "",
        "BODY1_L1":     b1[0] if b1 else "",
        "BODY1_L2":     b1[1] if len(b1) > 1 else "",
        "BODY2_L1":     b2[0] if b2 else "",
        "BODY2_L2":     b2[1] if len(b2) > 1 else "",
        "STAT1_LABEL":  st1l,
        "STAT1_VAL":    st1v,
        "STAT2_LABEL":  st2l,
        "STAT2_VAL":    st2v,
        "STAT3_LABEL":  st3l,
        "STAT3_VAL":    st3v,
        "LESSON_L1":    lesson[0] if lesson else "",
        "LESSON_L2":    lesson[1] if len(lesson) > 1 else "",
    }))


def locked_cta(data):
    cta      = data.get("cta", {})
    subtitle = data.get("subtitle", "")
    hl       = wrap(cta.get("headline", "Ready to build smarter"), 22, 2)
    tagline  = wrap(cta.get("body", "Visit codedtx.com for more insights like this."), 48, 1)
    setup    = subtitle[:55] if subtitle else cta.get("headline", "")[:55]
    return html_wrap(fill(load_svg("template-codedtx-locked/template-cta.svg"), {
        "CTA_SETUP":       setup,
        "CTA_HL1":         hl[0] if hl else "",
        "CTA_HL2":         hl[1] if len(hl) > 1 else "",
        "CTA_ACTION_TEXT": cta.get("action", "CONTACT US"),
        "CTA_TAGLINE":     tagline[0] if tagline else "",
    }))


# ── codedtx-dark ──────────────────────────────────────────────────────────────

def dark_cover(data):
    tl = wrap(data.get("topic", "AI Engineering").upper(), 16, 2)
    sl = wrap(data.get("subtitle", "The tooling changed in eighteen months."), 38, 2)
    return html_wrap(fill(load_svg("template-codedtx-dark/template-cover.svg"), {
        "TITLE_LINE1":    tl[0] if tl else "",
        "TITLE_LINE2":    tl[1] if len(tl) > 1 else "",
        "SUBTITLE_LINE1": sl[0] if sl else "",
        "SUBTITLE_LINE2": sl[1] if len(sl) > 1 else "",
    }))


def dark_content(slide, num, total):
    hl      = wrap(slide.get("headline", "Speed without structure"), 22, 2)
    points  = slide.get("points", [])
    b1      = wrap(points[0] if points else "", 40, 2)
    b2      = wrap(points[1] if len(points) > 1 else "", 40, 2)
    section = slide.get("section_label", f"INSIGHT {num:02d}").upper()
    image_label = slide.get("image_label", slide.get("headline", "engineering framework"))
    img_uri = fetch_stock_image(image_label, slide_index=num - 1)

    svg = fill(load_svg("template-codedtx-dark/template-content.svg"), {
        "SLIDE_NUM":       f"{num:02d}",
        "SLIDE_TOTAL":     f"{total:02d}",
        "SECTION_TAG":     section,
        "HL1":             hl[0] if hl else "",
        "HL2":             hl[1] if len(hl) > 1 else "",
        "BODY1_L1":        b1[0] if b1 else "",
        "BODY1_L2":        b1[1] if len(b1) > 1 else "",
        "BODY2_L1":        b2[0] if b2 else "",
        "BODY2_L2":        b2[1] if len(b2) > 1 else "",
        "TAKEAWAY_TEXT":   points[0] if points else "Ship what you can explain and own.",
    })
    svg = swap_image_placeholder(svg, "codedtx-dark-content", img_uri)
    return html_wrap(svg)


def dark_cta(data):
    cta = data.get("cta", {})
    hl  = wrap(cta.get("headline", "Let's build software that holds up."), 22, 2)
    bd  = wrap(cta.get("body", "Visit codedtx.com for engineering perspectives."), 44, 2)
    return html_wrap(fill(load_svg("template-codedtx-dark/template-cta.svg"), {
        "CTA_HL1":    hl[0] if hl else "",
        "CTA_HL2":    hl[1] if len(hl) > 1 else "",
        "CTA_B1":     bd[0] if bd else "",
        "CTA_B2":     bd[1] if len(bd) > 1 else "",
        "CTA_ACTION": cta.get("action", "Contact Us"),
    }))


# ── dispatch ──────────────────────────────────────────────────────────────────

TEMPLATES = {
    "ai-engineering": (aie_cover, aie_content, aie_cta),
    "ott-insight":    (ott_cover, ott_content, ott_cta),
    "design-impact":  (di_cover,  di_content,  di_cta),
    "codedtx-dark":   (dark_cover, dark_content, dark_cta),
    "codedtx-locked": (locked_cover, locked_content, locked_cta),
}

# Default content slide used to pad when fewer than 5 slides provided
DEFAULT_SLIDE = {
    "headline": "Key Insight",
    "points": [
        "Important point one to understand here",
        "Second key point your audience needs",
        "Third takeaway that drives action",
    ],
    "image_label": "abstract",
    "section_label": "INSIGHT",
}


# ── main ──────────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description="CodeDTX LinkedIn carousel builder")
    ap.add_argument("--input",    required=True)
    ap.add_argument("--output",   required=True)
    ap.add_argument("--template", default="auto",
                    choices=["auto"] + list(TEMPLATES.keys()))
    ap.add_argument("--no-pdf",   action="store_true",
                    help="Skip PDF compilation")
    args = ap.parse_args()

    with open(args.input) as f:
        data = json.load(f)

    bad = check_dashes(data)
    if bad:
        print("ERROR: Dash " + repr(bad[0]) + " in: " + repr(bad[1][:80]))
        sys.exit(1)

    tmpl_name = select_template(
        data.get("topic", ""),
        args.template,
        subtitle=data.get("subtitle", ""),
        slides=data.get("slides", []),
    )
    fn_cover, fn_content, fn_cta = TEMPLATES[tmpl_name]
    print("Template selected: " + tmpl_name)

    # ── Enforce exactly CONTENT_SLIDES content slides ──
    slides_raw = data.get("slides", [])
    if len(slides_raw) > CONTENT_SLIDES:
        print(
            "  [Note] " + str(len(slides_raw)) + " slides in brief — "
            "using first " + str(CONTENT_SLIDES) + " (7-slide structure)"
        )
        slides_raw = slides_raw[:CONTENT_SLIDES]
    while len(slides_raw) < CONTENT_SLIDES:
        idx = len(slides_raw) + 1
        pad = dict(DEFAULT_SLIDE)
        pad["section_label"] = "INSIGHT " + str(idx)
        slides_raw.append(pad)
        print("  [Note] Padded slide " + str(idx) + " with default content")

    os.makedirs(args.output, exist_ok=True)

    n = 0
    # Slide 1 — Cover
    n += 1
    save_slide(fn_cover(data), args.output, n)

    # Slides 2–6 — Content (exactly 5)
    for i, sl in enumerate(slides_raw):
        n += 1
        save_slide(fn_content(sl, n, SLIDES_REQUIRED), args.output, n)

    # Slide 7 — CTA
    n += 1
    save_slide(fn_cta(data), args.output, n)

    print("\nRendering " + str(n) + " slides to PNG...")
    render_pngs(args.output, n)

    if not args.no_pdf:
        print("\nCompiling PDF...")
        compile_pdf(args.output, n, tmpl_name)

    print("\nDone — " + str(n) + " slides | " + args.output)
    print("Carousel: " + args.output + "carousel.pdf")


if __name__ == "__main__":
    main()
