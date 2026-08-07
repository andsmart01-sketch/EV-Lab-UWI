# Section 1: Project Overview

**Author:** Andrew Smart
**Institution:** University of the West Indies, Mona Campus
**Supervisor:** Dr Louis-Ray Harris, Department of Physics
**Period:** 8 June – 3 August 2026
**Status:** Final

---

## 1.1 Background

Every time a Jamaican driver fills up at the pump, a portion of that money leaves the island. Jamaica spends approximately US$1.6 billion each year importing petroleum-based fuel, and the transportation sector is the single largest reason why, accounting for 34.4% of total national petroleum consumption (Government of Jamaica, 2023). The environmental cost compounds the economic one: in 2019, transport was responsible for 21.3% of Jamaica's total greenhouse gas emissions of 11.94 million tonnes of CO₂ equivalent (Government of Jamaica, 2023).

In direct response to this dependency, the Government of Jamaica published its National Electric Vehicle Policy in June 2023, setting targets of 12% electric vehicle penetration among privately owned vehicles, 16% among public transport, and 100% of the government fleet by 2030, alongside a goal of approximately 50% renewable electricity generation by the same year (Government of Jamaica, 2023). The ambition is clear. What no publicly available tool currently answers is whether these targets are financially realistic for ordinary Jamaican drivers, and whether electrifying the country's taxi and public passenger vehicle fleet is economically viable under present conditions.

The scale of the distance still to be travelled is difficult to state precisely, and that difficulty is itself a finding of this study. The policy recorded 150 registered electric vehicles and 25 public charging points as of late 2022 (Government of Jamaica, 2023). By mid-2026 the charging position had improved substantially, with two competing networks operating roughly 110 public charging points between them. The vehicle position remains genuinely unclear, because Jamaica does not publish a count of battery electric vehicles separately from hybrids. Section 6 examines this measurement gap in detail.

---

## 1.2 Research Objectives

This eight-week study is designed to produce a data-driven, quantitative answer to that problem. Specifically, it aims to:

1. Quantify and compare the total cost of ownership of battery electric vehicles (BEVs) against internal combustion engine (ICE) vehicles under current Jamaican fuel prices, electricity tariffs and vehicle acquisition costs.
2. Model the environmental impact of passenger fleet electrification under both the current Jamaican grid emissions intensity and the government's projected 2030 renewable scenario, including the carbon cost of battery manufacture.
3. Assess the economic feasibility of electrifying Jamaica's taxi and public passenger vehicle fleet, accounting for financing, maintenance and the choice of charging tariff.
4. Situate Jamaica's transition within the Caribbean and wider Latin American context, identifying where Jamaica leads and where it lags.
5. Audit the implementation status of the 2023 National Electric Vehicle Policy against publicly available evidence.
6. Deliver all findings through an interactive dashboard usable by both policy planners and private consumers making real purchasing decisions.

**Scope exclusion.** Hybrid electric vehicles, whether conventional or plug-in, are excluded throughout. The 2030 targets concern electric vehicles, and including hybrids would make the comparison incoherent. This exclusion matters more than anticipated: Section 6 shows that Jamaica's most widely cited "EV" import figure includes hybrids and therefore cannot be used to measure a target that excludes them.

---

## 1.3 Who This Research Is For

This project serves two audiences whose needs differ substantially.

**Private car owners** face a concrete financial question: given current fuel prices, electricity rates and the upfront premium on electric vehicles, does switching make financial sense? The answer depends on individual driving patterns, annual distance and access to charging, all of which differ from driver to driver. The dashboard therefore includes a consumer calculator taking the user's own vehicle, usage and charging arrangements, and returning a personalised cost comparison and the point at which the electric vehicle overtakes.

**Public and fleet transit operators** face different constraints: route distances, passenger throughput, financing terms and access to fleet-scale charging. These operators work on thin margins in a sector already under pressure. For them the question is not only whether electric vehicles are cheaper to run, but whether the capital cost is manageable. Section 6 reports the central finding for this audience, which is that the viability of an electric taxi in Jamaica depends less on the vehicle than on when the operator is able to charge it.

---

## 1.4 Deliverables

1. **An interactive dashboard** of seven modules built in Python using Plotly Dash, covering policy tracking, regional comparison, consumer cost comparison, taxi feasibility, national fleet projection, emissions, and historic fuel prices. A route cost map was scoped early in the project but was not built, for the reasons given in Section 8.3, and does not form part of the delivered dashboard.
2. **A user guide** presenting each module with step-by-step operating instructions, written for a reader with no technical background.
3. **This report**, presenting methods, results, policy analysis and limitations.

Print-ready posters can be exported from dashboard outputs as required.

---

