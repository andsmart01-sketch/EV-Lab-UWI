# ── vehicles.py ────────────────────────────────────────────────────────────────
# Jamaica EV Lab — UWI Mona, 2026
# Vehicle database for ICE and BEV models relevant to the Jamaican market.
#
# DATA SOURCES:
#   New ICE prices  : Toyota Jamaica (toyotajamaica.com, June 2026) in USD,
#                     converted at J$158.53/USD (exchange-rates.org, June 15 2026)
#   Used ICE prices : Jacars.net and Jamaicars.com asking prices, June 2026.
#                     These are market asking prices, not confirmed transaction prices.
#   New EV prices   : ATL Automotive / BYD Jamaica (byd.atlautomotive.com) does NOT
#                     publish prices. Fields marked None require a dealer quote.
#   Used EV prices  : Auto Craft Japan Jamaica estimates (autocraftjapan.com, June 2026).
#                     Ranges are mid-market asking prices for Jamaica.
#   Consumption     : Real-world estimates for Jamaican driving conditions (heat,
#                     stop-and-go traffic, hilly terrain). Adjusted from WLTP/JC08
#                     manufacturer figures. Users should adjust for their vehicle.
#   Maintenance     : Industry estimates for Jamaica. ICE figures include oil changes,
#                     filters, belts, and routine servicing. BEV figures include
#                     brake fluid, tyres, and annual inspection only.
#   Depreciation    : Estimated rates based on Jamaican used car market observations.
#                     ICE: 18% year 1, 12% subsequent. BEV: 22% year 1, 12% subsequent.
#   Manufacturing   : BEV manufacturing CO2 is NOT stored as a hardcoded per-model
#                     total. It is derived from battery capacity and the battery
#                     supply-chain carbon intensity reported in Bieker (2021).
#                     See the MANUFACTURING CO2 section at the bottom of this file.
#
# NOTE: All prices flagged with price_verified=False require confirmation before
# use in formal analysis. Replace with confirmed dealer quotes when available.
# ────────────────────────────────────────────────────────────────────────────────

USD_TO_JMD = 158.53  # exchange-rates.org, June 15, 2026


def _usd(amount):
    """Convert USD to JMD and round to nearest thousand."""
    return round(amount * USD_TO_JMD / 1000) * 1000


# ── ICE VEHICLES ────────────────────────────────────────────────────────────────
# 10 most market-relevant ICE models for Jamaica, new and used variants.

