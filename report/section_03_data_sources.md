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

**Petrojam reference fuel prices.** A 611-row weekly series covering January 2015 to August 2026 for 87 octane, 90 octane and automotive diesel. This is the ex-refinery reference price and already includes Special Consumption Tax. It is the base for all fuel cost calculations and for the historic price module.

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

**EVRange.** A physics-based electric vehicle range model built by a colleague from the same field runs, calibrated on BYD Yuan Plus measurements over the T1 highway, Red Hills and Spur Tree Hill (EVRange, 2026). It supplies the distance, duration and energy consumption for each corridor in the Route Cost Map; the cost layer on top of it is this study's. The model is unpublished and runs on its author's own hardware, so the dashboard serves cached responses rather than depending on it being reachable. Its author also supplied start and end coordinates for three measured corridors and a written description of the model, reproduced in Appendix A. Section 5.8 sets out how it is used and what its calibration does and does not cover.

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