## 1.5 Scope and Approach to Uncertainty

The study covers light passenger vehicles and public passenger vehicles operating in Jamaica, with comparative data from the wider Caribbean and Latin America. All cost and emissions figures reflect conditions during the June to August 2026 collection period. Fuel prices, electricity tariffs and vehicle availability are subject to change, and the dashboard is built to be updated rather than to be a fixed snapshot.

This report states its uncertainties explicitly rather than presenting a uniform confidence it does not have. Where a figure is measured, it says so. Where a figure is derived, estimated or unverified, it says that too, and Section 8 collects these in one place.

This is not a stylistic preference. During the project a significant intermediate finding was produced and then found to be wrong once a further source was obtained. The error and its correction are documented in Section 6.4. A report presenting only its surviving conclusions would misrepresent how the analysis actually proceeded, and would leave the reader unable to judge which findings are robust and which are provisional.

Formal data requests were made to several institutions. Several went unanswered, most consequentially to the ministry responsible for the policy. Where institutional data was not forthcoming, the study used secondary sources and states their provenance. Section 3 records which requests were made and which were answered.

---

## References

Government of Jamaica. (2023). *National electric vehicle policy*. Ministry of Energy, Telecommunications and Transport.

---

*Next section: Section 2, Background and Literature Review*

---

# Section 2: Background and Literature Review

---

## 2.1 Jamaica's Structural Fuel Dependency

Jamaica's exposure to imported petroleum is not a recent development or the consequence of any single event. It is a decades-long structural feature of the economy. Transport accounts for 34.4% of national petroleum consumption and 21.3% of greenhouse gas emissions (Government of Jamaica, 2023), which means the fuel import bill and the emissions inventory are substantially the same problem viewed from two directions.

The events of 2026 around the Strait of Hormuz are best understood as the latest instance of that structural vulnerability rather than as its cause. Regional pump prices rose across most CARICOM markets between July 2025 and May 2026, with the CARICOM average moving from US$1.32 to US$1.41 per litre, an increase of about 6.9%. The global average in the same dataset rose from US$1.19 to US$1.45, an increase of about 21.8% (Energy Chamber of Trinidad and Tobago, 2026). That the regional increase was smaller than the global one reflects the varying use of subsidies, fixed pricing and tax caps across the region, not any reduction in underlying exposure.

The relevant literature point is that fuel price volatility affects an importing island economy through a different mechanism than it affects a producer. For Jamaica, a price shock is a balance-of-payments event before it is a consumer event.

## 2.2 Life-Cycle Emissions of Electric Vehicles

The claim that an electric vehicle is cleaner than a petrol equivalent is conditional, not absolute, and the conditions are the grid it charges from and the emissions incurred manufacturing its battery.

Bieker (2021) provides the standard global comparison, assessing life-cycle emissions across Europe, the United States, China and India. Two elements of that work are used directly in this study. First, battery production carbon intensity, reported as approximately 60 kg CO₂e per kWh for European and United States supply chains and 68 kg CO₂e per kWh for China and India. Second, the finding that the bulk of life-cycle emissions arise from fuel and electricity production and consumption rather than from vehicle manufacture, which is what makes grid intensity the dominant variable.

The methodological point that matters for this project is the distinction between a vehicle's total cradle-to-gate manufacturing emissions and the *premium* of a battery electric vehicle over an equivalent combustion vehicle. Carbon payback analysis requires the second quantity, not the first. Section 5 sets out how this study derives it, and Section 6.4 describes what happened when the two were previously conflated.

## 2.3 Electric Bus Energy Consumption

Public transport electrification is treated separately in the literature because bus energy consumption differs from passenger car consumption by roughly an order of magnitude, and applying car figures to buses produces results that are not merely imprecise but directionally wrong.

Gao et al. (2017), working at Oak Ridge National Laboratory, simulated electric bus operation against real Knoxville Area Transit route data and standardised drive cycles. They report electric bus consumption of 1.35 kWh/km as a real-world average, with a range of 1.24 to 2.48 kWh/km across standardised cycles, against 1.7 to 3.3 kWh/km of mechanical energy for the diesel equivalent. Critically for comparison purposes, they also report diesel *fuel* energy of 5.52 kWh/km at 32.5% engine efficiency, which converts to approximately 55.5 litres per 100 km. They further find that regenerative braking accounts for roughly 29% of the electric bus energy saving.

This paper is the source for both figures used in the public transport stream of this study's fleet model. Its applicability rests on the vehicle class matching: the bus piloted by the Jamaica Urban Transit Company is a 12-metre transit bus seating 35 with standing room for 20, which is the class the study models.

## 2.4 Caribbean Electric Vehicle Adoption

