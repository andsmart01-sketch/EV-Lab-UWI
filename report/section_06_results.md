# Section 6: Results

---

## 6.1 Consumer Cost Comparison

Under mid-2026 conditions, with 90 octane at an effective J$247 per litre and home charging at J$42/kWh, a new BYD Yuan Plus at J$7,670,000 does not overtake a used Toyota Corolla at J$3,800,000 within a ten-year ownership period. The purchase price differential of J$3.87 million is too large to be recovered by running-cost savings alone at typical private mileage.

The comparison changes with three variables, and the dashboard exposes all of them:

- **Distance.** Higher daily mileage brings the crossover forward, because the saving is per kilometre while the premium is fixed.
- **Charging split.** Moving from home charging to public charging removes a substantial part of the saving.
- **Vehicle pairing.** A used electric vehicle against a new petrol vehicle, which is the choice many Jamaican buyers actually face, produces a materially different result from new against used.

The finding for the private buyer is therefore conditional rather than categorical, and the honest answer is that it depends on the buyer. This is why the module is built as a calculator rather than as a verdict.

## 6.2 Regional Comparison

Jamaica sits low on adoption despite a mid-range fuel price. Two comparisons are more informative than the overall trend.

**Jamaica and The Bahamas both pay US$1.46 per litre.** Bahamian battery electric vehicle share of new sales is approximately 13%; Jamaica's is approximately 3%. Identical fuel price, four times the adoption.

**Jamaica and Barbados both levy 10% import duty.** Barbadian dealers report electric vehicle share of new sales rising from 10% in 2025 to approximately 20% in 2026, with hybrids and electric vehicles together reaching 72% of new sales in the first half of 2026. Jamaica remains near 3%.

Fuel price and headline duty rate, the two variables most often invoked, therefore do not explain Jamaica's position. What differs is the depth of the fiscal package and the surrounding conditions. Barbados layers a four-year excise and VAT holiday on top of its 10% duty, adds accelerated write-offs for company purchases and interest-free loans for public officers, and has electrified 89% of its bus fleet. It also operates an **alternate fuel levy** of BBD$25 per month on low-emission vehicles, introduced in 2023 specifically to recover fuel tax revenue lost as drivers switch, which is a working implementation of the revenue problem modelled in Section 6.5.

Trinidad and Tobago provides the counter-case. It has removed all customs duty, motor vehicle tax and VAT on battery electric vehicle imports since January 2022, and its pump price of US$1.14 sits below the CARICOM average of US$1.41. Zero duty and below-average fuel have not produced visible adoption, which further weakens any single-variable explanation.

Caveat: the Barbadian figures are dealer-reported rather than registry data, and Barbados has a substantial used-import channel, so they are not strictly the same measure as the IEA sales-share figures used elsewhere in the module.

## 6.3 Taxi Feasibility

This produced the study's clearest finding.

Modelling a BYD Yuan Plus operating 40 trips per day at J$200 per trip, six days a week over five years, cumulative net income varies as follows purely by charging arrangement:

| Charging | Rate (J$/kWh) | 5-year cumulative net |
|---|---|---|
| Home, JPS residential | 42.00 | **+J$779,352** |
| JPS overnight | 50.11 | +J$366,910 |
| Evergo, flat | 96.00 | −J$1,966,872 |
| JPS evening peak | 130.63 | −J$3,728,015 |

**A J$4.5 million swing produced by a scheduling decision**, larger than the price difference between any two vehicles in the database.

Only the two cheapest arrangements are profitable at all. A driver charging on the JPS evening peak pays 2.6 times what the same driver pays overnight on the same network, and 36% more than Evergo's flat rate.

The petrol baseline remains ahead: a used Toyota Probox returns J$2,065,890 over the same period. Notably, a **late-model Probox at J$2.3 million returns only J$1,320,960**, less than the older unit, because the additional J$650,000 of purchase price is not recovered by lower servicing within five years. Buying a fresher petrol taxi is not a better decision than keeping an older one.

The conclusion for this audience is therefore specific: an electric taxi in Jamaica is viable only with depot or home charging and disciplined overnight scheduling, and even then does not yet beat a used Probox on a five-year horizon.

