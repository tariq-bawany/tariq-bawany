#!/usr/bin/env python3
import json

W, H = 480, 260
pink = "#00d9ff"; purple = "#ffb020"
bg1 = "#050a14"; bg2 = "#0d1a2e"
text_light = "#eaf3ff"; muted = "#7d94b8"; panel = "rgba(255,255,255,0.05)"; border = "rgba(0,217,255,0.18)"

with open("stats_data.json") as f:
    data = json.load(f)

# GitHub's conventional per-language colors (subset, extend as needed)
LANG_COLORS = {
    "JavaScript": "#f1e05a", "TypeScript": "#3178c6", "Python": "#3572A5",
    "HTML": "#e34c26", "CSS": "#563d7c", "Java": "#b07219", "C": "#555555",
    "C++": "#f34b7d", "C#": "#178600", "PHP": "#4F5D95", "Ruby": "#701516",
    "Go": "#00ADD8", "Rust": "#dea584", "Swift": "#F05138", "Kotlin": "#A97BFF",
    "Shell": "#89e051", "Vue": "#41b883", "Dart": "#00B4AB", "Jupyter Notebook": "#DA5B0B",
    "SCSS": "#c6538c", "EJS": "#a91e50",
}

LANGS = data.get("top_languages") or []
if not LANGS:
    LANGS = [("No language data yet", 100.0)]

rows = []
row_y0 = 50
row_h = 33
bar_w = 430
for i, (lang, pct) in enumerate(LANGS[:6]):
    color = LANG_COLORS.get(lang, "#8f9bb3")
    y = row_y0 + i * row_h
    delay = 0.5 + i * 0.15
    rows.append(f'''<g transform="translate(24,{y})" opacity="0">
    <animate attributeName="opacity" from="0" to="1" begin="{delay:.2f}s" dur="0.4s" fill="freeze"/>
    <text x="0" y="-6" font-family="'Segoe UI',sans-serif" font-size="12.5" fill="{text_light}">{lang}</text>
    <text x="{bar_w}" y="-6" text-anchor="end" font-family="'Consolas',monospace" font-size="12" fill="{muted}">{pct:g}%</text>
    <rect x="0" y="0" width="{bar_w}" height="9" rx="4.5" fill="{panel}" stroke="{border}" stroke-width="0.75"/>
    <rect x="0" y="0" width="0" height="9" rx="4.5" fill="{color}">
        <animate attributeName="width" from="0" to="{bar_w*pct/100:.1f}" begin="{delay+0.1:.2f}s" dur="0.9s" fill="freeze" calcMode="spline" keySplines="0.2 0.8 0.2 1"/>
    </rect>
    <rect x="0" y="0" width="0" height="9" rx="4.5" fill="#ffffff" opacity="0.25">
        <animate attributeName="width" from="0" to="{bar_w*pct/100:.1f}" begin="{delay+0.1:.2f}s" dur="0.9s" fill="freeze" calcMode="spline" keySplines="0.2 0.8 0.2 1"/>
        <animate attributeName="opacity" values="0.25;0" begin="{delay+1.0:.2f}s" dur="0.6s" fill="freeze"/>
    </rect>
</g>''')

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Top languages">
<defs>
    <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stop-color="{bg1}"/>
        <stop offset="100%" stop-color="{bg2}"/>
    </linearGradient>
    <filter id="blurSoft" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="30"/></filter>
    <clipPath id="outer"><rect x="0" y="0" width="{W}" height="{H}" rx="18"/></clipPath>
</defs>
<g clip-path="url(#outer)">
    <rect width="{W}" height="{H}" fill="url(#bgGrad)"/>
    <circle cx="{W-50}" cy="30" r="90" fill="{pink}" opacity="0.10" filter="url(#blurSoft)"/>
    <text x="24" y="30" font-family="'Segoe UI',sans-serif" font-size="15" font-weight="700" fill="{text_light}">🧠 Most Used Languages</text>
    {''.join(rows)}
    <rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="17" fill="none" stroke="{border}" stroke-width="1"/>
</g>
</svg>'''
with open("langs.svg", "w") as f:
    f.write(svg)
print("langs.svg", len(svg), "bytes")