The regional literature is thinner than the global literature and unevenly distributed. UNEP (2025) provides the most useful recent overview of Caribbean e-mobility, covering Antigua and Barbuda, Barbados, Grenada, Jamaica, Saint Kitts and Nevis, and Saint Lucia, and situating national programmes within GEF-funded regional support.

Three regional observations recur and are relevant to this study's comparative work. First, small island states face charging network economics that differ fundamentally from continental markets, because short average trip distances reduce the range problem while small populations weaken the commercial case for dense infrastructure. Second, several Caribbean states have adopted fiscal incentives of comparable generosity with markedly different adoption outcomes, which suggests fiscal policy is necessary but not sufficient. Third, the CCREEE position paper on Caribbean e-mobility identifies a distinctive regional barrier in the prevalence of unofficial vehicle imports, which arrive without manufacturer warranty or spare parts access.

The comparative analysis in Section 6.2 tests the second of these observations directly using Barbados, which shares Jamaica's headline import duty rate.

## 2.5 Electrification of Small-Scale Public Transport

Chile provides the most directly relevant programme evidence for the taxi question this study addresses. The Agencia de Sostenibilidad Energética, with the Ministry of Energy and GEF funding, has run two programmes, *Mi Taxi Eléctrico* and *Más Transporte Eléctrico*, placing 405 electric vehicles into small-scale public transport across ten regions (Agencia de Sostenibilidad Energética & Centro de Movilidad Sostenible, 2026).

The reported outcomes provide external benchmarks against which this study's modelled results can be sanity-checked: average savings exceeding 3 million Chilean pesos per driver per year from lower operating costs, and more than 3,900 tonnes of CO₂ avoided annually across the replaced fleet, equivalent to roughly 9.6 tonnes per vehicle.

The barriers the Chilean study identifies are as useful as its outcomes, and all four have Jamaican analogues: delays by distribution companies in connecting residential chargers, driver distrust of the technology, digital exclusion in application processes given the age profile of drivers, and an absence of locally trained charging infrastructure installers.

## 2.6 Battery End-of-Life in the Caribbean Context

Turnbull (2024), working in the same department, reviewed Jamaica's legislative framework for electric vehicle battery management and found that no existing Act classifies electric vehicle batteries as hazardous waste. The National Solid Waste Management Act (2001) is assessed as the most relevant instrument but lacks specific provision for them, while the Transport Authority Act, Road Traffic Act and Public Health Act each address only fragments of the problem. The study recommends amendment to classify electric vehicle batteries as hazardous waste and the introduction of Extended Producer Responsibility to shift end-of-life costs from the state to importers and manufacturers.

That legislative finding is used in Section 4 of this report and corroborates, from an independent direction, the policy gaps this study identifies through implementation tracking.

## 2.7 Where This Study Sits

The existing literature establishes that electric vehicle benefits are conditional on grid intensity and battery manufacture, that Caribbean adoption varies widely under similar fiscal regimes, and that Jamaica's battery end-of-life framework is not yet fit for purpose.

What it does not provide is a Jamaica-specific, current-price, user-adjustable quantification of those conditions. The prevailing analyses either apply regional averages to Jamaica or use figures that have since gone stale. This study addresses that gap by building the comparison from Jamaican price data collected during the study period, by making the assumptions visible and adjustable rather than fixed, and by stating explicitly which inputs are measured and which are estimated.

---

## References

Agencia de Sostenibilidad Energética & Centro de Movilidad Sostenible. (2026). *Electromovilidad en el transporte público menor: resultados, impacto y lecciones de los programas Mi Taxi Eléctrico y Más Transporte Eléctrico*.

Bieker, G. (2021). *A global comparison of the life-cycle greenhouse gas emissions of combustion engine and electric passenger cars*. International Council on Clean Transportation.

Caribbean Centre for Renewable Energy and Energy Efficiency. (n.d.). *The future of e-mobility in the Caribbean* [Position paper].

Energy Chamber of Trinidad and Tobago. (2026, May 21). *Gasoline prices rise across most of CARICOM*.

Gao, Z., Lin, Z., LaClair, T. J., Liu, C., Li, J.-M., Birky, A. K., & Ward, J. (2017). Battery capacity and recharging needs for electric buses in city transit service. *Energy, 122*, 588–600.

Government of Jamaica. (2023). *National electric vehicle policy*. Ministry of Energy, Telecommunications and Transport.

Turnbull, K. (2024). *Pioneering electric mobility: A framework for EV battery management in the Caribbean* [Final report]. Department of Physics, University of the West Indies, Mona.

United Nations Environment Programme. (2025, April 7). *Caribbean leading the charge to electric mobility*.

---

