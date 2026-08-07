# Section 8: Limitations, Conclusions and Further Work

---

## 8.1 Limitations

### 8.1.1 Unverified Vehicle Prices

Twelve of 21 vehicles in the database carry unverified prices: all eight used petrol vehicles and all four used electric vehicles. These are asking prices from Jacars.net, Jamaicars.com and Auto Craft Japan, not confirmed transactions. The nine verified prices are the four new Toyotas from Toyota Jamaica and five BYD models from ATL Automotive.

Two matter more than the rest. The **used Toyota Probox at J$1,650,000** is the baseline against which every electric vehicle in the taxi module is measured, so an error there shifts eleven comparisons at once. The **Nissan Tiida at J$2,000,000** has no named source, only "estimated from the Jamaican used car market", and serves as the second petrol taxi baseline.

### 8.1.2 Derived Consumption Figures

Nine of twelve vehicles in the taxi module use derived rather than measured consumption. Only the Toyota Probox, BYD Yuan Plus and Nissan Leaf have real urban figures. The remainder are scaled by uplift factors of 1.41 for petrol and 1.15 for electric.

**The petrol uplift rests on a single vehicle.** It is applied to two others. An urban consumption measurement for the Nissan Tiida, the second most common route taxi, would be the single most valuable additional field measurement after bus consumption.

### 8.1.3 Missing Denominators

Two of three headline targets cannot be measured. Registered vehicles are not disaggregated into private, commercial and government, so the 12% private target has no denominator. The government fleet publishes neither a total nor an electric count. The private fleet figure used in the model, 540,113, is an **upper bound**, derived by subtracting public passenger vehicles from all fit-certified vehicles, and still contains commercial and government vehicles.

### 8.1.4 Remaining Estimates in Live Calculations

| Input | Value | Basis |
|---|---|---|
| Government fleet size | 3,500 | **Unsourced estimate** |
| Petrol urban uplift | 1.41× | Single vehicle, applied to three |
| Fleet average battery | 55 kWh | Assumption for manufacturing debt |
| Japan/Korea battery intensity | 60 kg CO₂e/kWh | Nearest published analogue, not sourced |

The government fleet figure is the weakest input in any live calculation and drives the entire government stream of the fleet model.

### 8.1.5 Maintenance Risk in the Fuel Price Series

The fuel price series cannot be collected automatically, for the reasons set out in Section 3.6, and is maintained by manual weekly entry. This is a limitation of a different kind from the others here: it does not bias any result, but it will silently degrade the dashboard if nobody performs it.

The risk is concrete. Every running-cost figure in every module derives from the most recent price in that series. A dashboard left unattended will not display an error; it will display confident figures based on a price that is months old. Two mitigations are in place. The startup log states the source and date of the price and exchange rate it loaded, so a stale series is visible to anyone who starts the application. And entry runs through a validation tool applying the same date, range and duplicate checks the automated path would have used, so manual entry is not a lower standard of care than automated collection, only a slower one.

The dependency ends if Petrojam grants access or supplies the series directly. Until then it should be treated as a standing obligation attached to the dashboard rather than as a solved problem.

### 8.1.6 Methodological Limitations

**Glider parity.** The manufacturing premium assumes the body shell and non-battery drivetrain of a BEV and an equivalent ICE vehicle carry comparable production emissions. Electric vehicles are heavier and use more aluminium, so the derived premium is a lower bound.

**Historic grid intensity.** Pre-2022 grid intensity is held flat at 0.474 kg CO₂/kWh because no year-by-year Jamaican series was obtained. The pre-LNG grid was dirtier, so retrospective avoided emissions are an upper bound; substituting a declining series reduces them by approximately 13%.

**Bus figures are not Jamaican.** The 135 kWh/100 km and 55.5 L/100 km figures come from Knoxville Area Transit data. The vehicle class matches, but Jamaican terrain, traffic and continuous air-conditioning load differ. JUTC measured its own consumption during the pilot and has not published it.

**Barbadian adoption figures are dealer-reported**, not registry data, and Barbados has a substantial used-import channel. They are not strictly the same measure as the IEA sales-share figures used for other countries.

### 8.1.7 Regional Data Sparsity

Nine of nineteen countries appear in the summary table but on neither chart, because no published battery electric vehicle sales share exists for them. Caribbean vehicle registries do not generally publish it. Fields were left empty rather than estimated, which is why the regional charts look sparser than the table.

### 8.1.8 Errors Identified and Corrected During the Study

Recorded because the pattern is instructive rather than to catalogue mistakes.

**The electric bus error.** A finding that electric buses would increase emissions on Jamaica's grid was produced, circulated, and then found wrong. The cause was a partial correction: the electric consumption figure was fixed from a car value to a bus value, while the diesel figure beside it, also a car value, was not checked. Corrected, electric buses reduce emissions by 57%. **A partial correction produced a confident result from an internally inconsistent comparison, which is more dangerous than no correction.**

**The manufacturing CO₂ conflation.** Values labelled as the electric-over-combustion premium were consistently 2.2 to 2.4 times the battery production emissions implied by any published source, indicating they were whole-vehicle cradle-to-gate totals. Used as premiums they roughly doubled every carbon payback figure.

**The 6,606 figure.** Recorded as Jamaica's electric vehicle fleet total. It is a twelve-month import flow and the source series explicitly includes hybrids.

**A stale Trinidad fuel price.** A value of US$0.40 per litre, years out of date, supported a confident and entirely false conclusion about why Trinidad's zero-duty regime had not produced adoption. The verified May 2026 figure is US$1.14.