ICE_VEHICLES = {

    # ── NEW ICE ─────────────────────────────────────────────────────────────────

    "toyota-yaris-new": {
        "label": "Toyota Yaris 1.5L Sedan (New, 2024)",
        "make": "Toyota", "model": "Yaris", "variant": "1.5L Sedan",
        "condition": "new", "year": 2024,
        "price_jmd": _usd(31920),
        "price_verified": True,
        "price_source": "Toyota Jamaica (toyotajamaica.com, June 2026)",
        "consumption_per_100km": 7.0,
        "consumption_basis": "combined",
        "engine_cc": 1500,
        "transmission": "Automatic",
        "seats": 5,
        "annual_maintenance_jmd": 90000,
        "depreciation_y1": 0.18,
        "depreciation_subsequent": 0.12,
        "notes": "Entry sedan on Toyota Jamaica lineup. No standard Corolla sold new in Jamaica."
    },

    "toyota-raize-new": {
        "label": "Toyota Raize 1.0T Compact SUV (New, 2024)",
        "make": "Toyota", "model": "Raize", "variant": "1.0T Compact SUV",
        "condition": "new", "year": 2024,
        "price_jmd": _usd(32930),
        "price_verified": True,
        "price_source": "Toyota Jamaica (toyotajamaica.com, June 2026)",
        "consumption_per_100km": 7.5,
        "consumption_basis": "combined",
        "engine_cc": 1000,
        "transmission": "Automatic",
        "seats": 5,
        "annual_maintenance_jmd": 95000,
        "depreciation_y1": 0.18,
        "depreciation_subsequent": 0.12,
        "notes": "Turbocharged 1.0L compact SUV. Popular for urban Jamaican driving."
    },

    "toyota-yaris-cross-new": {
        "label": "Toyota Yaris Cross (New, 2024)",
        "make": "Toyota", "model": "Yaris Cross", "variant": "Compact Crossover",
        "condition": "new", "year": 2024,
        "price_jmd": _usd(39731),
        "price_verified": True,
        "price_source": "Toyota Jamaica (toyotajamaica.com, June 2026)",
        "consumption_per_100km": 8.0,
        "consumption_basis": "combined",
        "engine_cc": 1500,
        "transmission": "Automatic",
        "seats": 5,
        "annual_maintenance_jmd": 100000,
        "depreciation_y1": 0.18,
        "depreciation_subsequent": 0.12,
        "notes": "Crossover variant of the Yaris. Good ground clearance for Jamaican roads."
    },

    "toyota-rav4-new": {
        "label": "Toyota RAV4 2.5L SUV (New, 2024)",
        "make": "Toyota", "model": "RAV4", "variant": "2.5L SUV",
        "condition": "new", "year": 2024,
        "price_jmd": _usd(50388),
        "price_verified": True,
        "price_source": "Toyota Jamaica (toyotajamaica.com, June 2026)",
        "consumption_per_100km": 10.5,
        "consumption_basis": "combined",
        "engine_cc": 2500,
        "transmission": "Automatic",
        "seats": 5,
        "annual_maintenance_jmd": 120000,
        "depreciation_y1": 0.18,
        "depreciation_subsequent": 0.12,
        "notes": "Mid-size SUV. One of the best selling models in Jamaica."
    },

    # ── USED ICE ────────────────────────────────────────────────────────────────

    "toyota-corolla-used": {
        "label": "Toyota Corolla 1.8L Sedan (Used, 2019-2021)",
        "make": "Toyota", "model": "Corolla", "variant": "1.8L Sedan",
        "condition": "used", "year": 2020,
        "price_jmd": 3800000,
        "price_verified": False,
        "price_source": "Jamaicars.com / SBT Japan Jamaica asking prices, June 2026. "
                        "Range: J$3.1M-J$5M. Midpoint used.",
        "consumption_per_100km": 7.5,
        "consumption_basis": "combined",
        "engine_cc": 1800,
        "transmission": "Automatic",
        "seats": 5,
        "annual_maintenance_jmd": 85000,
        "depreciation_y1": 0.12,
        "depreciation_subsequent": 0.10,
        "notes": "Most popular car in Jamaica. Around one third of Kingston vehicles "
                 "are various Corolla generations (Best Selling Cars Blog). "
                 "Lower depreciation rate applied as used vehicle."
    },

    "honda-fit-used": {
        "label": "Honda Fit 1.5L Hatchback (Used, 2019-2021)",
        "make": "Honda", "model": "Fit", "variant": "1.5L Hatchback",
        "condition": "used", "year": 2020,
        "price_jmd": 2900000,
        "price_verified": False,
        "price_source": "Jacars.net asking prices, June 2026. "
                        "Range: J$2.5M-J$3.5M. Midpoint used.",
        "consumption_per_100km": 6.5,
        "consumption_basis": "combined",
        "engine_cc": 1500,
        "transmission": "Automatic",
        "seats": 5,
        "annual_maintenance_jmd": 80000,
        "depreciation_y1": 0.12,
        "depreciation_subsequent": 0.10,
        "notes": "Very popular used import in Jamaica. Compact and fuel efficient."
    },

    "honda-crv-used": {
        "label": "Honda CR-V 1.5T SUV (Used, 2020-2022)",
        "make": "Honda", "model": "CR-V", "variant": "1.5T SUV",
        "condition": "used", "year": 2021,
        "price_jmd": 10900000,
        "price_verified": False,
        "price_source": "Jacars.net asking price, June 2026. Single listing at J$10.9M.",
        "consumption_per_100km": 8.5,
        "consumption_basis": "combined",
        "engine_cc": 1500,
        "transmission": "Automatic",
        "seats": 5,
        "annual_maintenance_jmd": 110000,
        "depreciation_y1": 0.12,
        "depreciation_subsequent": 0.10,
        "notes": "Popular compact SUV. Honda is third best-selling brand in Jamaica "
                 "(Jamaica Observer, Jan 2025)."
    },

    "suzuki-swift-used": {
        "label": "Suzuki Swift 1.2L Hatchback (Used, 2018-2021)",
        "make": "Suzuki", "model": "Swift", "variant": "1.2L Hatchback",
        "condition": "used", "year": 2019,
        "price_jmd": 1900000,
        "price_verified": False,
        "price_source": "Jacars.net asking prices, June 2026. "
                        "Range: J$1.5M-J$2.3M. Midpoint used.",
        "consumption_per_100km": 6.0,
        "consumption_basis": "combined",
        "engine_cc": 1200,
        "transmission": "Automatic",
        "seats": 5,
        "annual_maintenance_jmd": 70000,
        "depreciation_y1": 0.12,
        "depreciation_subsequent": 0.10,
        "notes": "Budget-friendly compact hatchback. Popular with first-time buyers."
    },

    "nissan-tiida-used": {
        "label": "Nissan Tiida 1.6L Sedan (Used, 2016-2019)",
        "make": "Nissan", "model": "Tiida", "variant": "1.6L Sedan",
        "condition": "used", "year": 2017,
        "price_jmd": 2000000,
        "price_verified": False,
        "price_source": "Estimated from Jamaican used car market. "
                        "Range: J$1.5M-J$2.5M. Midpoint used.",
        "consumption_per_100km": 7.0,
        "consumption_basis": "combined",
        "engine_cc": 1600,
        "transmission": "Automatic",
        "seats": 5,
        "annual_maintenance_jmd": 80000,
        "depreciation_y1": 0.12,
        "depreciation_subsequent": 0.10,
        "notes": "Widely used as taxi (route taxi) in Jamaica. Relevant for fleet module."
    },

    "toyota-probox-used": {
        "label": "Toyota Probox 1.5L Van (Used, 2015-2019)",
        "make": "Toyota", "model": "Probox", "variant": "1.5L Commercial Van",
        "condition": "used", "year": 2017,
        "price_jmd": 1650000,
        "price_verified": False,
        "price_source": "Jacars.net asking prices, June-July 2026. "
                        "Range: J$0.85M-J$2.35M. Midpoint used.",
        "consumption_per_100km": 7.6,
        "consumption_basis": "combined",
        # Urban-duty figure retained for Module 6, where every vehicle is on an
        # urban basis. Module 1 uses the combined figure because every other ICE
        # entry in this table is combined-basis. Mixing the two would make the
        # 1.5L Probox appear thirstier than a 2.5L RAV4, which is not real.
        "consumption_urban_per_100km": 10.7,
        "engine_cc": 1500,
        "transmission": "Automatic",
        "seats": 5,
        "annual_maintenance_jmd": 120000,
        "depreciation_y1": 0.12,
        "depreciation_subsequent": 0.10,
        "notes": "Workhorse commercial van, very widely used as a route taxi and for "
                 "small business delivery in Jamaica. Consumption from inCarDoc user "
                 "data for the 1NZ-FE 1.5L: 7.6 L/100km combined, 10.7 L/100km urban. "
                 "Price is an asking price, not a confirmed sale."
    },

    "toyota-probox-late": {
        "label": "Toyota Probox 1.5L Van (Late-model import, 2022-2024)",
        "make": "Toyota", "model": "Probox", "variant": "1.5L Commercial Van",
        # "new" here means effectively new: low mileage, recent model year.
        # Toyota Jamaica does NOT list the Probox in its franchise-new lineup,
        # so no dealer-new price exists to quote. Every Probox in Jamaica is an
        # import; this entry is the fresh end of that market, the used entry is
        # the older end. Flagged as "new" so it picks up newer-vehicle loan
        # terms in Module 4 rather than used-vehicle terms.
        "condition": "new", "year": 2023,
        "price_jmd": 2300000,
        "price_verified": False,
        "price_source": "Jacars.net and JamaiCars.com asking prices, July 2026. "
                        "Observed range across 2014-2022 units J$0.85M-J$2.30M; "
                        "the top of that range is used here for a late-model unit. "
                        "Asking price, not a confirmed sale.",
        "consumption_per_100km": 7.6,
        "consumption_basis": "combined",
        "consumption_urban_per_100km": 10.7,
        "engine_cc": 1500,
        "transmission": "Automatic",
        "seats": 5,
        "annual_maintenance_jmd": 85000,
        "depreciation_y1": 0.16,
        "depreciation_subsequent": 0.11,
        "notes": "Fresh import counterpart to the used Probox, for testing whether "
                 "buying a newer petrol taxi beats buying an EV. Consumption is the "
                 "same inCarDoc figure as the used entry because no separate "
                 "measurement was found for the later model. Maintenance and "
                 "depreciation are ESTIMATES reflecting a younger vehicle, not "
                 "sourced figures."
    },

    "toyota-hilux-used": {
        "label": "Toyota Hilux 2.4L Pickup (Used, 2019-2021)",
        "make": "Toyota", "model": "Hilux", "variant": "2.4L Double Cab Pickup",
        "condition": "used", "year": 2020,
        "price_jmd": 5300000,
        "price_verified": False,
        "price_source": "Jacars.net asking prices, June 2026. "
                        "Range: J$5.25M-J$5.4M. Midpoint used.",
        "consumption_per_100km": 11.5,
        "consumption_basis": "combined",
        "engine_cc": 2400,
        "transmission": "Automatic",
        "seats": 5,
        "annual_maintenance_jmd": 130000,
        "depreciation_y1": 0.12,
        "depreciation_subsequent": 0.10,
        "notes": "Popular pickup truck for commercial and rural use in Jamaica."
    },
}


