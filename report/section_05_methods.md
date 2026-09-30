# Section 5: Methods

---

## 5.1 Currency and Price Basis

All Jamaican calculations are performed in Jamaican dollars, because every underlying source is natively JMD: Petrojam prices, the station survey, charging tariffs, dealer prices and loan terms. Converting to USD internally would introduce an exchange rate into calculations that do not require one.

Cross-country comparisons are presented in **US dollars**, for the opposite reason. Comparing Uruguay with Brazil through the Jamaican exchange rate would make every foreign figure move whenever the JMD moved. The regional module therefore uses USD throughout.

**Effective retail fuel price** is the quantity used in every cost calculation:

```
retail price = Petrojam reference price + station markup
```

The Petrojam reference already includes Special Consumption Tax. Markup is taken either from the user's own entered pump price, a specific surveyed station, or the Kingston survey average. For 90 octane in mid-2026 this gives approximately J$247 per litre against a Petrojam reference of J$213.

## 5.2 Total Cost of Ownership

For each vehicle and each year *y* of ownership:

```
cumulative cost(y) = depreciation to date + (annual energy + annual maintenance) × y
```

Depreciation applies a first-year rate and a subsequent-year rate to the purchase price. Annual energy cost is distance × consumption × the applicable price per unit. Where a mixture of home and public charging is specified, the effective electricity price is weighted accordingly.

The **crossover point** is found by linear interpolation between the years bracketing the sign change in the cost difference, and reported in years and months.

## 5.3 Emissions

Tailpipe and grid emissions:

```
annual ICE CO₂ = distance × (L/100km ÷ 100) × 2.31 kg/L
annual BEV CO₂ = distance × (kWh/100km ÷ 100) × grid intensity
```

using 2.31 kg CO₂ per litre for petrol and 2.68 for automotive diesel, with grid intensity selected from the three IRP scenarios.

### 5.3.1 Battery Manufacturing Premium

Carbon payback requires the *difference* in manufacturing emissions between an electric vehicle and the combustion vehicle it replaces, not the electric vehicle's total. Under the standard simplifying assumption that the body shell of a BEV and an equivalent ICE vehicle carry comparable production emissions, and that the electric motor and inverter approximately offset the engine, gearbox, exhaust and fuel system they replace, the difference reduces to the battery pack:

```
manufacturing premium (tonnes) = battery capacity (kWh) × intensity (kg CO₂e/kWh) ÷ 1000
```

Intensity is 68 kg CO₂e/kWh for China-manufactured packs and 60 for Europe and the United States, from Bieker (2021). Japanese and Korean packs are assigned the 60 figure as the nearest published analogue, which is an assumption rather than a sourced value.

This yields, for example, 3.39 tonnes for a 49.92 kWh BYD Yuan Plus.

**Limitation.** The glider-parity assumption is a simplification. Electric vehicles are typically heavier and use more aluminium, so the true premium is somewhat above the battery-only figure. These values should be read as a lower bound.

**Used vehicles.** Manufacturing emissions for a used import are amortised by remaining service life, on an assumed 15-year vehicle life, on the reasoning that a 2019 vehicle imported in 2026 did not cause its battery to be manufactured in 2026. A seven-year-old Nissan Leaf therefore carries 8/15 of its full 2.40 tonne premium, or 1.28 tonnes. Fleet-level calculations use the unamortised figure, because those vehicles are being newly manufactured somewhere in the world.

## 5.4 Taxi Feasibility

Annual revenue is trips per day × fare × working days per week × 52. Against it are set energy cost, maintenance and loan repayment, with the loan amortised by standard monthly payment formula and the deposit charged at year zero. Cumulative net income is tracked year by year, and crossover against a petrol baseline calculated as in 5.2.

