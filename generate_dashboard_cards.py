import os
import math
import urllib.request
import json
from datetime import datetime, timezone

# -------------------------------------------------------------
# 1. CONSTANTS & THEME
# -------------------------------------------------------------
WIDTH = 350
HEIGHT = 200
BG_COLOR = "#0d1117"
BORDER_COLOR = "#30363d"
TITLE_COLOR = "#58a6ff"
LABEL_COLOR = "#8b949e"
VALUE_COLOR = "#e6edf3"
ACCENT_GREEN = "#10b981"

LANG_COLORS = {
    "C#": "#178600",
    "Dart": "#00B4AB",
    "TypeScript": "#3178c6",
    "JavaScript": "#f1e05a",
    "Rust": "#dea584",
    "Python": "#3572A5",
    "Kotlin": "#A97BFF",
    "HTML": "#e34c26",
    "CSS": "#563d7c",
    "Go": "#00ADD8",
    "C++": "#f34b7d",
    "C": "#555555"
}

# Default Fallback Values
stats = {
    "stars": 86,
    "commits": "1.2k",
    "prs": 45,
    "issues": 0,
    "contributed_to": 13
}

periodic = {
    "today": 56,
    "month": 361,
    "year": "1,229",
    "total": "1,229"
}

languages_data = [
    ("C#", 54.4, "#178600"),
    ("Dart", 16.8, "#00B4AB"),
    ("TypeScript", 10.5, "#3178c6"),
    ("Rust", 8.2, "#dea584"),
    ("JavaScript", 5.6, "#f1e05a"),
    ("Kotlin", 4.5, "#A97BFF")
]

# -------------------------------------------------------------
# 2. FETCH LIVE GITHUB DATA
# -------------------------------------------------------------
try:
    # 2.1 Public Repos & Stars
    repos_url = 'https://api.github.com/users/divyviradiya2/repos?per_page=100'
    req = urllib.request.Request(repos_url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=8) as resp:
        repos = json.loads(resp.read().decode('utf-8'))
        total_stars = sum(r.get('stargazers_count', 0) for r in repos)
        if total_stars:
            stats["stars"] = total_stars

    # 2.2 PRs Count
    pr_url = 'https://api.github.com/search/issues?q=type:pr+author:divyviradiya2'
    req_pr = urllib.request.Request(pr_url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req_pr, timeout=8) as resp:
        prs_data = json.loads(resp.read().decode('utf-8'))
        stats["prs"] = prs_data.get('total_count', stats["prs"])

    # 2.3 Issues Count
    issue_url = 'https://api.github.com/search/issues?q=type:issue+author:divyviradiya2'
    req_issue = urllib.request.Request(issue_url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req_issue, timeout=8) as resp:
        issues_data = json.loads(resp.read().decode('utf-8'))
        stats["issues"] = issues_data.get('total_count', stats["issues"])

    # 2.4 Language Bytes Breakdown
    lang_bytes = {}
    for r in repos:
        if not r.get('fork'):
            l_url = r.get('languages_url')
            try:
                req_l = urllib.request.Request(l_url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req_l, timeout=4) as l_resp:
                    data = json.loads(l_resp.read().decode('utf-8'))
                    for k, v in data.items():
                        lang_bytes[k] = lang_bytes.get(k, 0) + v
            except:
                pass

    if lang_bytes:
        total_b = sum(lang_bytes.values())
        sorted_l = sorted(lang_bytes.items(), key=lambda x: x[1], reverse=True)[:5]
        languages_data = []
        for name, b in sorted_l:
            pct = (b / float(total_b)) * 100
            col = LANG_COLORS.get(name, "#8b949e")
            languages_data.append((name, pct, col))

    # 2.5 Contributions Calendar (Today, Month, Year)
    now = datetime.now(timezone.utc)
    today_str = now.strftime('%Y-%m-%d')
    this_month_str = now.strftime('%Y-%m')
    this_year_str = now.strftime('%Y')
    month_name = now.strftime('%b')

    c_url = 'https://github-contributions-api.jogruber.de/v4/divyviradiya2?y=all'
    req_c = urllib.request.Request(c_url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req_c, timeout=8) as resp:
        c_data = json.loads(resp.read().decode('utf-8'))
        contributions = c_data.get('contributions', [])
        if contributions:
            today_c = sum(c['count'] for c in contributions if c['date'] == today_str)
            month_c = sum(c['count'] for c in contributions if c['date'].startswith(this_month_str))
            year_c = sum(c['count'] for c in contributions if c['date'].startswith(this_year_str))
            total_c = sum(c['count'] for c in contributions)
            periodic["today"] = today_c
            periodic["month"] = month_c
            periodic["year"] = f"{year_c:,}"
            periodic["total"] = f"{total_c:,}"
            stats["commits"] = f"{total_c / 1000.0:.1f}k" if total_c >= 1000 else str(total_c)

