# Week 2 Progress Report
## EV Lab Research Project -- UWI Mona
**Period:** June 15-19, 2026
**Researcher:** Andrew Smart
**Supervisor:** Dr. Louis-Ray Harris (Rohan)

---

## What Was Done This Week

### Dashboard
- Module 1 (BEV vs ICE Calculator) built with vehicle dropdowns, purchase price and
  consumption inputs, daily km input, ownership period (1-20 years), six results cards,
  and a full TCO chart with depreciation and maintenance using plotly.graph_objects.
- Module 3 (Price Tracker) built with Plotly line chart of 600 weekly Petrojam fuel prices
  (January 2015 to June 11, 2026) across three fuel grades and a dashed reference line
  tracking the global fuel price input.
- Global sidebar converted from sliders to dcc.Input fields. 90 octane fuel price defaults
  to J$201 (real Petrojam June 11, 2026 price). Electricity rate defaults to J$50/kWh
  pending JPS data.
- Vehicle database built at data/vehicles.py with 10 ICE and 10 BEV models.

### Data
- Petrojam dataset cleaned and processed: 600 rows, January 2015 to June 2026,
  three fuel grades in J$/litre, saved to data/processed/fuel_prices.csv.
- Toyota Jamaica new vehicle prices verified from toyotajamaica.com.
- Used vehicle prices sourced from jacars.net and Auto Craft Japan Jamaica (market
  asking prices, not verified retail).

### Architecture
- Decision made: Layered monolith with Supabase backend (deferred to Week 3).
- Nine-table Supabase schema designed.
- GitHub Actions pipeline designed: four jobs (weekly Petrojam scrape, weekly BOJ
  exchange rate fetch, monthly JPS tariff monitor, monthly Toyota price monitor).
- EV_Lab_Architecture_Note.md saved to docs/.

### Supervisor Meeting
- Meeting held Thursday June 18, 2026 with Dr. Louis-Ray Harris.
- Key decisions recorded in docs/EV_Lab_Supervisor_Meeting_Jun19.docx.
- Standardised on 90 octane for all fuel comparisons.
- Policy gap analysis added as a deliverable.
- Module 7 to include a 2030 target progress tracker.

### Policy Work
- Full read-through of Jamaica National EV Policy (June 2023).
- Draft policy gap analysis begun: docs/ev_policy_gap_analysis.md.

---

## Pending / Blocked Items

- BYD and MG new vehicle prices: pending ATL Automotive response (email sent June 10).
- JPS electricity rate and grid emissions data: pending JPS response (email sent June 10).
- MSETT fleet registration data: pending response.
- Transport Authority PPV licensing data: pending response.

---

## Next Week Priorities

1. Contact JUTA on Tuesday June 23 regarding operator survey.
2. Collect field gas price data Monday June 22 from Kingston stations.
3. Begin Module 2 (Route Cost Map) once map API is confirmed with Dr. Harris.
4. Begin Module 4 (Fleet Penetration Simulator).
5. Write Section 2 of formal report (Literature Review).
6. Set supervisor meeting for next week (Monday, Wednesday, or Thursday preferred).

---

## Files Changed or Created This Week

| File | Action |
|------|--------|
| dashboard/app.py | Major additions for Modules 1 and 3 |
| dashboard/data_loader.py | New file |
| data/vehicles.py | New file |
| data/raw/Fuel_Prices_Sorted_Fixed.xlsx | New file (gitignored) |
| data/processed/fuel_prices.csv | New file |
| data/process_fuel_prices.py | New file |
| docs/EV_Lab_Architecture_Note.md | New file |
| docs/EV_Lab_Supervisor_Meeting_Jun19.docx | New file |
| docs/ev_policy_gap_analysis.md | New file |
| report/weekly/week_02_summary.md | This file |
