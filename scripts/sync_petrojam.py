"""
sync_petrojam.py — automatic weekly price sync.

Replaces the browser-based scrape in update_weekly.py. The flow is:

    1. Is this week's row already on file?  ->  stop, make zero requests
    2. GET petrojam.com/price/ via polite_fetch (cached, conditional, backoff)
    3. Parse the price TABLE by column header, not by regex over prose
    4. Keep only rows newer than what we hold
    5. Validate, back up, append, regenerate the derived CSV

Step 3 is the fix for the July 2026 corruption. The old code matched
"Diesel" in page text, which could hit any of ten diesel-like products, and
read a date that was not the price week. Reading a table by header removes
both failure modes.

Usage:
    python scripts/sync_petrojam.py            normal weekly run
    python scripts/sync_petrojam.py --force    ignore the freshness guard
    python scripts/sync_petrojam.py --dry-run  fetch and parse, write nothing
"""

from __future__ import annotations

import argparse
import shutil
import sys
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import polite_fetch
from petrojam_parser import PRICE_URL, parse_price_table, rows_newer_than

REPO_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = REPO_ROOT / "data" / "raw"
OUT_CSV = REPO_ROOT / "data" / "processed" / "fuel_prices.csv"

# The dashboard reads these three. The parser captures all ten products; the
# rest are kept in the workbook only if those columns already exist.
CORE = ["Date", "Gasolene 87", "Gasolene 90", "Auto Diesel"]


def find_workbook() -> Path:
    candidates = sorted(RAW_DIR.glob("Fuel_Prices*.xlsx"))
    candidates = [c for c in candidates if "backup" not in c.name.lower()]
    if not candidates:
        sys.exit(f"ERROR: no Fuel_Prices*.xlsx in {RAW_DIR}")
    return candidates[-1]


def fetch_price_page(force: bool = False):
    """
    Try a plain HTTP GET first. The table appears to be server-rendered, so a
    browser is usually unnecessary — and a plain GET can be cached and made
    conditional, which a browser session cannot.

    Falls back to Playwright only if the table is absent, which would indicate
    the content had moved behind JavaScript.
    """
    html, source = polite_fetch.fetch(
        PRICE_URL, min_age=timedelta(hours=12), force=force
    )
    if html:
        rows, problems = parse_price_table(html)
        if rows:
            print(f"  Fetched via HTTP [{source}] — no browser needed.")
            return rows, problems

    # A robots refusal is NOT a technical failure to route around. An earlier
    # version of this function fell through to Playwright whenever the plain
    # fetch returned nothing, including when it returned nothing because
    # robots.txt said no. That made the browser path a way of ignoring a rule
    # the HTTP path had just obeyed, which is precisely the evasion this
    # project does not do. Stop here instead.
    if source.startswith("robots-blocked"):
        return [], ["The site refused our client, so no browser fallback was "
                    "attempted. Getting past this would mean disguising the "
                    "request as a browser, which this project does not do. "
                    "Run scripts/diagnose_petrojam.py, then enter prices with "
                    "scripts/add_prices.py while access is sorted out."]

    print("  Table not found in the plain response; retrying with a browser.")
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("  Playwright is not installed, so the browser fallback is "
              "unavailable. Install it only if this path is actually needed:")
        print("    pip install playwright && playwright install chromium")
        return [], ["plain GET produced no table and no browser fallback available"]

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(user_agent=polite_fetch.USER_AGENT)
        page = ctx.new_page()
        page.goto(PRICE_URL, timeout=30000)
        page.wait_for_timeout(3000)
        html = page.content()
        browser.close()
    return parse_price_table(html)


def check_page_freshness(rows: list[dict], latest_held) -> list[str]:
    """
    Warn if the page we were served looks older than what we already hold.

    On 2026-07-31 a plain fetch of /price/ returned a copy whose newest row was
    16 July, while the same page in a browser showed 30 July. That is a cached
    copy being served to non-browser clients. It matters because a stale page
    and a week with no new prices produce identical output: zero rows to add.
    One is normal, the other means the pipeline has quietly stopped working.

    Petrojam publishes weekly, so the newest row on a healthy page should never
    be more than about 8 days behind what we hold.
    """
    problems: list[str] = []
    if not rows or latest_held is None:
        return problems

    newest = rows[0]["Date"]
    if newest < latest_held:
        gap = (latest_held - newest).days
        problems.append(
            f"STALE PAGE: the newest row served was {newest}, but we already "
            f"hold {latest_held}, which is {gap} days later. This is almost "
            f"certainly a cached copy, not a real regression in the data. "
            f"Check the page in a browser before trusting this run."
        )
    return problems


def append_rows(wb: Path, new_rows: list[dict], dry_run: bool = False) -> int:
    df = pd.read_excel(wb, sheet_name=0)
    df["_d"] = pd.to_datetime(df["Date"], format="mixed", errors="coerce")
    have = set(df["_d"].dropna().dt.date)

    to_add = [r for r in new_rows if r["Date"] not in have]
    if not to_add:
        print("  Nothing new to append.")
        return 0

    for r in sorted(to_add, key=lambda x: x["Date"]):
        wd = r["Date"].strftime("%A")
        flag = "" if wd == "Thursday" else f"   <- {wd}, not the usual Thursday"
        print(f"  ADD {r['Date']}  87={r['Gasolene 87']:.4f}  "
              f"90={r['Gasolene 90']:.4f}  diesel={r['Auto Diesel']:.4f}{flag}")

    if dry_run:
        print("  Dry run: nothing written.")
        return 0

    backup = wb.with_name(f"{wb.stem}.backup-{datetime.now():%Y%m%d-%H%M%S}.xlsx")
    shutil.copy2(wb, backup)
    print(f"  Backup: {backup.name}")

    add_df = pd.DataFrame([{k: r.get(k) for k in df.columns if k != "_d"}
                           for r in to_add])
    out = pd.concat([df.drop(columns=["_d"]), add_df], ignore_index=True)
    out["_d"] = pd.to_datetime(out["Date"], format="mixed", errors="coerce")
    out = out.dropna(subset=["_d"]).sort_values("_d")
    out["Date"] = out["_d"].dt.strftime("%Y-%m-%d")
    out = out.drop(columns=["_d"])

    out.to_excel(wb, sheet_name="Fuel Prices", index=False)
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUT_CSV, index=False)
    print(f"  Workbook: {len(out)} rows. CSV regenerated.")
    return len(to_add)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    print("Petrojam price sync")
    polite_fetch.warn_if_unattributed()

    wb = find_workbook()
    latest = polite_fetch.latest_price_date(wb)
    print(f"  Workbook: {wb.name}, latest row {latest}")

    if not args.force and polite_fetch.already_have_current_week(wb):
        print("  This week's prices are already on file. "
              "Stopping without any request.")
        return

    rows, problems = fetch_price_page(force=args.force)
    for p in problems:
        print(f"  ! {p}")
    if not rows:
        print("  No rows parsed. The workbook is unchanged.")
        print(f"  Manual fallback: {PRICE_URL} then scripts/add_prices.py")
        sys.exit(1)

    print(f"  Parsed {len(rows)} rows, newest {rows[0]['Date']}")

    for warning in check_page_freshness(rows, latest):
        print(f"  ! {warning}")

    new = rows_newer_than(rows, latest)
    if not new:
        print(f"  Nothing newer than {latest} on the page.")
    append_rows(wb, new, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