# ── BEV VEHICLES ────────────────────────────────────────────────────────────────
# 10 EV models available or emerging in the Jamaican market.
# Hybrids (Toyota Aqua, Prius, etc.) are explicitly excluded from this project.

BEV_VEHICLES = {

    # ── NEW BEV (ATL Automotive / BYD Jamaica) ──────────────────────────────────

    "byd-yuan-pro-new": {
        "label": "BYD Yuan Pro (New)",
        "make": "BYD", "model": "Yuan Pro", "variant": "Compact SUV",
        "condition": "new", "year": 2024,
        "price_jmd": 6_130_874,
        "price_verified": True,
        "price_source": "ATL Automotive, USD$38,803, July 2026",
        "consumption_per_100km": 15.0,
        "battery_kwh": 45.1,
        "range_km_nedc": 410,
        "range_km_realworld": 300,
        "seats": 5,
        "annual_maintenance_jmd": 40000,
        "depreciation_y1": 0.22,
        "depreciation_subsequent": 0.12,
        "battery_origin": "china",
        "notes": "Entry-level BYD SUV. Available in Jamaica. "
                 "BYD sold approximately 85 vehicles in Jamaica in 2024 "
                 "(Jamaica Observer, Jan 2025)."
    },

    "byd-yuan-plus-new": {
        "label": "BYD Yuan Plus Standard Range (New)",
        "make": "BYD", "model": "Yuan Plus", "variant": "Standard Range SUV",
        "condition": "new", "year": 2024,
        "price_jmd": 7_670_000,
        "price_verified": True,
        "price_source": "ATL Automotive, USD$48,544, July 2026",
        "consumption_per_100km": 14.0,
        "battery_kwh": 49.92,
        "range_km_nedc": 480,
        "range_km_realworld": 340,
        "seats": 5,
        "annual_maintenance_jmd": 40000,
        "depreciation_y1": 0.22,
        "depreciation_subsequent": 0.12,
        "battery_origin": "china",
        "notes": "Mid-range BYD compact SUV. Larger battery than Yuan Pro."
    },

    "byd-seal-new": {
        "label": "BYD Seal Electric Sedan (New)",
        "make": "BYD", "model": "Seal", "variant": "Electric Sedan",
        "condition": "new", "year": 2024,
        "price_jmd": 10_738_000,
        "price_verified": True,
        "price_source": "ATL Automotive, USD$67,962 (AWD), July 2026",
        "consumption_per_100km": 14.0,
        "battery_kwh": 60.0,
        "range_km_nedc": 570,
        "range_km_realworld": 420,
        "seats": 5,
        "annual_maintenance_jmd": 40000,
        "depreciation_y1": 0.22,
        "depreciation_subsequent": 0.12,
        "battery_origin": "china",
        "notes": "BYD flagship sedan. Longest range in BYD Jamaica lineup."
    },

    "byd-sealion7-new": {
        "label": "BYD Sealion 7 AWD (New)",
        "make": "BYD", "model": "Sealion 7", "variant": "AWD SUV",
        "condition": "new", "year": 2024,
        "price_jmd": 10_738_000,
        "price_verified": True,
        "price_source": "ATL Automotive, USD$67,962 (RWD), July 2026",
        "consumption_per_100km": 18.0,
        "battery_kwh": 82.56,
        "range_km_nedc": 480,
        "range_km_realworld": 360,
        "seats": 5,
        "annual_maintenance_jmd": 45000,
        "depreciation_y1": 0.22,
        "depreciation_subsequent": 0.12,
        "battery_origin": "china",
        "notes": "AWD dual motor SUV. Higher consumption due to AWD drivetrain."
    },

    "byd-atto8-new": {
        "label": "BYD Atto 8 (New, 2027)",
        "make": "BYD", "model": "Atto 8", "variant": "Large SUV",
        "condition": "new", "year": 2027,
        "price_jmd": 15_347_904,
        "price_verified": True,
        "price_source": "ATL Automotive, USD$97,088, July 2026",
        "consumption_per_100km": 20.0,
        "battery_kwh": 90.0,
        "range_km_nedc": 400,
        "range_km_realworld": 300,
        "seats": 7,
        "annual_maintenance_jmd": 80_000,
        "depreciation_y1": 0.20,
        "depreciation_subsequent": 0.12,
        "battery_origin": "china",
        "notes": "Price USD$97,088 confirmed ATL Automotive (atlautomotive.com, July 2026), "
                 "converted at J$158/USD. Consumption 20.0 kWh/100km and real-world range "
                 "300km are UNVERIFIED estimates pending field data. Seat count assumed 7 "
                 "for a large SUV and not confirmed with ATL.",
    },

    # ── USED BEV ────────────────────────────────────────────────────────────────

    "nissan-leaf-used": {
        "label": "Nissan Leaf 40kWh (Used, 2018-2020)",
        "make": "Nissan", "model": "Leaf", "variant": "40kWh Hatchback",
        "condition": "used", "year": 2019,
        "price_jmd": 3200000,
        "price_verified": False,
        "price_source": "Auto Craft Japan Jamaica estimates (autocraftjapan.com, June 2026). "
                        "Range: J$2.5M-J$4M. Midpoint used.",
        "consumption_per_100km": 16.0,
        "battery_kwh": 40.0,
        "range_km_nedc": 270,
        "range_km_realworld": 180,
        "seats": 5,
        "annual_maintenance_jmd": 35000,
        "depreciation_y1": 0.12,
        "depreciation_subsequent": 0.10,
        "battery_origin": "japan",
        "notes": "Most commonly available EV in Jamaica. Popular used import. "
                 "Real-world range significantly lower in Jamaican heat with AC. "
                 "Battery degradation a consideration for older units."
    },

    "hyundai-kona-ev-used": {
        "label": "Hyundai Kona Electric 64kWh (Used, 2020-2022)",
        "make": "Hyundai", "model": "Kona Electric", "variant": "64kWh SUV",
        "condition": "used", "year": 2021,
        "price_jmd": 7000000,
        "price_verified": False,
        "price_source": "Auto Craft Japan Jamaica estimates (autocraftjapan.com, June 2026). "
                        "Range: J$6M-J$8M. Midpoint used.",
        "consumption_per_100km": 16.0,
        "battery_kwh": 64.0,
        "range_km_nedc": 400,
        "range_km_realworld": 290,
        "seats": 5,
        "annual_maintenance_jmd": 38000,
        "depreciation_y1": 0.12,
        "depreciation_subsequent": 0.10,
        "battery_origin": "korea",
        "notes": "Longer range than Nissan Leaf. Better suited for inter-parish travel."
    },

    "kia-soul-ev-used": {
        "label": "Kia Soul EV 64kWh (Used, 2020-2022)",
        "make": "Kia", "model": "Soul EV", "variant": "64kWh Compact SUV",
        "condition": "used", "year": 2021,
        "price_jmd": 5200000,
        "price_verified": False,
        "price_source": "Auto Craft Japan Jamaica estimates (autocraftjapan.com, June 2026). "
                        "Range: J$4.5M-J$6M. Midpoint used.",
        "consumption_per_100km": 17.0,
        "battery_kwh": 64.0,
        "range_km_nedc": 383,
        "range_km_realworld": 270,
        "seats": 5,
        "annual_maintenance_jmd": 38000,
        "depreciation_y1": 0.12,
        "depreciation_subsequent": 0.10,
        "battery_origin": "korea",
        "notes": "Distinctive boxy styling. Good range for Jamaican inter-parish routes."
    },

    "tesla-model3-used": {
        "label": "Tesla Model 3 Standard Range (Used, 2020-2022)",
        "make": "Tesla", "model": "Model 3", "variant": "Standard Range Sedan",
        "condition": "used", "year": 2021,
        "price_jmd": 12000000,
        "price_verified": False,
        "price_source": "Auto Craft Japan Jamaica estimates (autocraftjapan.com, June 2026). "
                        "Range: J$10M-J$14M. Midpoint used.",
        "consumption_per_100km": 15.0,
        "battery_kwh": 60.0,
        "range_km_nedc": 500,
        "range_km_realworld": 370,
        "seats": 5,
        "annual_maintenance_jmd": 50000,
        "depreciation_y1": 0.12,
        "depreciation_subsequent": 0.10,
        "battery_origin": "china",
        "notes": "Premium EV. Right-hand-drive Model 3 is built at Giga Shanghai, so the "
                 "China battery supply-chain intensity is applied. "
                 "No Tesla service centre in Jamaica as of June 2026 -- "
                 "maintenance and parts availability is a practical concern for buyers."
    },
}


