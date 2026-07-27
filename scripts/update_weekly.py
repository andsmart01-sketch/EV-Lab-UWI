"""
Weekly data updater for Jamaica EV Dashboard.
Run every Wednesday after Petrojam publishes new prices.

Usage:
    python scripts/update_weekly.py

Requirements:
    pip install playwright requests
    playwright install chromium
"""

import json
import os
import sys
import csv
import requests
from datetime import datetime
from pathlib import Path

# Paths
REPO_ROOT   = Path(__file__).resolve().parent.parent
DATA_DIR    = REPO_ROOT / "data"
RAW_DIR     = DATA_DIR / "raw"
CONFIG_FILE = DATA_DIR / "live_config.json"

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
    print("Fetching USD/JMD exchange rate...")
    try:
        r = requests.get("https://open.er-api.com/v6/latest/USD", timeout=10)
        r.raise_for_status()
        data = r.json()
        rate = data["rates"]["JMD"]
        updated = data["time_last_update_utc"]
        print(f"  USD/JMD = {rate:.4f}  (as of {updated})")
        return rate, updated
    except Exception as e:
        print(f"  WARNING: Exchange rate fetch failed ({e}). Using existing value.")
        return None, None


# ── 2. Petrojam scrape ───────────────────────────────────────────

def scrape_petrojam():
    print("Launching headless browser to scrape Petrojam...")
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        sys.exit(
            "ERROR: Playwright not installed.\n"
            "Run: pip install playwright && playwright install chromium"
        )

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled"]
        )
        context = browser.new_context(
            ignore_https_errors=True,
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            extra_http_headers={
                "Accept-Language": "en-US,en;q=0.9",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            }
        )
        page = context.new_page()
        page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        # Step 1: go to the Prices listing page to find the latest week's URL
        print("  Finding latest price page...")
        page.goto("https://www.petrojam.com/price/", timeout=30000)
        page.wait_for_timeout(3000)

        # Find the first article/post link on the listing page
        latest_link = None
        for selector in ["article a", ".entry-title a", "h2 a", "h3 a", ".post a"]:
            el = page.query_selector(selector)
            if el:
                latest_link = el.get_attribute("href")
                break

        if not latest_link:
            # Fall back to direct URL pattern — try to find any link containing "petroleum-product-prices"
            links = page.query_selector_all("a[href*='petroleum-product-prices']")
            if links:
                latest_link = links[0].get_attribute("href")

        if not latest_link:
            browser.close()
            print("  WARNING: Could not find latest price page link on petrojam.com/price/")
            return None

        print(f"  Latest price page: {latest_link}")

        # Step 2: navigate to the latest price page
        page.goto(latest_link, timeout=30000)
        page.wait_for_timeout(3000)
        body_text = page.inner_text("body")
        browser.close()

    # Step 3: parse the page text
    # Expected format lines like:
    #   "Date: Wednesday, July 22, 2026"
    #   "E10 87: 204.4028"
    #   "E10 90: 213.2687"
    #   "Auto Diesel: 171.xxxx"  (or similar label)
    import re

    result = {}

    # Date
    date_match = re.search(r"Date[:\s]+(\w+ \d+,?\s+\d{4})", body_text)
    if date_match:
        result["date"] = date_match.group(1).strip()
    else:
        result["date"] = datetime.today().strftime("%B %d, %Y")
        print("  WARNING: Could not parse date from page. Using today.")

    # G87 pump price — last number on the "E10 87" line
    g87_match = re.search(r"E10\s*87\s*:\s*([\d.]+)", body_text)
    if g87_match:
        result["g87"] = g87_match.group(1)
    else:
        print("  WARNING: Could not find E10 87 price.")
        return None

    # G90 pump price
    g90_match = re.search(r"E10\s*90\s*:\s*([\d.]+)", body_text)
    if g90_match:
        result["g90"] = g90_match.group(1)
    else:
        print("  WARNING: Could not find E10 90 price.")
        return None

    # Diesel pump price — try several label variants
    diesel_match = re.search(
        r"(?:Auto Diesel|Diesel|Automotive Diesel)[^:]*:\s*([\d.]+)",
        body_text, re.IGNORECASE
    )
    if diesel_match:
        result["diesel"] = diesel_match.group(1)
    else:
        print("  WARNING: Could not find Diesel price.")
        return None

    print(f"  Date:    {result['date']}")
    print(f"  87:      J${result['g87']}/L")
    print(f"  90:      J${result['g90']}/L")
    print(f"  Diesel:  J${result['diesel']}/L")

    return [None, None], result  # match expected return shape