# Section 3: Data Sources and Stakeholders

---

## 3.1 Approach

Every figure used in this study falls into one of four categories, and the dashboard and this report distinguish between them consistently:

| Category | Meaning |
|---|---|
| **Measured** | Collected first-hand during the study, or supplied directly by the organisation that holds it |
| **Published** | Taken from a named institutional publication with a traceable citation |
| **Derived** | Calculated from measured or published figures by a stated method |
| **Estimated** | A reasoned assumption where no source could be obtained |

The distinction matters because a reader cannot judge a conclusion without knowing which category its inputs belong to. Section 8 lists every remaining estimated input.

---

## 3.2 Measured Data

**Petrojam reference fuel prices.** A 600-row weekly series covering January 2015 to June 2026 for 87 octane, 90 octane and automotive diesel. This is the ex-refinery reference price and already includes Special Consumption Tax. It is the base for all fuel cost calculations and for the historic price module.

**Kingston retail markup survey.** A field survey of 15 Kingston service stations across three dates in June and July 2026, yielding 113 station-date-grade observations. Mean markup above the Petrojam reference was J$29 per litre for 87 octane, J$34 for 90 octane and J$48 for diesel. Station-level markups within the complete-data subset ranged from J$15 to J$65 per litre, a spread of more than fourfold.

This survey exists because the Petrojam price is not the pump price, and the difference is neither small nor uniform. Using the reference price as though it were retail understates fuel cost by roughly 16% for 90 octane.

**BYD Yuan Plus field consumption.** Weighted consumption of 16.3 kWh/100 km measured across 16 Kingston route legs in the supervisor's vehicle. This is the only Jamaican real-world electric vehicle consumption figure in the study and is used as the primary electric taxi input.

**JPS Charge 'n Go tariff schedule.** The full time-of-use rate card, read from the operator's application in July 2026. Weekday rates: J$50.11/kWh from 22:00 to 06:00, J$61.33 from 06:00 to 18:00, J$130.63 from 18:00 to 22:00. Weekend rates: J$50.11 from 00:00 to 18:00, J$61.33 from 18:00 to 22:00, J$50.11 thereafter.

---

## 3.3 Data Supplied by Organisations

**Evergo.** Confirmed directly by Delano Mighty, Senior Engineer: a flat rate of J$96 per kWh applying to all chargers, all hours and all charging levels; 71 chargers comprising 52 Level 2 and 19 Level 3 or above; average session of 21.9 kWh over 51 minutes; lifetime utilisation approximately 1%, with a peak individual charger utilisation around 9% as of June 2026.

The utilisation figures are among the most analytically valuable data obtained. They indicate the constraint on adoption is not charger availability.

**ATL Automotive.** BYD vehicle pricing confirmed July 2026 for five models, giving the study its only verified new electric vehicle prices.

**JUTC.** Electric bus count of five units, four operational, supplied through the supervisor. The company did not publish energy consumption data from its pilot despite consumption being a stated aim of the trial.

---

## 3.4 Published Institutional Sources

**Planning Institute of Jamaica.** The *Economic and Social Survey Jamaica 2022* supplies the two fleet denominators used in this study: 575,041 vehicles certified fit by the Island Traffic Authority in 2022, and 34,928 vehicles licensed for public passenger service in the same year. It also records an average of 179 buses operating monthly in the Kingston Metropolitan Transport Region, the fifth consecutive annual decline.

**Statistical Institute of Jamaica**, via reporting in the *Jamaica Observer*: 6,606 vehicles imported between July 2022 and June 2023, against 2,854 the previous year. This series is explicitly described as covering "electric vehicles including hybrids", which is why it cannot be used as a battery electric vehicle count.

**METT 2022 Integrated Resource Plan.** Grid carbon intensity of 0.474 kg CO₂/kWh for the 2022 actual generation mix, 0.380 for the 2026 IRP projection and 0.275 for the 2030 target.

**Jamaica Customs Agency.** Confirmation that electric vehicles are exempt from General Consumption Tax, cleared under Additional National Code V14.

**Government of Jamaica (2023).** The National Electric Vehicle Policy itself, the source for all targets, goals and the 26 implementation actions audited in Section 4.

Regional comparison draws on the Energy Chamber of Trinidad and Tobago's compilation of GlobalPetrolPrices data for eleven CARICOM markets, the IEA *Global EV Outlook 2026*, and per-country policy sources recorded individually in the dashboard.

---

## 3.5 Institutional Requests: Outcomes

