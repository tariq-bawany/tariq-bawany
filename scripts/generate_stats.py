#!/usr/bin/env python3
import json, math, sys

W, H = 480, 260
pink = "#00d9ff"; purple = "#ffb020"; lightpink = "#7ee8ff"
bg1 = "#050a14"; bg2 = "#0d1a2e"
text_light = "#eaf3ff"; muted = "#7d94b8"; panel = "rgba(255,255,255,0.05)"; border = "rgba(0,217,255,0.18)"

with open("stats_data.json") as f:
    data = json.load(f)


def fmt(n):
    return f"{n:,}"


# decorative fill scale caps - just for the bar visuals, not exact percentages
CAPS = {"Total Stars": 500, "Total Commits": 3000, "Repositories": 60, "Followers": 300}

STATS = [
    ("Total Stars", fmt(data["total_stars"]), min(1.0, data["total_stars"] / CAPS["Total Stars"])),
    ("Total Commits", fmt(data["total_commits"]) + ("+" if data.get("commits_is_estimate") else ""),
     min(1.0, data["total_commits"] / CAPS["Total Commits"])),
    ("Repositories", fmt(data["total_repos"]), min(1.0, data["total_repos"] / CAPS["Repositories"])),
    ("Followers", fmt(data["followers"]), min(1.0, data["followers"] / CAPS["Followers"])),
]

# overall rank ring: average of the four capped ratios
RANK_PCT = sum(s[2] for s in STATS) / len(STATS)
RANK_PCT = max(0.06, RANK_PCT)
# derive a simple letter rank from RANK_PCT
if RANK_PCT >= 0.85: RANK = "S+"
elif RANK_PCT >= 0.65: RANK = "A+"
elif RANK_PCT >= 0.45: RANK = "A"
elif RANK_PCT >= 0.25: RANK = "B+"
else: RANK = "B"

cx, cy, r = 92, 130, 62
circumference = 2 * math.pi * r
dash = circumference * RANK_PCT

rows = []
row_y0 = 30
row_h = 52
for i, (label, val, pct) in enumerate(STATS):
    y = row_y0 + i * row_h
    bar_w = 190
    delay = 0.9 + i * 0.18
    rows.append(f'''<g transform="translate(210,{y})" opacity="0">
    <animate attributeName="opacity" from="0" to="1" begin="{delay:.2f}s" dur="0.5s" fill="freeze"/>
    <animateTransform attributeName="transform" type="translate" additive="sum" from="40,0" to="0,0" begin="{delay:.2f}s" dur="0.5s" fill="freeze" calcMode="spline" keySplines="0.2 0.8 0.2 1"/>
    <text x="0" y="0" font-family="'Segoe UI',sans-serif" font-size="13" fill="{muted}">{label}</text>
    <text x="{bar_w}" y="0" text-anchor="end" font-family="'Consolas',monospace" font-size="14" font-weight="700" fill="{text_light}">{val}</text>
    <rect x="0" y="8" width="{bar_w}" height="7" rx="3.5" fill="{panel}" stroke="{border}" stroke-width="0.75"/>
    <rect x="0" y="8" width="0" height="7" rx="3.5" fill="url(#barGrad)">
        <animate attributeName="width" from="0" to="{bar_w*pct:.1f}" begin="{delay+0.15:.2f}s" dur="0.9s" fill="freeze" calcMode="spline" keySplines="0.2 0.8 0.2 1"/>
    </rect>
</g>''')

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="GitHub stats">
<defs>
    <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stop-color="{bg1}"/>
        <stop offset="100%" stop-color="{bg2}"/>
    </linearGradient>
    <linearGradient id="ringGrad" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stop-color="{pink}"/>
        <stop offset="100%" stop-color="{purple}"/>
    </linearGradient>
    <linearGradient id="barGrad" x1="0%" y1="0%" x2="100%" y2="0%">
        <stop offset="0%" stop-color="{pink}"/>
        <stop offset="100%" stop-color="{purple}"/>
    </linearGradient>
    <filter id="blurSoft" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="30"/></filter>
    <clipPath id="outer"><rect x="0" y="0" width="{W}" height="{H}" rx="18"/></clipPath>
</defs>
<g clip-path="url(#outer)">
    <rect width="{W}" height="{H}" fill="url(#bgGrad)"/>
    <circle cx="60" cy="30" r="90" fill="{purple}" opacity="0.12" filter="url(#blurSoft)"/>
    <text x="24" y="26" font-family="'Segoe UI',sans-serif" font-size="15" font-weight="700" fill="{text_light}">📊 GitHub Stats</text>

    <g transform="translate({cx},{cy})">
        <circle r="{r}" fill="none" stroke="{panel}" stroke-width="12"/>
        <circle r="{r}" fill="none" stroke="url(#ringGrad)" stroke-width="12" stroke-linecap="round"
            stroke-dasharray="{circumference:.1f}" stroke-dashoffset="{circumference:.1f}" transform="rotate(-90)">
            <animate attributeName="stroke-dashoffset" from="{circumference:.1f}" to="{circumference-dash:.1f}" begin="0.4s" dur="1.4s" fill="freeze" calcMode="spline" keySplines="0.2 0.8 0.2 1"/>
        </circle>
        <text x="0" y="-4" text-anchor="middle" font-family="'Segoe UI',sans-serif" font-size="34" font-weight="800" fill="{text_light}" opacity="0">{RANK}
            <animate attributeName="opacity" from="0" to="1" begin="1.5s" dur="0.5s" fill="freeze"/>
        </text>
        <text x="0" y="18" text-anchor="middle" font-family="'Segoe UI',sans-serif" font-size="11" fill="{muted}" opacity="0">RANK
            <animate attributeName="opacity" from="0" to="1" begin="1.6s" dur="0.5s" fill="freeze"/>
        </text>
    </g>

    {''.join(rows)}
    <rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="17" fill="none" stroke="{border}" stroke-width="1"/>
</g>
</svg>'''
with open("stats.svg", "w") as f:
    f.write(svg)
print("stats.svg", len(svg), "bytes — rank", RANK)