# EV Lab Research Project — UWI Mona

**Researcher:** Andrew Smart
**Supervisor:** Dr Louis-Ray Harris
**Institution:** University of the West Indies, Mona Campus
**Fieldwork:** June 8 to August 3, 2026 (8 weeks), with dashboard and report
work continuing after that date.

---

## Project Overview

This project quantifies the economic and environmental impacts of adopting
electric and conventional internal combustion engine vehicles in Jamaica and
the wider Caribbean. The main deliverable is an interactive dashboard built in
Python with **Plotly Dash**, supporting both macro-level policy planning and
private consumer decision-making, alongside an eight-section formal report.

---

## Setup

Python 3.11 is what this was developed against. From the repository root:

```bash
pip install -r requirements.txt
python dashboard/app.py
```

Then open http://127.0.0.1:8050. Ctrl+C to stop.

`requirements.txt` at the root is the only dependency list. Dash reads the
Python files at startup only, so **restart after any code change**, and use
Ctrl+Shift+R in the browser after a CSS change.

For auto-reload while editing, set `EVLAB_DEBUG=1` first. Never do this on a
server: debug mode exposes an interactive Python console on the error page.

---

## Deployment

Do not run `app.py` directly in production. Use a WSGI server against the
`server` object the module exposes:

```bash
gunicorn -w 4 -b 0.0.0.0:8050 dashboard.app:server     # Linux
waitress-serve --listen=0.0.0.0:8050 dashboard.app:server   # Windows
```

Set `EVLAB_CONTACT` to a departmental or project address before running the
weekly updater on a server, so outgoing requests carry a contact point. See
`scripts/polite_fetch.py` for why.

### The Route Cost Map and EVRange

Module 5 takes its energy figures from EVRange, a colleague's routing API at
`https://api.evrange.dpdns.org` (a permanent named Cloudflare Tunnel; the
default is in `dashboard/routing_client.py` and `EVRANGE_API_URL` overrides
it). One environment variable is needed, and it is never committed anywhere:

```
EVRANGE_API_KEY=<key Rohan sends>
```

Without it the module still runs, serving whatever is in
`data/evrange_cache/` and showing a red placeholder banner for anything that
is not cached. That is by design: the API runs on a laptop with no uptime
guarantee, so the dashboard reads the committed cache first and only calls
the API for input combinations nobody pre-fetched.

To populate the cache once the API is up, from the repository root with the
key set:

```
python scripts/fetch_evrange_cache.py --list-models   # get the evSpecIds
# paste the two ids into EV_SPEC_IDS in dashboard/module_route.py
python scripts/fetch_evrange_cache.py                 # fetch and cache, ~4 min
git add data/evrange_cache && git commit
```

Calls are spaced to stay under the API's limit of 20 per minute, across all
gunicorn workers.

---

## Repository Structure

```
ev-lab-repo/
├── dashboard/        # Plotly Dash application code
│   ├── app.py            all modules and callbacks
│   ├── data_loader.py    price series and exchange rate
│   ├── module7_policy.py policy tracker
│   ├── module_route.py   route cost map
│   ├── routes.py         measured runs, corridors, coordinates, tolls
│   ├── routing_client.py EVRange API client, cache first
│   └── route_costs.py    cost and emissions layer on top of EVRange
├── data/
│   ├── raw/          # Original data as received. Never edit. Not tracked.
│   ├── processed/    # Cleaned, analysis-ready datasets. Tracked.
│   ├── surveys/      # Google Form exports, kept local, not tracked
│   └── vehicles.py   # 21 vehicles, single source of truth
├── docs/             # Handoff notes, data request letters, user guide
├── report/           # Eight-section formal report, APA 7th
├── scripts/          # Weekly price updater and manual price entry
├── survey/           # Survey links and design notes
└── requirements.txt
```

### A note on the price series