| Organisation | Purpose | Outcome |
|---|---|---|
| Evergo | Charging tariff and utilisation | **Answered in full** |
| ATL Automotive | BYD pricing | **Answered** |
| JUTC | Bus fleet and consumption | Fleet count via supervisor; consumption not supplied |
| METT | Fleet penetration figures | **No response** |
| Tax Administration Jamaica | Registered vehicles by category | Not contacted |
| Transport Authority | Licensed public passenger vehicles | Not contacted |
| Bureau of Standards Jamaica | EV and EVSE standards | Not contacted |
| NEPA | Battery waste framework | Not contacted |

The ministry's non-response is the single most consequential gap. It is the reason the dashboard cannot display current penetration against the 2030 targets, and Section 4 sets out what could be established without it.

Three of the uncontacted bodies are, on the evidence of this study, more likely to hold usable data than the ministry: the Bureau of Standards Jamaica is named in three separate policy actions, NEPA in four, and the Transport Authority holds the public passenger vehicle denominator.

---

## 3.6 Fuel Prices: Published but Not Machine-Readable

Petrojam publishes its weekly ex-refinery reference prices as an HTML table at petrojam.com/price/, covering ten products across 59 pages of history. The figures are public, and the price series underpinning every fuel cost in this dashboard comes from them.

They cannot be collected automatically. Requests from a plainly identified research client are refused with HTTP 403 by an AWS load balancer, on every path tried including /robots.txt itself. The refusal is not a crawling policy: the site's robots.txt reads `User-agent: * / Disallow:`, which permits automated access, and the price page carries `meta-robots: index, follow`. The block sits in front of the site rather than in it, and appears to reject clients that do not present as a browser.

Getting past it would require the request to misrepresent itself as a browser. That was not done. A state-owned public body returning 403 to an identified client is declining, and the appropriate response to a decline is to ask rather than to change costume until the answer changes. A request has been drafted to Petrojam's public enquiries address, with the Access to Information Act as the fallback route, and it names the specific technical finding so the operator can act on it.

Two consequences follow. The price series is maintained by manual entry, with a validated paste tool and the same range and duplicate checks the automated path would have applied. And the freshness of the series depends on a person, which is recorded in Section 8 as a maintenance risk rather than presented as solved.

A separate observation is worth recording for anyone repeating this. A plain client and a browser were served *different* copies of the same page on the same day: the browser showed prices to 30 July 2026, while a plain request returned a cached copy ending 16 July. Any future automated collection needs a staleness check comparing the newest row served against the newest row already held, or it will silently collect nothing while appearing to succeed.

---

## 3.7 Data Not Obtained

The following were sought and not found in any public source:

- Any count of battery electric vehicles in Jamaica distinguishable from hybrids
- Registered vehicle totals disaggregated into private, commercial and government
- Government fleet size, or the number of electric vehicles within it
- Energy consumption from JUTC's electric bus pilot
- A year-by-year historic series for Jamaican grid carbon intensity
- Confirmed transaction prices for used vehicles, as distinct from asking prices

Each absence has a consequence recorded in Section 8.

---

# Section 4: EV Policy Gap Analysis

---

## 4.1 Method

The 2023 National Electric Vehicle Policy sets out commitments across six goals. This study tracked 26 of them, comprising the implementation actions in the policy document together with its three headline 2030 fleet targets, and assessed each against publicly available evidence as at July 2026.

Each action carries one of six statuses, mapped to the policy's own achievement language:

| Status | Meaning |
|---|---|
| Confirmed | Fully achieved |
| In progress | Mostly achieved |
| Partial | Somewhat achieved |
| Not confirmed | Little achieved, or no public evidence located |
| Not implemented | Same as or worse than baseline |
| Not started | No score available |

The distinction between "Not confirmed" and "Not implemented" is deliberate and important. "Not confirmed" reports an absence of public evidence, which is not the same as evidence of absence. Where this study checked a specific document and found the relevant content missing, that is stated as such and carries more weight.

## 4.2 Overall Position

Of 26 tracked commitments as at July 2026:

| Status | Count |
|---|---|
| Confirmed | 1 |
| In progress | 1 |
| Partial | 7 |
| Not confirmed | 15 |
| Not implemented | 1 |
| Not started | 1 |

Fifteen of the 26 carry a cited source. The remaining eleven rest on unsuccessful searches.

## 4.3 Goal-by-Goal

**Goal 1: Import standards and registration.** Three partial, three not confirmed. The policy defines "setting the technical requirements to import electric vehicles" principally as an age limit of three years from manufacture. That threshold is operative, since only vehicles under three years old qualify for the reduced duty, and it has since been written into law for a second vehicle class by the Road Traffic (Licence Duties) Order 2024. What has not been delivered is the National Electric Vehicle Import Guideline the policy requires, and the Customs pages a prospective importer would consult carry no EV-specific guidance.