**Corrupt scraped fuel prices.** The original price scraper matched `Label: value` patterns over the prose of Petrojam's weekly announcement pages. It produced two rows in July 2026 in which the 87 and 90 octane figures were exactly right while the diesel figure was low by about J$57.50 and the date was wrong by six to eight days. A regex for "Diesel" over prose can match any of several diesel products, and the date it finds may be a publication date rather than the price week. The rows were removed and the collector rewritten to read the structured price table by column header, which removes the ambiguity rather than patching around it. **Partially correct output is the hardest kind to notice: two of the four fields were right, which is exactly what makes the other two easy to accept.**

**Omitted resale value in the taxi model.** The taxi feasibility module tracked cash flow only, so at the end of the ownership period the vehicle was treated as worthless. This understated every option and understated them unequally, because the more expensive the vehicle the more capital was silently written off. At five years the surveyed combustion van gave up J$952,657 of unrecorded residual value against J$2,867,792 for the new electric SUV and J$1,847,578 for the used electric hatchback: an average of roughly J$1.4 million more surrendered by the electric vehicles than by the combustion vehicle, in a module whose sole purpose is to compare them. Corrected by adding the residual value on the same declining-balance basis used elsewhere in the dashboard, less any loan still outstanding at the point of sale. **The omission favoured no vehicle deliberately; it simply penalised whichever cost more, which in this comparison is always the electric one.**

Five of these six were caught by checking a figure against its source, or by asking what a model leaves out, rather than accepting a number because it was already in the dataset.

---

## 8.2 Conclusions

**1.** For the private buyer the answer is conditional. A new electric vehicle does not overtake a used petrol vehicle within ten years at typical private mileage, but the result reverses under higher mileage, home charging, or a used-electric against new-petrol pairing. This is why the output is a calculator rather than a verdict.

**2.** For the taxi operator the answer is specific and actionable. Charging arrangement produces a J$4,507,367 five-year swing, larger than the price difference between any two vehicles in the database. Counting resale value, an electric taxi is profitable over five years on every charging arrangement except the JPS evening peak, and on home or overnight charging it beats the used Probox baseline by roughly J$1.35 million. The case for depot or home charging rests on the size of the swing rather than on the alternatives losing money. See Section 6.3: an earlier version of this conclusion, produced before resale value was counted, held that only the two cheapest arrangements were profitable and that the electric taxi did not beat the Probox. Both statements were artefacts of the omission.

**3.** Electric vehicles are cleaner in Jamaica, with carbon payback of 2.0 years for a BYD Yuan Plus at the current grid, and electric buses reduce emissions by 57% against diesel. Both results are conditional on grid intensity, which the utility is not required to publish.

**4.** Fiscal policy alone has not worked. Jamaica matches The Bahamas on fuel price and Barbados on duty rate while trailing both substantially on adoption. Depth of fiscal package, the 1,000-unit cap and administrative friction are the surviving explanations.

**5.** Implementation is administratively stalled. Fifteen of 26 commitments unevidenced, the oldest overdue since December 2023, and the only fully delivered goal was funded by a utility foundation and a development bank.

**6.** Two of three targets cannot be measured from public data. That is a policy failure in itself.

---

## 8.3 Further Work

**Immediate, and low cost.**

- Request registered vehicle totals by category from Tax Administration Jamaica or the Island Traffic Authority, and licensed public passenger vehicle figures from the Transport Authority. Two emails would resolve two of three denominators.
- Request JUTC's electric bus consumption data. The pilot measured it.
- Search the Bureau of Standards Jamaica and NEPA directly. Between them they are named in seven outstanding policy actions, and neither has been contacted. A dated negative result from an official source is citable evidence of non-publication.

**Data collection.**

- An urban consumption measurement for the Nissan Tiida, to replace the single-vehicle petrol uplift factor.
- A second station price survey, to establish whether markups are stable or volatile.
- Confirmed transaction prices for used vehicles, particularly the Probox baseline.

**Dashboard.**

- Build the Route Cost Map, which was scoped in week 2 as an eighth module and subsequently dropped rather than shipped empty. It was to show operating cost per kilometre across six Kingston route-taxi corridors: Half Way Tree to Papine, Red Hills, Three Miles, Downtown Crossroads, Manor Park, and Backgate to Spanish Town. Two things blocked it. No mapping data source was agreed, and no measured corridor distances were ever collected, so the module could not have been populated without inventing the distances it displayed. The underlying cost per kilometre arithmetic already exists in the Taxi Feasibility Tool, so the work needed is data collection rather than modelling.
- Add the Chilean benchmark of 9.6 tonnes CO₂ avoided per taxi per year as a validation reference.

**Analysis.**

- Source a year-by-year Jamaican grid intensity series to replace the flat pre-2022 assumption.
- Extend the Saint Lucia and Chile entries in the regional module; both are currently thin relative to their analytical value.
- Investigate charging installer training, which Chile identifies as a barrier and which no Jamaican policy action covers.

---

## 8.4 Closing

The question this study set out to answer was whether Jamaica's 2030 electric vehicle targets are realistic. On the evidence assembled, the targets are not primarily limited by vehicle economics, consumer interest or charger availability, since utilisation of roughly 1% indicates chargers are not the constraint.

They are limited by a bounded incentive, by administrative commitments that have not been delivered, and by an inability to measure progress at all. The most consequential single finding is not any cost or emissions figure. It is that two of the three targets Jamaica set itself cannot be evaluated from anything Jamaica publishes.
