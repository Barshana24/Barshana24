#!/usr/bin/env python3
"""Generate the README panels in assets/.

Every panel is a drawing sheet: dark substrate, blueprint grid, a sheet label on
the top left, a shell command on the top right, and an accent hairline along the
bottom edge. Run this after editing any content below.

    python tools/build_panels.py

Nothing here is animated on purpose. GitHub renders README SVGs in secure static
mode, so animation timelines never advance and anything that depends on one
renders at its start value.
"""

from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "assets"

W = 1000

BG = "#0a0e14"
CARD_BG = "#0b1017"
INSET = "#171e2a"
GRID_FINE = "#111926"
GRID_MAJOR = "#18212f"
BORDER = "#1d2634"
RULE = "#19212e"

T1 = "#e8eef5"
T2 = "#c9d1d9"
T3 = "#8b949e"
T4 = "#6e7681"
T5 = "#55606f"
T6 = "#4b5563"

CY = "#22d3ee"
VI = "#a78bfa"
GR = "#34d399"
AM = "#fbbf24"

SANS = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Inter, Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"

DOT = "&#183;"

# Panels are 1000 units wide but GitHub scales them down to the reader's
# content column, which on a phone is under 400px. Sizes below are authored at
# a comfortable desktop scale and lifted by this factor so the smallest labels
# survive that reduction. Raising it further starts crowding the two-column
# layouts in brief.svg, so re-render and check for collisions if you change it.
TYPE_SCALE = 1.15


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _size(size):
    return round(size * TYPE_SCALE, 1)


def mono(x, y, size, fill, text, anchor=None, ls=None, opacity=None, weight=None):
    a = f' text-anchor="{anchor}"' if anchor else ""
    l = f' letter-spacing="{ls}"' if ls is not None else ""
    o = f' opacity="{opacity}"' if opacity is not None else ""
    w = f' font-weight="{weight}"' if weight else ""
    return (f'<text x="{x}" y="{y}" font-size="{_size(size)}" fill="{fill}" '
            f'font-family="{MONO}"{a}{l}{o}{w}>{text}</text>')


def sans(x, y, size, fill, text, anchor=None, ls=None, weight=None, opacity=None):
    a = f' text-anchor="{anchor}"' if anchor else ""
    l = f' letter-spacing="{ls}"' if ls is not None else ""
    w = f' font-weight="{weight}"' if weight else ""
    o = f' opacity="{opacity}"' if opacity is not None else ""
    return (f'<text x="{x}" y="{y}" font-size="{_size(size)}" fill="{fill}" '
            f'font-family="{SANS}"{a}{l}{w}{o}>{text}</text>')


def rule(x1, y, x2, color=RULE):
    return f'<path d="M{x1} {y}H{x2}" stroke="{color}" stroke-width="1"/>'