**Goal 2: Charging infrastructure.** One partial, three not confirmed, all now past their June 2026 deadline. No national charging deployment plan was traced. The Office of Utilities Regulation consulted on electric vehicles in 2021, producing preliminary recommendations and drawing a formal response from JPS, but that process predates the policy. Charging network growth is occurring commercially rather than under a published national plan.

**Goal 3: Charging network operation.** Two not confirmed, both due June 2028 and therefore not yet overdue.

**Goal 4: Battery end-of-life.** One partial, three not confirmed, one not started. This is the weakest goal. The draft Green Paper covering electric vehicle batteries went to Cabinet in December 2020 and was never finalised; the operative instrument remains the 2018 hazardous waste policy, which predates the EV policy. Turnbull (2024) independently finds that no Act classifies electric vehicle batteries as hazardous waste.

One control has arrived, but from outside the policy. From 1 January 2025, exporting electrical and electronic waste from Jamaica requires the Prior Informed Consent procedure under the 2022 Basel Convention amendment, with NEPA obtaining approval from transit and importing states before issuing a permit. Its scope covers batteries used in motor vehicles. This is a treaty obligation, not a policy delivery.

**Goal 5: Skills and training.** One confirmed, one in progress, one partial. The only goal substantially delivered. Project eDrive, funded by the JPS Foundation and IDB Lab, runs two NVQ-J programmes through HEART/NSTA Trust for 200 technicians, with 15 instructors holding UK Institute of the Motor Industry certifications following a 2022 train-the-trainer programme. Jamaica was the first Caribbean country to establish an IMI-certified electric vehicle training programme. Three HEART/NSTA campuses are equipped and delivering.

**Goal 6: Adoption, incentives and targets.** One partial, four not confirmed, one not implemented. The Low Emission Zone commitment is the single item recorded as not implemented, its June 2024 deadline passed with no gazette notice located.

## 4.4 The Four Structural Gaps

Grouping the individual findings produces four categories more useful than a list.

**Measurement.** Jamaica does not publish a count of battery electric vehicles distinguishable from hybrids, does not disaggregate its fleet into private, commercial and government, and publishes nothing at all about the government fleet. JUTC has not published consumption data from its bus pilot. The consequence is that two of three headline targets cannot be measured even in principle from public data.

**Standards not issued.** No lithium-ion battery quality standard; no battery health threshold for used imports; no charging equipment safety standard; no interoperability standard; no Low Emission Zone; no published implementation plan for the policy itself.

**Delivery by others.** Charging built commercially by JPS and Evergo. Training delivered by a utility foundation and a development bank. Recycling handled by a private company exporting abroad. The one battery transport control arriving via an international treaty.

**Design limits.** The reduced import duty was capped at 1,000 units. A cap of that magnitude cannot produce a 12% share of a fleet in the hundreds of thousands, which means the principal incentive is bounded by design rather than by uptake. A dealer interviewed by the *Jamaica Observer* reported importing vehicles that proved not to qualify for the concession, discovering this only on arrival, which is the predictable consequence of the missing import guideline.

## 4.5 What Can Actually Be Measured

Using the *Economic and Social Survey Jamaica 2022* denominators, one target becomes measurable:

**Public transport, 16% by 2030.** Jamaica licensed 34,928 public passenger vehicles in 2022. JUTC operates five electric buses, four in service. That is approximately **0.014%** of the licensed fleet. Measured against JUTC's own operable fleet of roughly 350 buses it is **1.4%**.

**Private vehicles, 12% by 2030.** Of 575,041 vehicles certified fit in 2022, 34,928 were public passenger vehicles, leaving approximately 540,000 private, commercial and government vehicles combined. Because these are not disaggregated and no battery electric vehicle count exists, no share can be calculated.

**Government fleet, 100% by 2030.** Neither numerator nor denominator is public.

## 4.6 Assessment

The evidence does not support a characterisation of Jamaica as either on track or simply behind. A more accurate reading is **fiscally active and administratively stalled**.

The fiscal instruments were delivered promptly and have been extended: duty reduced from 30% to 10%, licence fees waived, General Consumption Tax exempted, and the framework widened to electric bikes by the Road Traffic (Licence Duties) Order 2024. The administrative commitments, the standards, guidelines, plans and disclosure requirements, are largely outstanding, and the goal that did succeed succeeded because a utility foundation and a development bank funded it.

That pattern, rather than the aggregate count of incomplete actions, is the substantive finding of this section.

---

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

## 5.8 Implementation

Python 3.11 with Plotly Dash. Vehicle data is held in a single module so that prices, battery capacities and maintenance figures cannot drift between modules. Derived quantities such as the manufacturing premium are computed by function rather than stored, so that correcting an input propagates automatically.