except Exception as e:
    print(f"Notice: Using fallback or cached values: {e}")

os.makedirs("assets", exist_ok=True)

# -------------------------------------------------------------
# 3. GENERATE CARD 1: STATS CARD (assets/stats-card.svg)
# -------------------------------------------------------------
stats_svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {HEIGHT}" width="100%" height="{HEIGHT}">
  <defs>
    <linearGradient id="cardBg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0d1117"/>
      <stop offset="100%" stop-color="#090d13"/>
    </linearGradient>
  </defs>

  <style>
    .title {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-weight: 600; font-size: 17px; fill: {TITLE_COLOR}; }}
    .label {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-size: 13px; fill: {LABEL_COLOR}; }}
    .val {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-weight: 700; font-size: 13.5px; fill: {VALUE_COLOR}; }}
    .icon {{ fill: {LABEL_COLOR}; }}
  </style>

  <rect x="0.5" y="0.5" width="{WIDTH - 1}" height="{HEIGHT - 1}" rx="6" fill="url(#cardBg)" stroke="{BORDER_COLOR}" stroke-width="1"/>
  <text x="25" y="34" class="title">Stats</text>

  <g transform="translate(25, 62)">
    <!-- Total Stars -->
    <g transform="translate(0, 0)">
      <path class="icon" d="M8 .25a.75.75 0 0 1 .673.418l1.882 3.815 4.21.612a.75.75 0 0 1 .416 1.279l-3.046 2.97.719 4.192a.75.75 0 0 1-1.088.791L8 12.347l-3.766 1.98a.75.75 0 0 1-1.088-.79l.72-4.194L.818 6.374a.75.75 0 0 1 .416-1.28l4.21-.611L7.327.668A.75.75 0 0 1 8 .25Z"/>
      <text x="22" y="11" class="label">Total Stars:</text>
      <text x="145" y="11" class="val">{stats["stars"]}</text>
    </g>

    <!-- Total Commits -->
    <g transform="translate(0, 26)">
      <path class="icon" d="M10.5 7.75a2.5 2.5 0 1 1-5 0 2.5 2.5 0 0 1 5 0Zm1.43.75a4.002 4.002 0 0 0-7.86 0H.75a.75.75 0 1 0 0 1.5h3.32a4.002 4.002 0 0 0 7.86 0h3.32a.75.75 0 1 0 0-1.5h-3.32Z"/>
      <text x="22" y="11" class="label">Total Commits:</text>
      <text x="145" y="11" class="val">{stats["commits"]}</text>
    </g>

    <!-- Total PRs -->
    <g transform="translate(0, 52)">
      <path class="icon" d="M7.177 3.073L9.573.677A.25.25 0 0 1 10 .854v4.792a.25.25 0 0 1-.427.177L7.177 3.427a.25.25 0 0 1 0-.354ZM3.75 2.5a.75.75 0 1 0 0 1.5.75.75 0 0 0 0-1.5Zm-2.25.75a2.25 2.25 0 1 1 3 2.122v5.256a2.251 2.251 0 1 1-1.5 0V5.372A2.25 2.25 0 0 1 1.5 3.25Zm11 7.5a.75.75 0 1 0 0 1.5.75.75 0 0 0 0-1.5Zm-2.25.75a2.25 2.25 0 1 1 3 2.122v.128a.75.75 0 0 1-1.5 0v-.128a2.25 2.25 0 0 1-1.5-2.122Z"/>
      <text x="22" y="11" class="label">Total PRs:</text>
      <text x="145" y="11" class="val">{stats["prs"]}</text>
    </g>

    <!-- Total Issues -->
    <g transform="translate(0, 78)">
      <path class="icon" d="M8 9.5a1.5 1.5 0 1 0 0-3 1.5 1.5 0 0 0 0 3ZM8 0a8 8 0 1 1 0 16A8 8 0 0 1 8 0ZM1.5 8a6.5 6.5 0 1 0 13 0 6.5 6.5 0 0 0-13 0Z"/>
      <text x="22" y="11" class="label">Total Issues:</text>
      <text x="145" y="11" class="val">{stats["issues"]}</text>
    </g>

    <!-- Contributed to -->
    <g transform="translate(0, 104)">
      <path class="icon" d="M2 2.5A2.5 2.5 0 0 1 4.5 0h8.75a.75.75 0 0 1 .75.75v12.5a.75.75 0 0 1-.75.75h-2.5a.75.75 0 0 0-.75.75v1.25a.75.75 0 0 1-1.28.53L7.47 14.25a.75.75 0 0 0-.53-.22H4.5A2.5 2.5 0 0 1 2 11.5v-9Zm10.5 10V1.5H4.5a1 1 0 0 0-1 1v9a1 1 0 0 0 1 1h2.44a2.25 2.25 0 0 1 1.59.66l1.47 1.47V13.25a2.25 2.25 0 0 1 2-2.22V11H12.5v1.5ZM4.5 12h7a.75.75 0 0 0 .75-.75V11H4.5a1 1 0 0 0-1 1v-.25c.2.16.45.25.75.25Z"/>
      <text x="22" y="11" class="label">Contributed to:</text>
      <text x="145" y="11" class="val">{stats["contributed_to"]}</text>
    </g>
  </g>

  <!-- Octocat Silhouette Badge on Right -->
  <g transform="translate(255, 68)" fill="#8b949e" opacity="0.38">
    <circle cx="36" cy="36" r="36" fill="#21262d"/>
    <path fill="#0d1117" d="M36 12C22.7 12 12 22.7 12 36c0 10.6 6.9 19.6 16.4 22.8 1.2.2 1.6-.5 1.6-1.2v-4.1c-6.7 1.4-8.1-3.2-8.1-3.2-1.1-2.8-2.7-3.5-2.7-3.5-2.2-1.5.2-1.5.2-1.5 2.4.2 3.7 2.5 3.7 2.5 2.1 3.7 5.7 2.6 7.1 2 .2-1.5.8-2.6 1.5-3.2-5.3-.6-10.9-2.7-10.9-11.9 0-2.6.9-4.8 2.5-6.5-.2-.6-1.1-3.1.2-6.4 0 0 2-.6 6.6 2.5 1.9-.5 4-.8 6.1-.8 2.1 0 4.1.3 6.1.8 4.6-3.1 6.6-2.5 6.6-2.5 1.3 3.3.5 5.8.2 6.4 1.5 1.7 2.5 3.8 2.5 6.5 0 9.2-5.6 11.2-11 11.8.9.7 1.6 2.2 1.6 4.4v6.6c0 .6.4 1.4 1.6 1.2C53.1 55.6 60 46.6 60 36 60 22.7 49.3 12 36 12Z"/>
  </g>
