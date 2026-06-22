# data/process_station_survey.py
# Processes weekly station survey Excel files and builds a running
# markup tracker CSV in data/processed/
#
# Usage: python data/process_station_survey.py
# Add a new weekly file to data/raw/ named station_survey_YYYY_MM_DD.xlsx
# and re-run this script to update the processed output.

import pandas as pd
from pathlib import Path
import glob

RAW_DIR       = Path("data/raw")
PROCESSED_DIR = Path("data/processed")
PETROJAM_CSV  = PROCESSED_DIR / "fuel_prices.csv"

# ── Load Petrojam reference prices ────────────────────────────────
petrojam = pd.read_csv(PETROJAM_CSV, parse_dates=["Date"])
petrojam = petrojam.sort_values("Date").reset_index(drop=True)

def get_petrojam_ref(survey_date):
    """Return the most recent Petrojam price on or before the survey date."""
    survey_date = pd.to_datetime(survey_date)
    prior = petrojam[petrojam["Date"] <= survey_date]
    if prior.empty:
        return None
    row = prior.iloc[-1]
    return {
        "petrojam_date":    row["Date"].strftime("%Y-%m-%d"),
        "petrojam_ref_87":  round(row["Gasolene 87"], 2),
        "petrojam_ref_90":  round(row["Gasolene 90"], 2),
        "petrojam_ref_diesel": round(row["Auto Diesel"], 2),
    }

# ── Process each weekly survey file ───────────────────────────────
survey_files = sorted(glob.glob(str(RAW_DIR / "station_survey_*.xlsx")))
print(f"Found {len(survey_files)} survey file(s).")

all_records = []

for filepath in survey_files:
    fname = Path(filepath).stem
    survey_date = "-".join(fname.split("_")[2:5])  # YYYY-MM-DD from filename

    df = pd.read_excel(filepath)
    df.columns = ["name", "location", "g87", "g90", "diesel"]
    df["survey_date"] = survey_date
    df["parish"] = "Kingston"
    df["brand"] = df["name"].apply(lambda x:
        "TotalEnergies" if "Total" in str(x) else
        "RUBiS"         if "RUBi"  in str(x) or "Rubis" in str(x) else
        "Texaco"        if "Texaco" in str(x) else
        "Independent"
    )

    ref = get_petrojam_ref(survey_date)
    if ref:
        df["petrojam_date"]       = ref["petrojam_date"]
        df["petrojam_ref_87"]     = ref["petrojam_ref_87"]
        df["petrojam_ref_90"]     = ref["petrojam_ref_90"]
        df["petrojam_ref_diesel"] = ref["petrojam_ref_diesel"]
        df["markup_87"]           = (df["g87"]    - ref["petrojam_ref_87"]).round(2)
        df["markup_90"]           = (df["g90"]    - ref["petrojam_ref_90"]).round(2)
        df["markup_diesel"]       = (df["diesel"] - ref["petrojam_ref_diesel"]).round(2)

    all_records.append(df)
    print(f"  Processed {fname}: {len(df)} stations, date {survey_date}")

# ── Save full station-level records ───────────────────────────────
full_df = pd.concat(all_records, ignore_index=True)
full_df.to_csv(PROCESSED_DIR / "station_surveys.csv", index=False)
print(f"\nSaved {len(full_df)} station records to data/processed/station_surveys.csv")

# ── Build weekly markup summary ────────────────────────────────────
summary = full_df.groupby("survey_date").agg(
    stations_surveyed  = ("name", "count"),
    petrojam_ref_90    = ("petrojam_ref_90", "first"),
    retail_avg_87      = ("g87",    "mean"),
    retail_avg_90      = ("g90",    "mean"),
    retail_avg_diesel  = ("diesel", "mean"),
    markup_avg_87      = ("markup_87",     "mean"),
    markup_avg_90      = ("markup_90",     "mean"),
    markup_avg_diesel  = ("markup_diesel", "mean"),
    markup_min_90      = ("markup_90",     "min"),
    markup_max_90      = ("markup_90",     "max"),
).round(2).reset_index()

summary.to_csv(PROCESSED_DIR / "markup_summary.csv", index=False)
print(f"Saved weekly markup summary to data/processed/markup_summary.csv")
print()
print("=== MARKUP SUMMARY ===")
print(summary.to_string(index=False))