---

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
| Home, JPS residential | 42.00 | **+J$4,367,089** |
| JPS overnight | 50.11 | +J$3,954,647 |
| Evergo, flat | 96.00 | +J$1,620,865 |
| JPS evening peak | 130.63 | −J$140,278 |

**A J$4.5 million swing produced by a scheduling decision**, larger than the price difference between any two vehicles in the database.

A driver charging on the JPS evening peak pays 2.6 times what the same driver pays overnight on the same network, and 36% more than Evergo's flat rate.

Petrol comparison: a used Toyota Probox returns J$3,018,547 over the same period. A **late-model Probox at J$2.3 million returns J$2,533,140**, less than the older unit, because the additional J$650,000 of purchase price is not recovered by lower servicing and slower depreciation within five years. Buying a fresher petrol taxi is not a better decision than keeping an older one.

### A correction that changed two conclusions

The figures above are restated. An earlier version of the taxi model tracked cash flow only and therefore treated the vehicle as worthless on the last day of the ownership period. Adding the resale value, less any loan still outstanding, raises every electric figure by J$3,587,737 and the Probox figures by J$952,657 and J$1,212,180 respectively.

Two conclusions reverse.

**Evergo becomes viable.** At a flat J$96/kWh the operator was previously J$1,966,872 down over five years. Counting the asset they still own, they are J$1,620,865 up. The earlier claim that only the two cheapest arrangements are profitable was an artefact of the omission. Only the JPS evening peak now loses money, and it loses only J$140,278, which is close enough to breakeven that it should be read as "no better than not doing it" rather than as a clear loss.

**The electric taxi overtakes the Probox.** On home charging the BYD Yuan Plus returns J$4,367,089 against the used Probox's J$3,018,547, a margin of J$1,348,542. The earlier finding that an electric taxi "does not yet beat a used Probox over five years" was wrong, and wrong in a specific direction: the omission penalised whichever vehicle cost more, and the electric vehicle costs 4.6 times the Probox.

**What did not change is the headline.** The swing between best and worst charging arrangement is J$4,507,367 before the correction and J$4,507,367 after it, to the dollar. Resale value does not depend on when the operator charges, so it adds the same constant to all four rows. The study's clearest finding is unaffected by its most consequential error, which is worth stating plainly because it would be easy to present the correction as either more or less damaging than it was.

The revised conclusion for this audience: an electric taxi in Jamaica is profitable over five years on any charging arrangement except the evening peak, beats the used Probox baseline when charged at home or overnight, and remains acutely sensitive to charging discipline. The case for depot or home charging rests on the size of the swing, not on the alternatives being unprofitable.

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

---

# Section 7: Discussion

---

## 7.1 The Central Argument

The results support a single connected argument.

Jamaica's electric vehicle transition is **fiscally active and administratively stalled**, and the consequences of that imbalance fall hardest on the users the policy is meant to serve.

The fiscal instruments arrived promptly and have been extended: duty reduced from 30% to 10%, licence fees waived, General Consumption Tax exempted, and the framework widened to electric bikes in December 2024. Those are real, dated, verifiable measures.

The administrative instruments have not arrived. No import guideline, no battery standard, no charging equipment standard, no interoperability standard, no Low Emission Zone, no national deployment plan, no published implementation plan, and no requirement on the utility to disclose grid carbon intensity. Fifteen of 26 tracked commitments remain unevidenced, and the four in Goal 1 that would tell an importer what qualifies are among the oldest overdue.

Meanwhile the progress that has occurred came from outside the state. Charging was built commercially by JPS and Evergo. Technician and first-responder training was delivered by the JPS Foundation and the Inter-American Development Bank. Battery collection is run by a private company exporting abroad. The one battery transport control that now exists arrived through a Basel Convention obligation. Four independent instances, all pointing the same way.

## 7.2 Why Fiscal Policy Alone Has Not Worked

The regional comparison isolates the variables unusually cleanly.

Jamaica and The Bahamas pay the same US$1.46 per litre, and Bahamian adoption is roughly four times higher. Jamaica and Barbados levy the same 10% import duty, and Barbadian adoption is roughly seven times higher. Trinidad and Tobago charges zero duty with below-average fuel prices and has not visibly moved. Neither fuel price nor headline duty rate explains the pattern.

Three explanations survive the comparison.

**Depth versus headline.** Barbados layers a four-year excise and VAT holiday, accelerated corporate write-offs and interest-free loans for public officers on top of its 10%. Jamaica matched the headline rate and largely stopped. The next Jamaican fiscal move, if there is one, is more plausibly excise and consumption tax relief than a further duty cut.

