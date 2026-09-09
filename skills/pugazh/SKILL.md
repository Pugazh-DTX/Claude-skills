---
name: pugazh
description: "Use when generating Pugazh's 3-page Instagram carousel (Cover/Content/CTA) for any topic — dark navy/dot-grid design system with a topic-driven Stats row, Illustration zone, and Callout bar."
---

# Pugazh Instagram Carousel Template

A reusable 3-page (Cover / Content / CTA) Instagram carousel system, 1080x1350 per page, built from vector SVG so it regenerates dynamically for any topic. Originally reverse-engineered from Pugazh's Figma-exported reference carousel (OTT/streaming dev content) and rebuilt as an editable, parameterized generator.

## When to use this

Whenever Pugazh asks for an Instagram carousel / IG post set / 3-slide deck in "his pattern" or "his template", or names a topic and expects Cover + Content + CTA slides back. Default audience/voice: technical, OTT/streaming and frontend-engineering topics (but the template works for any topic).

## Design system (fixed — do not change without being asked)

- Canvas: 1080x1350 per page (Instagram portrait).
- Background: solid navy `#0D1B2A` + a subtle dot-grid overlay (`<pattern>` of small circles, fill `#6A809A`, opacity ~0.16).
- Top accent bar: solid `#FF5A00`, full width, 10px tall, at y=0. A hairline divider (`#1E3048`, opacity 0.6) sits at y=120 under the header zone.
- Signature gradient (used for CTA buttons / callout bars / gradient text): linear, stops `#FF0063` → (0.48) `#FF7600` → (1) `#FFA200` (magenta → orange → amber).
- Accent palette for badges/cards/icons, cycled per item: orange `#FF5A00`, cyan `#22D3EE`, green `#3DDB7C`, purple `#A78BFA`, gold `#FFB800` (plus pink `#FF0063` for the gradient).
- Text colors: headlines white `#FFFFFF`/`#DCE8F4`, body/secondary `#9FB4CC` or `#8FA6C0`, panel/card fill `#12233A` with `#22384f` border.
- Font: Arial/Helvetica sans-serif, bold (700-800) for headlines, 400-600 for body. Headlines/labels are real `<text>`/`<tspan>` elements (NOT text-outlined paths) so they stay editable — this was a deliberate change from the original Figma export, which flattened text to paths.
- Footer: 3-dot page-progress indicator centered near the bottom, plus a small logo watermark (orange square + "PLIVE STUDIO" wordmark, opacity 0.55) — swap the wordmark if a different brand is needed.
- Decorative "dashboard mockup" illustration: an abstract cluster of rounded panels, a line-chart path with dot markers, progress bars, and two ring/arc gauges, tinted with one accent color. This stands in for the original's hand-illustrated dashboard graphic; treat it as a placeholder unless real illustration/logo assets are supplied.

## Page structure (per topic)

**1. Cover** — kicker pill/label, multi-line bold title, one-line subtitle, illustration cluster, a 5-item badge row (2 cols) summarizing the topic's sub-themes, footer.

**2. Content** — kicker + heading, then three required zones in this order:
 - **Stats row**: 3 side-by-side cards, each with a short bold value (a term/number/acronym) + a wrapped label line, left border in a cycling accent color.
 - **Illustration zone**: labeled "ILLUSTRATION ZONE", the dashboard-mockup graphic plus a one-line caption underneath explaining what it represents.
 - **Callout bar**: a full-width rounded bar filled with the signature gradient, dark text, a bold title + 1-3 lines of supporting body copy (word-wrapped to fit).

