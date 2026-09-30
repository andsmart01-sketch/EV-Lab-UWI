# EV Lab project handoff

Andrew Smart, UWI Mona physics. Supervisor Dr Louis-Ray Harris.
Plotly Dash dashboard comparing battery electric vehicles against petrol and
diesel vehicles in Jamaica, plus an eight-section report.

Last updated 16 September 2026.

---

## Do these first

**1. Commit and push.** One commit on `main` is not on GitHub
(`cc1c801`, the fetched road geometry), and the 3 September fixes below are
still uncommitted in the working tree. If the server deploys from GitHub, the
map has no road geometry and none of the deployment fixes are present.

```
cd "C:\Users\Andrew Smart\ev-lab-repo"
git add -A
git commit
git push origin main
```

Then **check it starts from a clean clone**, not from this working copy. That
is the step that catches anything still missing from the repository.

**2. Send the Petrojam email.** Drafted at `docs/petrojam_data_request.md`.
Three bracketed fields to fill in, and copy Dr Harris. This is the only thing
that unblocks automated fuel price collection, and it improves the report
whether or not it succeeds.

**3. Ask Dr Harris the cost basis question.** It is the one open decision that
changes results rather than presentation. See "Open decisions" below.

**4. Do not commit `data/evrange_cache/` yet.** The server came up on
16 September (hostname `https://api.evrange.dpdns.org`, now the default in
`routing_client.py`; key in `EVRANGE_API_KEY`, never in a file). The ids are
in `EV_SPEC_IDS` and the cache was populated locally the same day, 76
entries, no failures. But the first comparison against the recorded runs
found the model returning about half the measured energy (71 Wh/km against
173 measured, band 151 to 204), no change with direction on Red Hills Road
where the car recorded +3.2 and minus 1.3 kWh, and `hasTolls` raised on ten
of nineteen routes of which one touches a toll road. Until Rohan has fixed
his end, committing the cache would put those figures on screen under a
green "Figures from EVRange" banner. `docs/rohan_status_2026-09-16.md` is
the note to him with the numbers. When he has changed something:

```
set EVRANGE_API_KEY=...
python scripts\fetch_evrange_cache.py --force
```

Read the `vs measured` column before committing. The aggregate over the
sixteen Kingston runs should land inside 151 to 204 Wh/km, and the Red Hills
Road pair (runs 9 and 10) should differ sharply by direction. If both hold,
`git add data\evrange_cache` and commit. Still owed from his side: the
spreadsheet of runs with coordinates and consumption.

---

## How to run it

```
conda activate EVlab
cd "C:\Users\Andrew Smart\ev-lab-repo"
python dashboard\app.py
```

Then open http://127.0.0.1:8050. Ctrl+C to stop.

Dash reads the Python files only at startup, so **restart after any code
change**, and use Ctrl+Shift+R in the browser after a CSS change, since
browsers cache stylesheets aggressively.

`set EVLAB_DEBUG=1` first for auto-reload while editing. Never on a server:
debug mode exposes a Python console on the error page.

The "development server" warning at startup is normal and not a problem on a
laptop. For deployment, `gunicorn` on Linux or `waitress` on Windows.

---

## Module numbering (this trips everyone up)

Display numbers do not match the internal tab ids.

| Display | Internal | Module |
|---|---|---|
| 1 | tab-7 | Fiscal Policy and Duty Tracker |
| 2 | tab-8 | Caribbean Regional Comparison |
| 3 | tab-1 | EV vs ICE Calculator |
| 4 | tab-6 | Taxi Feasibility Tool |
| 5 | tab-2 | Route Cost Map |
| 6 | tab-4 | Fleet Penetration Simulator |
| 7 | tab-5 | Emissions Impact Calculator |
| 8 | tab-3 | Gas and Energy Price Tracker |

Dr Harris uses display numbers. The code uses tab ids. `MODULE_INFO` in
`app.py` is the single source of display order, and `module_number()` reads the
number off its position, so changing that dict changes the whole interface.

**The numbering moved twice and has ended up back where it started.** The Route
Cost Map was cut on 7 August 2026, which pulled displays 6, 7 and 8 up to 5, 6
and 7. It was restored at display 5 later the same day, once sixteen measured
runs existed to populate it, which pushed them back down. The table above is
current as of 3 September 2026 and agrees with Dr Harris's August review notes.
Only material written inside that one-day window uses the seven-module
numbering.

---

## State of play

### Dashboard: Dr Harris's August review is complete

All fifteen items done and committed. Verified: 8 layouts build, Dash
validates 41 callbacks, every chart has visible axes, no chart pairs blue with
green, My Car computes in both modules, all three grid scenarios reproduce
exactly at their slider marks.

