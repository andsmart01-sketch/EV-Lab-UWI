import pandas as pd
from pathlib import Path

raw_path = Path("data/raw/Fuel_Prices_Sorted_Fixed.xlsx")
out_path = Path("data/processed/fuel_prices.csv")

df = pd.read_excel(raw_path, sheet_name="Fuel Prices")
df["Date"] = pd.to_datetime(df["Date"])
df = df.sort_values("Date").reset_index(drop=True)
df = df.dropna()
df.to_csv(out_path, index=False)

print(f"Saved {len(df)} rows to {out_path}")
print(f"Date range: {df['Date'].min().date()} to {df['Date'].max().date()}")