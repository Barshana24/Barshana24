#!/usr/bin/env python3
"""Generate the README panels in assets/.

Every panel is a drawing sheet: dark substrate, blueprint grid, a sheet label on
the top left, a shell command on the top right, and an accent hairline along the
bottom edge. Run this after editing any content below.

    python tools/build_panels.py

Two constraints shaped this file, both worth knowing before you change it.

1. Panels are composited into four files rather than one file each.
   raw.githubusercontent.com rate limits unauthenticated traffic, and fifteen
   images on one page reliably drew HTTP 429 for a third of them. Panels are
   stacked inside a taller SVG with transparent gaps between them, which looks
   identical to separate images but costs one request instead of fifteen.

2. Nothing is animated. GitHub renders README SVGs in secure static mode, so
   animation timelines never advance and anything depending on one renders
   frozen at its start value.
"""

from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "assets"

W = 1000
GAP = 22

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
# layout in the brief panel, so re-render and check for collisions.
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


def sheet_head(num, name, cmd, y=34, w=W, caret=True):
    parts = [
        f'<rect x="40" y="{y - 6}" width="6" height="6" fill="{CY}"/>',
        mono(58, y, 10, T5, f"SHEET {num} / {name}", ls=2.2),
    ]
    if cmd:
        end = w - 52 if caret else w - 40
        parts.append(mono(end, y, 10, CY, esc(cmd), anchor="end", opacity=0.72))
        if caret:
            parts.append(f'<rect x="{w - 46}" y="{y - 10}" width="2" height="12" fill="{CY}"/>')
    return "\n    ".join(parts)


def brackets(w, h, inset=18, arm=16, color=CY, op=0.34):
    a, i = arm, inset
    return (f'<g stroke="{color}" stroke-width="1.2" fill="none" opacity="{op}" stroke-linecap="square">'
            f'<path d="M{i} {i + a}V{i}h{a}"/>'
            f'<path d="M{w - i - a} {i}h{a}v{a}"/>'
            f'<path d="M{w - i} {h - i - a}v{a}h-{a}"/>'
            f'<path d="M{i + a} {h - i}H{i}v-{a}"/>'
            f'</g>')


class Panel:
    """One drawing sheet, positioned by the compositor rather than itself."""

    def __init__(self, uid, h, body, aria, w=W, major_grid=False, glow=None,
                 corner_marks=False, hairline=CY, radius=14):
        self.uid = uid
        self.w = w
        self.h = h
        self.aria = aria
        self.major_grid = major_grid
        self.glow = glow
        self.corner_marks = corner_marks
        self.hairline = hairline
        self.radius = radius
        self.body = body

    def defs(self):
        d = [f'<clipPath id="c{self.uid}"><rect x="0" y="0" width="{self.w}" '
             f'height="{self.h}" rx="{self.radius}"/></clipPath>']
        if self.glow:
            _, _, _, _, col, op = self.glow
            d.append(f'<radialGradient id="g{self.uid}" cx="50%" cy="50%" r="50%">'
                     f'<stop offset="0%" stop-color="{col}" stop-opacity="{op}"/>'
                     f'<stop offset="100%" stop-color="{col}" stop-opacity="0"/>'
                     f'</radialGradient>')
        if self.hairline == CY:
            d.append(f'<linearGradient id="h{self.uid}" x1="0" y1="0" x2="1" y2="0">'
                     f'<stop offset="0%" stop-color="{CY}" stop-opacity="0"/>'
                     f'<stop offset="24%" stop-color="{CY}" stop-opacity="0.7"/>'
                     f'<stop offset="60%" stop-color="{VI}" stop-opacity="0.5"/>'
                     f'<stop offset="90%" stop-color="{GR}" stop-opacity="0.42"/>'
                     f'<stop offset="100%" stop-color="{GR}" stop-opacity="0"/>'
                     f'</linearGradient>')
        else:
            d.append(f'<linearGradient id="h{self.uid}" x1="0" y1="0" x2="1" y2="0">'
                     f'<stop offset="0%" stop-color="{self.hairline}" stop-opacity="0.75"/>'
                     f'<stop offset="100%" stop-color="{self.hairline}" stop-opacity="0"/>'
                     f'</linearGradient>')
        return d

    def render(self, y):
        w, h, u = self.w, self.h, self.uid
        glow = ""
        if self.glow:
            cx, cy, rx, ry, _, _ = self.glow
            glow = f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="url(#g{u})"/>'
        major = f'<rect width="{w}" height="{h}" fill="url(#gf)"/>' if self.major_grid else ""
        if self.major_grid:
            major = f'<rect width="{w}" height="{h}" fill="url(#gm)"/>'
        marks = "\n    " + brackets(w, h) if self.corner_marks else ""
        return f'''  <g transform="translate(0 {y})">
    <rect x="0" y="0" width="{w}" height="{h}" rx="{self.radius}" fill="{BG}"/>
    <g clip-path="url(#c{u})">
      <rect width="{w}" height="{h}" fill="url(#gf)"/>
      {major}
      {glow}
      <rect x="0" y="{h - 2}" width="{w}" height="2" fill="url(#h{u})"/>
    </g>{marks}
    {self.body}
  </g>
'''