**Consumption basis.** All figures in this module are urban-basis, because Kingston route taxi work is stop-and-go by definition, whereas the vehicle database is combined-basis for private-buyer comparison. Where a real urban measurement exists it is used directly. Where none exists, the combined figure is scaled by an uplift derived from the vehicles that have both: 1.41 for petrol, from inCarDoc Toyota Probox data, and 1.15 for electric, averaging the BYD Yuan Plus and Nissan Leaf observations.

**These uplifts are assumptions**, and the petrol factor rests on a single vehicle. Nine of twelve vehicles in this module carry derived rather than measured consumption, and are marked as such in the interface with dotted rather than solid plot lines.

## 5.5 National Fleet Projection

Adoption follows a logistic S-curve parameterised by steepness and midpoint year, applied separately to three streams with their own fleet sizes, distances, consumption figures and 2030 targets. Emissions avoided is the difference between the all-combustion counterfactual and the mixed fleet. Revenue foregone is new electric vehicles multiplied by the per-vehicle difference in import revenue.

The three streams use different fuel chemistry: petrol at 2.31 kg CO₂/L for private and government, diesel at 2.68 for public transport, and separate consumption figures for each. Section 6.4 explains why this matters more than it appears to.

## 5.6 Fleet Emissions Counterfactual

A separate calculation asks what emissions would be at any chosen level of private fleet electrification, in both directions.

**Retrospective**, 2015 to 2026, interpolates fleet size between the 2015 CEIC/OICA anchor of 190,000 and the current estimate, and values avoided fuel at each year's actual Petrojam annual mean, giving a monetary result grounded in real historic prices rather than an assumption.

**Forward**, 2026 to 2035, grows the fleet at 2.5% annually and holds fuel price flat, because this study has no defensible fuel price forecast.

Battery manufacturing is charged as a one-off at period start, using an assumed 55 kWh average pack.

**Limitation.** Grid intensity is held at the 2022 value of 0.474 for all pre-2022 years, because no year-by-year Jamaican series was obtained. The pre-LNG grid was dirtier, so retrospective avoided emissions are an upper bound. A UNEP DTU and OLADE study places Jamaica's 2015 grid at 0.7324 t CO₂/MWh on an operating-margin basis; substituting a declining series reduces avoided emissions by approximately 13%.

## 5.7 Regional Comparison

Nineteen countries, fourteen Caribbean. Fields are left empty rather than estimated where no source exists, which is why nine countries appear in the summary table but not on the charts. Caribbean fuel prices all come from a single May 2026 compilation, because pump prices are only comparable if collected on the same date on the same basis.

## 5.8 Route Cost Map

The Route Cost Map costs a single journey over a corridor that was driven during data collection. It joins two layers with different provenance, and the interface labels which is which. Energy over the route comes from EVRange, an external model built by a colleague from the same field runs. Money and emissions are computed by this study from the prices in Sections 5.1 and 5.3.

### 5.8.1 Energy Model

EVRange (2026) is a physics-based range model calibrated on the Jamaican road network. It is unpublished, and the description below is a summary of the account its author supplied for this report (R. Brown, personal communication, August 7, 2026), reproduced in full in Appendix A.

The model divides a route into segments of roughly 500 m on long road steps, or down to individual waypoints on steps shorter than 3 km, and sums the energy demand of each. Per segment it evaluates aerodynamic drag, rolling resistance, the work done against gravity on a climb, and the energy recovered by regenerative braking both on descents and when decelerating to a stop. Cabin cooling is treated as a load that rises with ambient temperature, from nothing at 22 °C to full capacity at 38 °C. Stop-start overhead is represented by an idle fraction tied to segment speed, from 0.35 below 20 km/h down to 0.02 at highway speed.

The physics output is then scaled by a piecewise terrain correction fitted to measured BYD Yuan Plus runs on three Jamaican corridors: the T1 highway, Red Hills, and Spur Tree Hill. On near-flat gradients the correction interpolates between an urban anchor of 0.70, fitted on Kingston runs, and a highway anchor of 1.09, fitted on the T4 run at 83 km/h. The four conditions exposed as controls in the interface act on the model as follows: ambient temperature scales the cooling load; driving mode multiplies the final consumption by 0.93 for eco, 1.00 for normal or 1.10 for sport; cargo mass and passenger count enter the vehicle mass in every force term; and the tyre pressure factor scales the rolling resistance coefficient.

