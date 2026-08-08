#!/usr/bin/env python3
import json

W, H = 680, 200
pink = "#00d9ff"; purple = "#ffb020"; gold = "#ffd700"
bg1 = "#050a14"; bg2 = "#0d1a2e"
text_light = "#eaf3ff"; muted = "#7d94b8"; panel = "rgba(255,255,255,0.05)"; border = "rgba(0,217,255,0.18)"

with open("stats_data.json") as f:
    data = json.load(f)

RANK_COLORS = {
    "SSS": "#ff2e8c", "SS": "#ffd700", "S": "#ffb020",
    "A+": "#00d9ff", "A": "#38d9ff", "B": "#50fa7b",
}

trophies = data.get("trophies") or []
TROPHIES = [(label, RANK_COLORS.get(rank, "#8f9bb3"), rank) for (label, value, rank) in trophies]

cell_w = 104
cell_h = 150
gap = 8
x0 = 12
y0 = 30

cells = []
for i, (label, color, rank) in enumerate(TROPHIES):
    x = x0 + i * (cell_w + gap)
    delay = 0.25 + i * 0.16
    cells.append(f'''<g transform="translate({x},{y0})" opacity="0">
    <animate attributeName="opacity" from="0" to="1" begin="{delay:.2f}s" dur="0.4s" fill="freeze"/>
    <animateTransform attributeName="transform" type="translate" additive="sum" from="0,18" to="0,0" begin="{delay:.2f}s" dur="0.45s" fill="freeze" calcMode="spline" keySplines="0.25 1.4 0.4 1"/>
    <rect width="{cell_w}" height="{cell_h}" rx="12" fill="{panel}" stroke="{color}" stroke-opacity="0.55" stroke-width="1.3"/>
    <circle cx="{cell_w/2}" cy="46" r="26" fill="none" stroke="{color}" stroke-width="2" opacity="0.35">
        <animate attributeName="r" values="24;30;24" dur="2.4s" begin="{delay+0.5:.2f}s" repeatCount="indefinite"/>
        <animate attributeName="opacity" values="0.5;0.15;0.5" dur="2.4s" begin="{delay+0.5:.2f}s" repeatCount="indefinite"/>
    </circle>
    <text x="{cell_w/2}" y="54" text-anchor="middle" font-size="26">🏆</text>
    <text x="{cell_w/2}" y="90" text-anchor="middle" font-family="'Segoe UI',sans-serif" font-size="11" fill="{muted}">{label}</text>
    <text x="{cell_w/2}" y="120" text-anchor="middle" font-family="'Consolas',monospace" font-size="22" font-weight="800" fill="{color}">{rank}</text>
    <g clip-path="url(#cellClip{i})">
        <rect x="-180" y="-40" width="60" height="{cell_h+80}" fill="#ffffff" opacity="0.18" transform="rotate(20)">
            <animateTransform attributeName="transform" type="translate" additive="sum" from="-20,0" to="{cell_w+220},0" dur="3.6s" begin="{2.5+i*0.2:.2f}s" repeatCount="indefinite"/>
        </rect>
    </g>
    <clipPath id="cellClip{i}"><rect width="{cell_w}" height="{cell_h}" rx="12"/></clipPath>
</g>''')

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="GitHub trophies">
<defs>
    <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stop-color="{bg1}"/>
        <stop offset="100%" stop-color="{bg2}"/>
    </linearGradient>
    <clipPath id="outer"><rect x="0" y="0" width="{W}" height="{H}" rx="18"/></clipPath>
</defs>
<g clip-path="url(#outer)">
    <rect width="{W}" height="{H}" fill="url(#bgGrad)"/>
    {''.join(cells)}
    <rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="17" fill="none" stroke="{border}" stroke-width="1"/>
</g>
</svg>'''
with open("trophies.svg", "w") as f:
    f.write(svg)
print("trophies.svg", len(svg), "bytes")