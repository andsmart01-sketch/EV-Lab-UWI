"""
petrojam_parser.py — parse the Petrojam price table.

WHY THIS REPLACES THE OLD SCRAPER
---------------------------------
The previous approach navigated to petrojam.com/price/, followed the first
article link to an individual "PETROLEUM PRODUCT PRICES" post, and ran regexes
of the form  Label: value  over the page text. It produced two corrupt rows in
July 2026: the 87 and 90 octane figures were exactly right, but the dates were
wrong by 6 to 8 days and the diesel figure was low by about J$57.50 every time.

Both failures have the same root cause. The post pages are prose, so a regex
matching "Diesel" can hit any of several diesel-like products, and the date it
finds may be a publication date rather than the price week.

The listing page at /price/ carries a proper HTML table with a header row and
one row per week, covering ten products. Parsing that table by COLUMN HEADER
removes the entire class of bug: there is no ambiguity about which number is
Auto Diesel because the header says so, and no ambiguity about the date
because it is its own column.

DESIGN NOTES
------------
* Columns are located by header text, never by position. If Petrojam inserts a
  product column the parser keeps working.
* Every row is validated. A row with an unparseable date or an implausible
  price is rejected and reported, never written.
* All ten products are captured, not just the three the dashboard currently
  uses. They cost nothing extra and Kerosene, Propane, HFO and ULSD are all
  plausibly useful later.
* The table appears to be server-rendered, so a plain HTTP GET should work and
  a browser is only a fallback.
"""

from __future__ import annotations

import re
from datetime import datetime

from bs4 import BeautifulSoup

PRICE_URL = "https://www.petrojam.com/price/"

# Canonical name -> substrings that identify that column in the header row.
# Matching is done on a whitespace-normalised, lowercased header.
COLUMN_ALIASES = {
    "Date":        ["date"],
    "Gasolene 87": ["gasolene 87", "gasoline 87", "e10 87", "87"],
    "Gasolene 90": ["gasolene 90", "gasoline 90", "e10 90", "90"],
    "Auto Diesel": ["auto diesel", "automotive diesel"],
    "Kerosene":    ["kerosene"],
    "Propane":     ["propane"],
    "Butane":      ["butane"],
    "HFO":         ["hfo", "heavy fuel"],
    "Asphalt":     ["asphalt"],
    "ULSD":        ["ulsd", "ultra low sulphur", "ultra-low sulfur"],
}

# The three the dashboard needs. Everything else is a bonus.
REQUIRED = ["Date", "Gasolene 87", "Gasolene 90", "Auto Diesel"]

PRICE_MIN, PRICE_MAX = 20.0, 500.0   # J$/L; propane sits near 80, ULSD near 250

DATE_FORMATS = ["%B %d, %Y", "%b %d, %Y", "%Y-%m-%d", "%d/%m/%Y"]


def _norm(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "")).strip().lower()


def _match_column(header: str) -> str | None:
    """
    Map one header cell to a canonical column name.

    Order matters: 'auto diesel' is tested before the bare '87'/'90' aliases so
    that a header like 'Auto Diesel' can never be captured by a looser rule.
    Longer aliases are tried first for the same reason.
    """
    h = _norm(header)
    if not h:
        return None
    best, best_len = None, 0
    for canonical, aliases in COLUMN_ALIASES.items():
        for alias in aliases:
            if alias in h and len(alias) > best_len:
                best, best_len = canonical, len(alias)
    return best


def _parse_date(text: str):
    t = _norm(text).title().replace("Sept ", "Sep ")
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(t, fmt).date()
        except ValueError:
            continue
    return None


def parse_price_table(html: str):
    """
    Extract price rows from the Petrojam listing page.

    Returns (rows, problems) where rows is a list of dicts keyed by canonical
    column name, newest first, and problems is a list of human-readable strings
    describing anything rejected.
    """
    # lxml is faster and more forgiving of broken markup, but it needs a
    # compiled wheel and is a common install failure on Windows. Python's own
    # html.parser handles this page fine, so lxml is preferred, not required.
    try:
        soup = BeautifulSoup(html, "lxml")
    except Exception:
        soup = BeautifulSoup(html, "html.parser")

    problems: list[str] = []

    # Find the table whose header contains a Date column and at least two fuels.
    target, colmap = None, None
    for table in soup.find_all("table"):
        head = table.find("thead")
        if not head:
            continue
        headers = [c.get_text() for c in head.find_all(["th", "td"])]
        mapping = {}
        for idx, h in enumerate(headers):
            canonical = _match_column(h)
            if canonical and canonical not in mapping.values():
                mapping[idx] = canonical
        if "Date" in mapping.values() and len(mapping) >= 3:
            target, colmap = table, mapping
            break

    if target is None:
        problems.append("No price table with a recognisable header row was found. "
                        "The page layout may have changed.")
        return [], problems

    missing = [c for c in REQUIRED if c not in colmap.values()]
    if missing:
        problems.append(f"Header row is missing required columns: {missing}")
        return [], problems

    rows = []
    for body in target.find_all("tbody"):
        for tr in body.find_all("tr"):
            cells = tr.find_all("td")
            if not cells:
                continue

            record, bad = {}, None
            for idx, canonical in colmap.items():
                if idx >= len(cells):
                    continue
                raw = cells[idx].get_text()
                if canonical == "Date":
                    d = _parse_date(raw)
                    if d is None:
                        bad = f"unreadable date {_norm(raw)!r}"
                        break
                    record["Date"] = d
                else:
                    txt = _norm(raw).replace(",", "")
                    if not txt:
                        continue
                    try:
                        v = float(txt)
                    except ValueError:
                        bad = f"{canonical} not numeric: {txt!r}"
                        break
                    if not (PRICE_MIN <= v <= PRICE_MAX):
                        bad = f"{canonical}={v} outside J${PRICE_MIN:.0f}-{PRICE_MAX:.0f}"
                        break
                    record[canonical] = v

            if bad:
                problems.append(f"Row rejected ({bad})")
                continue
            if not all(k in record for k in REQUIRED):
                problems.append(f"Row rejected (missing {[k for k in REQUIRED if k not in record]})")
                continue
            rows.append(record)

    rows.sort(key=lambda r: r["Date"], reverse=True)
    return rows, problems


def rows_newer_than(rows, cutoff):
    """Only the rows strictly newer than a date already held locally."""
    if cutoff is None:
        return rows
    return [r for r in rows if r["Date"] > cutoff]
