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

1. **An interactive dashboard** of eight modules built in Python using Plotly Dash, covering policy tracking, regional comparison, consumer cost comparison, taxi feasibility, route cost mapping, national fleet projection, emissions, and historic fuel prices. The route cost map was scoped early, set aside when no measured corridor distances existed to populate it, and built once sixteen measured route-taxi runs had been collected. Section 8.3 records what remains open on it.
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