**3. CTA** — illustration cluster, two small star/sparkle accents flanking a large centered bold headline (multi-line), a 5-card feature/recap row (same content as Cover's badges, restyled as bordered cards with a small color-block icon), a full-width gradient pill button with the CTA copy, divider + footer.

## Workflow for a new topic

1. From the topic, derive: kicker (category label), cover title (2-4 short lines) + subtitle, 5 badge/sub-theme labels (each auto-assigned one of the 5 accent colors in order), a content heading, 3 stats (short value + explanatory label), an illustration caption, a callout title + 1-2 sentence body, a CTA headline (2 lines), 5 feature cards mirroring the badges, and CTA button copy (e.g. "Save This Guide", "Get Started").
2. Reuse the reference implementation below rather than re-deriving the design from scratch — copy `ig-carousel-generator.html`'s structure (or adapt inline) so PNG export keeps working: text must stay in `<text>/<tspan>` wrapped via canvas `measureText` (see `wrapTextByWidth`), never `<foreignObject>` — foreignObject taints the export canvas in Chromium and breaks the PNG download.
3. Build/update a single self-contained HTML file: a left-hand form (topic, cover title/subtitle, 5 badges+colors, content heading, 3 stats, illustration caption, callout title/text, CTA headline, 5 cards+colors, CTA button) that live-renders all three SVGs and offers per-page SVG + PNG (2x scale) download buttons. Pre-fill the form with the new topic's derived content so it renders correctly on load.
4. Verify before delivering: load the file headlessly (e.g. Playwright + `/opt/pw-browsers/chromium`), confirm zero console/page errors, confirm all 3 `<svg>` elements render, and confirm PNG export produces a non-empty blob for each page (this catches foreignObject-taint regressions).
5. Deliver via SendUserFile (or write into a connected folder if one exists). This is a revisit-by-nature tool (Pugazh will reuse it per topic), so if an Artifact-persisting tool is available in the session, persist it there instead of/alongside a one-off SendUserFile.

## Reference implementation

The following is a known-good, verified (zero console errors, PNG export confirmed working) generator built for the topic "Challenges of Frontend Development for Smart TVs". Copy this file as the starting point and swap only the default-data constants (`defaultBadges`, `defaultStats`, `defaultCtaCards`) and the pre-filled form field values for a new topic — the builder functions (`buildCover`, `buildContent`, `buildCta`, `illustrationCluster`, `badgePill`, `multilineText`, `wrapTextByWidth`, `defsBlock`, `bgBlock`, `logoWatermark`, `pageFooter`, `star`) are the reusable design-system implementation and should only change if the design itself is being revised.

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Instagram Carousel Generator — Cover / Content / CTA</title>
<style>
  :root{
    --navy:#0D1B2A; --navy2:#1E3048; --line:#28405B; --graytext:#6A809A;
    --white:#DCE8F4; --orange:#FF5A00; --cyan:#22D3EE; --green:#3DDB7C;
    --purple:#A78BFA; --gold:#FFB800; --pink:#FF0063;
    --panel:#12233A; --panelBorder:#22384f;
  }
  *{box-sizing:border-box;}
  body{
    margin:0; font-family:-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;
    background:#0a1420; color:#e8eef5; display:flex; min-height:100vh;
  }
  #panel{
    width:380px; flex-shrink:0; background:var(--panel); border-right:1px solid var(--panelBorder);
    padding:20px; overflow-y:auto; height:100vh;
  }
  #panel h1{font-size:16px; margin:0 0 4px;}
  #panel p.hint{font-size:12px; color:#8aa0b8; margin:0 0 18px; line-height:1.5;}
  .field{margin-bottom:14px;}
  .field label{display:block; font-size:11px; text-transform:uppercase; letter-spacing:.05em; color:#8aa0b8; margin-bottom:5px;}
  .field input, .field textarea{
    width:100%; background:#0d1c2e; border:1px solid var(--panelBorder); color:#e8eef5;
    border-radius:6px; padding:8px 10px; font-size:13px; font-family:inherit; resize:vertical;
  }
  .field textarea{min-height:44px;}
  fieldset{border:1px solid var(--panelBorder); border-radius:8px; margin-bottom:16px; padding:12px;}
  legend{font-size:12px; font-weight:600; padding:0 6px; color:#cfe0f0;}
  .row5 .field{display:inline-block; width:100%;}
  .item-row{display:flex; gap:6px; margin-bottom:6px; align-items:center;}
  .item-row input{flex:1;}
  .item-row select{background:#0d1c2e; border:1px solid var(--panelBorder); color:#e8eef5; border-radius:6px; padding:6px;}
  button{
    cursor:pointer; border:none; border-radius:6px; padding:9px 14px; font-size:13px; font-weight:600;
  }
  .btn-primary{background:linear-gradient(90deg,#FF0063,#FF7600,#FFA200); color:#fff; width:100%; margin-top:6px;}
  .downloads{display:flex; gap:8px; margin-top:8px; flex-wrap:wrap;}
  .downloads button{background:#1c3350; color:#cfe0f0; flex:1; min-width:100px; font-size:12px;}
  .downloads button:hover{background:#264063;}
  #stage{
    flex:1; display:flex; gap:24px; padding:28px; overflow-x:auto; align-items:flex-start;
    background:
      radial-gradient(circle at 20% 20%, #0e1b2c 0%, #0a1420 60%);
  }
  .page-wrap{flex-shrink:0; text-align:center;}
  .page-wrap .pw-label{font-size:12px; color:#8aa0b8; margin-bottom:8px; letter-spacing:.05em; text-transform:uppercase;}
  .page-wrap svg{width:340px; height:425px; border-radius:10px; box-shadow:0 12px 40px rgba(0,0,0,.5); display:block;}
</style>
</head>
<body>

<div id="panel">
  <h1>Carousel Generator</h1>
  <p class="hint">Edit any field — all three slides re-render live. Design system (navy bg, dot grid, orange accent bar, magenta→orange→amber gradient, badge/card rows) is fixed; content is per-topic.</p>

  <fieldset>
    <legend>Topic</legend>
    <div class="field">
      <label>Kicker (small label above title)</label>
      <input id="kicker" value="OTT / STREAMING DEV">
    </div>
    <div class="field">
      <label>Cover title (use \n for line breaks)</label>
      <textarea id="coverTitle">Challenges of Frontend\nDevelopment for\nSmart TVs</textarea>
    </div>
    <div class="field">
      <label>Cover subtitle</label>
      <textarea id="coverSubtitle">What breaks when your app runs on a TV, not a phone</textarea>
    </div>
  </fieldset>

  <fieldset>
    <legend>Cover — badge row (5)</legend>
    <div id="badgeRow"></div>
  </fieldset>

  <fieldset>
    <legend>Content page</legend>
    <div class="field">
      <label>Heading</label>
      <input id="contentHeading" value="5 Things That Make TV Frontend Hard">
    </div>
    <label style="display:block;font-size:11px;text-transform:uppercase;letter-spacing:.05em;color:#8aa0b8;margin:10px 0 5px;">Stats row (3)</label>
    <div id="statsRow"></div>
    <div class="field">
      <label>Illustration zone caption</label>
      <input id="illoCaption" value="Low RAM, weak CPUs — every KB and frame counts">
    </div>
    <div class="field">
      <label>Callout bar title</label>
      <input id="calloutTitle" value="Player Behavior">
    </div>
    <div class="field">
      <label>Callout bar text</label>
      <textarea id="calloutText">Buffering, DRM, and playback states must stay TV-safe across every OS and remote.</textarea>
    </div>
  </fieldset>

  <fieldset>
    <legend>CTA page</legend>
    <div class="field">
      <label>CTA headline (use \n for line breaks)</label>
      <textarea id="ctaHeadline">Build TV Apps\nThat Just Work</textarea>
    </div>
    <label style="display:block;font-size:11px;text-transform:uppercase;letter-spacing:.05em;color:#8aa0b8;margin:10px 0 5px;">Feature cards (5)</label>
    <div id="ctaCards"></div>
    <div class="field">
      <label>CTA button text</label>
      <input id="ctaButton" value="Save This Guide">
    </div>
  </fieldset>

  <button class="btn-primary" onclick="renderAll()">Regenerate</button>
</div>

<div id="stage">
  <div class="page-wrap">
    <div class="pw-label">1 · Cover</div>
    <div id="coverHolder"></div>
    <div class="downloads">
      <button onclick="downloadSVG('cover')">SVG</button>
      <button onclick="downloadPNG('cover')">PNG</button>
    </div>
  </div>
  <div class="page-wrap">
    <div class="pw-label">2 · Content</div>
    <div id="contentHolder"></div>
    <div class="downloads">
      <button onclick="downloadSVG('content')">SVG</button>
      <button onclick="downloadPNG('content')">PNG</button>
    </div>
  </div>
  <div class="page-wrap">
    <div class="pw-label">3 · CTA</div>
    <div id="ctaHolder"></div>
    <div class="downloads">
      <button onclick="downloadSVG('cta')">SVG</button>
      <button onclick="downloadPNG('cta')">PNG</button>
    </div>
  </div>
</div>

<script>
const W = 1080, H = 1350;
const ACCENTS = {
  orange: '#FF5A00', cyan:'#22D3EE', green:'#3DDB7C', purple:'#A78BFA', gold:'#FFB800', pink:'#FF0063'
};
const ACCENT_KEYS = Object.keys(ACCENTS);

/* ---------- default data: SWAP THESE PER TOPIC ---------- */
const defaultBadges = ['LG webOS','Samsung Tizen','Remote Nav','Perf Budget','Player QoE'];
const defaultBadgeColors = ['orange','cyan','green','purple','gold'];
const defaultStats = [
  {value:'webOS', label:"LG's TV OS — Enact/React quirks"},
  {value:'Tizen', label:"Samsung's TV OS — different APIs"},
  {value:'D-Pad', label:'Remote-only nav, no mouse or touch'}
];
const defaultCtaCards = [
  {label:'webOS', color:'orange'},
  {label:'Tizen', color:'cyan'},
  {label:'D-Pad Nav', color:'green'},
  {label:'Perf Budget', color:'purple'},
  {label:'Player QoE', color:'gold'}
];

/* ---------- build dynamic list inputs ---------- */
function buildBadgeInputs(){
  const el = document.getElementById('badgeRow');
  el.innerHTML = defaultBadges.map((b,i)=>`
    <div class="item-row">
      <input data-badge="${i}" value="${esc(b)}">
      <select data-badge-color="${i}">
        ${ACCENT_KEYS.map(k=>`<option value="${k}" ${k===defaultBadgeColors[i]?'selected':''}>${k}</option>`).join('')}
      </select>
    </div>`).join('');
}
function buildStatsInputs(){
  const el = document.getElementById('statsRow');
  el.innerHTML = defaultStats.map((s,i)=>`
    <div class="item-row">
      <input data-stat-value="${i}" style="max-width:70px" value="${esc(s.value)}">
      <input data-stat-label="${i}" value="${esc(s.label)}">
    </div>`).join('');
}
function buildCtaCardInputs(){
  const el = document.getElementById('ctaCards');
  el.innerHTML = defaultCtaCards.map((c,i)=>`
    <div class="item-row">
      <input data-card-label="${i}" value="${esc(c.label)}">
      <select data-card-color="${i}">
        ${ACCENT_KEYS.map(k=>`<option value="${k}" ${k===c.color?'selected':''}>${k}</option>`).join('')}
      </select>
    </div>`).join('');
}
function esc(s){return (s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');}

/* ---------- shared SVG building blocks ---------- */
function defsBlock(id){
  return `
  <defs>
    <pattern id="dots-${id}" width="26" height="26" patternUnits="userSpaceOnUse">
      <circle cx="2" cy="2" r="1.5" fill="#6A809A" opacity="0.16"/>
    </pattern>
    <linearGradient id="grad-${id}" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#FF0063"/>
      <stop offset="0.48" stop-color="#FF7600"/>
      <stop offset="1" stop-color="#FFA200"/>
    </linearGradient>
    <linearGradient id="fade-${id}" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#12233A" stop-opacity="0"/>
      <stop offset="1" stop-color="#12233A" stop-opacity="0.9"/>
    </linearGradient>
  </defs>`;
}
function bgBlock(id){
  return `
  <rect width="${W}" height="${H}" fill="#0D1B2A"/>
  <rect width="${W}" height="${H}" fill="url(#dots-${id})"/>
  <rect x="0" y="0" width="${W}" height="10" fill="#FF5A00"/>
  <line x1="0" y1="120" x2="${W}" y2="120" stroke="#1E3048" stroke-width="1" opacity="0.6"/>`;
}
function logoWatermark(y){
  return `
  <g opacity="0.55">
    <rect x="${W/2-58}" y="${y}" width="14" height="14" rx="4" fill="#FF5A00"/>
    <text x="${W/2-38}" y="${y+11}" font-family="Arial,Helvetica,sans-serif" font-size="14" font-weight="700" fill="#DCE8F4" letter-spacing="1">PLIVE STUDIO</text>
  </g>`;
}
function pageFooter(pageNum){
  return `
  <g opacity="0.6">
    ${[0,1,2].map(i=>`<circle cx="${W/2-16+i*16}" cy="${H-40}" r="${i===pageNum?5:3.5}" fill="${i===pageNum?'#FF7600':'#28405B'}"/>`).join('')}
  </g>`;
}
function star(cx,cy,scale,color){
  return `<path transform="translate(${cx},${cy}) scale(${scale})" d="M0 -10 L2.4 -2.4 L10 0 L2.4 2.4 L0 10 L-2.4 2.4 L-10 0 L-2.4 -2.4 Z" fill="${color}" opacity="0.85"/>`;
}
/* abstract "dashboard mockup" illustration built from primitive shapes — placeholder for real illustration assets */
function illustrationCluster(x,y,w,h,id,accent){
  const c = ACCENTS[accent] || '#FF5A00';
  return `
  <g>
    <rect x="${x}" y="${y}" width="${w}" height="${h}" rx="20" fill="#12233A" stroke="#22384f" stroke-width="1.5"/>
    <rect x="${x+24}" y="${y+24}" width="${w-48}" height="${h*0.36}" rx="12" fill="#0D1B2A"/>
    <path d="M${x+24} ${y+24+h*0.30} L${x+24+(w-48)*0.2} ${y+24+h*0.14} L${x+24+(w-48)*0.42} ${y+24+h*0.22} L${x+24+(w-48)*0.68} ${y+24+h*0.06} L${x+24+(w-48)} ${y+24+h*0.16}"
      fill="none" stroke="${c}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
    ${[0.2,0.42,0.68,1].map(f=>`<circle cx="${x+24+(w-48)*f}" cy="${y+24+h*(f===0.2?0.14:f===0.42?0.22:f===0.68?0.06:0.16)}" r="4.5" fill="${c}"/>`).join('')}
    <rect x="${x+24}" y="${y+24+h*0.44}" width="${(w-48)*0.42}" height="14" rx="7" fill="#1E3048"/>
    <rect x="${x+24}" y="${y+24+h*0.44}" width="${(w-48)*0.28}" height="14" rx="7" fill="${c}"/>
    <rect x="${x+24}" y="${y+24+h*0.56}" width="${(w-48)*0.7}" height="10" rx="5" fill="#1E3048"/>
    <rect x="${x+24}" y="${y+24+h*0.68}" width="${(w-48)*0.5}" height="10" rx="5" fill="#1E3048"/>
    <circle cx="${x+w-56}" cy="${y+h-56}" r="30" fill="none" stroke="${c}" stroke-width="6" opacity="0.9"/>
    <path d="M${x+w-56} ${y+h-86} A30 30 0 0 1 ${x+w-26} ${y+h-56}" fill="none" stroke="#FFA200" stroke-width="6" stroke-linecap="round"/>
    <circle cx="${x+50}" cy="${y+h-46}" r="18" fill="none" stroke="#28405B" stroke-width="5"/>
    <circle cx="${x+50}" cy="${y+h-46}" r="18" fill="none" stroke="${c}" stroke-width="5" stroke-dasharray="70 113" stroke-linecap="round"/>
  </g>`;
}
function badgePill(cx,y,w,label,accent){
  const c = ACCENTS[accent]||'#FF5A00';
  return `
  <g>
    <rect x="${cx-w/2}" y="${y}" width="${w}" height="46" rx="23" fill="#12233A" stroke="#22384f" stroke-width="1.5"/>
    <circle cx="${cx-w/2+22}" cy="${y+23}" r="6" fill="${c}"/>
    <text x="${cx-w/2+38}" y="${y+29}" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="600" fill="#DCE8F4">${esc(label)}</text>
  </g>`;
}
function multilineText(x,y,lines,size,weight,fill,lh,anchor){
  anchor = anchor||'start';
  return `<text x="${x}" y="${y}" font-family="Arial,Helvetica,sans-serif" font-size="${size}" font-weight="${weight}" fill="${fill}" text-anchor="${anchor}">
    ${lines.map((l,i)=>`<tspan x="${x}" dy="${i===0?0:lh}">${esc(l)}</tspan>`).join('')}
  </text>`;
}
/* word-wrap plain text into lines that fit maxWidth, using real font metrics
   (avoids <foreignObject>, which taints the canvas on PNG export) */
function wrapTextByWidth(text, maxWidth, fontSize, fontWeight){
  fontWeight = fontWeight || 400;
  const canvas = wrapTextByWidth._canvas || (wrapTextByWidth._canvas = document.createElement('canvas'));
  const ctx = canvas.getContext('2d');
  ctx.font = `${fontWeight} ${fontSize}px Arial, Helvetica, sans-serif`;
  const words = (text||'').split(/\s+/).filter(Boolean);
  const lines = [];
  let cur = '';
  for(const w of words){
    const test = cur ? cur + ' ' + w : w;
    if(cur && ctx.measureText(test).width > maxWidth){
      lines.push(cur);
      cur = w;
    } else {
      cur = test;
    }
  }
  if(cur) lines.push(cur);
  return lines;
}

/* ---------- COVER ---------- */
function buildCover(d){
  const titleLines = d.coverTitle.split('\\n');
  const badgeW = 190;
  return `
<svg viewBox="0 0 ${W} ${H}" xmlns="http://www.w3.org/2000/svg">
  ${defsBlock('cover')}
  ${bgBlock('cover')}
  <rect x="72" y="150" width="220" height="40" rx="20" fill="none" stroke="url(#grad-cover)" stroke-width="1.5"/>
  <text x="90" y="176" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="700" letter-spacing="1.5" fill="#FFA200">${esc(d.kicker.toUpperCase())}</text>

  ${multilineText(72, 300, titleLines, 66, 800, '#FFFFFF', 74)}
  <text x="72" y="${300 + titleLines.length*74 + 46}" font-family="Arial,Helvetica,sans-serif" font-size="24" font-weight="400" fill="#8FA6C0">${esc(d.coverSubtitle)}</text>

  ${illustrationCluster(72, 300 + titleLines.length*74 + 90, W-144, 330, 'cover', d.badgeColors[0])}

  ${d.badges.map((b,i)=>{
      const row = Math.floor(i/2), col = i%2;
      const cx = 72 + badgeW/2 + col*(badgeW+24);
      const y = 300 + titleLines.length*74 + 90 + 330 + 40 + row*60;
      return badgePill(cx, y, badgeW, b, d.badgeColors[i]);
    }).join('')}

  ${logoWatermark(H-70)}
  ${pageFooter(0)}
</svg>`;
}

/* ---------- CONTENT ---------- */
function buildContent(d){
  const statW = (W-144-2*24)/3;
  return `
<svg viewBox="0 0 ${W} ${H}" xmlns="http://www.w3.org/2000/svg">
  ${defsBlock('content')}
  ${bgBlock('content')}

  <text x="72" y="200" font-family="Arial,Helvetica,sans-serif" font-size="15" font-weight="700" letter-spacing="1.5" fill="#FFA200">${esc((d.kicker||'').toUpperCase())}</text>
  ${multilineText(72, 250, [d.contentHeading], 44, 800, '#FFFFFF', 50)}

  <!-- Stats row -->
  ${d.stats.map((s,i)=>{
    const x = 72 + i*(statW+24);
    const y = 300;
    const c = ACCENTS[ACCENT_KEYS[i%ACCENT_KEYS.length]];
    return `
    <g>
      <rect x="${x}" y="${y}" width="${statW}" height="150" rx="16" fill="#12233A" stroke="#22384f" stroke-width="1.5"/>
      <rect x="${x}" y="${y}" width="6" height="150" rx="3" fill="${c}"/>
      <text x="${x+22}" y="${y+52}" font-family="Arial,Helvetica,sans-serif" font-size="30" font-weight="800" fill="#FFFFFF">${esc(s.value)}</text>
      ${multilineText(x+22, y+84, wrapTextByWidth(s.label, statW-40, 15, 400).slice(0,3), 15, 400, '#9FB4CC', 20)}
    </g>`;
  }).join('')}

  <!-- Illustration zone -->
  <text x="72" y="500" font-family="Arial,Helvetica,sans-serif" font-size="17" font-weight="700" letter-spacing="1" fill="#8FA6C0">ILLUSTRATION ZONE</text>
  ${illustrationCluster(72, 520, W-144, 420, 'content2', 'cyan')}
  <text x="${W/2}" y="${520+420+42}" text-anchor="middle" font-family="Arial,Helvetica,sans-serif" font-size="19" fill="#9FB4CC">${esc(d.illoCaption)}</text>

  <!-- Callout bar -->
  <rect x="72" y="1060" width="${W-144}" height="150" rx="18" fill="url(#grad-content)"/>
  <text x="104" y="1112" font-family="Arial,Helvetica,sans-serif" font-size="26" font-weight="800" fill="#0D1B2A">${esc(d.calloutTitle)}</text>
  ${multilineText(104, 1150, wrapTextByWidth(d.calloutText, W-144-64, 17, 600).slice(0,3), 17, 600, '#0D1B2A', 24)}

  ${logoWatermark(H-40)}
  ${pageFooter(1)}
</svg>`;
}

/* ---------- CTA ---------- */
function buildCta(d){
  const headlineLines = d.ctaHeadline.split('\\n');
  const cardW = (W-144-4*16)/5;
  return `
<svg viewBox="0 0 ${W} ${H}" xmlns="http://www.w3.org/2000/svg">
  ${defsBlock('cta')}
  ${bgBlock('cta')}

  ${illustrationCluster(72, 160, W-144, 380, 'cta', 'purple')}

  ${star(120, 590, 1.1, '#FFB800')}
  ${star(W-120, 590, 0.9, '#FFB800')}
  ${multilineText(W/2, 660, headlineLines, 56, 800, '#FFFFFF', 64, 'middle')}

  <!-- feature cards -->
  ${d.ctaCards.map((c,i)=>{
    const x = 72 + i*(cardW+16);
    const y = 800;
    const col = ACCENTS[c.color]||'#FF5A00';
    return `
    <g>
      <rect x="${x}" y="${y}" width="${cardW}" height="120" rx="14" fill="#12233A" stroke="${col}" stroke-width="1.5" opacity="0.95"/>
      <rect x="${x+16}" y="${y+16}" width="26" height="26" rx="8" fill="${col}"/>
      ${multilineText(x+16, y+74, wrapTextByWidth(c.label, cardW-24, 13, 700).slice(0,3), 13, 700, '#DCE8F4', 16)}
    </g>`;
  }).join('')}

  <!-- gradient CTA bar -->
  <rect x="180" y="1000" width="${W-360}" height="82" rx="41" fill="url(#grad-cta)"/>
  <text x="${W/2}" y="1050" text-anchor="middle" font-family="Arial,Helvetica,sans-serif" font-size="24" font-weight="800" fill="#0D1B2A">${esc(d.ctaButton)} →</text>

  <line x1="72" y1="1120" x2="${W-72}" y2="1120" stroke="#1E3048" stroke-width="1" opacity="0.5"/>
  ${logoWatermark(H-60)}
  ${pageFooter(2)}
</svg>`;
}

/* ---------- gather state from form ---------- */
function gatherState(){
  const badges=[], badgeColors=[];
  for(let i=0;i<5;i++){
    badges.push(document.querySelector(`[data-badge="${i}"]`).value);
    badgeColors.push(document.querySelector(`[data-badge-color="${i}"]`).value);
  }
  const stats=[];
  for(let i=0;i<3;i++){
    stats.push({
      value: document.querySelector(`[data-stat-value="${i}"]`).value,
      label: document.querySelector(`[data-stat-label="${i}"]`).value
    });
  }
  const ctaCards=[];
  for(let i=0;i<5;i++){
    ctaCards.push({
      label: document.querySelector(`[data-card-label="${i}"]`).value,
      color: document.querySelector(`[data-card-color="${i}"]`).value
    });
  }
  return {
    kicker: document.getElementById('kicker').value,
    coverTitle: document.getElementById('coverTitle').value,
    coverSubtitle: document.getElementById('coverSubtitle').value,
    badges, badgeColors,
    contentHeading: document.getElementById('contentHeading').value,
    stats,
    illoCaption: document.getElementById('illoCaption').value,
    calloutTitle: document.getElementById('calloutTitle').value,
    calloutText: document.getElementById('calloutText').value,
    ctaHeadline: document.getElementById('ctaHeadline').value,
    ctaCards,
    ctaButton: document.getElementById('ctaButton').value
  };
}

let svgCache = {};
function renderAll(){
  const d = gatherState();
  svgCache.cover = buildCover(d);
  svgCache.content = buildContent(d);
  svgCache.cta = buildCta(d);
  document.getElementById('coverHolder').innerHTML = svgCache.cover;
  document.getElementById('contentHolder').innerHTML = svgCache.content;
  document.getElementById('ctaHolder').innerHTML = svgCache.cta;
}

function downloadSVG(page){
  const blob = new Blob([svgCache[page]], {type:'image/svg+xml'});
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url; a.download = `${page}.svg`;
  document.body.appendChild(a); a.click(); a.remove();
  URL.revokeObjectURL(url);
}
function downloadPNG(page){
  const svgStr = svgCache[page];
  const svgBlob = new Blob([svgStr], {type:'image/svg+xml;charset=utf-8'});
  const url = URL.createObjectURL(svgBlob);
  const img = new Image();
  img.onload = function(){
    const scale = 2;
    const canvas = document.createElement('canvas');
    canvas.width = W*scale; canvas.height = H*scale;
    const ctx = canvas.getContext('2d');
    ctx.scale(scale, scale);
    ctx.drawImage(img, 0, 0, W, H);
    URL.revokeObjectURL(url);
    canvas.toBlob(function(blob){
      const a = document.createElement('a');
      a.href = URL.createObjectURL(blob);
      a.download = `${page}.png`;
      document.body.appendChild(a); a.click(); a.remove();
    });
  };
  img.src = url;
}

/* ---------- init ---------- */
buildBadgeInputs();
buildStatsInputs();
buildCtaCardInputs();
renderAll();
document.getElementById('panel').addEventListener('input', ()=>{
  clearTimeout(window.__rt);
  window.__rt = setTimeout(renderAll, 250);
});
</script>
</body>
</html>
```