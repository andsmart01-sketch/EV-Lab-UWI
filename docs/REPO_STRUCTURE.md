# EV Lab Repository Structure
## UWI Mona EV Lab Research Project (June 8 -- August 3, 2026)

---

## Folder Map

```
ev-lab-repo/
|
|-- dashboard/               Dash 4.2.0 application
|   |-- app.py               Main entry point. Run: python dashboard/app.py
|   |-- data_loader.py       Exposes load_fuel_prices() and get_latest_prices()
|
|-- data/
|   |-- raw/                 Original source files (gitignored for large files)
|   |-- processed/           Cleaned datasets ready for dashboard consumption
|   |-- vehicles.py          Vehicle database: 10 ICE, 10 BEV models
|   |-- process_fuel_prices.py  One-off processing script for Petrojam data
|
|-- docs/                    Research documentation and institutional files
|   |-- responses/           Institutional response emails (when received)
|   |-- EV_Lab_Architecture_Note.md
|   |-- ev_policy_gap_analysis.md
|   |-- EV_Lab_Supervisor_Meeting_Jun19.docx
|
|-- report/                  Formal written report (APA 7th edition)
|   |-- section_01_project_overview.md
|   |-- section_02_literature_review.md   (in progress)
|   |-- weekly/              One-page progress summary per week (separate from report)
|       |-- week_01_summary.md
|       |-- week_02_summary.md
|       |-- ...
|
|-- presentation/            Running slide deck for supervisor and final presentation
|   |-- slides/              One slide exported per week minimum
|
|-- survey/                  Survey instruments
|   |-- consumer_fuel_survey/
|   |-- juta_operator_survey/
```

---

## What Goes Where

| Content | Location |
|---------|----------|
| Dashboard Python code | dashboard/ |
| Raw data files from institutions | data/raw/ |
| Cleaned, processed data ready for dashboard | data/processed/ |
| Vehicle specs and prices | data/vehicles.py |
| Architecture decisions | docs/ |
| Emails received from institutions | docs/responses/ |
| Formal report sections (APA 7th) | report/section_XX_*.md |
| Weekly one-page progress summaries | report/weekly/week_XX_summary.md |
| Supervisor presentation slides | presentation/slides/ |
| Survey question text and form links | survey/ |

---

## Key Rules

- The weekly summaries in report/weekly/ are NOT part of the formal report.
  They are informal progress logs for supervisor communication.
- The formal report sections in report/ will be compiled into the final
  submission document at the end of Week 8.
- Raw data files should be gitignored unless small and non-confidential.
- All institutional response emails should be saved to docs/responses/ on receipt.
- Dashboard-to-poster exports go to a dedicated exports/ subfolder when that
  feature is built (Week 6 target).

---

## Running the Dashboard

```bash
# In CMD terminal (not PowerShell)
conda activate EVlab
cd C:\Users\Andrew Smart\ev-lab-repo
python dashboard/app.py
# Open http://localhost:8050
```

**Import rule in app.py:** use `from data_loader import ...`
not `from dashboard.data_loader import ...`
Running `python dashboard/app.py` adds dashboard/ to Python's path directly.