# ── MANUFACTURING CO2 ───────────────────────────────────────────────────────────
#
# WHY THIS IS DERIVED RATHER THAN HARDCODED
#
# Two conflicting hardcoded sets previously existed in this project: a
# `manufacturing_co2_tonnes` field here (Yuan Pro 8.1, Yuan Plus 9.0, Seal 10.8,
# Sealion 7 14.9, Leaf 7.2, Kona 11.5, Soul 11.5, Model 3 10.8) and a
# `BEV_MANUFACTURING_CO2_PREMIUM` dict in app.py (7.2, 8.1, 9.5, 12.4, 5.8, 9.0,
# 9.0, 8.8). Neither was traceable to a source. The app.py set was labelled
# "premium above an equivalent ICE car" but its values are roughly 2.2 to 2.4
# times the battery production emissions implied by any published figure, which
# means they were cradle-to-gate vehicle TOTALS (battery plus body plus
# drivetrain), not premiums. Using a total where a premium belongs roughly
# doubles the BEV carbon debt and roughly doubles the carbon payback period.
#
# THE METHOD USED INSTEAD
#
# Carbon payback needs the DIFFERENCE in manufacturing emissions between a BEV
# and the ICE car it replaces, not the BEV total. Under the standard simplifying
# assumption that the body shell ("glider") of a BEV and an equivalent ICE car
# carry the same production emissions, and that the electric motor and inverter
# roughly offset the engine, gearbox, exhaust and fuel system they replace, the
# difference collapses to the battery pack. So:
#
#     manufacturing premium (tonnes) = battery_kwh * intensity / 1000
#
# This has three advantages over a hardcoded table: every number is reproducible
# from a published intensity, it updates automatically when battery capacity is
# corrected, and it does not require a Jamaica-specific ICE manufacturing figure
# that does not exist.
#
# LIMITATION TO STATE IN THE REPORT
#
# The glider-parity assumption is a simplification. BEVs are typically heavier
# and use more aluminium, so the true premium is somewhat above the battery-only
# figure. Treat these values as a lower bound on the manufacturing premium.
#
# SOURCE
#
# Bieker, G. (2021). A global comparison of the life-cycle greenhouse gas
# emissions of combustion engine and electric passenger cars. ICCT.
# https://theicct.org/publication/a-global-comparison-of-the-life-cycle-greenhouse-gas-emissions-of-combustion-engine-and-electric-passenger-cars/
# The study assumes 60 kg CO2e/kWh for battery production in Europe and the
# United States and 68 kg CO2e/kWh in China and India.

