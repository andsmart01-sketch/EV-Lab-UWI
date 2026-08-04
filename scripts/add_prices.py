"""
add_prices.py — paste Petrojam price rows straight in, no scraping.

WHY
---
The scraper is a convenience, not the system of record. When it misses weeks,
or when Petrojam supplies a series by email, you need a way to enter rows by
hand that is as safe as the automated path: same validation, same duplicate
handling, same date normalisation, and a regenerated CSV at the end.

USAGE
-----
    python scripts/add_prices.py

Then paste rows and press Ctrl+Z then Enter (Windows) or Ctrl+D (macOS/Linux).

Accepted per line, in order: date, 87 octane, 90 octane, diesel.
Separators can be commas, tabs or multiple spaces. These all work:

    2026-06-18, 193.38, 200.83, 211.75
    June 18, 2026   193.38   200.83   211.75
    18/06/2026,193.38,200.83,211.75

Or non-interactively:

    python scripts/add_prices.py --file newrows.txt
    python scripts/add_prices.py --dry-run       (validate, write nothing)

WHAT IT GUARANTEES
------------------
* Dates normalised to ISO (YYYY-MM-DD), fixing the mixed formats already in
  the file.
* Duplicate dates are reported and skipped, never silently overwritten.
* Prices sanity-checked against a plausible range; anything outside it is
  refused rather than written.
* A timestamped backup of the workbook before any write.
* The derived CSV regenerated so the dashboard and the freshness guard agree.
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = REPO_ROOT / "data" / "raw"
OUT_CSV = REPO_ROOT / "data" / "processed" / "fuel_prices.csv"

COLS = ["Date", "Gasolene 87", "Gasolene 90", "Auto Diesel"]

# Refuse anything outside this band. Jamaican pump-reference prices have sat
# between roughly J$100 and J$400 for a decade; a value outside that is far
# more likely to be a typo or a misaligned column than a real price.
PRICE_MIN, PRICE_MAX = 80.0, 400.0

DATE_FORMATS = [
    "%Y-%m-%d", "%B %d, %Y", "%b %d, %Y", "%d/%m/%Y",
    "%d-%m-%Y", "%m/%d/%Y", "%d %B %Y", "%d %b %Y",
]


def find_workbook() -> Path:
    # Exclude the timestamped backups this script writes, otherwise a run
    # after several backups exist can pick up an old copy and silently undo
    # everything added since.
    candidates = [c for c in sorted(RAW_DIR.glob("Fuel_Prices*.xlsx"))
                  if "backup" not in c.name.lower()]
    if not candidates:
        sys.exit(f"ERROR: no Fuel_Prices*.xlsx in {RAW_DIR}")
    return candidates[-1]


def parse_date(token: str):
    token = token.strip().rstrip(",")
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(token, fmt).date()
        except ValueError:
            continue
    return None


def parse_line(line: str):
    """Return (date, g87, g90, diesel) or (None, reason)."""
    raw = line.strip()
    if not raw or raw.startswith("#"):
        return None, None

    # Pull the three trailing numbers; whatever precedes them is the date.
    nums = re.findall(r"-?\d+\.?\d*", raw)
    if len(nums) < 3:
        return None, "fewer than three numbers found"

    price_tokens = nums[-3:]
    cut = raw.rfind(price_tokens[0])
    date_part = raw[:cut].strip().rstrip(",;\t ")

    d = parse_date(date_part)
    if d is None:
        return None, f"could not read a date from {date_part!r}"

    try:
        vals = [float(x) for x in price_tokens]
    except ValueError:
        return None, "prices are not numeric"

    for label, v in zip(COLS[1:], vals):
        if not (PRICE_MIN <= v <= PRICE_MAX):
            return None, f"{label} = {v} is outside J${PRICE_MIN:.0f}-{PRICE_MAX:.0f}"

    return (d, *vals), None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", help="read rows from a file instead of stdin")
    ap.add_argument("--dry-run", action="store_true", help="validate only")
    args = ap.parse_args()

    wb = find_workbook()
    df = pd.read_excel(wb, sheet_name=0)
    df["_d"] = pd.to_datetime(df["Date"], format="mixed", errors="coerce")
    existing = set(df["_d"].dropna().dt.date)

    print(f"Workbook : {wb.name}")
    print(f"Existing : {len(df)} rows, latest {max(existing)}")
    print()

    if args.file:
        lines = Path(args.file).read_text().splitlines()
    else:
        print("Paste rows: date, 87, 90, diesel")
        print("Finish with Ctrl+Z then Enter (Windows) or Ctrl+D (Mac/Linux).")
        print("-" * 58)
        lines = sys.stdin.read().splitlines()

    good, skipped, bad = [], [], []
    for line in lines:
        parsed, err = parse_line(line)
        if parsed is None:
            if err:
                bad.append((line.strip(), err))
            continue
        if parsed[0] in existing:
            skipped.append(parsed[0])
            continue
        good.append(parsed)
        existing.add(parsed[0])

    print()
    for row in sorted(good):
        d, a, b, c = row
        # Petrojam publishes on Thursdays. Verified against the series: 581 of
        # 602 rows are Thursdays. An earlier version of this line said
        # Wednesday and so flagged every correct row as suspicious.
        weekday = d.strftime("%A")
        flag = "" if weekday == "Thursday" else f"   <- {weekday}, not a Thursday"
        print(f"  ADD   {d}  87={a:>9.4f}  90={b:>9.4f}  diesel={c:>9.4f}{flag}")
    for d in sorted(skipped):
        print(f"  SKIP  {d}  already present")
    for line, err in bad:
        print(f"  BAD   {line[:44]!r}: {err}")

    print()
    print(f"{len(good)} to add, {len(skipped)} duplicates, {len(bad)} rejected")

    if not good:
        print("Nothing to write.")
        return
    if args.dry_run:
        print("Dry run: nothing written.")
        return

    backup = wb.with_suffix(f".backup-{datetime.now():%Y%m%d-%H%M%S}.xlsx")
    shutil.copy2(wb, backup)
    print(f"Backup written to {backup.name}")

    new = pd.DataFrame(good, columns=["_d"] + COLS[1:])
    new["Date"] = new["_d"]
    out = pd.concat([df, new], ignore_index=True)
    out["_d"] = pd.to_datetime(out["Date"], format="mixed", errors="coerce")
    out = out.dropna(subset=["_d"]).sort_values("_d")

    # Normalise every date to ISO on the way out, which also cleans up the
    # mixed formats already in the workbook.
    out["Date"] = out["_d"].dt.strftime("%Y-%m-%d")
    out = out[COLS]
    out.to_excel(wb, sheet_name="Fuel Prices", index=False)
    print(f"Workbook updated: {len(out)} rows")

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUT_CSV, index=False)
    print(f"CSV regenerated : {OUT_CSV.relative_to(REPO_ROOT)}")
    print(f"Series now runs to {out['Date'].max()}")
    print()
    print("Restart the dashboard to pick up the new prices.")


if __name__ == "__main__":
    main()