The dashboard reads `data/raw/Fuel_Prices*.xlsx` when it is present. That
workbook is the system of record and is **not** tracked, because `.gitignore`
keeps raw institutional data out of the repository.

So that a clean clone still runs, `data_loader.load_fuel_prices()` falls back
to `data/processed/fuel_prices.csv`, which is tracked and which
`scripts/add_prices.py` regenerates on every run. The startup log says which of
the two was used. If the two ever disagree, the workbook is right and the CSV
needs regenerating.

---

## Dashboard Modules

Eight modules, numbered here as they appear in the sidebar and on the home
page. `MODULE_INFO` in `dashboard/app.py` is the single source of display
order; the internal tab ids do not match the display numbers and are
historical.

| # | Internal id | Module | Status |
|---|---|--------|--------|
| 1 | tab-7 | Fiscal Policy & Duty Tracker | Built. Statuses last verified June 2026. |
| 2 | tab-8 | Caribbean Regional Comparison | Built |
| 3 | tab-1 | EV vs. ICE Calculator | Built |
| 4 | tab-6 | Taxi Feasibility Tool | Built |
| 5 | tab-2 | Route Cost Map | Built. Consumption basis open, see below. |
| 6 | tab-4 | Fleet Penetration Simulator | Built |
| 7 | tab-5 | Emissions Impact Calculator | Built |
| 8 | tab-3 | Gas & Energy Price Tracker | Built |

The Route Cost Map was scoped in week 2, dropped in early August 2026 rather
than shipped without measured distances, and restored at display 5 once
sixteen measured Kingston route-taxi runs and their road geometry were
collected. Its aggregate consumption figure is 173 Wh/km on recorded distances
with a stated band of 151 to 204 Wh/km. Recomputing on OSRM road distances
gives 153 Wh/km, which sits inside that band. Which basis to quote is an open
question for the supervisor.

---

## Data Sources

Requests were sent on 10 June 2026 to the institutions listed in
`docs/responses/README.md`, which is the record of who was contacted and at
what address.

**As of 3 September 2026 no responses have been filed** and
`docs/responses/` is empty apart from its README.

Two things still need reconciling before this table can be stated with
confidence:

- `docs/HANDOFF.md` records that BSJ, NEPA, the Transport Authority and TAJ
  were never contacted, which contradicts the contact log. One of the two is
  wrong.
- The Petrojam data access request at `docs/petrojam_data_request.md` is
  drafted but has three bracketed fields still unfilled, and there is no
  record of it having been sent.

Sources used in the analysis regardless of institutional response are cited in
report Section 3.

---

## Fuel prices

Petrojam publishes weekly, on Thursdays (verified: 581 of 602 rows in the
series). Automated collection is blocked: every path on petrojam.com,
including `/robots.txt`, returns HTTP 403 from an edge filter, while
robots.txt itself permits crawling.

Getting past that would mean disguising the request as a browser. That was
deliberately not done and should not be done. Report Section 3.6 documents it.

Until access is granted, enter rows by hand:

```bash
python scripts/add_prices.py
```

Paste `date, 87, 90, diesel` rows. Validated, deduplicated, backed up, and the
CSV regenerated. `scripts/diagnose_petrojam.py` re-tests access without
attempting to defeat it.

---

## Surveys

- **Consumer Fuel Tracking Survey:** link not yet recorded in
  `survey/survey_links.md`.
- **JUTA Operator Survey:** link not yet recorded in
  `survey/survey_links.md`.

Both placeholders are outstanding.

---

## Report

`report/section_0N_*.md` are the source of truth. `report/full_report.md` and
`report/EV_Lab_Report_2026.docx` are both generated, so anything typed
directly into either is lost on the next rebuild. Rebuild with
`report/build_report.sh` on Linux or macOS, `report/build_report.bat` on
Windows. Both need `pandoc`.

---

## Further reading

`docs/HANDOFF.md` is the fuller working document: module numbering, known
traps, open decisions, and the record of errors found and corrected during the
project.
