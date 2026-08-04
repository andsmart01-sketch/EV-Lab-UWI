"""
Weekly data updater for Jamaica EV Dashboard.

Run Thursday evening, after Petrojam publishes. Thursday is not a guess: of
the 602 rows in the price series, 581 are dated on a Thursday, and every row
from April to June 2026 is.

Usage:
    python scripts/update_weekly.py            normal weekly run
    python scripts/update_weekly.py --force    ignore the freshness guard

Requirements:
    pip install requests beautifulsoup4 lxml pandas openpyxl

Playwright is NOT required. The price table on petrojam.com/price/ is served
in the HTML, so a plain GET is enough. Playwright is used only as a fallback
if that table ever disappears from the raw response, and the script degrades
to a clear message rather than an exception if it is not installed.
"""

import json
import os
import sys
import csv
from datetime import datetime, timedelta
from pathlib import Path

# Shared polite HTTP layer: caching, conditional requests, backoff, and an
# honest User-Agent. See scripts/polite_fetch.py for why this exists.
sys.path.insert(0, str(Path(__file__).resolve().parent))
import polite_fetch

# Paths
REPO_ROOT   = Path(__file__).resolve().parent.parent
DATA_DIR    = REPO_ROOT / "data"
RAW_DIR     = DATA_DIR / "raw"
CONFIG_FILE = DATA_DIR / "live_config.json"
# The freshness guard must check the SAME file the dashboard reads, which is
# the .xlsx in data/raw. The derived .csv lags whenever process_fuel_prices.py
# has not been rerun, which would cause a needless scrape.
PRICES_CSV  = DATA_DIR / "processed" / "fuel_prices.csv"   # derived output

def find_csv():
    # Check raw/ subfolder first, then data/ root
    candidates = sorted((DATA_DIR / "raw").glob("Fuel_Prices*.xlsx"))
    if not candidates:
        candidates = sorted(DATA_DIR.glob("Fuel_Prices*.xlsx"))
    if not candidates:
        sys.exit("ERROR: No Fuel_Prices .xlsx found in data/raw/ or data/")
    return candidates[-1]


# ── 1. Exchange rate ──────────────────────────────────────────────

def fetch_exchange_rate():
    """
    Fetched through polite_fetch, so a rerun within 12 hours costs no request
    at all and a failure falls back to the last good cached copy rather than
    hammering the endpoint.
    """
    print("Fetching USD/JMD exchange rate...")
    body, source = polite_fetch.fetch(
        "https://open.er-api.com/v6/latest/USD",
        min_age=timedelta(hours=12),
    )
    if body is None:
        print("  WARNING: Exchange rate unavailable. Using existing value.")
        return None, None
    try:
        data = json.loads(body)
        rate = data["rates"]["JMD"]
        updated = data["time_last_update_utc"]
        print(f"  USD/JMD = {rate:.4f}  (as of {updated})  [{source}]")
        return rate, updated
    except Exception as e:
        print(f"  WARNING: Could not parse exchange rate ({e}). Using existing value.")
        return None, None


# ── 2. Petrojam scrape ───────────────────────────────────────────

# ── 2. Petrojam prices ───────────────────────────────────────────
#
# This used to drive a headless browser to the /price/ listing, follow the
# first article link to an individual post, and run "Label: value" regexes over
# the prose on that post. It produced two corrupt rows in July 2026: 87 and 90
# octane were exactly right, but the dates were 6 to 8 days out and diesel was
# low by about J$57.50 every week. A regex for "Diesel" over prose can match
# any of several diesel products, and the date it finds may be a publication
# date rather than the price week.
#
# The work now lives in sync_petrojam.py, which reads the HTML TABLE on
# /price/ by column header. That removes both failure modes: the header says
# which number is Auto Diesel, and the date is its own column.

def sync_petrojam_prices(force=False):
    """
    Bring the local price series up to date. Returns the newest date now held,
    or None if nothing changed. Makes zero requests when this week's row is
    already on file.
    """
    import sync_petrojam as sp

    wb = sp.find_workbook()
    latest = polite_fetch.latest_price_date(wb)
    print(f"  Workbook: {wb.name}, latest row {latest}")

    if not force and polite_fetch.already_have_current_week(wb):
        print("  This week's prices are already on file. "
              "Skipping entirely (0 requests). Use --force to fetch anyway.")
        return latest

    rows, problems = sp.fetch_price_page(force=force)
    for prob in problems:
        print(f"  ! {prob}")

    if not rows:
        print("  No rows parsed, so the series is unchanged.")
        print("  Manual fallback: https://www.petrojam.com/price/ then")
        print("                   python scripts/add_prices.py")
        return latest

    print(f"  Parsed {len(rows)} rows from the table, newest {rows[0]['Date']}")
    added = sp.append_rows(wb, sp.rows_newer_than(rows, latest))
    return polite_fetch.latest_price_date(wb) if added else latest



# ── 4. Write live config ─────────────────────────────────────────

def update_config(rate, rate_updated, petrojam_date):
    config = {}
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE) as f:
                config = json.load(f)
        except Exception:
            pass

    if rate is not None:
        config["usd_to_jmd"]         = round(rate, 4)
        config["rate_updated_utc"]   = rate_updated
    if petrojam_date:
        # sync_petrojam_prices returns a datetime.date, which json cannot
        # serialise. Normalise to an ISO string before writing.
        config["petrojam_last_date"] = (
            petrojam_date.isoformat()
            if hasattr(petrojam_date, "isoformat") else str(petrojam_date)
        )

    config["script_last_run"] = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)
    print(f"  Config written to {CONFIG_FILE}")


# ── Main ─────────────────────────────────────────────────────────

if __name__ == "__main__":
    force = "--force" in sys.argv

    print("=" * 55)
    print("Jamaica EV Dashboard — Weekly Data Updater")
    print(f"Running at {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}")
    print("=" * 55)

    # Warn once if the scraper is running without a contact address.
    polite_fetch.warn_if_unattributed()

    # Exchange rate
    rate, rate_updated = fetch_exchange_rate()

    # Petrojam
    print("\nPetrojam fuel prices")
    petrojam_date = sync_petrojam_prices(force=force)

    # Config
    print("\nWriting live config...")
    update_config(rate, rate_updated, petrojam_date)

    print("\nDone.")
    print("Restart the dashboard to load the updated prices and exchange rate.")