</svg>'''

with open("assets/stats-card.svg", "w", encoding="utf-8") as f:
    f.write(stats_svg)
print("Generated assets/stats-card.svg successfully!")

# -------------------------------------------------------------
# 4. GENERATE CARD 2: LANGUAGES DONUT CARD (assets/languages-card.svg)
# -------------------------------------------------------------
# Calculate Donut slices
cx = 265
cy = 108
r = 45
circumference = 2 * math.pi * r

donut_paths = []
curr_offset = 0.0
for name, pct, col in languages_data:
    slice_len = (pct / 100.0) * circumference
    dash_array = f"{slice_len:.2f} {circumference - slice_len:.2f}"
    dash_offset = f"{-curr_offset:.2f}"
    donut_paths.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{col}" stroke-width="22" stroke-dasharray="{dash_array}" stroke-dashoffset="{dash_offset}" transform="rotate(-90 {cx} {cy})"/>')
    curr_offset += slice_len

# Legend items
legend_items = []
for i, (name, pct, col) in enumerate(languages_data[:5]):
    ly = 65 + i * 24
    legend_items.append(f'''
    <g transform="translate(25, {ly})">
      <rect width="13" height="13" rx="2" fill="{col}"/>
      <text x="22" y="11" class="label">{name}</text>
      <text x="135" y="11" class="val">{pct:.1f}%</text>
    </g>''')

legend_svg = "\n".join(legend_items)
donut_svg_circles = "\n    ".join(donut_paths)

languages_svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {HEIGHT}" width="100%" height="{HEIGHT}">
  <defs>
    <linearGradient id="cardBg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0d1117"/>
      <stop offset="100%" stop-color="#090d13"/>
    </linearGradient>
  </defs>

  <style>
    .title {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-weight: 600; font-size: 17px; fill: {TITLE_COLOR}; }}
    .label {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-size: 13px; fill: {LABEL_COLOR}; }}
    .val {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-weight: 600; font-size: 12px; fill: {VALUE_COLOR}; }}
  </style>

  <rect x="0.5" y="0.5" width="{WIDTH - 1}" height="{HEIGHT - 1}" rx="6" fill="url(#cardBg)" stroke="{BORDER_COLOR}" stroke-width="1"/>
  <text x="25" y="34" class="title">Top Languages by Commit</text>

  <!-- Legend -->
  {legend_svg}

  <!-- Donut Chart -->
  <g>
    <!-- Background track ring -->
    <circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#161b22" stroke-width="22"/>
    {donut_svg_circles}
  </g>
</svg>'''