BATTERY_PRODUCTION_CO2_KG_PER_KWH = {
    "china":  68,   # Bieker (2021), China supply chain
    "india":  68,   # Bieker (2021), India supply chain
    "europe": 60,   # Bieker (2021), EU supply chain
    "us":     60,   # Bieker (2021), US supply chain
    # Bieker (2021) does not cover Japan or Korea. Both have grid carbon
    # intensities between the EU and China, and both are mature manufacturing
    # bases. The EU/US figure is applied as the nearest published analogue.
    # ASSUMPTION, not a sourced value. Flag in the report.
    "japan":  60,
    "korea":  60,
}

DEFAULT_BATTERY_ORIGIN = "china"

# USED BEVs AND SUNK MANUFACTURING EMISSIONS
#
# A 2019 Nissan Leaf imported into Jamaica in 2026 did not cause its battery to
# be manufactured in 2026. Those emissions were incurred years earlier for the
# first owner. Charging the full premium to the second owner overstates the
# carbon payback of exactly the vehicles most Jamaicans can actually afford,
# since used imports are the realistic entry point into EV ownership here.
#
# The premium is therefore amortised over assumed vehicle life: a buyer is
# charged the share of the battery debt corresponding to the service life still
# ahead of the vehicle. New vehicles carry the full premium.
#
#     factor = max(life - age, 1) / life
#
# Bieker (2021) assumes an average passenger car useful lifetime of 15 to 18
# years. The conservative end of that range is used here, which charges used
# buyers MORE than the upper end would.

