import pandas as pd
from pathlib import Path

def load_fuel_prices():
    raw_dir = Path(__file__).parent.parent / "data" / "raw"
    candidates = sorted(raw_dir.glob("Fuel_Prices*.xlsx"))
    if not candidates:
        raise FileNotFoundError("No Fuel_Prices xlsx found in data/raw/")
    xlsx_path = candidates[-1]

    df = pd.read_excel(xlsx_path)
    df["Date"] = pd.to_datetime(df["Date"], format="mixed", dayfirst=False, errors="coerce")
    df = df.dropna(subset=["Date"])
    df = df.sort_values("Date").reset_index(drop=True)

    # Standardise column names in case they differ slightly
    col_map = {}
    for col in df.columns:
        low = col.lower()
        if "87" in low:
            col_map[col] = "Gasolene 87"
        elif "90" in low:
            col_map[col] = "Gasolene 90"
        elif "diesel" in low:
            col_map[col] = "Auto Diesel"
        elif "date" in low:
            col_map[col] = "Date"
    df = df.rename(columns=col_map)

    # Drop rows with no price data
    df = df.dropna(subset=["Gasolene 87", "Gasolene 90", "Auto Diesel"])
    return df

def get_latest_prices():
    df = load_fuel_prices()
    latest = df.iloc[-1]
    return {
        "date": latest["Date"].strftime("%B %d, %Y"),
        "g87": round(latest["Gasolene 87"], 2),
        "g90": round(latest["Gasolene 90"], 2),
        "diesel": round(latest["Auto Diesel"], 2),
    }


# Where the last exchange rate came from. Read this after calling
# get_live_exchange_rate() so logs and the interface can say which of the three
# paths was actually taken, rather than showing a bare number that looks
# identical whether it is today's cached rate or a hardcoded fallback.
LAST_RATE_SOURCE = "not loaded"


def get_live_exchange_rate(fallback=156.0):
    """
    USD/JMD exchange rate, in order of preference:
      1. data/live_config.json, written by scripts/update_weekly.py
      2. a live call to open.er-api.com (free, no API key)
      3. the hardcoded fallback

    Sets LAST_RATE_SOURCE so the caller can report which path was used.
    """
    global LAST_RATE_SOURCE
    import json
    from pathlib import Path

    # First try the local config written by update_weekly.py
    config_path = Path(__file__).resolve().parent.parent / "data" / "live_config.json"
    if config_path.exists():
        try:
            with open(config_path) as f:
                config = json.load(f)
            rate = config.get("usd_to_jmd")
            if rate and isinstance(rate, (int, float)) and rate > 100:
                stamp = config.get("rate_updated_utc", "date unknown")
                LAST_RATE_SOURCE = f"live_config.json, updated {stamp}"
                return float(rate)
        except Exception:
            pass

    # Fall back to live API call
    try:
        import requests
        r = requests.get("https://open.er-api.com/v6/latest/USD", timeout=5)
        r.raise_for_status()
        rate = r.json()["rates"]["JMD"]
        LAST_RATE_SOURCE = "live call to open.er-api.com"
        return float(rate)
    except Exception:
        LAST_RATE_SOURCE = (f"HARDCODED FALLBACK {fallback}. No cache and no "
                            f"network. Figures using USD are not current.")
        return fallback