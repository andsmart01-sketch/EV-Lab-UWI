# Cost basis: what is actually wrong, and what to do about it

For Dr Louis-Ray Harris. Andrew Smart, 7 August 2026.

The dashboard projects costs forward over an ownership period. This memo sets
out what basis each projection currently uses, corrects the way I had been
describing the problem, and asks you to decide one thing.

Short version: the problem is smaller and different from what I thought. Only
one projection is genuinely wrong. The escalation option I had been considering
turns out not to be available, and I can show why from our own data.

---

## 1. The correction to my own framing

I had been describing this as "depreciation compounds while fuel is held flat,
so the model is internally inconsistent." That framing is wrong, and it matters
because it points at the wrong fix.

Depreciation is not a price. A car loses value because it gets older and has
more kilometres on it, and it would do that in an economy with zero inflation.
The same is true of the other things that vary by year in the dashboard: grid
carbon intensity falls because generating plant changes, and the vehicle fleet
grows because people buy cars. These are physical quantities.

Fuel prices, electricity tariffs and maintenance costs are prices.

Once you separate the two, the picture changes. Every physical quantity in the
dashboard evolves over time. Every price is held at its 2026 level. That is not
an inconsistency. That is a coherent constant-2026-dollar treatment, which is
the standard way to do this, and it is what most of the code is already doing
whether or not it was deliberate.

So the three-way choice I had framed for you was the wrong question.

---

## 2. The escalation option is not available, and our own data shows it

I had proposed "all nominal with escalation" as one of three options, using
figures of 7.1 per cent a year for gasolene 87 and 9.3 per cent for diesel,
taken from our price series.

Those numbers are arithmetically correct and analytically useless. They are
endpoint-to-endpoint compound growth rates, and our series starts in January
2015, near the bottom of the 2014 to 2016 oil price crash, and ends in a 2026
recovery. Choosing different endpoints inside the same 607-observation series
gives completely different answers.

Nominal growth in ex-refinery price, by method and window:

| Window | Grade | Endpoint CAGR | Log-linear trend |
|---|---|---|---|
| 2015 to 2026 | Gasolene 87 | 7.07% | 5.81% |
| 2015 to 2026 | Auto Diesel | 7.98% | 7.00% |
| 2016 to 2026 | Gasolene 87 | 7.09% | 5.49% |
| 2016 to 2026 | Auto Diesel | 9.29% | 6.45% |
| 2021 to 2026 | Gasolene 87 | 5.41% | **-1.90%** |
| 2021 to 2026 | Auto Diesel | 9.24% | **-1.84%** |

The last two rows are the important ones. Over the most recent five years, the
endpoint calculation says diesel rose 9.2 per cent a year, while a trend fitted
through every observation in the same window says it fell slightly. Both
describe the same data.

The annual means show why:

| Year | 87 | 90 | Diesel |
|---|---|---|---|
| 2021 | 146.08 | 150.96 | 140.39 |
| 2022 | 191.89 | 196.54 | 210.35 |
| 2023 | 173.08 | 177.66 | 182.96 |
| 2024 | 168.74 | 176.49 | 171.06 |
| 2025 | 155.69 | 162.69 | 162.53 |
| 2026 | 175.11 | 182.34 | 186.87 |

Prices peaked in 2022, fell for three years, and turned up again in 2026. There
is no trend here to extrapolate. Any escalation rate I picked would be a
selection of endpoints dressed up as a finding, and it would sit in a report
whose Section 8.1.8 is a catalogue of exactly that kind of error.

I should note that the fleet module already reached this conclusion. Its own
code comment reads: "This project has no defensible fuel price forecast, so no
trend is assumed." That principle is correct and should be applied everywhere.

---

## 3. The one projection that is genuinely wrong

The taxi module treats the loan repayment as if it were a real quantity. It is
not. A loan is a fixed nominal contract, so its burden falls in real terms every
year that prices rise, and in a constant-2026-dollar model it has to be
discounted back.

At present the model adds the same nominal annuity to each year's costs
undeflated. This overstates the true burden of every loan, and it overstates
the larger loans most, which means it penalises the electric vehicles.