**The unit cap.** Jamaica's concession was capped at 1,000 units, justified as limiting revenue loss to J$18 million over five years. A cap of that size cannot deliver 12% of a fleet of several hundred thousand. The principal incentive is bounded by design rather than by demand, which is a different and more tractable problem than consumer reluctance.

**Administrative friction.** A dealer reported importing vehicles that proved ineligible for the concession, discovering this only on arrival, and described the concession as "a non-starter". That is the predictable operational consequence of the missing import guideline. An incentive a buyer cannot confidently claim in advance is worth less than its nominal value.

## 7.3 The Charging Finding and What It Implies

The taxi results show a J$4.5 million five-year swing produced entirely by when the operator charges. Home charging at J$42 and JPS overnight at J$50.11 are profitable; Evergo's flat J$96 and JPS evening peak at J$130.63 are not.

Three implications follow.

For **operators**, the vehicle choice matters less than the charging arrangement. An electric taxi without depot or home charging is not currently a viable proposition in Jamaica on a five-year horizon.

For **policy**, this is the most actionable finding in the study. Depot charging infrastructure for public passenger vehicle operators would do more for the 16% target than a further duty reduction, because it converts an unprofitable proposition into a profitable one without any change to vehicle price. Barbados's low-interest revolving fund for public service vehicle operators is a precedent.

For **the tariff itself**, a 2.6-fold intraday spread is a powerful behavioural instrument that is currently invisible to most buyers. No consumer-facing tool in Jamaica exposed it before this dashboard, and a driver who does not know the spread exists cannot respond to it.

## 7.4 Emissions: Conditional, Not Categorical

Carbon payback of 2.0 years for a BYD Yuan Plus at the current grid is a robust result, and considerably better than this project believed at its midpoint. It rests on deriving the manufacturing premium from battery capacity rather than charging a whole-vehicle total.

The corrected bus finding of a 57% reduction restores the case for public transport electrification, and holds even on the worst-case drive cycle.

Both results, however, are conditional on grid intensity, and Jamaica has no requirement on its utility to publish it. The same electric bus can be shown as substantially cleaner or marginally worse depending on which assumption is applied. That makes the missing disclosure requirement a substantive analytical gap rather than an administrative one, and it is the reason this study reports emissions under three explicit grid scenarios rather than one headline number.

## 7.5 Measurement as a Policy Failure

Two of the three headline targets cannot be measured from public data. Not measured with difficulty: measured at all.

Jamaica does not publish a battery electric vehicle count distinguishable from hybrids. The most cited figure, 6,606 for July 2022 to June 2023, is a twelve-month import flow explicitly covering "electric vehicles including hybrids". It is neither a stock nor purely electric, yet it circulates widely as though it were both. Fleet totals are not disaggregated into private, commercial and government. Nothing at all is published about the government fleet.

A target that cannot be measured cannot be managed, and its absence of reporting is a finding in itself. It also means any confident public claim about Jamaican electric vehicle penetration should be treated with suspicion, including claims in this report, which is why Section 6 reports what can be measured and states plainly what cannot.

## 7.6 Recommendations

**For policy.**

1. Publish a battery electric vehicle count separate from hybrids, and disaggregate registered vehicles into private, commercial and government. Nothing else in the policy can be evaluated until this exists.
2. Replace or substantially raise the 1,000-unit concession cap, which cannot deliver the target it supports.
3. Publish the National Electric Vehicle Import Guideline. It is more than two years overdue and its absence is producing documented commercial harm.
4. Prioritise depot charging for public passenger vehicle operators over further vehicle-side incentives. The evidence in Section 6.3 indicates this is where the 16% target is won or lost.
5. Require the utility to publish grid carbon intensity, without which no environmental claim can be independently verified.
6. Amend the National Solid Waste Management Act to classify electric vehicle batteries as hazardous waste, and introduce Extended Producer Responsibility, as Turnbull (2024) recommends.

**For consumers and operators.**

7. Charge overnight. On the JPS network this is the difference between a profitable and an unprofitable electric taxi.
8. Treat charging arrangements as part of the purchase decision, not an afterthought.

## 7.7 Contribution

This study provides the first Jamaica-specific, current-price, user-adjustable quantification of the electric vehicle cost and emissions question, built from prices collected during the study period rather than regional averages.

Its more durable contribution may be methodological. Several widely circulated Jamaican electric vehicle figures do not withstand checking: the 6,606 import figure is routinely presented as a fleet count, JUTC bus numbers vary between sources, and a stale Trinidad fuel price of US$0.40 supported an entirely false conclusion until corrected against a May 2026 compilation. Two errors within this project's own analysis were caught the same way, by checking a figure against its source rather than accepting it because it was already in the dataset.

---

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
