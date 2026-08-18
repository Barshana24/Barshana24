#!/usr/bin/env python3
"""Generate the README panels in assets/.

Every panel is a drawing sheet: dark substrate, blueprint grid, a sheet label on
the top left, a shell command on the top right, and an accent hairline along the
bottom edge. Run this after editing any content below.

    python tools/build_panels.py

Two constraints shaped this file, both worth knowing before you change it.

1. Panels are composited into two files rather than one file each. They are
   stacked inside a taller SVG with transparent gaps between them, which looks
   identical to separate images at a fraction of the requests. This matters
   because raw.githubusercontent.com rate limits requests that reach origin
   with HTTP 429. The thing that actually forces origin hits is a unique query
   string, so the README links these files with no ?v= cache-buster; keeping
   the URL stable means visitors are served from the CDN edge instead.

2. Nothing is animated. GitHub renders README SVGs in secure static mode, so
   animation timelines never advance and anything depending on one renders
   frozen at its start value.
"""

import json
import textwrap
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "assets"

W = 1000
GAP = 22

# Narrow canvas for phones. A 1000-wide sheet scaled into a ~390px phone column
# renders 13px body text at 5px, so the README serves these instead through a
# <picture> media query. Authoring narrower means the same absolute type sizes
# come out proportionally much larger after scaling.
NW = 480
NM = 22
NI = NW - NM * 2

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

# A literal middot, not the &#183; entity. Copy that runs through wrap()/lines()
# gets escaped on the way out, which would turn an entity into visible
# "&#183;" text. A real character survives escaping untouched.
DOT = "·"

# Panels are 1000 units wide but GitHub scales them down to the reader's
# content column, which on a phone is under 400px. Sizes below are authored at
# a comfortable desktop scale and lifted by this factor so the smallest labels
# survive that reduction. Raising it further starts crowding the two-column
# layout in the systems map, so re-render and check for collisions.
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


def sheet_head(num, name, cmd, y=34, w=W, caret=True, x=40, size=10, ls=2.2):
    parts = [
        f'<rect x="{x}" y="{y - 6}" width="6" height="6" fill="{CY}"/>',
        mono(x + 18, y, size, T5, f"SHEET {num} / {name}", ls=ls),
    ]
    if cmd:
        end = w - x - 12 if caret else w - x
        parts.append(mono(end, y, size, CY, esc(cmd), anchor="end", opacity=0.72))
        if caret:
            parts.append(f'<rect x="{w - x - 6}" y="{y - 10}" width="2" height="12" fill="{CY}"/>')
    return "\n    ".join(parts)


def wrap(text, max_px, size, is_mono=False):
    """Split text to fit max_px, estimating advance width from the font size.

    The narrow layouts wrap a lot of copy and hand-wrapping every string is how
    lines end up overlapping the next column, so estimate instead. The factors
    are deliberately pessimistic.
    """
    per_char = _size(size) * (0.62 if is_mono else 0.55)
    return textwrap.wrap(text, width=max(8, int(max_px / per_char))) or [""]