ASSUMED_VEHICLE_LIFE_YEARS = 15
CURRENT_YEAR = 2026


def bev_manufacturing_premium_tonnes(vehicle_key, amortise_used=True):
    """
    Tonnes of CO2e of BEV manufacturing emissions in excess of an equivalent
    ICE car, approximated by battery pack production emissions.

    If amortise_used is True (default), the premium charged to a used vehicle
    is scaled by its remaining share of assumed service life. Pass
    amortise_used=False for the full cradle-to-gate battery premium, which is
    the correct quantity for fleet-level accounting where the vehicle is being
    newly manufactured somewhere in the world.

    Returns None if the vehicle is not a BEV or has no battery capacity on
    record, so callers must handle the missing case explicitly rather than
    silently falling back to a made-up default.
    """
    v = BEV_VEHICLES.get(vehicle_key)
    if v is None:
        return None
    kwh = v.get("battery_kwh")
    if not kwh:
        return None
    origin = v.get("battery_origin", DEFAULT_BATTERY_ORIGIN)
    intensity = BATTERY_PRODUCTION_CO2_KG_PER_KWH.get(
        origin, BATTERY_PRODUCTION_CO2_KG_PER_KWH[DEFAULT_BATTERY_ORIGIN]
    )
    full = kwh * intensity / 1000.0
    if amortise_used:
        full *= _remaining_life_fraction(v)
    return full


