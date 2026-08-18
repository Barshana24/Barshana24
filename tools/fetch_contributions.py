#!/usr/bin/env python3
"""Fetch the public contribution calendar and cache it for build_panels.py.

    python tools/fetch_contributions.py

Writes tools/contributions.json. Re-run it whenever you want the contributions
sheet to catch up, then re-run build_panels.py.

Why scrape instead of using the API: the contributions calendar is only exposed
through GraphQL, which needs an authenticated token. The same numbers are public
at /users/<login>/contributions, which needs no credentials at all.

The panel this feeds is a snapshot and says so on its face. That is deliberate.
Every third-party service that renders this live was either paused or returning
an error card, and a stale-but-correct number beats a broken banner.
"""

import json
import re
import urllib.request
from datetime import date
from pathlib import Path

LOGIN = "Barshana24"
HERE = Path(__file__).resolve().parent
OUT = HERE / "contributions.json"

URL = f"https://github.com/users/{LOGIN}/contributions"


def fetch(url):
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (compatible; profile-readme-build)",
        "X-Requested-With": "XMLHttpRequest",
    })
    with urllib.request.urlopen(req, timeout=45) as r:
        return r.read().decode("utf-8", "replace")


def parse(html):
    # Counts live in the tooltips, keyed to each cell by id. Attribute order on
    # the <td> is not stable, so pull each attribute out of the tag separately.
    counts = {}
    for m in re.finditer(r'<tool-tip[^>]*\bfor="([^"]+)"[^>]*>([^<]*)</tool-tip>', html):
        target, text = m.group(1), m.group(2)
        n = re.match(r"\s*(\d+)\s+contribution", text)
        counts[target] = int(n.group(1)) if n else 0

    days = []
    for tag in re.findall(r"<td[^>]*>", html):
        if "ContributionCalendar-day" not in tag:
            continue
        d = re.search(r'data-date="(\d{4}-\d{2}-\d{2})"', tag)
        if not d:
            continue
        cid = re.search(r'id="([^"]+)"', tag)
        lvl = re.search(r'data-level="(\d+)"', tag)
        pos = re.search(r"contribution-day-component-(\d+)-(\d+)", cid.group(1) if cid else "")
        days.append({
            "date": d.group(1),
            "count": counts.get(cid.group(1), 0) if cid else 0,
            "level": int(lvl.group(1)) if lvl else 0,
            "row": int(pos.group(1)) if pos else 0,
            "week": int(pos.group(2)) if pos else 0,
        })

    days.sort(key=lambda x: x["date"])
    return days


def streaks(days):
    """Longest run of consecutive days with at least one contribution."""
    best = run = 0
    for d in days:
        run = run + 1 if d["count"] > 0 else 0
        best = max(best, run)
    return best


def main():
    days = parse(fetch(URL))
    if not days:
        raise SystemExit("no day cells parsed; the calendar markup may have changed")

    active = [d for d in days if d["count"] > 0]
    payload = {
        "login": LOGIN,
        "fetched": date.today().isoformat(),
        "first": days[0]["date"],
        "last": days[-1]["date"],
        "total": sum(d["count"] for d in days),
        "active_days": len(active),
        "longest_streak": streaks(days),
        "busiest": max(d["count"] for d in days),
        "weeks": max(d["week"] for d in days) + 1,
        "days": [{k: d[k] for k in ("date", "count", "level", "row", "week")} for d in days],
    }
    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(payload, indent=1) + "\n")
    print(f"wrote {OUT.name}: {payload['total']} contributions across "
          f"{len(days)} days ({payload['first']} to {payload['last']})")
    print(f"  active days {payload['active_days']}, longest streak "
          f"{payload['longest_streak']}, busiest day {payload['busiest']}")


if __name__ == "__main__":
    main()