def lines(x, y, size, fill, text, max_px, step, is_mono=False, **kw):
    """Wrap text and lay it out downward. Returns (markup, y after last line)."""
    wrapped = wrap(text, max_px, size, is_mono)
    f = mono if is_mono else sans
    out = [f(x, y + i * step, size, fill, esc(ln), **kw) for i, ln in enumerate(wrapped)]
    return "\n    ".join(out), y + len(wrapped) * step


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
        # Heights are computed from wrapped copy and fractional grid pitches, so
        # round here rather than leaving a fractional viewBox on the composite.
        self.h = int(round(h))
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

    # newline="\n" so the SVGs are written LF even on Windows. Text mode would
    # otherwise emit CRLF and leave git renormalising every file on commit.
    with open(OUT / name, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("".join(out))
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


# The brief and signals sheets were removed on request. The bio they carried now
# lives only on the identity sheet, and the stat tiles are gone entirely.

# ---------------------------------------------------------------- sheet 02

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
    b = [sheet_head("02", "SYSTEMS MAP", "$ stack --resolve --weighted"),
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


# ---------------------------------------------------------------- sheet 03

STAGES = [
    ("01", "INGEST", "Python " + DOT + " BigQuery", False),
    ("02", "STORE", "PostgreSQL", False),
    ("03", "REASON", "Ollama, local", True),
    ("04", "SERVE", "FastAPI", False),
    ("05", "INTERFACE", "React / Next.js", False),
]


def p_pipeline():
    h = 268
    b = [sheet_head("03", "PIPELINE", "$ trace --end-to-end"), rule(40, 50, 960),
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


# ---------------------------------------------------------------- sheet 04

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
    b = [sheet_head("04", "WORK MANIFEST", "$ ls ./projects --selected"), rule(40, 50, 960),
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


# ---------------------------------------------------------------- sheet 05

PRS = [
    ("43", "add --json to report json and compare runs", GR),
    ("47", "add aobench list coverage", GR),
    ("50", "pay down mypy --strict debt in cli/", AM),
]


def p_upstream():
    h = 296
    b = [sheet_head("05", "UPSTREAM", "$ git log --author=Barshana24"), rule(40, 50, 960),
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


# ---------------------------------------------------------------- sheet 06

# The contribution heatmap is drawn here from cached real data rather than
# pulled from a service. Every third-party renderer for this was broken:
# github-readme-stats is deployment-paused, streak-stats returns an error card,
# and the activity graph intermittently served "Can't fetch any contribution"
# as a full-width banner. Refresh with tools/fetch_contributions.py.

CONTRIB_PATH = Path(__file__).resolve().parent / "contributions.json"

# Level ramp, teal through to the cyan accent, monotonically brighter so it reads
# as intensity. Index 0 is the empty-day colour. Level 1 is deliberately well
# clear of it: most active days sit at level 1, and a dim level 1 made the whole
# grid read as one flat block.
HEAT = ["#161d2b", "#155e70", "#1b93ab", "#22c5e0", "#7de8f7"]

MONTHS = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN",
          "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]


def load_contrib():
    try:
        return json.loads(CONTRIB_PATH.read_text(encoding="utf-8"))
    except FileNotFoundError:
        print("  ! contributions.json missing, skipping sheet 08."
              " Run tools/fetch_contributions.py first.")
        return None


CONTRIB = load_contrib()


def heat_grid(x0, y0, cell, gap, label_gap=26, month_size=8.5, min_label_px=26):
    """Draw the week-by-day heatmap. Returns (markup, width, height)."""
    pitch = cell + gap
    by_week = {}
    for d in CONTRIB["days"]:
        by_week.setdefault(d["week"], {})[d["row"]] = d
    weeks = sorted(by_week)

    out, labels = [], []
    last_month, last_x = None, -999
    for w in weeks:
        x = x0 + w * pitch
        first = min(by_week[w].values(), key=lambda d: d["date"])
        month = int(first["date"][5:7])
        if month != last_month and x - last_x >= min_label_px:
            labels.append(mono(x, y0 - 9, month_size, T5, MONTHS[month - 1], ls=1.1))
            last_x = x
        last_month = month
        for row, d in by_week[w].items():
            out.append(f'<rect x="{x}" y="{round(y0 + row * pitch, 1)}" width="{cell}" '
                       f'height="{cell}" rx="{round(cell * 0.22, 1)}" '
                       f'fill="{HEAT[min(d["level"], 4)]}"/>')

    width = len(weeks) * pitch - gap
    height = 7 * pitch - gap
    return "\n    ".join(labels + out), width, height


def contrib_stats():
    c = CONTRIB
    return [("CONTRIBUTIONS", str(c["total"]), CY),
            ("ACTIVE DAYS", str(c["active_days"]), GR),
            ("LONGEST STREAK", f"{c['longest_streak']}d", VI),
            ("BUSIEST DAY", str(c["busiest"]), AM)]


def p_contrib():
    grid, gw, gh = heat_grid(74, 102, 13, 3)
    b = [sheet_head("06", "CONTRIBUTIONS", "$ git log --since=1.year | wc -l"),
         rule(40, 50, 960),
         mono(40, 74, 9.5, T5,
              f"LAST 12 MONTHS  {DOT}  SNAPSHOT {CONTRIB['fetched']}", ls=1.5),
         grid]
    for row, day in ((1, "MON"), (3, "WED"), (5, "FRI")):
        b.append(mono(64, 102 + row * 16 + 10, 8, T6, day, anchor="end", ls=0.8))

    y = 102 + gh + 26
    b.append(rule(40, y, 960))
    for i, (label, value, col) in enumerate(contrib_stats()):
        x = 40 + i * 196
        b.append(mono(x, y + 22, 8.5, T5, label, ls=1.4))
        b.append(sans(x, y + 48, 20, T1, value, weight=700))
        b.append(f'<rect x="{x}" y="{y + 56}" width="34" height="2" rx="1" fill="{col}"/>')

    # legend, right aligned against the grid edge
    lx = 74 + gw - 5 * 15
    b.append(mono(lx - 12, y + 46, 8, T6, "LESS", anchor="end", ls=1.0))
    for i, c in enumerate(HEAT):
        b.append(f'<rect x="{lx + i * 15}" y="{y + 38}" width="11" height="11" rx="2" fill="{c}"/>')
    b.append(mono(lx + 5 * 15 + 2, y + 46, 8, T6, "MORE", ls=1.0))

    aria = (f"Contributions in the last 12 months as of {CONTRIB['fetched']}: "
            f"{CONTRIB['total']} contributions across {CONTRIB['active_days']} active days, "
            f"longest streak {CONTRIB['longest_streak']} days, busiest day "
            f"{CONTRIB['busiest']} contributions.")
    return Panel("con", y + 76, "\n    ".join(b), aria,
                 glow=(880, -20, 380, 150, CY, 0.11))


# ---------------------------------------------------------------- sheet 07

BLOCK = [
    [("DRAWN BY", "BARSHANA CHATTERJEE"), ("LOCATION", "KOLKATA, IN"), ("SHEETS", "07")],
    [("DISCIPLINE", "AI SYSTEMS / RF"), ("STATUS", "OPEN TO COLLABORATION"), ("REVISION", "05")],
]


def p_titleblock():
    h = 176
    b = [sheet_head("07", "TITLE BLOCK", "$ contact --print")]
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


# ================================================================ narrow set
# Same content and palette, laid out in a single column on a 480 canvas. Two
# column blocks stack, and the pipeline runs top to bottom instead of left to
# right, because five boxes side by side at phone width is unreadable.


def n_head(num, name, cmd=None):
    return sheet_head(num, name, cmd, y=30, w=NW, x=NM, size=8.5, ls=1.6)


def n_header():
    b = [n_head("01", "IDENTITY"),
         # right-anchored short of the margin so it clears the corner bracket
         mono(NW - 42, 30, 8.5, T4, "@Barshana24", anchor="end"),
         sans(NM, 74, 24, T1, "BARSHANA", weight=700, ls=0.4),
         sans(NM, 104, 24, T1, "CHATTERJEE", weight=700, ls=0.4),
         '<g stroke="#243044" stroke-width="1">'
         f'<path d="M{NM} 120h150"/><path d="M{NM} 115v10"/><path d="M{NM + 150} 115v10"/></g>']
    tag, y = lines(NM, 148, 12, T3,
                   "I build things that put AI to work on real data, usually on a local model.",
                   NI, 19)
    b.append(tag)
    b.append(mono(NM, y + 14, 8.5, T4, f"PYTHON {DOT} TYPESCRIPT {DOT} FASTAPI", ls=1.0))
    b.append(mono(NM, y + 30, 8.5, T4, f"OLLAMA {DOT} POSTGRES {DOT} NEXT.JS", ls=1.0))
    b.append(f'<circle cx="{NM + 4}" cy="{y + 52}" r="3.2" fill="{GR}"/>')
    b.append(mono(NM + 16, y + 56, 8.5, T4, "KOLKATA, IN", ls=1.3))
    b.append(mono(NM, y + 74, 8.5, GR, "&gt; open to collaboration", ls=1.1))
    h = y + 96

    # small waveguide mark, kept as a signature but scaled to the narrow column
    vias = "".join(f'<circle cx="{x}" cy="{yy}" r="2" fill="{BG}" stroke="{CY}" '
                   f'stroke-width="0.9" opacity="0.5"/>'
                   for yy in (60, 96) for x in range(NW - 130, NW - 24, 15))
    b.append(f'<g opacity="0.85">{vias}'
             f'<path d="M{NW - 130} 78 q11 -13 22 0 q11 13 22 0 q11 -13 22 0 q11 13 22 0" '
             f'fill="none" stroke="{CY}" stroke-width="1.3" stroke-dasharray="5 8" opacity="0.8"/>'
             f'{mono(NW - 130, 116, 7.5, T6, "SIW / TE10", ls=1.3)}</g>')

    aria = ("Barshana Chatterjee, at Barshana24, Kolkata India. I build things that put AI "
            "to work on real data, usually on a local model. Open to collaboration.")
    return Panel("nhdr", h, "\n    ".join(b), aria, w=NW, major_grid=True,
                 glow=(NW - 40, 20, 200, 150, CY, 0.16), corner_marks=True)


def n_stack():
    b = [n_head("02", "SYSTEMS MAP", "$ stack -w"), rule(NM, 44, NW - NM)]
    y = 68
    for title, items in (("LANGUAGES", LANGS), ("RUNTIME / DATA", RUNTIME)):
        b.append(mono(NM, y, 8.5, "#5a6472", title, ls=1.6))
        y += 24
        for nm, val, color in items:
            b.append(f'<circle cx="{NM + 4}" cy="{y - 4}" r="3.2" fill="{color}"/>')
            b.append(sans(NM + 16, y, 11, T2, esc(nm)))
            b.append(mono(NW - NM, y, 8.5, T4, str(val), anchor="end"))
            b.append(f'<rect x="{NM}" y="{y + 8}" width="{NI}" height="4" rx="2" fill="{INSET}"/>')
            b.append(f'<rect x="{NM}" y="{y + 8}" width="{round(NI * val / 100)}" height="4" '
                     f'rx="2" fill="{color}"/>')
            y += 32
        y += 10

    b.append(rule(NM, y - 4, NW - NM))
    note, y = lines(NM, y + 18, 8.5, T5,
                    f"ALSO  {DOT}  CHROME EXTENSIONS  {DOT}  CANVAS 2D  {DOT}  "
                    f"PDF REPORT PIPELINES  {DOT}  CISCO PACKET TRACER",
                    NI, 14, is_mono=True, ls=1.2)
    b.append(note)
    aria = ("Systems map, weighted by use. Languages: "
            + ", ".join(f"{n} {v}" for n, v, _ in LANGS)
            + ". Runtime and data: " + ", ".join(f"{n} {v}" for n, v, _ in RUNTIME) + ".")
    return Panel("nstk", int(y + 8), "\n    ".join(b), aria, w=NW,
                 glow=(NW // 2, NW, 260, 120, CY, 0.11))


def n_pipeline():
    b = [n_head("03", "PIPELINE", "$ trace"), rule(NM, 44, NW - NM),
         mono(NM, 66, 8.5, T5, "HOW A PROJECT GETS BUILT, TOP TO BOTTOM", ls=1.3)]
    y, bh, g = 84, 52, 22
    for i, (num, nm, tech, hero) in enumerate(STAGES):
        b.append(f'<rect x="{NM}" y="{y}" width="{NI}" height="{bh}" rx="9" '
                 f'fill="{CARD_BG}" stroke="{VI if hero else BORDER}"/>')
        b.append(mono(NM + 13, y + 20, 8.5, VI if hero else CY, num, ls=1.2))
        b.append(sans(NM + 44, y + 21, 12, T1, nm, weight=600))
        b.append(mono(NM + 44, y + 39, 9, T4, tech))
        y += bh
        if i < len(STAGES) - 1:
            cx = NM + NI // 2
            b.append(f'<path d="M{cx} {y + 3}v{g - 12}" stroke="#2b3a52" stroke-width="1"/>')
            b.append(f'<path d="M{cx - 3.5} {y + g - 9}l3.5 6l3.5 -6z" fill="#3d4f6b"/>')
            y += g

    b.append(rule(NM, y + 18, NW - NM))
    b.append(f'<circle cx="{NM + 4}" cy="{y + 40}" r="3.2" fill="{GR}"/>')
    note, y2 = lines(NM + 16, y + 44, 8.5, GR,
                     f"STEP 03 RUNS LOCALLY  {DOT}  NO KEYS, NO DATA LEAVING THE BOX",
                     NI - 16, 14, is_mono=True, ls=1.2)
    b.append(note)
    aria = ("Pipeline, how a project gets built: "
            + ", then ".join(f"{n} using {t}" for _, n, t, _ in STAGES)
            + ". Step 03 runs locally, so no keys and no data leave the box.")
    return Panel("npip", int(y2 + 8), "\n    ".join(b), aria, w=NW,
                 glow=(NW // 2, -20, 240, 130, VI, 0.10))


def n_work():
    b = [n_head("04", "WORK MANIFEST", "$ ls --selected"), rule(NM, 44, NW - NM),
         mono(NM, 66, 8.5, T5, f"SIX OF FOURTEEN REPOS  {DOT}  LINKS BELOW", ls=1.3)]
    return Panel("nwrk", 84, "\n    ".join(b),
                 "Work manifest. Six selected projects of fourteen public repositories.",
                 w=NW)


NCARD_W = NI
NCARD_GAP = 16


class NarrowCardGrid(Panel):
    """Project cards in one column, sized so the body copy stays readable."""

    def __init__(self):
        self.layouts = []
        y = 0
        for i, c in enumerate(CARDS):
            body, end = self._card(c, i)
            self.layouts.append((y, body))
            y += end + NCARD_GAP
        aria = " ".join(f"{c['slug']}, {c['lang']}. " + " ".join(c["desc"]) for c in CARDS)
        super().__init__("ngrid", y - NCARD_GAP, "", aria, w=NW)

    def _card(self, c, i):
        w, u = NCARD_W, f"ncd{i}"
        b = [sans(20, 30, 13, T1, esc(c["slug"]), weight=700),
             f'<rect x="20" y="38" width="24" height="2" rx="1" fill="{c["color"]}" opacity="0.6"/>',
             mono(w - 26, 29, 8.5, T4, c["lang"], anchor="end"),
             f'<circle cx="{w - 16}" cy="26" r="3.2" fill="{c["color"]}"/>']
        desc, y = lines(20, 60, 10.5, T3, " ".join(c["desc"]), w - 44, 17)
        b.append(desc)
        b.append(rule(20, y + 4, w - 20))
        b.append(mono(20, y + 22, 8, T5, f"  {DOT}  ".join(c["meta"]), ls=1.1))
        h = int(y + 34)
        chrome = [f'<rect x="0" y="0" width="{w}" height="{h}" rx="11" fill="{CARD_BG}"/>',
                  f'<g clip-path="url(#c{u})">',
                  f'  <rect width="{w}" height="{h}" fill="url(#gf)"/>',
                  f'  <rect x="0" y="0" width="3" height="{h}" fill="{c["color"]}" opacity="0.85"/>',
                  f'  <rect x="0" y="{h - 2}" width="{w}" height="2" fill="url(#h{u})"/>',
                  '</g>',
                  f'<rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="11" '
                  f'fill="none" stroke="{BORDER}"/>']
        self._heights = getattr(self, "_heights", {})
        self._heights[i] = h
        return "\n      ".join(chrome + b), h

    def defs(self):
        d = []
        for i, c in enumerate(CARDS):
            h = self._heights[i]
            d.append(f'<clipPath id="cncd{i}"><rect x="0" y="0" width="{NCARD_W}" '
                     f'height="{h}" rx="11"/></clipPath>')
            d.append(f'<linearGradient id="hncd{i}" x1="0" y1="0" x2="1" y2="0">'
                     f'<stop offset="0%" stop-color="{c["color"]}" stop-opacity="0.75"/>'
                     f'<stop offset="100%" stop-color="{c["color"]}" stop-opacity="0"/>'
                     f'</linearGradient>')
        return d

    def render(self, y):
        out = [f'  <g transform="translate({NM} {y})">']
        for cy, body in self.layouts:
            out.append(f'    <g transform="translate(0 {cy})">\n      {body}\n    </g>')
        out.append("  </g>\n")
        return "\n".join(out)


def n_upstream():
    b = [n_head("05", "UPSTREAM", "$ git log"), rule(NM, 44, NW - NM)]
    body, y = lines(NM, 70, 11.5, T2,
                    "AOBench is a role-aware, permission-enforced benchmark for AI agents "
                    "that operate HPC systems: SLURM, telemetry, RBAC. I work on its CLI.",
                    NI, 18)
    b.append(body)
    y += 18
    b.append(mono(NM, y, 8.5, T5, "PULL REQUESTS AUTHORED", ls=1.5))
    y += 22
    for num, title, col in PRS:
        b.append(f'<circle cx="{NM + 4}" cy="{y - 4}" r="3.2" fill="{col}"/>')
        b.append(mono(NM + 16, y, 9.5, col, f"#{num}"))
        t, y = lines(NM + 52, y, 10.5, T2, title, NI - 52, 16)
        b.append(t)
        y += 10
    b.append(mono(NM, y + 8, 8, T5, "88 TASKS / 29 ENVIRONMENTS", ls=1.2))
    aria = ("Upstream. AOBench is a role-aware, permission-enforced benchmark for AI agents "
            "that operate HPC systems. I work on its command line interface. Pull requests "
            "authored: " + "; ".join(f"{n}, {t}" for n, t, _ in PRS) + ".")
    return Panel("nups", int(y + 26), "\n    ".join(b), aria, w=NW,
                 glow=(NW - 40, NW, 220, 130, GR, 0.10))


def n_contrib():
    # Cells shrink to fit 53 weeks into the narrow column. Day-of-week labels are
    # dropped; at this size they cost more room than they explain.
    grid, gw, gh = heat_grid(NM + 2, 96, 5.5, 1.4, month_size=7.5, min_label_px=30)
    b = [n_head("06", "CONTRIBUTIONS", "$ git log -1y"), rule(NM, 44, NW - NM),
         mono(NM, 66, 8, T5, f"LAST 12 MONTHS  {DOT}  {CONTRIB['fetched']}", ls=1.2),
         grid]

    y = 96 + gh + 20
    b.append(mono(NM, y, 8, T6, "LESS", ls=1.0))
    for i, c in enumerate(HEAT):
        b.append(f'<rect x="{NM + 34 + i * 13}" y="{y - 8}" width="10" height="10" rx="2" fill="{c}"/>')
    b.append(mono(NM + 34 + 5 * 13 + 2, y, 8, T6, "MORE", ls=1.0))

    y += 18
    b.append(rule(NM, y, NW - NM))
    cw = NI // 2
    for i, (label, value, col) in enumerate(contrib_stats()):
        x = NM + (i % 2) * cw
        ry = y + 24 + (i // 2) * 52
        b.append(mono(x, ry, 8, T5, label, ls=1.2))
        b.append(sans(x, ry + 24, 18, T1, value, weight=700))
        b.append(f'<rect x="{x}" y="{ry + 31}" width="30" height="2" rx="1" fill="{col}"/>')

    aria = (f"Contributions in the last 12 months as of {CONTRIB['fetched']}: "
            f"{CONTRIB['total']} contributions across {CONTRIB['active_days']} active days, "
            f"longest streak {CONTRIB['longest_streak']} days, busiest day "
            f"{CONTRIB['busiest']} contributions.")
    return Panel("ncon", y + 24 + 52 + 26, "\n    ".join(b), aria, w=NW,
                 glow=(NW - 40, -20, 220, 130, CY, 0.11))


def n_titleblock():
    b = [n_head("07", "TITLE BLOCK", "$ contact")]
    fields = [f for row in BLOCK for f in row]
    cw, ch = NI // 2, 40
    by = 46
    b.append(f'<rect x="{NM}" y="{by}" width="{NI}" height="{ch * 3}" rx="8" '
             f'fill="{CARD_BG}" stroke="{BORDER}"/>')
    b.append(f'<path d="M{NM + cw} {by}v{ch * 3}" stroke="{BORDER}" stroke-width="1"/>')
    for r in (1, 2):
        b.append(f'<path d="M{NM} {by + r * ch}h{NI}" stroke="{BORDER}" stroke-width="1"/>')
    order = [fields[0], fields[3], fields[1], fields[4], fields[2], fields[5]]
    for i, (label, value) in enumerate(order):
        x = NM + (i % 2) * cw + 11
        y = by + (i // 2) * ch
        b.append(mono(x, y + 15, 7, T6, label, ls=1.3))
        b.append(mono(x, y + 30, 8.5, T2, value, ls=0.4))
    aria = "Title block. " + ". ".join(f"{k}: {v}" for k, v in fields) + "."
    return Panel("nttl", by + ch * 3 + 16, "\n    ".join(b), aria, w=NW,
                 glow=(NW // 2, NW, 260, 120, VI, 0.10), corner_marks=True)


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    print("writing panels to", OUT)
    # Two files, split only where the README needs real HTML links in between.
    # Every extra file is another request against the rate limit described in
    # the module docstring, so resist adding more.
    compose("sheet-1.svg", [p_header(), p_stack(), p_pipeline()],
            title="Barshana Chatterjee")
    compose("sheet-2.svg", [p_work(), CardGrid(), p_upstream()] +
            ([p_contrib()] if CONTRIB else []) + [p_titleblock()],
            title="Work, upstream, contributions, contact")
    # Phone variants, selected by the <picture> media query in the README.
    compose("sheet-1-sm.svg", [n_header(), n_stack(), n_pipeline()],
            gap=16, title="Barshana Chatterjee")
    compose("sheet-2-sm.svg", [n_work(), NarrowCardGrid(), n_upstream()] +
            ([n_contrib()] if CONTRIB else []) + [n_titleblock()],
            gap=16, title="Work, upstream, contributions, contact")
    print("done")