**External validation.** Chile's *Mi Taxi Eléctrico* programme reports average savings above 3 million Chilean pesos per driver per year and 9.6 tonnes of CO₂ avoided per vehicle annually across 405 vehicles. The direction and rough magnitude are consistent with the modelled Jamaican results under favourable charging.

## 6.4 Emissions, and a Correction

### 6.4.1 Carbon Payback

Deriving the battery manufacturing premium from battery capacity rather than using stored totals produces carbon payback periods substantially shorter than previously held within this project:

| Vehicle | Payback |
|---|---|
| BYD Yuan Plus | 2.0 years |
| Nissan Leaf (used, amortised) | 1.5 years |
| BYD Seal | 2.4 years |

These are calculated at the current grid intensity of 0.474 kg CO₂/kWh and 40 km per day.

### 6.4.2 A Corrected Finding

An intermediate finding produced during this project stated that electric buses would **increase** carbon dioxide emissions on Jamaica's current grid. That finding was wrong, and the error is instructive.

The fleet model originally applied 16 kWh/100 km to all three streams, a passenger car figure. Recognising that a bus cannot consume what a car consumes, this was replaced with an estimated 100 kWh/100 km, and the model then showed electric buses increasing emissions. **The error was that the diesel figure sitting beside it, 10 L/100 km, is also a passenger car figure and was not checked.** The comparison was therefore between a realistic electric bus and a diesel bus with car-like fuel economy.

Gao et al. (2017) supply both correct figures for the 12-metre transit class: 135 kWh/100 km for the electric bus as a real-world average, and 55.5 L/100 km for the diesel equivalent, derived from reported fuel energy of 5.52 kWh/km at 32.5% engine efficiency.

Corrected, per bus at 40,000 km annually:

| | Annual CO₂ |
|---|---|
| Diesel at 55.5 L/100 km | 59.5 t |
| Electric at 135 kWh/100 km, current grid | 25.6 t |
| Electric at worst-case drive cycle, 248 kWh/100 km | 47.0 t |

**A 57% reduction, and still 21% lower on the worst-case drive cycle.** The public transport stream shows approximately 18,400 tonnes avoided in the final projection year on the current grid, rising to 24,300 tonnes at the 2030 grid target.

The methodological lesson is that a partial correction can be more dangerous than no correction, because it produces a confident result from an internally inconsistent comparison.

## 6.5 National Fleet Counterfactual

At the 12% private fleet target applied across 2015 to 2026, using actual Petrojam annual means:

- Gross CO₂ avoided: **418 kt**
- Battery manufacturing debt: **108 kt**
- Net CO₂ avoided: **310 kt**
- Petrol not burned: **297 million litres**
- Fuel spend avoided: **J$43.8 billion**
- Manufacturing debt repaid by: **2018**

At 100% penetration the net figure rises to approximately 2,582 kt and J$364.7 billion.

The fuel-spend figure is the most robust output in this module, because it uses real historic prices rather than an assumption. The emissions figure is an upper bound, for the grid-intensity reason set out in Section 5.6.

## 6.6 Charging Infrastructure

Jamaica has **two** public charging networks, not one, a fact absent from this project's earlier framing.

**Evergo:** 71 chargers, flat J$96/kWh at any hour, average session 21.9 kWh over 51 minutes, lifetime utilisation approximately 1% with a peak individual charger near 9%.

**JPS Charge 'n Go:** approximately 39 charging points across six parishes as of December 2025, on a three-band time-of-use tariff from J$50.11 to J$130.63.

Two observations follow. First, utilisation near 1% indicates the binding constraint on adoption is not charger availability. Second, no single source shows a driver every available charger, because each operator runs its own application, which is the practical form the missing national information platform takes.

## 6.7 Policy Implementation

Reported in full in Section 4. In summary: of 26 tracked commitments, one confirmed, one in progress, seven partial, fifteen not confirmed, one not implemented, one not started. Fifteen carry a citation.

The single measurable target stands at approximately 0.014% against a 16% goal.