def open_svg(w, h, aria, title, major_grid=False, glow_at=None):
    """Panel substrate: grid, glow, bottom hairline, rounded clip."""
    glow = ""
    if glow_at:
        cx, cy, rx, ry, col, op = glow_at
        glow = (f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" '
                f'fill="url(#glow)"/>')
        glow_def = (f'<radialGradient id="glow" cx="50%" cy="50%" r="50%">'
                    f'<stop offset="0%" stop-color="{col}" stop-opacity="{op}"/>'
                    f'<stop offset="100%" stop-color="{col}" stop-opacity="0"/>'
                    f'</radialGradient>')
    else:
        glow_def = ""

    major_def = ""
    major_use = ""
    if major_grid:
        major_def = (f'<pattern id="gm" width="100" height="100" patternUnits="userSpaceOnUse">'
                     f'<path d="M100 0H0V100" fill="none" stroke="{GRID_MAJOR}" stroke-width="1"/>'
                     f'</pattern>')
        major_use = f'<rect width="{w}" height="{h}" fill="url(#gm)"/>'

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img"
     aria-label="{esc(aria)}" font-family="{SANS}">
  <title>{esc(title)}</title>
  <defs>
    <clipPath id="card"><rect x="0" y="0" width="{w}" height="{h}" rx="14"/></clipPath>
    <pattern id="gf" width="20" height="20" patternUnits="userSpaceOnUse">
      <path d="M20 0H0V20" fill="none" stroke="{GRID_FINE}" stroke-width="1"/>
    </pattern>
    {major_def}
    {glow_def}
    <linearGradient id="hair" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="{CY}" stop-opacity="0"/>
      <stop offset="24%" stop-color="{CY}" stop-opacity="0.7"/>
      <stop offset="60%" stop-color="{VI}" stop-opacity="0.5"/>
      <stop offset="90%" stop-color="{GR}" stop-opacity="0.42"/>
      <stop offset="100%" stop-color="{GR}" stop-opacity="0"/>
    </linearGradient>
  </defs>
  <rect x="0" y="0" width="{w}" height="{h}" rx="14" fill="{BG}"/>
  <g clip-path="url(#card)">
    <rect width="{w}" height="{h}" fill="url(#gf)"/>
    {major_use}
    {glow}
    <rect x="0" y="{h - 2}" width="{w}" height="2" fill="url(#hair)"/>
  </g>
'''


def sheet_head(num, name, cmd, y=34, w=W, caret=True):
    """Sheet label on the left, shell command on the right."""
    parts = [
        f'<rect x="40" y="{y - 6}" width="6" height="6" fill="{CY}"/>',
        mono(58, y, 10, T5, f"SHEET {num} / {name}", ls=2.2),
    ]
    if cmd:
        end = w - 52 if caret else w - 40
        parts.append(mono(end, y, 10, CY, esc(cmd), anchor="end", opacity=0.72))
        if caret:
            parts.append(f'<rect x="{w - 46}" y="{y - 10}" width="2" height="12" fill="{CY}"/>')
    return "\n  ".join(parts)


def brackets(w, h, inset=18, arm=16, color=CY, op=0.34):
    a, i = arm, inset
    return (f'<g stroke="{color}" stroke-width="1.2" fill="none" opacity="{op}" stroke-linecap="square">'
            f'<path d="M{i} {i + a}V{i}h{a}"/>'
            f'<path d="M{w - i - a} {i}h{a}v{a}"/>'
            f'<path d="M{w - i} {h - i - a}v{a}h-{a}"/>'
            f'<path d="M{i + a} {h - i}H{i}v-{a}"/>'
            f'</g>')


def write(name, body):
    (OUT / name).write_text(body + "</svg>\n", encoding="utf-8")
    print(f"  {name}")


# ---------------------------------------------------------------- sheet 01

def build_header():
    h = 250
    aria = ("Barshana Chatterjee. I build things that put AI to work on real data, "
            "usually on a local model.")
    s = open_svg(W, h, aria, "Barshana Chatterjee", major_grid=True,
                 glow_at=(880, 30, 360, 200, CY, 0.16))
    s += "  " + brackets(W, h) + "\n"
    s += "  " + sheet_head("01", "IDENTITY", None) + "\n"
    s += "  " + mono(960, 34, 11, T4, "@Barshana24", anchor="end") + "\n"
    s += "  " + sans(40, 100, 40, T1, "BARSHANA CHATTERJEE", weight=700, ls=0.4) + "\n"

    # dimension line, drawn to a fixed length so it never depends on font metrics
    s += (f'  <g stroke="#243044" stroke-width="1">'
          f'<path d="M40 121h300"/><path d="M40 116v10"/><path d="M340 116v10"/></g>\n')

    s += "  " + sans(40, 154, 15, T3, "I build things that put AI to work on real data, "
                     "usually on a local model.") + "\n"
    s += "  " + mono(40, 186, 11, T4, f"PYTHON {DOT} TYPESCRIPT {DOT} FASTAPI {DOT} OLLAMA {DOT} "
                     f"POSTGRES {DOT} NEXT.JS", ls=1.1) + "\n"
    s += f'  <circle cx="44" cy="212" r="3.5" fill="{GR}"/>\n'
    s += "  " + mono(58, 216, 10, T4, f"KOLKATA, IN  {DOT}  LOCAL-FIRST AI  {DOT}  "
                     f"OPEN TO COLLABORATION", ls=1.5) + "\n"

    # SIW waveguide cross-section, a nod to the antenna work
    vias = "".join(f'<circle cx="{x}" cy="{y}" r="2.5"/>'
                   for y in (84, 152) for x in range(726, 935, 16))
    wave = ("M726 118 " + " ".join("q13 -21 26 0 q13 21 26 0" for _ in range(4)))
    s += f'''  <g opacity="0.9">
    <g stroke="#1b3a44" stroke-width="1"><path d="M726 84h208"/><path d="M726 152h208"/></g>
    <g fill="{BG}" stroke="{CY}" stroke-width="1" opacity="0.55">{vias}</g>
    <path d="{wave}" fill="none" stroke="{CY}" stroke-width="1.6" stroke-dasharray="6 10" opacity="0.85"/>
    <g stroke="#243044" stroke-width="1"><path d="M712 84v68"/><path d="M707 84h10"/><path d="M707 152h10"/></g>
    {mono(700, 121, 9, T5, "a", anchor="end")}
    {mono(726, 178, 9, T6, "SIW WAVEGUIDE / TE10", ls=1.6)}
  </g>
