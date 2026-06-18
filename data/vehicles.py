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
        "engine_cc": 1600,
        "transmission": "Automatic",
        "seats": 5,
        "annual_maintenance_jmd": 80000,
        "depreciation_y1": 0.12,
        "depreciation_subsequent": 0.10,
        "notes": "Widely used as taxi (route taxi) in Jamaica. Relevant for fleet module."
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
        "price_jmd": None,
        "price_verified": False,
        "price_source": "ATL Automotive / BYD Jamaica (byd.atlautomotive.com) does not "
                        "publish prices. Enter confirmed dealer quote.",
        "consumption_per_100km": 15.0,
        "battery_kwh": 45.1,
        "range_km_nedc": 410,
        "range_km_realworld": 300,
        "seats": 5,
        "annual_maintenance_jmd": 40000,
        "depreciation_y1": 0.22,
        "depreciation_subsequent": 0.12,
        "manufacturing_co2_tonnes": 8.1,
        "notes": "Entry-level BYD SUV. Sold by ATL Automotive Group in Jamaica. "
                 "BYD sold approximately 85 vehicles in Jamaica in 2024 "
                 "(Jamaica Observer, Jan 2025)."
    },

    "byd-yuan-plus-new": {
        "label": "BYD Yuan Plus Standard Range (New)",
        "make": "BYD", "model": "Yuan Plus", "variant": "Standard Range SUV",
        "condition": "new", "year": 2024,
        "price_jmd": None,
        "price_verified": False,
        "price_source": "ATL Automotive / BYD Jamaica. Price not published. "
                        "Enter confirmed dealer quote.",
        "consumption_per_100km": 14.0,
        "battery_kwh": 49.92,
        "range_km_nedc": 480,
        "range_km_realworld": 340,
        "seats": 5,
        "annual_maintenance_jmd": 40000,
        "depreciation_y1": 0.22,
        "depreciation_subsequent": 0.12,
        "manufacturing_co2_tonnes": 9.0,
        "notes": "Mid-range BYD compact SUV. Larger battery than Yuan Pro."
    },

    "byd-seal-new": {
        "label": "BYD Seal Electric Sedan (New)",
        "make": "BYD", "model": "Seal", "variant": "Electric Sedan",
        "condition": "new", "year": 2024,
        "price_jmd": None,
        "price_verified": False,
        "price_source": "ATL Automotive / BYD Jamaica. Price not published. "
                        "Enter confirmed dealer quote.",
        "consumption_per_100km": 14.0,
        "battery_kwh": 60.0,
        "range_km_nedc": 570,
        "range_km_realworld": 420,
        "seats": 5,
        "annual_maintenance_jmd": 40000,
        "depreciation_y1": 0.22,
        "depreciation_subsequent": 0.12,
        "manufacturing_co2_tonnes": 10.8,
        "notes": "BYD flagship sedan. Longest range in BYD Jamaica lineup."
    },

    "byd-sealion7-new": {
        "label": "BYD Sealion 7 AWD (New)",
        "make": "BYD", "model": "Sealion 7", "variant": "AWD SUV",
        "condition": "new", "year": 2024,
        "price_jmd": None,
        "price_verified": False,
        "price_source": "ATL Automotive / BYD Jamaica. Price not published. "
                        "Enter confirmed dealer quote.",
        "consumption_per_100km": 18.0,
        "battery_kwh": 82.56,
        "range_km_nedc": 480,
        "range_km_realworld": 360,
        "seats": 5,
        "annual_maintenance_jmd": 45000,
        "depreciation_y1": 0.22,
        "depreciation_subsequent": 0.12,
        "manufacturing_co2_tonnes": 14.9,
        "notes": "AWD dual motor SUV. Higher consumption due to AWD drivetrain."
    },

    "byd-atto3-new": {
        "label": "BYD Atto 3 (New)",
        "make": "BYD", "model": "Atto 3", "variant": "Electric SUV",
        "condition": "new", "year": 2024,
        "price_jmd": None,
        "price_verified": False,
        "price_source": "ATL Automotive / BYD Jamaica. Price not published. "
                        "Enter confirmed dealer quote.",
        "consumption_per_100km": 14.0,
        "battery_kwh": 60.48,
        "range_km_nedc": 420,
        "range_km_realworld": 320,
        "seats": 5,
        "annual_maintenance_jmd": 40000,
        "depreciation_y1": 0.22,
        "depreciation_subsequent": 0.12,
        "manufacturing_co2_tonnes": 10.9,
        "notes": "Also available through ATL Automotive. Similar spec to Yuan Plus "
                 "but larger body."
    },

    "mg-zs-ev-new": {
        "label": "MG ZS EV (New)",
        "make": "MG", "model": "ZS EV", "variant": "Electric SUV",
        "condition": "new", "year": 2024,
        "price_jmd": None,
        "price_verified": False,
        "price_source": "MG Jamaica price not publicly available. "
                        "Enter confirmed dealer quote from ATL Automotive.",
        "consumption_per_100km": 16.0,
        "battery_kwh": 50.3,
        "range_km_nedc": None,
        "range_km_realworld": 320,
        "seats": 5,
        "annual_maintenance_jmd": 40000,
        "depreciation_y1": 0.22,
        "depreciation_subsequent": 0.12,
        "manufacturing_co2_tonnes": 9.1,
        "notes": "MG is part of ATL Automotive Group in Jamaica. "
                 "One of the growing Chinese EV brands in the market."
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
        "manufacturing_co2_tonnes": 7.2,
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
        "manufacturing_co2_tonnes": 11.5,
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
        "manufacturing_co2_tonnes": 11.5,
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
        "manufacturing_co2_tonnes": 10.8,
        "notes": "Premium EV. No Tesla service centre in Jamaica as of June 2026 -- "
                 "maintenance and parts availability is a practical concern for buyers."
    },
}


# ── COMBINED LOOKUP ─────────────────────────────────────────────────────────────

ALL_VEHICLES = {**ICE_VEHICLES, **BEV_VEHICLES}


def get_ice_dropdown_options():
    """Return list of dcc.Dropdown options for ICE vehicles."""
    return [{"label": v["label"], "value": k} for k, v in ICE_VEHICLES.items()]


def get_bev_dropdown_options():
    """Return list of dcc.Dropdown options for BEV vehicles."""
    return [{"label": v["label"], "value": k} for k, v in BEV_VEHICLES.items()]


def get_vehicle(key):
    """Return vehicle dict by key. Returns None if key not found."""
    return ALL_VEHICLES.get(key)