def _remaining_life_fraction(v):
    """Share of assumed service life still ahead of this vehicle. 1.0 if new."""
    if v.get("condition") != "used":
        return 1.0
    age = max(CURRENT_YEAR - v.get("year", CURRENT_YEAR), 0)
    remaining = max(ASSUMED_VEHICLE_LIFE_YEARS - age, 1)
    return remaining / ASSUMED_VEHICLE_LIFE_YEARS


def bev_manufacturing_premium_note(vehicle_key, amortise_used=True):
    """Human-readable derivation string for display in the dashboard."""
    v = BEV_VEHICLES.get(vehicle_key)
    if v is None or not v.get("battery_kwh"):
        return "No battery capacity on record for this vehicle."
    origin = v.get("battery_origin", DEFAULT_BATTERY_ORIGIN)
    intensity = BATTERY_PRODUCTION_CO2_KG_PER_KWH.get(
        origin, BATTERY_PRODUCTION_CO2_KG_PER_KWH[DEFAULT_BATTERY_ORIGIN]
    )
    full = v["battery_kwh"] * intensity / 1000.0
    base = (f"{v['battery_kwh']:.2f} kWh x {intensity} kg CO2e/kWh "
            f"({origin} supply chain) = {full:.2f} t")
    frac = _remaining_life_fraction(v)
    if amortise_used and frac < 1.0:
        age = CURRENT_YEAR - v["year"]
        base += (f", amortised to {full * frac:.2f} t for a {age}-year-old vehicle "
                 f"with {ASSUMED_VEHICLE_LIFE_YEARS - age} of "
                 f"{ASSUMED_VEHICLE_LIFE_YEARS} years of service life remaining")
    return base + ". Bieker (2021), ICCT."


