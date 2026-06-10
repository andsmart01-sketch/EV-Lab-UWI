# Section 1: Project Overview

**Author:** Andrew Smart  
**Institution:** University of the West Indies, Mona Campus  
**Supervisor:** [Supervisor Name]  
**Date:** June 2026  
**Status:** Draft

---

## 1.1 Background

Every time a Jamaican driver fills up at the pump, a portion of that money leaves the island. Jamaica spends approximately US$1.6 billion each year importing petroleum-based fuel, and the transportation sector is the single largest reason why, accounting for 34.4% of total national petroleum consumption (Government of Jamaica, 2023). The environmental cost compounds the economic one: in 2019, transport was responsible for 21.3% of Jamaica's total greenhouse gas emissions of 11.94 million tonnes of CO₂ equivalent (Government of Jamaica, 2023).

In direct response to this dependency, the Government of Jamaica published its National Electric Vehicle Policy in June 2023, setting a target of 12% EV penetration among privately owned vehicles and 16% among public transport by 2030, alongside a goal of 50% renewable electricity generation by the same year (Government of Jamaica, 2023). The ambition is clear, yet what no publicly available tool currently answers is whether these targets are financially realistic for ordinary Jamaican drivers, and whether electrifying the country's taxi and public passenger vehicle fleet is economically viable under current conditions.

As of late 2022, only 150 electric vehicles were registered in Jamaica, served by 25 public charging points (Government of Jamaica, 2023). That figure represents a starting point, not a trajectory. The distance between where Jamaica is and where its own policy says it needs to be by 2030 is the central problem this research addresses.

---

## 1.2 Research Objectives

This eight-week study (June 8 – August 3, 2026) is designed to produce a data-driven, quantitative answer to that problem. Specifically, it aims to:

1. Quantify and compare the total cost of ownership (TCO) of battery electric vehicles (BEVs), plug-in hybrid electric vehicles (PHEVs), conventional hybrid electric vehicles (HEVs), and internal combustion engine (ICE) vehicles under current Jamaican fuel prices, electricity tariffs, and vehicle acquisition costs.
2. Model the environmental impact of passenger fleet electrification under both the current Jamaican grid emissions intensity and the government's projected 2030 renewable energy scenario.
3. Assess the economic feasibility of electrifying Jamaica's taxi and public passenger vehicle (PPV) fleet, including cost per passenger and fuel per passenger metrics.
4. Situate Jamaica's EV transition within the broader Caribbean regional context, identifying where Jamaica leads and where it lags.
5. Deliver all findings through an interactive, publicly accessible Python (Streamlit) dashboard, designed to be useful to both policy planners and private consumers making real purchasing decisions.

---

## 1.3 Who This Research Is For

This project serves two distinct audiences, whose needs differ substantially.

**Private car owners** face a concrete financial question: given current fuel prices, electricity rates, and the approximately 30% upfront cost premium on EVs relative to comparable ICE vehicles (Government of Jamaica, 2023), does switching make financial sense? The answer depends on individual driving patterns, annual mileage, and access to charging infrastructure, all of which differ from driver to driver. The dashboard developed in this project will include a consumer-facing calculator that allows users to enter their own vehicle and usage data and receive a personalised cost comparison and payback period estimate.

**Public and fleet transit operators** face a different set of constraints: route distances, passenger throughput, operating cost per passenger-kilometre, and the availability of fleet-scale charging. These operators function on thin margins in a sector that is already under pressure. For them, the relevant question is not just whether EVs are cheaper to run, but whether the upfront capital cost and infrastructure requirements are manageable at scale. The dashboard will model this using primary data sourced from the Transport Authority of Jamaica, the Jamaica Urban Transit Company (JUTC), and the Consumer Affairs Commission.

---

## 1.4 Primary Deliverables

Three outputs will be produced by the end of the study period:

1. **An eight-module interactive dashboard** deployed on Streamlit Community Cloud, covering: consumer cost comparison, route cost mapping, fuel and energy price tracking, fleet penetration simulation, emissions impact modelling, taxi and PPV feasibility analysis, fiscal policy and import duty tracking, and Caribbean regional comparison.

2. **A formal written report** (the document of which this section forms part), documenting all methodology, data sources, findings, and policy recommendations. The report is written progressively throughout the eight weeks, with one section completed per week.

3. **Print-ready research posters** exported directly from dashboard outputs, suitable for academic presentation and public communication at UWI Mona.

---

## 1.5 Scope and Limitations

This study focuses on light passenger vehicles and public passenger vehicles operating in Jamaica, with comparative data drawn from the wider Caribbean where available. All cost and emissions figures reflect conditions during the June–August 2026 data collection period; fuel prices, electricity tariffs, and vehicle availability are subject to change. Where responses to formal institutional data requests have not yet been received, verified proxy estimates from IEA datasets and Inter-American Development Bank regional baselines are used and explicitly flagged as estimates throughout the dashboard interface.

Primary data collection includes a short anonymous consumer fuel tracking survey deployed via Google Forms and a short operator survey administered in collaboration with the Jamaica Urban Transport Authority (JUTA). Both surveys are designed to supplement, not replace, institutional data.

---

## References

Government of Jamaica. (2023). *Electric vehicle policy*. Ministry of Science, Energy, Telecommunications and Transport.

---

*Next section: Section 2, Background and Literature Review (due June 19, 2026)*
