# EV Lab Research Project — UWI Mona

**Researcher:** Andrew Smart  
**Supervisor:** [Supervisor Name]  
**Institution:** University of the West Indies, Mona Campus  
**Timeline:** June 8 – August 3, 2026 (8 weeks)

---

## Project Overview

This project quantifies the economic and environmental impacts of adopting electric, hybrid, and conventional ICE vehicles across Jamaica and the wider Caribbean. The primary deliverable is an interactive Python (Streamlit) dashboard supporting both macro-level policy planning and private consumer decision-making.

---

## Repository Structure

```
ev-lab-repo/
├── data/
│   ├── raw/          # Original data files as received — never edit these
│   ├── processed/    # Cleaned, analysis-ready datasets
│   └── surveys/      # Google Form exports (kept local, not tracked by Git)
├── docs/             # Policy documents, data request letters, literature notes
├── dashboard/        # Streamlit application code
├── survey/           # Survey links, QR codes, survey design notes
├── report/           # Progressive formal report (one section per week)
└── README.md
```

---

## Dashboard Modules

| # | Module | Status |
|---|--------|--------|
| 1 | EV / Hybrid vs. ICE Calculator | Planned — Week 1-2 |
| 2 | Route Cost Map | Planned — Week 3 |
| 3 | Gas & Energy Price Tracker | Planned — Week 2 |
| 4 | Fleet Penetration Simulator | Planned — Week 3 |
| 5 | Emissions Impact Calculator | Planned — Week 3 |
| 6 | Taxi Feasibility Tool | Planned — Week 3 |
| 7 | Fiscal Policy & Duty Tracker | Planned — Week 4 |
| 8 | Caribbean Regional Comparison | Planned — Week 3-4 |

---

## Data Sources

| Institution | Data Asset | Status |
|-------------|-----------|--------|
| MSETT | EV/hybrid registry & fleet stats | Request sent |
| Petrojam | Historical fuel price bulletins | Request sent |
| JPS | Electricity tariffs & grid emissions factor | Request sent |
| STATIN | Grid emissions intensity (backup) | Request sent |
| Transport Authority | PPV & taxi counts by parish | Request sent |
| JUTA | Operator routes & cost per passenger | Request sent |
| NEPA | Transport sector emissions baselines | Request sent |
| CSGM | Public transport operating costs | Request sent |
| IEA | Regional transport emissions data | Literature |

---

## Surveys

- **Consumer Fuel Tracking Survey:** [Google Form link — add when live]
- **JUTA Operator Survey:** Deployed Week 3 (target: Tuesday June 23)

---

## Setup

```bash
pip install -r dashboard/requirements.txt
streamlit run dashboard/app.py
```

---

## Deployment

Live dashboard: [Streamlit Cloud URL — add when deployed, Week 4]