def parse_petrojam_row(headers, data_row):
    """
    Map the raw Petrojam columns to our CSV schema:
    Date, Gasolene 87, Gasolene 90, Auto Diesel
    Returns a dict or None if parsing fails.
    """
    result = {}

    # Flexible column matching
    col_map = {
        "date":      ["date", "week", "effective"],
        "g87":       ["87", "gasolene 87", "super"],
        "g90":       ["90", "gasolene 90", "premium"],
        "diesel":    ["diesel", "auto diesel"],
    }

    for key, aliases in col_map.items():
        for i, h in enumerate(headers):
            if any(alias in h.lower() for alias in aliases) and i < len(data_row):
                result[key] = data_row[i].replace(",", "").strip()
                break

    if not all(k in result for k in ["date", "g87", "g90", "diesel"]):
        print(f"  WARNING: Could not map all columns. Got: {result}")
        return None

    # Parse date — Petrojam often uses formats like "July 23, 2026" or "23-Jul-26"
    raw_date = result["date"]
    for fmt in ["%B %d, %Y", "%d-%b-%y", "%d-%b-%Y", "%Y-%m-%d", "%d/%m/%Y"]:
        try:
            parsed = datetime.strptime(raw_date, fmt)
            result["date_parsed"] = parsed.strftime("%Y-%m-%d")
            break
        except ValueError:
            continue
    else:
        # Use today as fallback
        result["date_parsed"] = datetime.today().strftime("%Y-%m-%d")
        print(f"  WARNING: Could not parse date '{raw_date}'. Using today's date.")

    return result


# ── 3. Append to CSV ─────────────────────────────────────────────

def update_csv(csv_path, parsed):
    """Append a new row to the xlsx if the date is not already present."""
    import openpyxl
    # Support both old and new key names
    if "date_parsed" in parsed:
        date_str = parsed["date_parsed"]
    elif "date" in parsed:
        raw = parsed["date"]
        date_str = raw
        for fmt in ["%B %d, %Y", "%B %d %Y", "%d-%b-%y", "%d-%b-%Y", "%Y-%m-%d"]:
            try:
                from datetime import datetime as _dt
                date_str = _dt.strptime(raw, fmt).strftime("%Y-%m-%d")
                break
            except ValueError:
                continue
    else:
        sys.exit("ERROR: parsed dict has no date key")

    wb = openpyxl.load_workbook(csv_path)
    ws = wb.active

    # Read header row to find column positions
    headers = [cell.value for cell in ws[1]]

    # Map our keys to column indices (1-based)
    col_date    = next((i+1 for i, h in enumerate(headers) if h and "date" in str(h).lower()), None)
    col_g87     = next((i+1 for i, h in enumerate(headers) if h and "87" in str(h)), None)
    col_g90     = next((i+1 for i, h in enumerate(headers) if h and "90" in str(h)), None)
    col_diesel  = next((i+1 for i, h in enumerate(headers) if h and "diesel" in str(h).lower()), None)

    if not all([col_date, col_g87, col_g90, col_diesel]):
        print(f"  WARNING: Could not map all columns. Headers found: {headers}")
        return False

    # Check for duplicate date
    for row in ws.iter_rows(min_row=2, values_only=True):
        existing_date = row[col_date - 1]
        if existing_date and str(existing_date).strip() == date_str:
            print(f"  xlsx already has an entry for {date_str}. No new row added.")
            return False

    # Append new row in correct column order
    new_row = [""] * len(headers)
    new_row[col_date   - 1] = date_str
    new_row[col_g87    - 1] = float(parsed["g87"])
    new_row[col_g90    - 1] = float(parsed["g90"])
    new_row[col_diesel - 1] = float(parsed["diesel"])

    ws.append(new_row)
    wb.save(csv_path)
    print(f"  Appended row to {csv_path.name}: {date_str} | 87={parsed['g87']} | 90={parsed['g90']} | Diesel={parsed['diesel']}")
    return True


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
        config["petrojam_last_date"] = petrojam_date

    config["script_last_run"] = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)
    print(f"  Config written to {CONFIG_FILE}")


# ── Main ─────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 55)
    print("Jamaica EV Dashboard — Weekly Data Updater")
    print(f"Running at {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}")
    print("=" * 55)

    # Exchange rate
    rate, rate_updated = fetch_exchange_rate()

    # Petrojam
    csv_path = find_csv()
    print(f"\nFuel price CSV: {csv_path.name}")
    result = scrape_petrojam()
    petrojam_date = None

    if result:
        _, parsed = result
        if parsed:
            added = update_csv(csv_path, parsed)
            petrojam_date = parsed.get("date_parsed") or parsed.get("date")
            if added:
                print(f"\nNew Petrojam prices for {petrojam_date}:")
                print(f"  87-octane:  J${parsed['g87']}/L")
                print(f"  90-octane:  J${parsed['g90']}/L")
                print(f"  Diesel:     J${parsed['diesel']}/L")
        else:
            print("  Petrojam data could not be parsed. CSV unchanged.")
    else:
        print("  Petrojam scrape failed. CSV unchanged.")
        print("  Manual fallback: visit https://www.petrojam.com/price/")
        print("  and add a row to", csv_path.name)

    # Config
    print("\nWriting live config...")
    update_config(rate, rate_updated, petrojam_date)

    print("\nDone.")
    print("Restart the dashboard to load the updated prices and exchange rate.")
