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

Seven modules, numbered here as they appear in the sidebar and on the home page.

| # | Module | Status |
|---|--------|--------|
| 1 | Fiscal Policy & Duty Tracker | Complete |
| 2 | Caribbean Regional Comparison | Complete |
| 3 | EV vs. ICE Calculator | Complete |
| 4 | Taxi Feasibility Tool | Complete |
| 5 | Fleet Penetration Simulator | Complete |
| 6 | Emissions Impact Calculator | Complete |
| 7 | Gas & Energy Price Tracker | Complete |

A Route Cost Map was scoped in week 2 as an eighth module and dropped in
August 2026 rather than shipped empty, because no mapping data source was
agreed and no corridor distances were collected. It is carried in the report
as further work, Section 8.3.

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
