import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data" / "processed"

def load_fuel_prices():
    df = pd.read_csv(DATA_DIR / "fuel_prices.csv", parse_dates=["Date"])
    df = df.sort_values("Date").reset_index(drop=True)
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