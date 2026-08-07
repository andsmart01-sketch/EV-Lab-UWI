# EV Lab project handoff

Andrew Smart, UWI Mona physics. Supervisor Dr Louis-Ray Harris.
Plotly Dash dashboard comparing battery electric vehicles against petrol and
diesel vehicles in Jamaica, plus an eight-section report.

Last updated 7 August 2026.

---

## Do these first

**1. Push. There are 13 commits on `main` that are not on GitHub.**

```
cd "C:\Users\Andrew Smart\ev-lab-repo"
git push origin main
```

**2. Send the Petrojam email.** Drafted at `docs/petrojam_data_request.md`.
Three bracketed fields to fill in, and copy Dr Harris. This is the only thing
that unblocks automated fuel price collection, and it improves the report
whether or not it succeeds.

**3. Ask Dr Harris the cost basis question.** It is the one open decision that
changes results rather than presentation. See "Open decisions" below.

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
| 5 | tab-2 | Route Cost Map (**unbuilt**, placeholder) |
| 6 | tab-4 | Fleet Penetration Simulator |
| 7 | tab-5 | Emissions Impact Calculator |
| 8 | tab-3 | Gas and Energy Price Tracker |

Dr Harris uses display numbers. The code uses tab ids.

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

### Report: eight sections, 10,979 words

`report/section_0N_*.md` are the **source of truth**. `full_report.md` and
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

Series is current to **30 July 2026**. `scripts/diagnose_petrojam.py` re-tests
access without attempting to defeat it. If access is granted,
`scripts/sync_petrojam.py` is written, tested and ready, and
`scripts/install_schedule.bat` registers a Thursday 18:00 task.

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

**Route Cost Map (display module 5).** Still a placeholder. Decide whether it
ships marked "in development" or is cut, because the user guide covers eight
modules and one is empty.

---

## Outstanding work

- README still says Streamlit rather than Dash, lists all eight modules as
  "Planned", and has `[Supervisor Name]` as a placeholder. First thing anyone
  visiting the repo reads.
- Screenshots for the user guide. 21 slides carry marked placeholders and no
  images are embedded yet.
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
dashboard/app.py              ~4,400 lines, all modules and callbacks
dashboard/module7_policy.py   policy tracker, ACTIONS and POLICY_GAPS
dashboard/assets/style.css    typography, justification, line length
data/vehicles.py              21 vehicles, single source of truth, My Car
data/raw/Fuel_Prices*.xlsx    price series, what the dashboard reads
scripts/add_prices.py         manual price entry, validated
scripts/sync_petrojam.py      automated sync, ready if access is granted
scripts/diagnose_petrojam.py  re-test access without defeating it
scripts/polite_fetch.py       caching, conditional GET, backoff, robots
report/section_0N_*.md        source of truth for the report
report/build_report.bat       rebuild full_report.md and the docx
docs/EV_Dashboard_User_Guide.pptx   34 slides, 21 screenshot placeholders
docs/petrojam_data_request.md       drafted, unsent
```