with open("assets/languages-card.svg", "w", encoding="utf-8") as f:
    f.write(languages_svg)
print("Generated assets/languages-card.svg successfully!")

# -------------------------------------------------------------
# 5. GENERATE CARD 3: PERIODIC CONTRIBUTIONS (assets/contributions-card.svg)
# -------------------------------------------------------------
now = datetime.now(timezone.utc)
month_name = now.strftime('%B')
this_year_str = now.strftime('%Y')

contributions_svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {HEIGHT}" width="100%" height="{HEIGHT}">
  <defs>
    <linearGradient id="cardBg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0d1117"/>
      <stop offset="100%" stop-color="#090d13"/>
    </linearGradient>
    <linearGradient id="greenBar" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#064e3b"/>
      <stop offset="50%" stop-color="#059669"/>
      <stop offset="100%" stop-color="#10b981"/>
    </linearGradient>
  </defs>

  <style>
    .title {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-weight: 600; font-size: 17px; fill: {TITLE_COLOR}; }}
    .label {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-size: 13px; fill: {LABEL_COLOR}; }}
    .val {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-weight: 700; font-size: 13.5px; fill: {VALUE_COLOR}; }}
    .highlight-val {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-weight: 800; font-size: 14px; fill: {ACCENT_GREEN}; }}
    .icon {{ fill: {LABEL_COLOR}; }}
    .icon-green {{ fill: {ACCENT_GREEN}; }}
  </style>

  <rect x="0.5" y="0.5" width="{WIDTH - 1}" height="{HEIGHT - 1}" rx="6" fill="url(#cardBg)" stroke="{BORDER_COLOR}" stroke-width="1"/>
  <text x="25" y="34" class="title">Periodic Contributions</text>

  <g transform="translate(25, 62)">
    <!-- 1. Today's Activity -->
    <g transform="translate(0, 0)">
      <path class="icon-green" d="M8.75 0a.75.75 0 0 1 .71.507l1.75 5.25a.75.75 0 0 1-.71.993H7.5v4.5a.75.75 0 0 1-1.37.42l-4.5-6a.75.75 0 0 1 .6-.17H5.25V.75A.75.75 0 0 1 6 0h2.75Z"/>
      <text x="22" y="11" class="label">Today's Activity:</text>
      <text x="160" y="11" class="highlight-val">{periodic["today"]}</text>
    </g>

    <!-- 2. This Month's Activity -->
    <g transform="translate(0, 28)">
      <path class="icon" d="M4.75 0a.75.75 0 0 1 .75.75V2h4.5V.75a.75.75 0 0 1 1.5 0V2h1.75C14.216 2 15 2.784 15 3.75v9.5A1.75 1.75 0 0 1 13.25 15H1.75A1.75 1.75 0 0 1 0 13.25v-9.5C0 2.784.784 2 1.75 2H3.5V.75A.75.75 0 0 1 4.75 0ZM1.5 6.5v6.75c0 .138.112.25.25.25h11.5a.25.25 0 0 0 .25-.25V6.5h-12Zm11.75-3H1.75a.25.25 0 0 0-.25.25V5h12v-1.25a.25.25 0 0 0-.25-.25Z"/>
      <text x="22" y="11" class="label">This Month ({month_name}):</text>
      <text x="160" y="11" class="val">{periodic["month"]}</text>
    </g>

    <!-- 3. This Year's Activity -->
    <g transform="translate(0, 56)">
      <path class="icon" d="M3.75 2h7.5a.75.75 0 0 1 .75.75V4h1.75A2.25 2.25 0 0 1 16 6.25v.5a3.25 3.25 0 0 1-3.25 3.25H11.5a4.25 4.25 0 0 1-3.25 4.14v1.61h2a.75.75 0 0 1 0 1.5H4.75a.75.75 0 0 1 0-1.5h2V14.14A4.25 4.25 0 0 1 3.5 10H2.25A3.25 3.25 0 0 1-1 6.75v-.5A2.25 2.25 0 0 1 1.25 4H3V2.75A.75.75 0 0 1 3.75 2ZM3 5.5H1.75a.75.75 0 0 0-.75.75v.5c0 .966.784 1.75 1.75 1.75H3V5.5Zm9 3h.25c.966 0 1.75-.784 1.75-1.75v-.5a.75.75 0 0 0-.75-.75H12v3Z"/>
      <text x="22" y="11" class="label">This Year ({this_year_str}):</text>
      <text x="160" y="11" class="val">{periodic["year"]}</text>
    </g>

    <!-- 4. Total Lifetime Activity -->
    <g transform="translate(0, 84)">
      <path class="icon" d="M10.5 7.75a2.5 2.5 0 1 1-5 0 2.5 2.5 0 0 1 5 0Zm1.43.75a4.002 4.002 0 0 0-7.86 0H.75a.75.75 0 1 0 0 1.5h3.32a4.002 4.002 0 0 0 7.86 0h3.32a.75.75 0 1 0 0-1.5h-3.32Z"/>
      <text x="22" y="11" class="label">Total Activity:</text>
      <text x="160" y="11" class="val">{periodic["total"]}</text>
    </g>
  </g>

  <!-- Right Side Visual Accent -->
  <g transform="translate(265, 82)">
    <circle cx="20" cy="20" r="32" fill="none" stroke="#21262d" stroke-width="5"/>
    <circle cx="20" cy="20" r="32" fill="none" stroke="url(#greenBar)" stroke-width="5" stroke-dasharray="201" stroke-dashoffset="48" stroke-linecap="round" transform="rotate(-90 20 20)"/>
    <text x="20" y="17" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto" font-size="11" font-weight="bold" fill="{ACCENT_GREEN}" text-anchor="middle">ACTIVE</text>
    <text x="20" y="30" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto" font-size="9" fill="{LABEL_COLOR}" text-anchor="middle">2026</text>
  </g>
</svg>'''

with open("assets/contributions-card.svg", "w", encoding="utf-8") as f:
    f.write(contributions_svg)
print("Generated assets/contributions-card.svg successfully!")