'''
    write("header.svg", s)


# ---------------------------------------------------------------- sheet 02

FOCUS = [
    (CY, "LOCAL-LLM TOOLING", "docs, code review, prompt compression"),
    (VI, "AGENT BENCHMARKS", "upstream CLI work on AOBench for HPC"),
    (GR, f"RF {DOT} DSP", "SIW antenna design, Springer Nature paper"),
]

# Keep these lines short. The focus column starts at x=580 and long lines here
# are what collide with it first on wider fallback fonts.
BIO = [
    "I build things that put AI to work on real data, usually on",
    "a local model. Most of what I ship runs fully offline: no",
    "API keys, and nothing leaves the machine it runs on.",
]


def build_brief():
    h = 300
    aria = " ".join(BIO) + " Current focus: " + "; ".join(f"{a}, {b}" for _, a, b in FOCUS)
    s = open_svg(W, h, aria, "Brief", glow_at=(120, 300, 380, 170, VI, 0.12))
    s += "  " + sheet_head("02", "BRIEF", "$ whoami --verbose") + "\n"
    s += "  " + rule(40, 50, 960) + "\n"

    for i, line in enumerate(BIO):
        s += "  " + sans(40, 86 + i * 22, 13.5, T2, esc(line)) + "\n"

    # operating principle, set off with an accent bar
    s += "  " + mono(40, 180, 9.5, T5, "OPERATING PRINCIPLE", ls=1.8) + "\n"
    s += f'  <rect x="40" y="192" width="2" height="46" rx="1" fill="{CY}" opacity="0.7"/>\n'
    s += "  " + sans(56, 212, 14, T1, "If a model can run on the machine that already") + "\n"
    s += "  " + sans(56, 232, 14, T1, "holds the data, it should.") + "\n"

    s += "  " + mono(580, 86, 9.5, T5, "CURRENT FOCUS", ls=1.8) + "\n"
    for i, (col, label, desc) in enumerate(FOCUS):
        y = 122 + i * 44
        s += f'  <rect x="580" y="{y - 8}" width="5" height="5" fill="{col}"/>\n'
        s += "  " + mono(596, y, 10, col, label, ls=1.3) + "\n"
        s += "  " + sans(596, y + 18, 11.5, T4, esc(desc)) + "\n"

    s += "  " + rule(40, 258, 960) + "\n"
    s += "  " + mono(40, 282, 10, GR, "&gt; open to collaboration", ls=1.2) + "\n"
    write("brief.svg", s)


# ---------------------------------------------------------------- sheet 03

TILES = [
    ("PUBLIC REPOS", "14", CY),
    ("SHIPPED TOOLS", "6", GR),
    ("UPSTREAM PRs", "3", VI),
    ("PUBLICATIONS", "1", AM),
]


def build_signals():
    h = 152
    aria = "Signals. " + ", ".join(f"{l}: {v}" for l, v, _ in TILES)
    s = open_svg(W, h, aria, "Signals")
    s += "  " + sheet_head("03", "SIGNALS", "$ stat --profile") + "\n"

    tw, gap = 218, 16
    for i, (label, value, col) in enumerate(TILES):
        x = 40 + i * (tw + gap)
        s += (f'  <rect x="{x}" y="{56}" width="{tw}" height="74" rx="10" '
              f'fill="{CARD_BG}" stroke="{BORDER}"/>\n')
        s += "  " + mono(x + 14, 78, 8.5, T5, label, ls=1.6) + "\n"
        s += "  " + sans(x + 14, 112, 26, T1, value, weight=700) + "\n"
        s += f'  <rect x="{x + 14}" y="{120}" width="56" height="2" rx="1" fill="{col}"/>\n'
    write("signals.svg", s)


# ---------------------------------------------------------------- sheet 04

LANGS = [
    ("Python", 92, "#3572A5"),
    ("TypeScript", 84, "#3178c6"),
    ("SQL", 70, "#e38c00"),
    ("JavaScript", 48, "#f1e05a"),
    ("MATLAB", 22, "#e16737"),
]

RUNTIME = [
    ("Ollama / local LLMs", 90, VI),
    ("FastAPI", 78, "#05998b"),
    ("React / Next.js", 72, "#61dafb"),
    ("PostgreSQL", 58, "#7aa6d6"),
    ("BigQuery", 44, "#4285f4"),
]

TRACK = 412


def build_stack():
    h = 352
    aria = ("Stack, weighted by use. Languages: "
            + ", ".join(f"{n} {v}" for n, v, _ in LANGS)
            + ". Runtime and data: " + ", ".join(f"{n} {v}" for n, v, _ in RUNTIME) + ".")
    s = open_svg(W, h, aria, "Systems map", glow_at=(500, 356, 520, 150, CY, 0.11))
    s += "  " + sheet_head("04", "SYSTEMS MAP", "$ stack --resolve --weighted") + "\n"
    s += "  " + rule(40, 50, 960) + "\n"
    s += f'  <path d="M500 66v228" stroke="#161d29" stroke-width="1"/>\n'
    s += "  " + mono(40, 82, 10, "#5a6472", "LANGUAGES", ls=1.8) + "\n"
    s += "  " + mono(530, 82, 10, "#5a6472", "RUNTIME / DATA", ls=1.8) + "\n"

    for col_x, items in ((40, LANGS), (530, RUNTIME)):
        bx = col_x + 18
        for i, (name, val, color) in enumerate(items):
            y = 110 + i * 38
            s += f'  <circle cx="{col_x + 5}" cy="{y - 4}" r="3.5" fill="{color}"/>\n'
            s += "  " + sans(bx, y, 12.5, T2, esc(name)) + "\n"
            s += "  " + mono(bx + TRACK, y, 10, T4, str(val), anchor="end") + "\n"
            s += (f'  <rect x="{bx}" y="{y + 14}" width="{TRACK}" height="4" rx="2" fill="{INSET}"/>\n'
                  f'  <rect x="{bx}" y="{y + 14}" width="{round(TRACK * val / 100)}" height="4" '
                  f'rx="2" fill="{color}"/>\n')

    s += "  " + rule(40, 302, 960) + "\n"
    s += "  " + mono(40, 326, 10, T5,
                     f"ALSO  {DOT}  CHROME EXTENSIONS  {DOT}  CANVAS 2D  {DOT}  "
                     f"PDF REPORT PIPELINES  {DOT}  CISCO PACKET TRACER", ls=1.4) + "\n"
    write("stack.svg", s)


# ---------------------------------------------------------------- sheet 05

STAGES = [
    ("01", "INGEST", "Python " + DOT + " BigQuery", False),
    ("02", "STORE", "PostgreSQL", False),
    ("03", "REASON", "Ollama, local", True),
    ("04", "SERVE", "FastAPI", False),
    ("05", "INTERFACE", "React / Next.js", False),
]


def build_pipeline():
    h = 268
    aria = ("End to end pipeline: " +
            " then ".join(f"{n} using {t}" for _, n, t, _ in STAGES) +
            ". Step 03 runs locally so no data leaves the machine.")
    s = open_svg(W, h, aria, "Pipeline", glow_at=(500, -20, 460, 170, VI, 0.10))
    s += "  " + sheet_head("05", "PIPELINE", "$ trace --end-to-end") + "\n"
    s += "  " + rule(40, 50, 960) + "\n"
    s += "  " + mono(40, 74, 9.5, T5, "HOW A PROJECT ACTUALLY GETS BUILT, LEFT TO RIGHT", ls=1.6) + "\n"

    bw, gap, by, bh = 156, 35, 100, 78
    for i, (num, name, tech, hero) in enumerate(STAGES):
        x = 40 + i * (bw + gap)
        stroke = VI if hero else BORDER
        s += (f'  <rect x="{x}" y="{by}" width="{bw}" height="{bh}" rx="10" '
              f'fill="{CARD_BG}" stroke="{stroke}"/>\n')
        s += "  " + mono(x + 13, by + 21, 8.5, CY if not hero else VI, num, ls=1.4) + "\n"
        s += "  " + sans(x + 13, by + 44, 12.5, T1, name, weight=600) + "\n"
        s += "  " + mono(x + 13, by + 64, 9, T4, tech) + "\n"
        if i < len(STAGES) - 1:
            ax, axe = x + bw + 6, x + bw + gap - 12
            s += (f'  <path d="M{ax} {by + bh // 2}H{axe}" stroke="#2b3a52" stroke-width="1"/>\n'
                  f'  <path d="M{axe} {by + bh // 2 - 3.5}l6 3.5l-6 3.5z" fill="#3d4f6b"/>\n')

    s += "  " + rule(40, 210, 960) + "\n"
    s += f'  <circle cx="45" cy="232" r="3.5" fill="{GR}"/>\n'
    s += "  " + mono(58, 236, 10, GR,
                     f"STEP 03 RUNS ON THE LOCAL MACHINE  {DOT}  NO KEYS, NO DATA LEAVING THE BOX",
                     ls=1.3) + "\n"
    write("pipeline.svg", s)


# ---------------------------------------------------------------- sheet 06

CARDS = [
    dict(slug="technical-doc-generator", lang="Python", color="#3572A5",
         desc=["Point it at a codebase and get back a README, an",
               "API reference, a UML diagram, and inline comments.",
               "Runs fully offline on a local model."],
         meta=["OFFLINE", "OLLAMA", "DOCS"]),
    dict(slug="ai-code-reviewer", lang="TypeScript", color="#3178c6",
         desc=["Scores code across ten quality dimensions and",
               "exports a PDF report. No cloud API keys required,",
               "so nothing you review is uploaded."],
         meta=["OFFLINE", "FASTAPI", "PDF"]),
    dict(slug="Token_minimiser", lang="JavaScript", color="#f1e05a",
         desc=["Chrome extension that shrinks prompts before they",
               "reach ChatGPT, Claude, or Gemini. Same instructions,",
               "15-45% fewer tokens, works in any text box."],
         meta=["MIT", "EXTENSION", "OFFLINE"]),
    dict(slug="FunellQ", lang="TypeScript", color="#3178c6",
         desc=["Funnel analytics on Google's public GA4 e-commerce",
               "dataset. Finds where shoppers drop off, then sizes",
               "the biggest leak in real revenue."],
         meta=["BIGQUERY", "ANALYTICS"]),
    dict(slug="Siglo-GTM-tool", lang="Python", color="#3572A5",
         desc=["GTM intelligence platform that scores signals,",
               "member targets, and open opportunities into a",
               "ranked list of business development plays."],
         meta=["SCORING", "PIPELINE"]),
    dict(slug="EduBot", lang="TypeScript", color="#3178c6",
         desc=["Study assistant for engineering students in their",
               "own language, with quizzes, flashcards, and",
               "interview prep."],
         meta=["MULTILINGUAL", "CHATBOT"]),
]

CARD_W, CARD_H = 480, 172


def build_cards():
    for i, c in enumerate(CARDS, start=1):
        w, h = CARD_W, CARD_H
        aria = f"{c['slug']}, {c['lang']}. " + " ".join(c["desc"])
        s = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img"
     aria-label="{esc(aria)}" font-family="{SANS}">
  <title>{esc(c["slug"])}</title>
  <defs>
    <clipPath id="cc"><rect x="0" y="0" width="{w}" height="{h}" rx="12"/></clipPath>
    <pattern id="gf" width="20" height="20" patternUnits="userSpaceOnUse">
      <path d="M20 0H0V20" fill="none" stroke="{GRID_FINE}" stroke-width="1"/>
    </pattern>
    <linearGradient id="hair" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="{c["color"]}" stop-opacity="0.75"/>
      <stop offset="100%" stop-color="{c["color"]}" stop-opacity="0"/>
    </linearGradient>
  </defs>
  <rect x="0" y="0" width="{w}" height="{h}" rx="12" fill="{CARD_BG}"/>
  <g clip-path="url(#cc)">
    <rect width="{w}" height="{h}" fill="url(#gf)"/>
    <rect x="0" y="0" width="3" height="{h}" fill="{c["color"]}" opacity="0.85"/>
    <rect x="0" y="{h - 2}" width="{w}" height="2" fill="url(#hair)"/>
  </g>
  <rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="12" fill="none" stroke="{BORDER}"/>
'''
        s += "  " + sans(24, 40, 15, T1, esc(c["slug"]), weight=700) + "\n"
        s += f'  <rect x="{24}" y="{48}" width="28" height="2" rx="1" fill="{c["color"]}" opacity="0.6"/>\n'
        s += "  " + mono(w - 36, 39, 9.5, T4, c["lang"], anchor="end") + "\n"
        s += f'  <circle cx="{w - 24}" cy="{35.5}" r="3.5" fill="{c["color"]}"/>\n'
        for j, line in enumerate(c["desc"]):
            s += "  " + sans(24, 78 + j * 19, 11.5, T3, esc(line)) + "\n"
        s += "  " + rule(24, 144, w - 24) + "\n"
        s += "  " + mono(24, 163, 8.5, T5, f"  {DOT}  ".join(c["meta"]), ls=1.3) + "\n"
        write(f"card-{i:02d}-{c['slug']}.svg", s)


