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

EVRange. (2026). *Physics-based EV range model calibrated on the Jamaican road network* [Unpublished computer software]. Route energy estimates via /api/routing/calculate.

Gao, Z., Lin, Z., LaClair, T. J., Liu, C., Li, J.-M., Birky, A. K., & Ward, J. (2017). Battery capacity and recharging needs for electric buses in city transit service. *Energy, 122*, 588–600.

Government of Jamaica. (2023). *National electric vehicle policy*. Ministry of Energy, Telecommunications and Transport.

Jamaica Observer. (2026, July 24). *TransJamaican Highway toll rates to increase from August 1*. https://www.jamaicaobserver.com/2026/07/24/transjamaican-highway-toll-rates-increase-august-1/

TransJamaican Highway. (2026). *Rates* [Toll rates effective August 1, 2026]. https://www.transjamhighways.com/toll_rates/

Turnbull, K. (2024). *Pioneering electric mobility: A framework for EV battery management in the Caribbean* [Final report]. Department of Physics, University of the West Indies, Mona.

United Nations Environment Programme. (2025, April 7). *Caribbean leading the charge to electric mobility*.