What changed: 16px base font, visible axes on all charts via `chart_layout()`,
blue and green separated, explicit dates on graphs, policy actions and policy
gaps as HTML tables, justified prose capped at 78 characters, country data
availability footnotes, asterisks on estimated prices, gas station list
replaced by a custom rate, grid intensity as a 0 to 100 per cent renewable
slider, My Car custom vehicle, taxi resale value, and the clarified running
cost saving label.

### Report: eight sections plus Appendix A, 13,244 words

`report/section_0N_*.md` are the **source of truth**. Appendix A is
`section_09_appendix_a_evrange.md`, named so the build script picks it up
last; it reproduces Rohan's model description verbatim because an examiner
cannot inspect his code. `full_report.md` and
`EV_Lab_Report_2026.docx` are both generated. Rebuild with
`report/build_report.bat`. Anything typed directly into the docx is lost on
the next rebuild.

### Fuel prices: manual, and this matters

Petrojam refuses automated collection. Every path including `/robots.txt`
returns HTTP 403 from an AWS load balancer, while robots.txt itself permits
crawling. This is an edge filter rejecting non-browser clients, not a crawling
policy.

**Getting past it would mean disguising the request as a browser. That was
deliberately not done, and should not be done.** Petrojam is a state-owned
public body, this is a research project with your name on it, and the correct
response to a refusal is to ask. Section 3.6 of the report documents this.

Until access is granted:

```
python scripts\add_prices.py
```

Paste `date, 87, 90, diesel` rows. Validated, deduplicated, backed up, and the
CSV regenerated. Petrojam publishes **Thursdays** (verified: 581 of 602 rows).

Series is current to **27 August 2026**. The four August weeks were entered by
hand on 3 September 2026 from https://www.petrojam.com/price/, after the
scheduled job had gone five weeks without adding a row. Note that they carry
Petrojam's full four-decimal figures while older rows were rounded to two on
entry, so the series now has mixed precision. Harmless for every figure the
dashboard displays, which rounds anyway.

**The weekly job fails silently, and this needs fixing before the server takes
it over.** `live_config.json` recorded `script_last_run` on 2 September while
`petrojam_last_date` sat at 30 July. The exchange rate half works, so the file
looks healthy. `update_weekly.py` should exit non-zero, or write a status
field, when the price sync returns no rows. Otherwise the next five weeks go
the same way.

Also set `EVLAB_CONTACT` on the server. Without it every request the job makes
carries `contact-not-configured`, which `polite_fetch.py` warns about at
startup and which is the opposite of the point of that module.

`scripts/diagnose_petrojam.py` re-tests
access without attempting to defeat it. If access is granted,
`scripts/sync_petrojam.py` is written, tested and ready, and
`scripts/install_schedule.bat` registers a Thursday 18:00 task.

---

## Deployment, and what was fixed on 3 September 2026

Two separate faults meant a clean clone could not start on a server at all.
Both are fixed, both were verified by cloning to an empty directory and
importing the app.

**The workbook is not in the repository.** `.gitignore` excludes `*.xlsx`, so
`data/raw/Fuel_Prices_Sorted_Fixed.xlsx` never travels, and
`load_fuel_prices()` raised `FileNotFoundError` at module level before Dash
loaded. `data_loader.py` now falls back to `data/processed/fuel_prices.csv`,
which is tracked and which `add_prices.py` regenerates on every run. The
workbook still wins when it is present. `LAST_PRICE_SOURCE` records which was
used and the startup log prints it, so a machine silently running on the
fallback is visible rather than indistinguishable.

**The documented gunicorn command did not work.** `app.py` imports
`data_loader`, `module7_policy`, `module_route`, `routes` and `route_costs` by
bare name, which only resolves with `dashboard/` on `sys.path`. That happens by
accident under `python dashboard/app.py` and not at all under
`gunicorn dashboard.app:server`. `app.py` now inserts its own directory first,
using `abspath` because `dirname(__file__)` is empty when the file is run from
inside its own folder. The documented command is now correct as written.

`dashboard/requirements.txt` listed streamlit, folium and streamlit-folium,
none of which anything imports. It is now a signpost to the root
`requirements.txt`, which is the only real dependency list.

Production, on the UWI server:

```
gunicorn -w 4 -b 0.0.0.0:8050 dashboard.app:server
```

Never with `EVLAB_DEBUG` set. Debug mode puts an interactive Python console on
the error page, so anyone who can make the app raise gets code execution.