def compose(name, panels, gap=GAP, title=""):
    """Stack panels vertically into one SVG with transparent gaps between them."""
    total = sum(p.h for p in panels) + gap * (len(panels) - 1)
    width = max(p.w for p in panels)
    aria = " ".join(p.aria for p in panels)

    defs = [f'<pattern id="gf" width="20" height="20" patternUnits="userSpaceOnUse">'
            f'<path d="M20 0H0V20" fill="none" stroke="{GRID_FINE}" stroke-width="1"/></pattern>',
            f'<pattern id="gm" width="100" height="100" patternUnits="userSpaceOnUse">'
            f'<path d="M100 0H0V100" fill="none" stroke="{GRID_MAJOR}" stroke-width="1"/></pattern>']
    for p in panels:
        defs.extend(p.defs())

    out = [f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {total}" width="{width}" height="{total}" role="img"
     aria-label="{esc(aria)}" font-family="{SANS}">
  <title>{esc(title or name)}</title>
  <defs>
    {chr(10).join("    " + d for d in defs).strip()}
  </defs>
''']
    y = 0
    for p in panels:
        out.append(p.render(y))
        y += p.h + gap
    out.append("</svg>\n")

    (OUT / name).write_text("".join(out), encoding="utf-8")
    print(f"  {name}  ({width}x{total})")


# ---------------------------------------------------------------- sheet 01

def p_header():
    h = 250
    b = [sheet_head("01", "IDENTITY", None)]
    b.append(mono(960, 34, 11, T4, "@Barshana24", anchor="end"))
    b.append(sans(40, 100, 40, T1, "BARSHANA CHATTERJEE", weight=700, ls=0.4))
    # dimension line, fixed length so it never depends on font metrics
    b.append('<g stroke="#243044" stroke-width="1">'
             '<path d="M40 121h300"/><path d="M40 116v10"/><path d="M340 116v10"/></g>')
    b.append(sans(40, 154, 15, T3, "I build things that put AI to work on real data, "
                  "usually on a local model."))
    b.append(mono(40, 186, 11, T4, f"PYTHON {DOT} TYPESCRIPT {DOT} FASTAPI {DOT} OLLAMA {DOT} "
                  f"POSTGRES {DOT} NEXT.JS", ls=1.1))
    b.append(f'<circle cx="44" cy="212" r="3.5" fill="{GR}"/>')
    b.append(mono(58, 216, 10, T4, f"KOLKATA, IN  {DOT}  LOCAL-FIRST AI  {DOT}  "
                  f"OPEN TO COLLABORATION", ls=1.5))

    vias = "".join(f'<circle cx="{x}" cy="{y}" r="2.5"/>'
                   for y in (84, 152) for x in range(726, 935, 16))
    wave = "M726 118 " + " ".join("q13 -21 26 0 q13 21 26 0" for _ in range(4))
    b.append(f'''<g opacity="0.9">
      <g stroke="#1b3a44" stroke-width="1"><path d="M726 84h208"/><path d="M726 152h208"/></g>
      <g fill="{BG}" stroke="{CY}" stroke-width="1" opacity="0.55">{vias}</g>
      <path d="{wave}" fill="none" stroke="{CY}" stroke-width="1.6" stroke-dasharray="6 10" opacity="0.85"/>
      <g stroke="#243044" stroke-width="1"><path d="M712 84v68"/><path d="M707 84h10"/><path d="M707 152h10"/></g>
      {mono(700, 121, 9, T5, "a", anchor="end")}
      {mono(726, 178, 9, T6, "SIW WAVEGUIDE / TE10", ls=1.6)}
    </g>''')

    aria = ("Barshana Chatterjee, at Barshana24. I build things that put AI to work on real "
            "data, usually on a local model. Kolkata, India. Open to collaboration.")
    return Panel("hdr", h, "\n    ".join(b), aria, major_grid=True,
                 glow=(880, 30, 360, 200, CY, 0.16), corner_marks=True)


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


def p_brief():
    h = 300
    b = [sheet_head("02", "BRIEF", "$ whoami --verbose"), rule(40, 50, 960)]
    for i, line in enumerate(BIO):
        b.append(sans(40, 86 + i * 22, 13.5, T2, esc(line)))

    b.append(mono(40, 180, 10, T5, "OPERATING PRINCIPLE", ls=1.8))
    b.append(f'<rect x="40" y="192" width="2" height="46" rx="1" fill="{CY}" opacity="0.7"/>')
    b.append(sans(56, 212, 14, T1, "If a model can run on the machine that already"))
    b.append(sans(56, 232, 14, T1, "holds the data, it should."))

    b.append(mono(580, 86, 10, T5, "CURRENT FOCUS", ls=1.8))
    for i, (col, label, desc) in enumerate(FOCUS):
        y = 122 + i * 44
        b.append(f'<rect x="580" y="{y - 8}" width="5" height="5" fill="{col}"/>')
        b.append(mono(596, y, 10, col, label, ls=1.3))
        b.append(sans(596, y + 18, 11.5, T4, esc(desc)))

    b.append(rule(40, 258, 960))
    b.append(mono(40, 282, 10, GR, "&gt; open to collaboration", ls=1.2))

    aria = ("Brief. " + " ".join(BIO) + " Operating principle: if a model can run on the "
            "machine that already holds the data, it should. Current focus: "
            + "; ".join(f"{a}, {c}" for _, a, c in FOCUS) + ". Open to collaboration.")
    return Panel("brf", h, "\n    ".join(b), aria, glow=(120, 300, 380, 170, VI, 0.12))


# ---------------------------------------------------------------- sheet 03

TILES = [
    ("PUBLIC REPOS", "14", CY),
    ("SHIPPED TOOLS", "6", GR),
    ("UPSTREAM PRs", "3", VI),
    ("PUBLICATIONS", "1", AM),
]


def p_signals():
    h = 152
    b = [sheet_head("03", "SIGNALS", "$ stat --profile")]
    tw, gap = 218, 16
    for i, (label, value, col) in enumerate(TILES):
        x = 40 + i * (tw + gap)
        b.append(f'<rect x="{x}" y="56" width="{tw}" height="74" rx="10" '
                 f'fill="{CARD_BG}" stroke="{BORDER}"/>')
        b.append(mono(x + 14, 78, 8.5, T5, label, ls=1.6))
        b.append(sans(x + 14, 112, 26, T1, value, weight=700))
        b.append(f'<rect x="{x + 14}" y="120" width="56" height="2" rx="1" fill="{col}"/>')
    aria = "Signals. " + ", ".join(f"{l}: {v}" for l, v, _ in TILES) + "."
    return Panel("sig", h, "\n    ".join(b), aria)


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


def p_stack():
    h = 352
    b = [sheet_head("04", "SYSTEMS MAP", "$ stack --resolve --weighted"),
         rule(40, 50, 960),
         f'<path d="M500 66v228" stroke="#161d29" stroke-width="1"/>',
         mono(40, 82, 10, "#5a6472", "LANGUAGES", ls=1.8),
         mono(530, 82, 10, "#5a6472", "RUNTIME / DATA", ls=1.8)]

    for col_x, items in ((40, LANGS), (530, RUNTIME)):
        bx = col_x + 18
        for i, (nm, val, color) in enumerate(items):
            y = 110 + i * 38
            b.append(f'<circle cx="{col_x + 5}" cy="{y - 4}" r="3.5" fill="{color}"/>')
            b.append(sans(bx, y, 12.5, T2, esc(nm)))
            b.append(mono(bx + TRACK, y, 10, T4, str(val), anchor="end"))
            b.append(f'<rect x="{bx}" y="{y + 14}" width="{TRACK}" height="4" rx="2" fill="{INSET}"/>')
            b.append(f'<rect x="{bx}" y="{y + 14}" width="{round(TRACK * val / 100)}" '
                     f'height="4" rx="2" fill="{color}"/>')

    b.append(rule(40, 302, 960))
    b.append(mono(40, 326, 10, T5,
                  f"ALSO  {DOT}  CHROME EXTENSIONS  {DOT}  CANVAS 2D  {DOT}  "
                  f"PDF REPORT PIPELINES  {DOT}  CISCO PACKET TRACER", ls=1.4))

    aria = ("Systems map, weighted by use. Languages: "
            + ", ".join(f"{n} {v}" for n, v, _ in LANGS)
            + ". Runtime and data: " + ", ".join(f"{n} {v}" for n, v, _ in RUNTIME) + ".")
    return Panel("stk", h, "\n    ".join(b), aria, glow=(500, 356, 520, 150, CY, 0.11))


# ---------------------------------------------------------------- sheet 05

STAGES = [
    ("01", "INGEST", "Python " + DOT + " BigQuery", False),
    ("02", "STORE", "PostgreSQL", False),
    ("03", "REASON", "Ollama, local", True),
    ("04", "SERVE", "FastAPI", False),
    ("05", "INTERFACE", "React / Next.js", False),
]


def p_pipeline():
    h = 268
    b = [sheet_head("05", "PIPELINE", "$ trace --end-to-end"), rule(40, 50, 960),
         mono(40, 74, 9.5, T5, "HOW A PROJECT ACTUALLY GETS BUILT, LEFT TO RIGHT", ls=1.6)]

    bw, gap, by, bh = 156, 35, 100, 78
    for i, (num, nm, tech, hero) in enumerate(STAGES):
        x = 40 + i * (bw + gap)
        b.append(f'<rect x="{x}" y="{by}" width="{bw}" height="{bh}" rx="10" '
                 f'fill="{CARD_BG}" stroke="{VI if hero else BORDER}"/>')
        b.append(mono(x + 13, by + 21, 8.5, VI if hero else CY, num, ls=1.4))
        b.append(sans(x + 13, by + 44, 12.5, T1, nm, weight=600))
        b.append(mono(x + 13, by + 64, 9, T4, tech))
        if i < len(STAGES) - 1:
            ax, axe = x + bw + 6, x + bw + gap - 12
            b.append(f'<path d="M{ax} {by + bh // 2}H{axe}" stroke="#2b3a52" stroke-width="1"/>')
            b.append(f'<path d="M{axe} {by + bh // 2 - 3.5}l6 3.5l-6 3.5z" fill="#3d4f6b"/>')

    b.append(rule(40, 210, 960))
    b.append(f'<circle cx="45" cy="232" r="3.5" fill="{GR}"/>')
    b.append(mono(58, 236, 10, GR,
                  f"STEP 03 RUNS ON THE LOCAL MACHINE  {DOT}  NO KEYS, NO DATA LEAVING THE BOX",
                  ls=1.3))

    aria = ("Pipeline, how a project gets built left to right: "
            + ", then ".join(f"{n} using {t}" for _, n, t, _ in STAGES)
            + ". Step 03 runs on the local machine, so no keys and no data leave the box.")
    return Panel("pip", h, "\n    ".join(b), aria, glow=(500, -20, 460, 170, VI, 0.10))


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

CARD_W, CARD_H, CARD_GAP = 488, 172, 24


def _card(c, i):
    """One project card, drawn at the origin. Positioned by p_cards."""
    w, h, u = CARD_W, CARD_H, f"cd{i}"
    b = [f'<rect x="0" y="0" width="{w}" height="{h}" rx="12" fill="{CARD_BG}"/>',
         f'<g clip-path="url(#c{u})">',
         f'  <rect width="{w}" height="{h}" fill="url(#gf)"/>',
         f'  <rect x="0" y="0" width="3" height="{h}" fill="{c["color"]}" opacity="0.85"/>',
         f'  <rect x="0" y="{h - 2}" width="{w}" height="2" fill="url(#h{u})"/>',
         f'</g>',
         f'<rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="12" fill="none" stroke="{BORDER}"/>',
         sans(24, 40, 15, T1, esc(c["slug"]), weight=700),
         f'<rect x="24" y="48" width="28" height="2" rx="1" fill="{c["color"]}" opacity="0.6"/>',
         mono(w - 36, 39, 9.5, T4, c["lang"], anchor="end"),
         f'<circle cx="{w - 24}" cy="35.5" r="3.5" fill="{c["color"]}"/>']
    for j, line in enumerate(c["desc"]):
        b.append(sans(24, 78 + j * 19, 11.5, T3, esc(line)))
    b.append(rule(24, 144, w - 24))
    b.append(mono(24, 163, 8.5, T5, f"  {DOT}  ".join(c["meta"]), ls=1.3))
    return "\n      ".join(b)


def p_work():
    h = 98
    b = [sheet_head("06", "WORK MANIFEST", "$ ls ./projects --selected"), rule(40, 50, 960),
         mono(40, 76, 9.5, T5,
              f"SIX OF FOURTEEN PUBLIC REPOSITORIES  {DOT}  LINKS BELOW", ls=1.6)]
    return Panel("wrk", h, "\n    ".join(b),
                 "Work manifest. Six selected projects of fourteen public repositories.")


class CardGrid(Panel):
    """Two columns of project cards, sharing the page substrate rather than its own."""

    def __init__(self):
        rows = (len(CARDS) + 1) // 2
        h = rows * CARD_H + (rows - 1) * CARD_GAP
        aria = " ".join(f"{c['slug']}, {c['lang']}. " + " ".join(c["desc"]) for c in CARDS)
        super().__init__("grid", h, "", aria)

    def defs(self):
        d = []
        for i, c in enumerate(CARDS):
            d.append(f'<clipPath id="ccd{i}"><rect x="0" y="0" width="{CARD_W}" '
                     f'height="{CARD_H}" rx="12"/></clipPath>')
            d.append(f'<linearGradient id="hcd{i}" x1="0" y1="0" x2="1" y2="0">'
                     f'<stop offset="0%" stop-color="{c["color"]}" stop-opacity="0.75"/>'
                     f'<stop offset="100%" stop-color="{c["color"]}" stop-opacity="0"/>'
                     f'</linearGradient>')
        return d

    def render(self, y):
        out = [f'  <g transform="translate(0 {y})">']
        for i, c in enumerate(CARDS):
            cx = (i % 2) * (CARD_W + CARD_GAP)
            cy = (i // 2) * (CARD_H + CARD_GAP)
            out.append(f'    <g transform="translate({cx} {cy})">\n      {_card(c, i)}\n    </g>')
        out.append("  </g>\n")
        return "\n".join(out)


# ---------------------------------------------------------------- sheet 07

PRS = [
    ("43", "add --json to report json and compare runs", GR),
    ("47", "add aobench list coverage", GR),
    ("50", "pay down mypy --strict debt in cli/", AM),
]


def p_upstream():
    h = 296
    b = [sheet_head("07", "UPSTREAM", "$ git log --author=Barshana24"), rule(40, 50, 960),
         sans(40, 84, 13.5, T2, "AOBench is a role-aware, permission-enforced benchmark for AI"),
         sans(40, 106, 13.5, T2, "agents that operate HPC systems: SLURM, telemetry, RBAC. I work"),
         sans(40, 128, 13.5, T2, "on its command line interface."),
         mono(40, 168, 9.5, T5, "PULL REQUESTS AUTHORED", ls=1.8),
         mono(960, 168, 9.5, T5, "88 TASKS / 29 ENVIRONMENTS", anchor="end", ls=1.4)]
    for i, (num, title, col) in enumerate(PRS):
        y = 200 + i * 30
        b.append(f'<circle cx="46" cy="{y - 4}" r="3.5" fill="{col}"/>')
        b.append(mono(62, y, 11, col, f"#{num}"))
        b.append(sans(100, y, 12.5, T2, esc(title)))

    aria = ("Upstream. AOBench is a role-aware, permission-enforced benchmark for AI agents "
            "that operate HPC systems: SLURM, telemetry, RBAC. I work on its command line "
            "interface. Pull requests authored: " + "; ".join(f"{n}, {t}" for n, t, _ in PRS) + ".")
    return Panel("ups", h, "\n    ".join(b), aria, glow=(880, 300, 380, 160, GR, 0.10))


# ---------------------------------------------------------------- sheet 08

# There is deliberately no contribution-graph panel. The usual third-party
# services for it are unreliable: github-readme-stats is deployment-paused,
# streak-stats returns an error card, and the activity graph intermittently
# renders "Can't fetch any contribution" as a full-width banner. GitHub already
# draws the real contribution calendar directly below the README, so nothing is
# lost by leaving it out.

BLOCK = [
    [("DRAWN BY", "BARSHANA CHATTERJEE"), ("LOCATION", "KOLKATA, IN"), ("SHEETS", "08")],
    [("DISCIPLINE", "AI SYSTEMS / RF"), ("STATUS", "OPEN TO COLLABORATION"), ("REVISION", "03")],
]


def p_titleblock():
    h = 176
    b = [sheet_head("08", "TITLE BLOCK", "$ contact --print")]
    bx, by, bw, bh = 40, 62, 920, 84
    cw, ch = bw // 3, bh // 2
    b.append(f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="8" '
             f'fill="{CARD_BG}" stroke="{BORDER}"/>')
    for i in (1, 2):
        b.append(f'<path d="M{bx + i * cw} {by}v{bh}" stroke="{BORDER}" stroke-width="1"/>')
    b.append(f'<path d="M{bx} {by + ch}h{bw}" stroke="{BORDER}" stroke-width="1"/>')
    for r, row in enumerate(BLOCK):
        for c, (label, value) in enumerate(row):
            x, y = bx + c * cw + 14, by + r * ch
            b.append(mono(x, y + 17, 8, T6, label, ls=1.6))
            b.append(mono(x, y + 33, 10.5, T2, value, ls=0.6))

    aria = "Title block. " + ". ".join(f"{k}: {v}" for row in BLOCK for k, v in row) + "."
    return Panel("ttl", h, "\n    ".join(b), aria, glow=(500, 180, 520, 150, VI, 0.10),
                 corner_marks=True)


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    print("writing panels to", OUT)
    # Two files, split only where the README needs real HTML links in between.
    # Every extra file is another request against the rate limit described in
    # the module docstring, so resist adding more.
    compose("sheet-1.svg", [p_header(), p_brief(), p_signals(), p_stack(), p_pipeline()],
            title="Barshana Chatterjee")
    compose("sheet-2.svg", [p_work(), CardGrid(), p_upstream(), p_titleblock()],
            title="Work, upstream, contact")
    print("done")