def build_work_header():
    h = 98
    s = open_svg(W, h, "Work manifest. Six selected projects of fourteen public repositories.",
                 "Work manifest")
    s += "  " + sheet_head("06", "WORK MANIFEST", "$ ls ./projects --selected") + "\n"
    s += "  " + rule(40, 50, 960) + "\n"
    s += "  " + mono(40, 76, 9.5, T5,
                     f"SIX OF FOURTEEN PUBLIC REPOSITORIES  {DOT}  ANY CARD OPENS ITS REPO", ls=1.6) + "\n"
    write("work.svg", s)


# ---------------------------------------------------------------- sheet 07

PRS = [
    ("43", "add --json to report json and compare runs", GR),
    ("47", "add aobench list coverage", GR),
    ("50", "pay down mypy --strict debt in cli/", AM),
]


def build_upstream():
    h = 296
    aria = ("Upstream work on AOBench, a role aware benchmark for AI agents that operate "
            "HPC systems. Pull requests: " + "; ".join(f"number {n}, {t}" for n, t, _ in PRS))
    s = open_svg(W, h, aria, "Upstream", glow_at=(880, 300, 380, 160, GR, 0.10))
    s += "  " + sheet_head("07", "UPSTREAM", "$ git log --author=Barshana24") + "\n"
    s += "  " + rule(40, 50, 960) + "\n"
    s += "  " + sans(40, 84, 13.5, T2, "AOBench is a role-aware, permission-enforced benchmark for AI") + "\n"
    s += "  " + sans(40, 106, 13.5, T2, "agents that operate HPC systems: SLURM, telemetry, RBAC. I work") + "\n"
    s += "  " + sans(40, 128, 13.5, T2, "on its command line interface.") + "\n"
    s += "  " + mono(40, 168, 9.5, T5, "PULL REQUESTS AUTHORED", ls=1.8) + "\n"

    for i, (num, title, col) in enumerate(PRS):
        y = 200 + i * 30
        s += f'  <circle cx="46" cy="{y - 4}" r="3.5" fill="{col}"/>\n'
        s += "  " + mono(62, y, 11, col, f"#{num}") + "\n"
        s += "  " + sans(100, y, 12.5, T2, esc(title)) + "\n"

    s += "  " + mono(960, 168, 9.5, T5, "88 TASKS / 29 ENVIRONMENTS", anchor="end", ls=1.4) + "\n"
    write("upstream.svg", s)