# ── COMBINED LOOKUP ─────────────────────────────────────────────────────────────

ALL_VEHICLES = {**ICE_VEHICLES, **BEV_VEHICLES}


import re as _re

# Language that means a figure was inferred rather than observed at source.
_ESTIMATE_PATTERN = _re.compile(r"estimat|assum|unverified|approx|proxy", _re.I)

# Marker appended to any label whose price is an estimate. Dr Harris asked for
# asterisks wherever there are estimates in the data, with an explanation.
ESTIMATE_MARK = " *"

ESTIMATE_FOOTNOTE = (
    "* Price is an estimate rather than an advertised figure. Where a dealer "
    "publishes a price, that price is used. Where none is published, the value "
    "is the midpoint of observed asking prices or a dealer's own estimate, and "
    "the vehicle is marked. Asking prices are not transaction prices, so the "
    "real figure is usually somewhat lower."
)

# Consumption is separately caveated. Every figure in this dataset is a
# real-world estimate for Jamaican conditions rather than a manufacturer test
# result, because manufacturer figures are measured on standard cycles that do
# not reflect Jamaican heat, hills or traffic.
CONSUMPTION_FOOTNOTE = (
    "Consumption figures are real-world estimates for Jamaican driving "
    "conditions, not manufacturer test-cycle values. Test-cycle figures are "
    "measured under conditions that do not reflect Jamaican heat, hills or "
    "traffic, and typically understate real consumption."
)


def price_is_estimated(vehicle_or_key):
    """True if this vehicle's price came from an estimate rather than a listing."""
    v = vehicle_or_key
    if isinstance(v, str):
        v = ALL_VEHICLES.get(v)
    if not v:
        return False
    return bool(_ESTIMATE_PATTERN.search(v.get("price_source", "") or ""))


def vehicle_label(key, vehicle=None):
    """Display label, with an asterisk when the price is an estimate."""
    v = vehicle if vehicle is not None else ALL_VEHICLES.get(key)
    if not v:
        return key
    return v["label"] + (ESTIMATE_MARK if price_is_estimated(v) else "")


def estimated_vehicle_keys():
    """Every vehicle whose price is an estimate. Used to build the footnote."""
    return [k for k, v in ALL_VEHICLES.items() if price_is_estimated(v)]


def get_ice_dropdown_options():
    """Return list of dcc.Dropdown options for ICE vehicles."""
    return [{"label": vehicle_label(k, v), "value": k}
            for k, v in ICE_VEHICLES.items()]


def get_bev_dropdown_options():
    """Return list of dcc.Dropdown options for BEV vehicles."""
    return [{"label": vehicle_label(k, v), "value": k}
            for k, v in BEV_VEHICLES.items()]


def get_vehicle(key):
    """Return vehicle dict by key. Returns None if key not found."""
    return ALL_VEHICLES.get(key)