Two points follow from this for how the results should be read. First, the terrain correction was fitted on one vehicle. Results for the BYD Yuan Plus carry the least model uncertainty of anything the module can produce. Results for the Nissan Leaf use the Leaf's own mass and drag terms but inherit a correction fitted on a different car, and the interface says so beside the vehicle selector. Whether the Leaf has a calibration of its own is a question that has been put to the model's author and not yet answered. Second, the model reports energy at the wheels. A charging tariff bills energy into the vehicle, and the difference between the two is charger and pack loss of roughly 10 to 15 per cent, which this study has not measured. No loss factor is applied, so the electric cost is a lower bound and the interface states this beneath every result.

### 5.8.2 Cost and Emissions Layer

For the electric vehicle:

```
energy (kWh) = distance (km) × consumption (Wh/km) ÷ 1000
electric cost = energy × charging rate
```

where the charging rate is the home tariff or the public rate chosen in the global settings, so that the same journey cannot cost a different amount here and in the calculator of Section 5.2. For the petrol comparison:

```
litres = distance × (L/100km ÷ 100)
petrol cost = litres × effective retail price
```

using the effective retail price of Section 5.1 and a Toyota Probox consumption figure that is an editable input, defaulting to 7.6 L/100km combined with 10.7 urban offered as the alternative. Emissions follow Section 5.3. The comparison is asymmetric by construction: the electric figure varies with gradient, speed and temperature through the model, while the petrol figure is one consumption value applied to the whole route. On a steep or congested corridor this understates petrol consumption and therefore understates the saving; on a flat highway run it overstates both. The interface records which petrol figure was used with every result.

### 5.8.3 Tolls

EVRange reports whether a route touches a Highway 2000 toll corridor. The detection is geometric, by bounding boxes over the T1 (Portmore) and T2 (May Pen) corridors, not from a live toll feed, and the model returns only a flag, not an amount or a plaza. Toll cost is therefore this study's addition. The only rate verified is the Portmore plaza Class 1 non-tag rate of J$400, effective 1 August 2026 (Jamaica Observer, 2026; TransJamaican Highway, 2026), and it is applied only on the one preset corridor known to cross that plaza, added equally to both vehicles. A route flagged by the model that is not known to cross Portmore is costed at zero, and the result says so, because the rates at the Vineyards, May Pen and Williamsfield plazas have not been sourced and charging a rate from the wrong plaza would be worse than charging none.

### 5.8.4 Availability and Caching

The model runs on its author's own hardware with no guarantee of uptime, and its author asked that requests be kept under 20 per minute. The dashboard therefore does not depend on the model being reachable. Responses for every preset corridor and vehicle at the default conditions are fetched once, stored in the repository, and served from disk. The model is called live only for input combinations that were not pre-fetched, with calls spaced to stay under the limit across all server processes, and each live response is added to the cache. When neither cache nor model is available, the page shows synthetic placeholder figures under a red banner stating that they must not be quoted. Placeholder output is excluded from the report by a guard in the code, and no figure in this document derives from it.

Corridors are offered as presets rather than through a free-text search, for the reason given in Section 8.3: every corridor on offer corresponds to a run with recorded consumption, so model output can be compared against what the vehicle measured. That comparison depends on the model's server being live and on the author's full run sheet, neither of which had been received at the time of writing, so no such comparison is reported here.

## 5.9 Implementation

Python 3.11 with Plotly Dash. Vehicle data is held in a single module so that prices, battery capacities and maintenance figures cannot drift between modules. Derived quantities such as the manufacturing premium are computed by function rather than stored, so that correcting an input propagates automatically.