# ---------------------------------------------------------------- sheet 08

def build_activity_header():
    h = 98
    s = open_svg(W, h, "Activity. Contribution history over the last year.", "Activity")
    s += "  " + sheet_head("08", "ACTIVITY", "$ git log --since=1.year --oneline | wc -l") + "\n"
    s += "  " + rule(40, 50, 960) + "\n"
    s += "  " + mono(40, 76, 9.5, T5, "CONTRIBUTION HISTORY, PULLED LIVE", ls=1.6) + "\n"
    write("activity.svg", s)


# ---------------------------------------------------------------- sheet 09

BLOCK = [
    [("DRAWN BY", "BARSHANA CHATTERJEE"), ("LOCATION", "KOLKATA, IN"), ("SHEETS", "09")],
    [("DISCIPLINE", "AI SYSTEMS / RF"), ("STATUS", "OPEN TO COLLABORATION"), ("REVISION", "02")],
]


def build_titleblock():
    h = 176
    flat = [f"{k}: {v}" for row in BLOCK for k, v in row]
    s = open_svg(W, h, "Title block. " + ". ".join(flat), "Title block",
                 glow_at=(500, 180, 520, 150, VI, 0.10))
    s += "  " + brackets(W, h) + "\n"
    s += "  " + sheet_head("09", "TITLE BLOCK", "$ contact --print") + "\n"

    bx, by, bw, bh = 40, 62, 920, 84
    cw, ch = bw // 3, bh // 2
    s += (f'  <rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="8" '
          f'fill="{CARD_BG}" stroke="{BORDER}"/>\n')
    for i in (1, 2):
        s += f'  <path d="M{bx + i * cw} {by}v{bh}" stroke="{BORDER}" stroke-width="1"/>\n'
    s += f'  <path d="M{bx} {by + ch}h{bw}" stroke="{BORDER}" stroke-width="1"/>\n'

    for r, row in enumerate(BLOCK):
        for c, (label, value) in enumerate(row):
            x = bx + c * cw + 14
            y = by + r * ch
            s += "  " + mono(x, y + 17, 8, T6, label, ls=1.6) + "\n"
            s += "  " + mono(x, y + 33, 10.5, T2, value, ls=0.6) + "\n"
    write("titleblock.svg", s)


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    print("writing panels to", OUT)
    build_header()
    build_brief()
    build_signals()
    build_stack()
    build_pipeline()
    build_work_header()
    build_cards()
    build_upstream()
    build_activity_header()
    build_titleblock()
    print("done")