Also set `EVRANGE_API_KEY` on the server if you want Module 5 to make live
calls for uncached inputs. Without it the module serves the committed cache
and shows the placeholder banner for everything else, which is acceptable for
a demonstration if the cache has been populated (item 4 above). The key must
never go in a file that is committed; `.env` is gitignored for this reason.
The hostname is built in; `EVRANGE_API_URL` overrides it only if Rohan's
tunnel ever moves.

---

## Open decisions

**Cost basis, with Dr Harris.** Projections are inconsistent: depreciation
compounds correctly and grid intensity varies by year, but fuel, electricity
and maintenance are held flat at 2026 prices. So one chart decarbonises the
grid while another holds fuel constant, biasing them in opposite directions.
Two charts in the same dashboard cannot be compared.

Andrew's own price series gives the rates: gasolene 87 at 7.1 per cent a year
over ten years, diesel at 9.3 per cent, both nominal. The trap is that
Jamaican inflation ran 5.5 per cent at May 2026 against a 4 to 6 per cent
target band, so escalating fuel nominally while holding vehicle prices in 2026
dollars double-counts inflation and flatters EVs.

The choice is not "escalate or not" but "pick one basis and apply it
everywhere": all real in 2026 dollars, all nominal with escalation, or real
with a sensitivity slider.

**Route Cost Map. Cut on 7 August 2026, restored the same day.** It was cut
because no mapping data source was agreed and no corridor distances had been
measured, so populating it would have meant inventing the numbers it displayed.
That blocker was then removed: sixteen route-taxi runs were measured in a BYD
Yuan Plus over the Kingston corridors named in report Section 8.3, road
geometry was fetched for all sixteen, and all nine endpoint coordinates are
filled in. The module is live at display 5.

What is still open on it is the consumption basis, not the existence of data.
The aggregate is **173 Wh/km** on the recorded distances, quoted with a band of
151 to 204 Wh/km. OSRM road distances total 92.2 km against the recorded 80.2
km, 15 per cent higher, and recomputing on those gives **153 Wh/km**. That sits
inside the stated band, so no conclusion changes either way. The useful reading
is that the discrepancy is one-sided: if road distances really are longer than
the vehicle recorded, the true value is below 173 rather than either side of
it. Worth a sentence in Section 5. Do not recompute the headline on OSRM
distances without deciding that with Dr Harris first.

**EVRange integration, checked 16 September 2026 against Rohan's messages.**
Everything on our side is built: server-side call with the key in an
environment variable, all ten request fields, a cache keyed on the request
body, 3 second spacing enforced across gunicorn workers (his limit is 20 a
minute per IP), slider on mouse-up and debounced inputs, disk cache served
before any live call, his three corridors as presets, Plotly map instead of
Mapbox GL, cost layer on his Wh/km, Portmore toll rate on the T4 preset,
citation on the page and in report Sections 2, 3, 5.8 and Appendix A.
`scripts/fetch_evrange_cache.py` populates the cache and lists `/api/ev-models`.

Hostname, key and ids all arrived on 16 September; see item 4 above for why
the cache is populated but not committed. Still owed: his run spreadsheet.

Three things learned from the live API on 16 September. `distanceKm` and
`avgWhkm` are per direction even for a return trip, while `socNeededPct`
covers the round trip; `build_costs` doubles the distance accordingly, and
the stub follows the same convention. `hasTolls` is a boolean from a
bounding box that is far too generous, so the J$400 Portmore rate is applied
only on the T4 preset, which is declared to cross it in `routes.py`; any
other flagged route is costed at zero and the basis panel explains why. And
only the Portmore Class 1 rate has been sourced.

In the report, Rohan's description is cited as a personal communication
(R. Brown, personal communication, August 7, 2026) in Section 5.8.1 and
Appendix A, and the model itself as EVRange (2026), the form he asked for.

---

## Outstanding work

- ~~README says Streamlit rather than Dash.~~ Rewritten 3 September 2026:
  framework, supervisor name, setup and deployment commands, the eight-module
  table, and the price-series note are all current. The data sources and
  surveys sections now state plainly what is unknown rather than implying
  everything was sent.
- Screenshots for the user guide. The guide is now 33 slides after the Route
  Cost Map slide was removed, and 21 of them carry marked placeholders with no
  images embedded yet. Counted 7 August 2026; the earlier figure of 21 out of
  34 was one slide short.
- BSJ, NEPA, Transport Authority and TAJ are named across seven or more
  outstanding policy actions and have never been contacted. A dated negative
  reply is citable evidence of non-publication.
- Urban consumption measurement for the Nissan Tiida, to replace a
  single-vehicle uplift factor applied to three vehicles.

---

## Things that cost time before, so they do not again

