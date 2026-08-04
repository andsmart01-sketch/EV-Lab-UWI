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

### 8.1.5 Methodological Limitations

**Glider parity.** The manufacturing premium assumes the body shell and non-battery drivetrain of a BEV and an equivalent ICE vehicle carry comparable production emissions. Electric vehicles are heavier and use more aluminium, so the derived premium is a lower bound.

**Historic grid intensity.** Pre-2022 grid intensity is held flat at 0.474 kg CO₂/kWh because no year-by-year Jamaican series was obtained. The pre-LNG grid was dirtier, so retrospective avoided emissions are an upper bound; substituting a declining series reduces them by approximately 13%.

**Bus figures are not Jamaican.** The 135 kWh/100 km and 55.5 L/100 km figures come from Knoxville Area Transit data. The vehicle class matches, but Jamaican terrain, traffic and continuous air-conditioning load differ. JUTC measured its own consumption during the pilot and has not published it.

**Barbadian adoption figures are dealer-reported**, not registry data, and Barbados has a substantial used-import channel. They are not strictly the same measure as the IEA sales-share figures used for other countries.

### 8.1.6 Regional Data Sparsity

Nine of nineteen countries appear in the summary table but on neither chart, because no published battery electric vehicle sales share exists for them. Caribbean vehicle registries do not generally publish it. Fields were left empty rather than estimated, which is why the regional charts look sparser than the table.

### 8.1.7 Errors Identified and Corrected During the Study

Recorded because the pattern is instructive rather than to catalogue mistakes.

**The electric bus error.** A finding that electric buses would increase emissions on Jamaica's grid was produced, circulated, and then found wrong. The cause was a partial correction: the electric consumption figure was fixed from a car value to a bus value, while the diesel figure beside it, also a car value, was not checked. Corrected, electric buses reduce emissions by 57%. **A partial correction produced a confident result from an internally inconsistent comparison, which is more dangerous than no correction.**

**The manufacturing CO₂ conflation.** Values labelled as the electric-over-combustion premium were consistently 2.2 to 2.4 times the battery production emissions implied by any published source, indicating they were whole-vehicle cradle-to-gate totals. Used as premiums they roughly doubled every carbon payback figure.

**The 6,606 figure.** Recorded as Jamaica's electric vehicle fleet total. It is a twelve-month import flow and the source series explicitly includes hybrids.

**A stale Trinidad fuel price.** A value of US$0.40 per litre, years out of date, supported a confident and entirely false conclusion about why Trinidad's zero-duty regime had not produced adoption. The verified May 2026 figure is US$1.14.

Three of these four were caught by checking a figure against its source rather than accepting it because it was already in the dataset.

---

## 8.2 Conclusions

**1.** For the private buyer the answer is conditional. A new electric vehicle does not overtake a used petrol vehicle within ten years at typical private mileage, but the result reverses under higher mileage, home charging, or a used-electric against new-petrol pairing. This is why the output is a calculator rather than a verdict.

**2.** For the taxi operator the answer is specific and actionable. Charging arrangement produces a J$4.5 million five-year swing, larger than any vehicle price difference. Only home charging and JPS overnight are profitable. An electric taxi without depot or home charging is not currently viable, and even with it does not yet beat a used Probox over five years.

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

- Complete the Route Cost Map, the one unbuilt module. Corridor data has been identified: Half Way Tree to Papine, Red Hills, Three Miles, Downtown Crossroads, Manor Park, and Backgate to Spanish Town.
- Add depreciation and resale value to the taxi module. Their absence currently penalises the electric case in a five-year comparison.
- Add the Chilean benchmark of 9.6 tonnes CO₂ avoided per taxi per year as a validation reference.

**Analysis.**

- Source a year-by-year Jamaican grid intensity series to replace the flat pre-2022 assumption.
- Extend the Saint Lucia and Chile entries in the regional module; both are currently thin relative to their analytical value.
- Investigate charging installer training, which Chile identifies as a barrier and which no Jamaican policy action covers.

---

## 8.4 Closing

The question this study set out to answer was whether Jamaica's 2030 electric vehicle targets are realistic. On the evidence assembled, the targets are not primarily limited by vehicle economics, consumer interest or charger availability, since utilisation of roughly 1% indicates chargers are not the constraint.

They are limited by a bounded incentive, by administrative commitments that have not been delivered, and by an inability to measure progress at all. The most consequential single finding is not any cost or emissions figure. It is that two of the three targets Jamaica set itself cannot be evaluated from anything Jamaica publishes.