Cost of the defect over a ten-year horizon, 20 per cent down, 11 per cent over
four years, which are the dashboard defaults:

| Inflation | BYD Yuan Plus overstated by | Probox overstated by | Net effect on the comparison |
|---|---|---|---|
| 4% | J$704,331 | J$151,518 | J$552,812 to the EV |
| 5% | J$864,082 | J$185,885 | J$678,198 to the EV |
| 6% | J$1,017,935 | J$218,982 | J$798,953 to the EV |

For scale, the published taxi headline is J$4,367,089 for the Yuan Plus against
J$3,018,547 for the Probox, a gap of J$1,348,542. Correcting the loan treatment
at 5 per cent inflation closes about half that gap in the direction that was
already favouring the EV.

It does not reverse anything. The electric taxi still wins. But it moves in the
same direction as the resale omission we found earlier, which did reverse two
conclusions, and for the same underlying reason: both defects penalise whichever
vehicle has more capital tied up, which is always the electric one.

The fix is a single discount factor applied to the loan payment inside the
cash-flow loop in `dashboard/app.py` around line 4196.

---

## 4. A smaller presentational issue

The fleet module's retrospective view values fuel at each year's actual Petrojam
annual mean, which is nominal money of the day. Its prospective view holds the
2026 mean flat, which is constant 2026 dollars. Both are correct for what they
are, and the module already prints a note saying which is in use, so nothing is
hidden.

The gap is that the note does not tell the reader the units differ between the
two views. Someone toggling from back to forward sees a "fuel value saved"
figure change basis without being told. That is a wording fix, not a modelling
one.

---

## 5. What I recommend

Adopt constant 2026 dollars everywhere, state it once in the methods section,
and fix the loan.

Concretely:

1. Keep all prices flat at 2026 levels. No fuel escalation, no electricity
   escalation, no maintenance escalation. Our data does not support a rate and
   inventing one would be worse than assuming none.
2. Keep every physical quantity evolving as it already does. Depreciation, grid
   intensity, fleet growth.
3. Discount the taxi loan payment to 2026 dollars, since it is the one nominal
   contract in the model.
4. Add a single sentence to the fleet module note explaining that the
   retrospective is in money of the day and the projection is in 2026 dollars.
5. State the basis in Section 5 of the report and in the module info panels.

I do not recommend the sensitivity slider I had previously suggested. It would
let a user dial in a fuel escalation rate, and given what Section 2 above shows,
every value they could pick would be indefensible. Offering the control implies
the number is knowable.

---

## 6. The decision I need from you

The recommendation above needs one input from you: **what inflation rate to
discount the loan at.**

The Bank of Jamaica's target band is 4.0 to 6.0 per cent over the medium term,
and BOJ projected in February 2026 that inflation would return to that band by
the end of the December 2026 quarter after temporary breaches over the June and
September quarters. STATIN reported annual headline inflation of 3.9 per cent at
January 2026.

I have not verified the current month's figure and should before we finalise.

Three options:

- **5 per cent**, the midpoint of the BOJ band. Defensible, easy to state, and
  it does not depend on any single month's print.
- **The latest STATIN annual headline figure**, which is current but moves with
  whatever month we happen to publish in.
- **A stated range**, showing the loan correction at 4 and 6 per cent and
  quoting results as a band.

I lean towards 5 per cent for the model with the 4 and 6 per cent figures
reported in the limitations section, because it gives one number to quote and
an honest range around it. But this is a judgement about how to present
uncertainty, which is yours rather than mine.

---

## Sources

- Fuel price series: `data/raw/Fuel_Prices_Sorted_Fixed.xlsx`, 607 weekly
  Petrojam ex-refinery observations, 1 January 2015 to 30 July 2026.
- Bank of Jamaica, inflation target of 4.0 to 6.0 per cent per annum over the
  medium term. https://boj.org.jm/core-functions/monetary-policy/what-is-inflation/the-inflation-target/
- Bank of Jamaica, Monetary Policy Press Release, February 2026.
  https://boj.org.jm/monetary-policy-press-release-february-2026/
- Statistical Institute of Jamaica, consumer price index releases.
  https://statinja.gov.jm/PressReleases.aspx?field1=cpi