**Restart before reporting a bug.** Two apparent bugs this session were
unrestarted processes serving old code. Dash has no hot reload with debug off.

**Stale `.git/index.lock`.** A crashed git process left a zero-byte lock dated
31 July that silently blocked every commit for four days. If git says another
process is running, check the lock's age before deleting it.

**Editing the docx or `full_report.md` directly.** Both are generated. Edit the
sections.

**Vehicle lookups must go through `resolve_vehicle()`.** Indexing
`ICE_VEHICLES` or `BEV_VEHICLES` directly raises `KeyError` the moment someone
picks My Car.

**Grid slider is in per cent renewable, not kg CO2 per kWh.** Convert with
`renewable_pct_to_intensity()`.

---

## The methodological thread

Five errors were found and corrected during this project, and the pattern is
consistent enough to be worth stating: **partially correct output is the
hardest kind to catch.**

- **Electric buses.** A partial correction fixed the electric consumption
  figure from a car value to a bus value but left the diesel figure beside it,
  also a car value, unchecked. Produced a confident, circulated, wrong finding
  that e-buses increase emissions. They reduce them by 57 per cent.
- **Manufacturing CO2.** Cradle-to-gate vehicle totals used as
  electric-over-petrol premiums, roughly doubling every carbon payback figure.
- **The 6,606 figure.** A twelve-month import flow including hybrids, recorded
  as Jamaica's EV fleet total.
- **Trinidad fuel price.** A stale US$0.40 supporting a confident and false
  conclusion. Verified figure US$1.14.
- **Scraped prices.** Two rows where the 87 and 90 octane figures were exactly
  right while diesel was low by J$57.50 and the date wrong by a week. Two of
  four fields correct is precisely what makes the other two easy to accept.
- **Omitted taxi resale.** Reversed two conclusions. See below.

All are recorded in report Section 8.1.8, deliberately, because the pattern is
more useful than the individual corrections.

### The taxi correction, because it reversed published conclusions

The taxi model tracked cash flow only, so the vehicle was treated as worthless
on the last day. This penalised whichever vehicle cost more, which is always
the electric one.

Counting resale less any loan outstanding adds J$3,587,737 to every electric
figure and J$952,657 to the Probox.

- **Evergo flips from −J$1,966,872 to +J$1,620,865.** The claim that only the
  two cheapest charging arrangements were profitable was an artefact.
- **The electric taxi now beats the Probox**, J$4,367,089 against J$3,018,547
  on home charging. The earlier "does not yet beat a used Probox" was wrong.
- **The headline survives untouched.** The best-to-worst charging swing is
  J$4,507,367 before and after, to the dollar, because resale does not depend
  on when you charge.

---

## Working preferences

- No em dashes in anything drafted.
- Straight answers, positive or negative, not softened.
- Real citations and URLs only. If a source would have to be invented, say so
  instead. Acknowledge uncertainty and pause for a decision rather than
  guessing.
- When experts disagree, explain the disagreement and ask.
- Prefer trusted Government of Jamaica sources and Jamaican industry sources.
- Ask as many clarifying questions as needed before starting.

---

## Repository map

```
dashboard/app.py              ~5,000 lines, all modules and callbacks
dashboard/data_loader.py      price series and exchange rate, with fallbacks
dashboard/module7_policy.py   policy tracker, ACTIONS and POLICY_GAPS
dashboard/module_route.py     route cost map, display module 5
dashboard/routes.py           measured runs, corridors, endpoint coordinates, tolls
dashboard/routing_client.py   EVRange client, cache first, cross-process throttle
dashboard/route_costs.py      cost and emissions layer on top of EVRange
data/evrange_cache/           EVRange responses, committed once populated (empty until Rohan's server is up)
scripts/fetch_evrange_cache.py  populate that cache, list /api/ev-models
dashboard/assets/style.css    typography, justification, line length
data/vehicles.py              21 vehicles, single source of truth, My Car
data/raw/Fuel_Prices*.xlsx    price series, NOT tracked by git
data/processed/fuel_prices.csv  tracked fallback, what a clean clone reads
data/route_geometry.json      road geometry for all sixteen measured runs
scripts/add_prices.py         manual price entry, validated
scripts/sync_petrojam.py      automated sync, ready if access is granted
scripts/diagnose_petrojam.py  re-test access without defeating it
scripts/polite_fetch.py       caching, conditional GET, backoff, robots
report/section_0N_*.md        source of truth for the report
report/build_report.bat       rebuild full_report.md and the docx
docs/EV_Dashboard_User_Guide.pptx   34 slides, 21 screenshot placeholders
docs/petrojam_data_request.md       drafted, unsent
```
