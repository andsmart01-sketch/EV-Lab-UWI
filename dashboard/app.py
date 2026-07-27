import dash
from dash import dcc, html, Input, Output
from data_loader import load_fuel_prices, get_latest_prices, get_live_exchange_rate
import plotly.express as px
import plotly.graph_objects as go
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'data'))
from vehicles import ICE_VEHICLES, BEV_VEHICLES, get_ice_dropdown_options, get_bev_dropdown_options
from module7_policy import build_module7_layout

app = dash.Dash(
    __name__,
    title="Jamaica EV Dashboard — UWI Mona",
    suppress_callback_exceptions=True
)
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''
# ── Data ──────────────────────────────────────────────────────────
fuel_df = load_fuel_prices()
latest_prices = get_latest_prices()
server = app.server  # Expose the Flask server for deployment on UWI server

# ── Layout ────────────────────────────────────────────────────────
def placeholder_layout():
    return html.P(
        "Module content will be built in accordance with the project timeline.",
        style={"color": "#777", "fontSize": "13px", "marginTop": "20px"}
    )


def serve_layout():
    return html.Div([

    dcc.Store(id="active-tab-store", data="home"),
    dcc.Store(id="effective-fuel-price-store", data=None),

    html.Div([

        # Sidebar -- navigation
        html.Div([
            html.Div([
                html.H2("Jamaica EV Dashboard", style={"color": "#fff", "fontSize": "16px", "margin": "0 0 2px"}),
                html.P("UWI Mona -- EV Lab 2026", style={"color": "var(--sidebar-text)", "fontSize": "11px", "margin": "0"}),
            ], style={"padding": "20px 20px 24px"}),

            html.Div(id="sidebar-nav-container"),

        ], style={
            "width": "230px", "minWidth": "230px",
            "backgroundColor": "var(--sidebar-bg)",
            "height": "100vh", "overflowY": "auto",
            "position": "sticky", "top": "0",
        }),

        # Main content
        html.Div([
            html.Div(id="m6-fuel-price-prompt"),
            html.Div(id="module-instructions"),
            html.Details([
                html.Summary("Global settings", style={
                    "fontSize": "13px", "fontWeight": "500",
                    "color": "var(--text-secondary)",
                    "cursor": "pointer", "padding": "12px 20px",
                }),
                html.Div([
                    html.Div([
                        html.Label("Fuel grade", style={
                            "fontSize": "12px", "fontWeight": "500",
                            "display": "block", "marginBottom": "4px",
                        }),
                        dcc.Dropdown(
                            id="fuel-grade-select",
                            options=[{"label": "87 octane", "value": "g87"},
                                     {"label": "90 octane", "value": "g90"}],
                            value="g90", clearable=False,
                            style={"width": "160px", "fontSize": "13px", "marginBottom": "8px"},
                        ),
                    ], style={"marginRight": "32px"}),
                    html.Div([
                        html.Label("Home charging rate (J$/kWh)", style={
                            "fontSize": "12px", "fontWeight": "500",
                            "display": "block", "marginBottom": "4px",
                        }),
                        dcc.Input(
                            id="electricity-rate-slider", type="number",
                            value=42, min=1, max=999, step=0.01, debounce=True,
                            style={"width": "160px", "padding": "6px 8px",
                                   "fontSize": "13px",
                                   "border": "1px solid var(--card-border)",
                                   "borderRadius": "6px"},
                        ),
                        html.P("Source: PM Holness, JIS statement, March 2026.", style={
                            "fontSize": "10px", "color": "var(--text-muted)", "marginTop": "2px",
                        }),
                    ], style={"marginRight": "32px"}),
                    html.Div([
                        html.Label("Public charging rate (J$/kWh)", style={
                            "fontSize": "12px", "fontWeight": "500",
                            "display": "block", "marginBottom": "4px",
                        }),
                        dcc.Input(
                            id="public-charging-rate", type="number",
                            value=96, min=1, max=200, step=0.01, debounce=True,
                            style={"width": "160px", "padding": "6px 8px",
                                   "fontSize": "13px",
                                   "border": "1px solid var(--card-border)",
                                   "borderRadius": "6px"},
                        ),
                        html.P("Source: Evergo, confirmed June 2026.", style={
                            "fontSize": "10px", "color": "var(--text-muted)", "marginTop": "4px",
                        }),
                    ], style={"marginRight": "32px"}),
                    html.Div([
                        html.Label("Retail markup source", style={
                            "fontSize": "12px", "fontWeight": "500",
                            "display": "block", "marginBottom": "4px",
                        }),
                        dcc.Dropdown(
                            id="markup-station-select",
                            options=[{"label": s["label"], "value": i}
                                     for i, s in enumerate(KINGSTON_STATION_MARKUPS)],
                            value=0,
                            clearable=False,
                            style={"width": "260px", "fontSize": "12px", "marginBottom": "8px"},
                        ),
                        html.P(
                            "The Petrojam reference price already includes Special Consumption Tax (SCT). "
                            "The retail markup is the additional amount each station charges above that reference. "
                            "Custom entry accepts the full pump price.",
                            style={"fontSize": "10px", "color": "var(--text-muted)",
                                   "marginTop": "0", "marginBottom": "6px", "maxWidth": "260px"},
                        ),
                        html.Div(id="markup-custom-input-wrapper", children=[
                            html.Label("Full retail price (J$/L)", style={
                                "fontSize": "12px", "fontWeight": "500",
                                "display": "block", "marginBottom": "4px",
                            }),
                            dcc.Input(
                                id="markup-custom-input", type="number",
                                placeholder="Enter the pump price you pay at your station",
                                value=None, min=50, max=600, step=0.5, debounce=True,
                                style={"width": "240px", "padding": "6px 8px",
                                       "fontSize": "13px",
                                       "border": "1px solid var(--card-border)",
                                       "borderRadius": "6px"},
                            ),
                        ], style={"display": "none"}),
                        html.Div(id="effective-fuel-price-display",
                                 style={"fontSize": "11px", "color": "var(--text-muted)",
                                        "marginTop": "6px"}),
                        html.P("Retail = Petrojam reference + markup. Markup defaults to Kingston "
                               "field survey averages (J$29 for 87, J$34 for 90, J$48 for diesel). "
                               "Select a station to use its measured markup, or enter your own.",
                               style={"fontSize": "10px", "color": "var(--text-muted)",
                                      "marginTop": "4px", "maxWidth": "260px"}),
                    ]),
                ], style={"display": "flex", "flexWrap": "wrap", "padding": "0 20px 16px"}),
            ], open=False, style={
                "backgroundColor": "var(--card-bg)",
                "border": "1px solid var(--card-border)",
                "borderRadius": "10px",
                "margin": "0 0 20px",
            }),

            html.Div(id="global-settings-summary", style={
                "backgroundColor": "#EBF5FB", "padding": "10px 16px",
                "borderRadius": "4px", "fontSize": "13px",
                "margin": "0 32px 16px",
            }),
            html.Div(id="page-header", style={"padding": "0 32px"}),
            html.Div([
                html.Div(homepage_layout(),      id="content-home"),
                html.Div(module1_layout(),       id="content-tab-1"),
                html.Div(placeholder_layout(),   id="content-tab-2"),
                html.Div(dcc.Graph(id="tab3-fuel-chart", style={"height": "480px"}), id="content-tab-3"),
                html.Div(module4_layout(),       id="content-tab-4"),
                html.Div(module5_layout(),       id="content-tab-5"),
                html.Div(module6_layout(),       id="content-tab-6"),
                html.Div(build_module7_layout(), id="content-tab-7"),
                html.Div(module8_layout(),       id="content-tab-8"),
            ], id="tab-content", style={"padding": "0 32px 28px"}),

        ], style={"flex": "1", "overflow": "auto", "backgroundColor": "var(--page-bg)"}),

    ], style={"display": "flex", "flex": "1", "overflow": "hidden"}),

], style={"display": "flex", "flexDirection": "column", "height": "100vh"})

USD_TO_JMD = get_live_exchange_rate(fallback=156.0)
print(f"[startup] USD/JMD rate loaded: {USD_TO_JMD:.4f}")

# ── Kingston retail markup data ──────────────────────────────────
# Derived from field survey of 15 Kingston stations across 3 survey dates
# in June-July 2026, 113 total station-date-grade observations.
KINGSTON_RETAIL_MARKUP_AVG = {
    "g87":    29,   # J$/L above Petrojam reference for 87 octane
    "g90":    34,   # J$/L above Petrojam reference for 90 octane
    "diesel": 48,   # J$/L above Petrojam reference for automotive diesel
}

# Only stations with complete data across all three survey dates for all three
# grades, 9 observations per station. Averages rounded to nearest whole J$/L.
# Sorted from lowest to highest markup.
KINGSTON_STATION_MARKUPS = [
    {"label": "Average across all Kingston stations",                              "markup": None,     "note": "Uses grade-specific mean above"},
    {"label": "Custom — enter full retail price (J$/L)",                          "markup": "custom", "note": ""},
    {"label": "Michael's Service Station (South Camp Road)",                       "markup": 15,       "note": "Lowest markup in complete-data set"},
    {"label": "Johnson's Petroleum (Beechwood Ave)",                               "markup": 25,       "note": ""},
    {"label": "Total Energies (National Heroes Circle)",                           "markup": 28,       "note": ""},
    {"label": "Total Energies Half Way Tree Clock Tower",                          "markup": 29,       "note": ""},
    {"label": "RUBiS Half Way Tree Clock Tower",                                   "markup": 30,       "note": ""},
    {"label": "Fesco Future Energy Source (Beechwood Ave)",                        "markup": 32,       "note": ""},
    {"label": "Texaco (Oxford Road, Half Way Tree)",                               "markup": 35,       "note": ""},
    {"label": "Boot Dunrobin Service Station (Dunrobin Ave)",                      "markup": 39,       "note": ""},
    {"label": "RUBiS (Upper Waterloo Road)",                                       "markup": 46,       "note": ""},
    {"label": "RUBiS (Hope Road)",                                                 "markup": 55,       "note": ""},
    {"label": "Total Energies (Hope Road)",                                        "markup": 65,       "note": "Highest markup in complete-data set"},
]

# ── Module 6: Taxi Feasibility constants ──────────────────────────
TAXI_VEHICLES = {
    "probox": {
        "label": "Toyota Probox 1.5 (used, ICE baseline)",
        "type": "ICE",
        "price_jmd": 1_650_000,   # Jacars.net asking prices June-July 2026, midpoint of range J$0.85M-J$2.35M
        "consumption_urban": 10.7,  # L/100km, real-world urban (inCarDoc user data, 1NZ-FE 1.5L)
        "consumption_combined": 7.6,  # L/100km, real-world combined (inCarDoc)
        "annual_maintenance_jmd": 120_000,
        "notes": "Real-world urban consumption 10.7 L/100km, combined 7.6 L/100km. Price is asking price, not confirmed sale."
    },
    "yuan_plus": {
        "label": "BYD Yuan Plus 2024 (new, primary EV)",
        "type": "EV",
        "price_jmd": None,
        "price_estimate_jmd": 7_670_000,  # ATL Automotive listing (atlautomotive.com, July 2026), converted at J$158/USD
        "consumption_measured": 16.3,  # kWh/100km, weighted from field trip data across 16 legs
        "battery_kwh": 49.92,
        "range_km_realistic": 340,
        "annual_maintenance_jmd": 40_000,
        "notes": "Consumption 16.3 kWh/100km is own field-trip measurement across 16 Kingston route legs, not manufacturer spec. Price J$7,670,000 confirmed from ATL Automotive listing (atlautomotive.com, July 2026), converted at J$158/USD."
    },
    "leaf": {
        "label": "Nissan Leaf 40kWh (used, budget EV)",
        "type": "EV",
        "price_jmd": 3_200_000,
        "consumption_measured": 18.0,  # kWh/100km, estimate for Jamaican urban conditions with AC
        "battery_kwh": 40.0,
        "range_km_realistic": 180,
        "annual_maintenance_jmd": 45_000,
        "notes": "180km realistic range means multiple public charging sessions per shift may be required. Battery degradation is a real concern for taxi-duty cycles in Jamaican heat."
    },
}

TAXI_DAY_PEAK_HOURS = 8
TAXI_DAY_OFFPEAK_HOURS = 4
TAXI_TRIPS_PER_HOUR_PEAK = 4
TAXI_TRIPS_PER_HOUR_OFFPEAK = 2
DEFAULT_FARE_PER_TRIP = 200
DEFAULT_PASSENGERS_PER_TRIP = 5
DEFAULT_TRIP_KM = 5
DEFAULT_LOAN_RATE_PCT = 11.0
DEFAULT_LOAN_YEARS = 4
DEFAULT_DOWNPAYMENT_PCT = 20
FLEET_HQ_CHARGE_RATE_JMD_PER_KWH = 60

# ── Module 4: Fleet Penetration Simulator ────────────────────────
FLEET_BASELINES = {
    "private": {
        "label": "Private Vehicle Fleet",
        "size_2015": 190_000,   # CEIC / OICA, Dec 2015 (published anchor, oldest solid data point)
        "current_estimate": 240_000,  # placeholder estimate assuming ~2.5% annual growth
        "current_source": "PLACEHOLDER: extrapolated from CEIC/OICA 2015 anchor. Not confirmed by STATIN or Transport Authority.",
        "target_pct_2030": 12,
        "km_per_year_avg": 12_000,
        "km_source": "PLACEHOLDER: international average for private vehicles, no Jamaica-specific figure",
        "avg_consumption_l_per_100km": 8.0,
        "avg_purchase_price_jmd": 4_500_000,
        "annual_ev_imports_2023": 280,   # MSTT via Jamaica Observer
    },
    "public": {
        "label": "Public Transport Fleet",
        "size_2015": None,
        "current_estimate": 400,
        "current_source": "JUTC operable fleet approximately 350–450 buses as of mid-2025 (Jamaica Gleaner, July 2025; Dr. L.-R. Harris, personal communication, July 2026). Covers JUTC formal buses only. Minibuses and route taxis are not included.",
        "target_pct_2030": 16,
        "km_per_year_avg": 40_000,
        "km_source": "PLACEHOLDER: taxi/bus estimate based on Kingston route data",
        "avg_consumption_l_per_100km": 10.0,
        "avg_purchase_price_jmd": 2_500_000,
        "annual_ev_imports_2023": None,
    },
    "goj": {
        "label": "Government of Jamaica Fleet",
        "size_2015": None,
        "current_estimate": 3_500,   # placeholder
        "current_source": "PLACEHOLDER: rough estimate. METT has not confirmed a GOJ fleet total.",
        "target_pct_2030": 100,
        "km_per_year_avg": 15_000,
        "km_source": "PLACEHOLDER: rough government use estimate",
        "avg_consumption_l_per_100km": 9.0,
        "avg_purchase_price_jmd": 5_000_000,
        "annual_ev_imports_2023": None,
    },
}

SCURVE_DEFAULTS = {
    "private": {"steepness": 0.6, "midpoint_year": 2032},
    "public":  {"steepness": 0.7, "midpoint_year": 2033},
    "goj":     {"steepness": 0.9, "midpoint_year": 2028},
}

SCURVE_PRESETS = {
    "private": {
        "conservative": {
            "steepness": 0.4,
            "midpoint_year": 2038,
            "note": (
                "Consistent with the current import rate (~280 EVs/year for the private fleet). "
                "No major new demand incentives assumed beyond the existing duty exemption. "
                "Reaches approximately 0.5% penetration by 2030."
            ),
        },
        "base": {
            "steepness": 0.6,
            "midpoint_year": 2032,
            "note": (
                "Moderate infrastructure expansion and some policy follow-through, "
                "but no feebates or direct purchase subsidies. "
                "Reaches approximately 2.8% penetration by 2030."
            ),
        },
        "optimistic": {
            "steepness": 1.0,
            "midpoint_year": 2029,
            "note": (
                "Strong policy package: feebates, subsidised public charging, "
                "and an active consumer awareness programme. "
                "Reaches approximately 8.8% penetration by 2030 -- still short of the 12% target."
            ),
        },
    },
    "public": {
        "conservative": {
            "steepness": 0.4,
            "midpoint_year": 2039,
            "note": (
                "Slow fleet replacement cycle with limited public financing for electric buses "
                "and minibuses. JUTC pilot does not scale significantly before 2030. "
                "Reaches approximately 0.4% penetration by 2030."
            ),
        },
        "base": {
            "steepness": 0.7,
            "midpoint_year": 2033,
            "note": (
                "JUTC pilot expands moderately. Minibus and route taxi EV uptake begins "
                "in the late 2020s but is constrained by financing and charging access. "
                "Reaches approximately 1.7% penetration by 2030."
            ),
        },
        "optimistic": {
            "steepness": 1.1,
            "midpoint_year": 2030,
            "note": (
                "Government-led procurement with international financing accelerates "
                "JUTC fleet transition. Concessional loans available to route taxi operators. "
                "Reaches approximately 8% penetration by 2030 -- still short of the 16% target."
            ),
        },
    },
    "goj": {
        "conservative": {
            "steepness": 0.5,
            "midpoint_year": 2035,
            "note": (
                "Budget constraints and slow procurement cycles delay the transition well past 2030. "
                "Reaches approximately 7.6% penetration by 2030 -- far short of the 100% target."
            ),
        },
        "base": {
            "steepness": 0.9,
            "midpoint_year": 2028,
            "note": (
                "Policy commitment partially delivered with some procurement delays. "
                "Fleet electrification proceeds but falls short of 100% by 2030. "
                "Reaches approximately 85.8% penetration by 2030."
            ),
        },
        "optimistic": {
            "steepness": 1.3,
            "midpoint_year": 2027,
            "note": (
                "Full budget commitment with a dedicated EV procurement programme. "
                "GOJ fleet leads national electrification. "
                "Reaches approximately 98% penetration by 2030 -- effectively on track."
            ),
        },
    },
}

# Jamaica Customs Agency FAQ: ICE import duty 20% + GCT 15% + levies.
# Rough project estimate on J$4.5M average vehicle. Actual varies with engine size and SCT.
ICE_IMPORT_REVENUE_PER_VEHICLE_JMD = 1_400_000
EV_IMPORT_REVENUE_PER_VEHICLE_JMD  =   200_000   # duty-exempt, GCT-exempt; residual fees only

# ── Module 8: Caribbean Regional Comparison Data ───────────────────
# Sources:
#   IEA Global EV Outlook 2026 (iea.org, May 2026)
#   OLADE EV Fleet Report 2024 (olade.org)
#   CARILEC (2025) for Barbados
#   Jamaica Gleaner (2023) for Jamaica fleet figures
#   OUR Jamaica (2021) for Cayman Islands
#   CARICOM EV Month webinar series (November 2025)

REGIONAL_DATA = [
    {
        "country": "Uruguay",
        "region": "Latin America",
        "ev_sales_share_pct": 30.0,
        "ev_fleet_total": 13500,
        "charging_stations": 180,
        "key_policy": "Tax exemptions and subsidies; nearly 100% renewable electricity grid",
        "import_duty_ev_pct": 0.0,
        "fuel_price_usd_per_litre": 2.00,
        "source_year": 2025,
        "source_url": "https://www.iea.org/reports/global-ev-outlook-2026",
    },
    {
        "country": "Costa Rica",
        "region": "Latin America",
        "ev_sales_share_pct": 17.0,
        "ev_fleet_total": 35000,
        "charging_stations": 450,
        "key_policy": "Law 9518 (2017): zero import duties and tax exemptions, being phased out 2025 to 2035",
        "import_duty_ev_pct": 0.0,
        "fuel_price_usd_per_litre": 1.45,
        "source_year": 2025,
        "source_url": "https://www.iea.org/reports/global-ev-outlook-2026",
    },
    {
        "country": "Colombia",
        "region": "Latin America",
        "ev_sales_share_pct": 10.0,
        "ev_fleet_total": 20000,
        "charging_stations": 300,
        "key_policy": "Import duty exemptions; one third of government fleet must be EV by 2025; Bogota operates large electric bus fleet",
        "import_duty_ev_pct": 0.0,
        "fuel_price_usd_per_litre": 0.90,
        "source_year": 2025,
        "source_url": "https://www.iea.org/reports/global-ev-outlook-2026",
    },
    {
        "country": "Brazil",
        "region": "Latin America",
        "ev_sales_share_pct": 9.0,
        "ev_fleet_total": 180000,
        "charging_stations": 12700,
        "key_policy": "Reduced import tariffs being reinstated; BYD assembly plant opened 2025; PHEV dominant over BEV",
        "import_duty_ev_pct": 10.0,
        "fuel_price_usd_per_litre": 1.10,
        "source_year": 2025,
        "source_url": "https://www.iea.org/reports/global-ev-outlook-2026",
    },
    {
        "country": "Barbados",
        "region": "Caribbean",
        "ev_sales_share_pct": None,
        "ev_fleet_total": 600,
        "charging_stations": 100,
        "key_policy": "15 free public charging stations; Caribbean leader in per capita EV usage",
        "import_duty_ev_pct": None,
        "fuel_price_usd_per_litre": 1.35,
        "source_year": 2023,
    },
    {
        "country": "Jamaica",
        "region": "Caribbean",
        "ev_sales_share_pct": 3.0,
        "ev_fleet_total": 6606,
        "charging_stations": 100,
        "key_policy": "National EV Policy 2023: 12% private, 16% public transport, 100% govt fleet by 2030; duty cut from 30% to 10%",
        "import_duty_ev_pct": 10.0,
        "fuel_price_usd_per_litre": 1.27,
        "source_year": 2024,
        "source_url": "https://www.iea.org/reports/global-ev-outlook-2026",
    },
    {
        "country": "Trinidad & Tobago",
        "region": "Caribbean",
        "ev_sales_share_pct": None,
        "ev_fleet_total": None,
        "charging_stations": None,
        "key_policy": "Fossil fuel exporter; heavily subsidised fuel prices; minimal EV policy framework",
        "import_duty_ev_pct": None,
        "fuel_price_usd_per_litre": 0.40,
        "source_year": 2024,
    },
    {
        "country": "Cayman Islands",
        "region": "Caribbean",
        "ev_sales_share_pct": None,
        "ev_fleet_total": 75,
        "charging_stations": None,
        "key_policy": "Small high-income jurisdiction; early adopter but no formal national EV policy",
        "import_duty_ev_pct": 0.0,
        "fuel_price_usd_per_litre": 1.60,
        "source_year": 2021,
    },
    {
        "country": "Dominican Republic",
        "region": "Caribbean",
        "ev_sales_share_pct": 0.7,
        "ev_fleet_total": 11169,
        "charging_stations": None,
        "key_policy": "Zero import duty on EVs; declining imports since 2022 peak (647 units in 2025 vs 2,732 in 2022); 150 electric school buses deployed; grid intensity 0.601 kg CO2/kWh (higher than Jamaica)",
        "import_duty_ev_pct": 0.0,
        "fuel_price_usd_per_litre": 1.30,
        "source_year": 2025,
        "source_url": "https://dominicantoday.com/dr/local/2025/11/23/the-import-of-electric-cars-shows-a-sustained-decline-in-the-dominican-republic/",
    },
    {
        "country": "Bahamas",
        "region": "Caribbean",
        "ev_sales_share_pct": 13.0,
        "ev_fleet_total": 530,
        "charging_stations": None,
        "key_policy": "10% import duty on EVs under US$70,000, 25% above; government targets 50% new auto EV sales by 2035; ~200,000 registered vehicles nationally; dealer-led adoption pattern",
        "import_duty_ev_pct": 10.0,
        "fuel_price_usd_per_litre": 1.30,
        "source_year": 2025,
        "source_url": "https://www.tribune242.com/news/2025/nov/10/quite-a-jump-govt-targeting-50-electric-vehicle-share-by-2035/",
    },
    {
        "country": "Guyana",
        "region": "Caribbean",
        "ev_sales_share_pct": None,
        "ev_fleet_total": 116,
        "charging_stations": 6,
        "key_policy": "100% duty-free and tax-free EV imports (strongest incentive in region); paradox of oil-producing country with slow uptake; 6 GEA charging stations along coast; electricity historically US$0.32/kWh, projected to halve with 2024 gas-to-energy project",
        "import_duty_ev_pct": 0.0,
        "fuel_price_usd_per_litre": 1.10,
        "source_year": 2024,
        "source_url": "https://oilnow.gy/news/worlds-largest-ev-brand-now-in-guyana-adding-momentum-to-vehicle-transition/",
    },
]


# ── Module 5: Emissions Data ───────────────────────────────────────
# Sources:
#   METT (2023). 2022 Jamaica Integrated Resource Plan.
#   Grid CO2 intensity derived from:
#     2022: 2.1 Mt CO2 / 4,425 GWh = 0.474 kg CO2/kWh
#     2030: 1.29 Mt CO2 / 4,688 GWh = 0.275 kg CO2/kWh (50% RE target)
#   Petrol combustion: 2.31 kg CO2/litre (90 octane, standard chemistry)
#   Manufacturing CO2 estimates from IEA lifecycle analysis literature.

GRID_SCENARIOS = {
    "current_2022": {
        "label": "Current grid (2022 mix: 11.5% renewable)",
        "intensity_kg_per_kwh": 0.474,
        "re_pct": 11.5,
    },
    "irp_2026": {
        "label": "IRP projected 2026 (26.7% renewable)",
        "intensity_kg_per_kwh": 0.380,
        "re_pct": 26.7,
    },
    "irp_2030": {
        "label": "IRP 2030 target (49.8% renewable)",
        "intensity_kg_per_kwh": 0.275,
        "re_pct": 49.8,
    },
}

CO2_PER_LITRE_PETROL = 2.31   # kg CO2/litre, 90 octane combustion
CO2_PER_LITRE_DIESEL = 2.68   # kg CO2/litre, automotive diesel

# Approximate BEV manufacturing CO2 premium above equivalent ICE vehicle
# due to battery production. Source: IEA lifecycle analysis literature.
# These are tonnes CO2 of additional manufacturing emissions for BEV vs ICE.
BEV_MANUFACTURING_CO2_PREMIUM = {
    "byd-yuan-pro-new":     7.2,
    "byd-yuan-plus-new":    8.1,
    "byd-seal-new":         9.5,
    "byd-sealion7-new":    12.4,
    "byd-atto8-new":       12.0,
    "nissan-leaf-used":     5.8,
    "hyundai-kona-ev-used": 9.0,
    "kia-soul-ev-used":     9.0,
    "tesla-model3-used":    8.8,
}


def module8_layout():
    import pandas as pd

    df = pd.DataFrame(REGIONAL_DATA)

    # ── Chart 1: Horizontal bar chart of EV sales share ──────────────
    df_bar = df[df["ev_sales_share_pct"].notna()].sort_values(
        "ev_sales_share_pct", ascending=True
    )
    bar_colors = [
        "#2E75B6" if c == "Jamaica" else
        "#1A7A6E" if r == "Caribbean" else
        "#AAAAAA"
        for c, r in zip(df_bar["country"], df_bar["region"])
    ]
    fig_bar = go.Figure()
    fig_bar.add_trace(go.Bar(
        x=df_bar["ev_sales_share_pct"],
        y=df_bar["country"],
        orientation="h",
        marker_color=bar_colors,
        text=[f"{v:.0f}%" for v in df_bar["ev_sales_share_pct"]],
        textposition="outside",
    ))
    fig_bar.add_vline(
        x=12,
        line_dash="dash",
        line_color="#C0392B",
        annotation_text="Jamaica 2030 target (12%)",
        annotation_position="top right",
        annotation_font_color="#C0392B",
        annotation_font_size=11,
    )
    fig_bar.update_layout(
        title={"text": "BEV New Car Sales Share by Country (%, most recent year)",
               "font": {"size": 14}},
        xaxis=dict(title="BEV New Car Sales Share (%)", range=[0, 40],
                   ticksuffix="%"),
        yaxis=dict(title=""),
        plot_bgcolor="#ffffff",
        paper_bgcolor="#ffffff",
        height=340,
        margin=dict(l=120, r=80, t=60, b=60),
        showlegend=False,
    )

    # ── Chart 2: Scatter plot fuel price vs EV adoption ──────────────
    df_scatter = df[
        df["ev_sales_share_pct"].notna() &
        df["fuel_price_usd_per_litre"].notna()
    ].copy()
    df_scatter["fuel_price_jmd_per_litre"] = (df_scatter["fuel_price_usd_per_litre"] * USD_TO_JMD).round(1)
    fig_scatter = go.Figure()

    df_jamaica = df_scatter[df_scatter["country"] == "Jamaica"]
    df_others  = df_scatter[df_scatter["country"] != "Jamaica"]

    fig_scatter.add_trace(go.Scatter(
        x=df_others["fuel_price_jmd_per_litre"],
        y=df_others["ev_sales_share_pct"],
        mode="markers+text",
        marker=dict(color="#1A7A6E", size=14),
        text=df_others["country"],
        textposition="top center",
        textfont=dict(size=11),
        name="Other countries",
    ))
    fig_scatter.add_trace(go.Scatter(
        x=df_jamaica["fuel_price_jmd_per_litre"],
        y=df_jamaica["ev_sales_share_pct"],
        mode="markers+text",
        marker=dict(color="#2E75B6", size=16, line=dict(color="#0E2A24", width=1.5)),
        text=df_jamaica["country"],
        textposition="top center",
        textfont=dict(size=11, color="#2E75B6"),
        name="Jamaica",
    ))

    import numpy as np
    if len(df_scatter) >= 2:
        z = np.polyfit(df_scatter["fuel_price_jmd_per_litre"], df_scatter["ev_sales_share_pct"], 1)
        trend_x = [df_scatter["fuel_price_jmd_per_litre"].min(), df_scatter["fuel_price_jmd_per_litre"].max()]
        trend_y = [z[0] * x + z[1] for x in trend_x]
        fig_scatter.add_trace(go.Scatter(
            x=trend_x, y=trend_y,
            mode="lines",
            line=dict(color="#B0B0B0", width=1.5, dash="dot"),
            name="Trend",
            hoverinfo="skip",
        ))

    fig_scatter.update_layout(
        title={"text": "Retail Fuel Price vs BEV Adoption Rate",
               "font": {"size": 14}},
        xaxis=dict(title="Retail Fuel Price (J$/litre)",
                   tickprefix="J$"),
        yaxis=dict(title="BEV New Car Sales Share (%)",
                   ticksuffix="%"),
        plot_bgcolor="#ffffff",
        paper_bgcolor="#ffffff",
        height=380,
        margin=dict(l=60, r=40, t=60, b=60),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="left", x=0, font=dict(size=11)),
    )

    # ── Summary table ─────────────────────────────────────────────────
    banner = {
        "backgroundColor": "#E1F5EE",
        "color": "#0E2A24",
        "fontWeight": "700",
        "fontSize": "15px",
        "padding": "10px 18px",
        "marginBottom": "12px",
        "marginTop": "20px",
        "borderRadius": "2px",
    }
    th = {
        "backgroundColor": "#1A9E75",
        "color": "white",
        "fontWeight": "600",
        "fontSize": "12px",
        "padding": "8px 12px",
        "textAlign": "left",
        "border": "1px solid #cccccc",
    }

    def td_style(country):
        base = {
            "padding": "7px 12px",
            "fontSize": "12px",
            "border": "1px solid #e0e0e0",
            "verticalAlign": "top",
        }
        if country == "Jamaica":
            base["backgroundColor"] = "#EBF5FB"
            base["fontWeight"] = "600"
        return base

    headers = ["Country", "Region", "BEV Sales Share",
               "EV Fleet Total", "Charging Stations",
               "Import Duty on EVs", "Key Policy Note", "Data Year", "Source"]

    rows = []
    for r in REGIONAL_DATA:
        tds = [
            html.Td(r["country"],                                                                               style=td_style(r["country"])),
            html.Td(r["region"],                                                                                style=td_style(r["country"])),
            html.Td(f"{r['ev_sales_share_pct']:.0f}%" if r["ev_sales_share_pct"] is not None else "No data",   style=td_style(r["country"])),
            html.Td(f"{r['ev_fleet_total']:,}" if r["ev_fleet_total"] is not None else "No data",               style=td_style(r["country"])),
            html.Td(f"{r['charging_stations']:,}" if r["charging_stations"] is not None else "No data",         style=td_style(r["country"])),
            html.Td(f"{r['import_duty_ev_pct']:.0f}%" if r["import_duty_ev_pct"] is not None else "No data",   style=td_style(r["country"])),
            html.Td(r["key_policy"],                                                                            style=td_style(r["country"])),
            html.Td(str(r["source_year"]),                                                                      style=td_style(r["country"])),
            html.Td(
                html.A("Source", href=r.get("source_url", "#"), target="_blank",
                       style={"color": "#1A9E75", "textDecoration": "underline"})
                if r.get("source_url") else "N/A",
                style=td_style(r["country"])
            ),
        ]
        rows.append(html.Tr(tds))

    table = html.Table(
        [html.Thead(html.Tr([html.Th(h, style=th) for h in headers])),
         html.Tbody(rows)],
        style={"width": "100%", "borderCollapse": "collapse",
               "fontSize": "12px"}
    )

    return html.Div([
        html.Div("BEV Adoption by Country", style=banner),
        dcc.Graph(figure=fig_bar, config={"displayModeBar": False}),

        html.Div("Fuel Price vs BEV Adoption Rate", style=banner),
        dcc.Graph(figure=fig_scatter, config={"displayModeBar": False}),
        html.P(
            "Each point is one country. The x-axis is retail fuel price in J$ per litre "
            "(USD converted at J$156 = US$1, approximate BOJ mid-rate 2025-2026); the "
            "y-axis is BEV share of new car sales (not total fleet stock). The dotted line is a "
            "simple linear trend across the five countries with adoption data. Barbados, Trinidad "
            "and Tobago, and Cayman Islands are excluded, no adoption-rate data available for them. "
            "The trend is directionally consistent (higher fuel prices, higher adoption) at the "
            "top of the range, but Jamaica's position, moderate fuel price, lowest adoption in the "
            "group, suggests fuel price alone doesn't explain the gap. Sources: IEA Global EV "
            "Outlook 2026 (iea.org); OLADE (2024).",
            style={"fontSize": "13px", "color": "#444",
                   "marginTop": "8px", "marginBottom": "20px"}
        ),

        html.Div("Regional Comparison Summary Table", style=banner),
        table,
        html.P(
            "Sources: IEA Global EV Outlook 2026 (iea.org); OLADE EV Fleet Report 2024 "
            "(olade.org); CARILEC (2025); Jamaica Gleaner (2023); OUR Jamaica (2021). "
            "Sales share figures refer to new car sales in the most recent reported year. "
            "Jamaica 2030 targets from METT National Electric Vehicle Policy (2023).",
            style={"fontSize": "11px", "color": "#999",
                   "marginTop": "14px", "borderTop": "1px solid #eee",
                   "paddingTop": "10px"}
        ),
    ], style={"padding": "4px"})


def module1_layout():
    lbl = {"fontSize": "12px", "fontWeight": "600", "color": "#555",
           "marginBottom": "4px", "display": "block"}
    inp = {"width": "100%", "padding": "6px 8px", "fontSize": "13px",
           "border": "1px solid #ccc", "borderRadius": "4px",
           "marginBottom": "6px", "boxSizing": "border-box"}
    hint = {"fontSize": "11px", "color": "#888", "marginBottom": "10px", "marginTop": "2px"}
    det_sum = {"cursor": "pointer", "fontWeight": "600", "fontSize": "13px",
               "padding": "6px 0", "marginBottom": "8px"}
    det_style = {"backgroundColor": "#fff", "border": "1px solid #e0e0e0",
                 "borderRadius": "6px", "padding": "14px 16px", "marginBottom": "10px"}

    ice_opts = get_ice_dropdown_options()
    ev_opts  = get_bev_dropdown_options()
    d_ice, d_ev = "toyota-yaris-new", "byd-yuan-pro-new"

    left_panel = html.Div([
        html.Details([
            html.Summary("Vehicle selection and costs", style=det_sum),

            html.H5("ICE Vehicle",
                    style={"color": "#C55A11", "marginTop": "4px", "marginBottom": "10px"}),
            html.Label("Select model", style=lbl),
            dcc.Dropdown(id="m1-ice-dropdown", options=ice_opts, value=d_ice,
                         clearable=False, style={"fontSize": "13px", "marginBottom": "10px"}),
            html.Label("Purchase price (J$)", style=lbl),
            dcc.Input(id="m1-ice-price", type="number", debounce=True,
                      value=ICE_VEHICLES[d_ice]["price_jmd"], style=inp),
            html.P("Auto-filled from selected model. Update with a confirmed sale price.", style=hint),
            html.Label("Fuel consumption (L/100km)", style=lbl),
            dcc.Input(id="m1-ice-consumption", type="number", debounce=True,
                      value=ICE_VEHICLES[d_ice]["consumption_per_100km"], step=0.1, style=inp),
            dcc.Slider(id="m1-ice-consumption-slider", min=3, max=25, step=0.1,
                       value=ICE_VEHICLES[d_ice]["consumption_per_100km"],
                       marks={3: "3", 10: "10", 17: "17", 25: "25"},
                       tooltip={"placement": "bottom", "always_visible": False}),
            html.P("Real-world estimates for Jamaican urban driving. Move slider or type to adjust.", style=hint),

            html.Hr(style={"margin": "10px 0", "borderColor": "#eee"}),

            html.H5("Electric Vehicle",
                    style={"color": "#1A7A6E", "marginTop": "4px", "marginBottom": "10px"}),
            html.Label("Select model", style=lbl),
            dcc.Dropdown(id="m1-ev-dropdown", options=ev_opts, value=d_ev,
                         clearable=False, style={"fontSize": "13px", "marginBottom": "10px"}),
            html.Label("Purchase price (J$)", style=lbl),
            dcc.Input(id="m1-ev-price", type="number", debounce=True,
                      placeholder="Enter dealer quote", value=None, style=inp),
            html.Div(id="m1-ev-note",
                     children=html.P(
                         f"Range: {BEV_VEHICLES[d_ev]['range_km_nedc']} km (NEDC). "
                         "Price not publicly listed — enter a confirmed dealer quote.",
                         style=hint)),
            html.Label("Energy consumption (kWh/100km)", style=lbl),
            dcc.Input(id="m1-ev-consumption", type="number", debounce=True,
                      value=BEV_VEHICLES[d_ev]["consumption_per_100km"], step=0.1, style=inp),
            dcc.Slider(id="m1-ev-consumption-slider", min=10, max=30, step=0.1,
                       value=BEV_VEHICLES[d_ev]["consumption_per_100km"],
                       marks={10: "10", 16: "16", 23: "23", 30: "30"},
                       tooltip={"placement": "bottom", "always_visible": False}),
            html.P("Estimated from battery capacity and NEDC range. Adjust for real-world conditions.", style=hint),
        ], open=True, style=det_style),

        html.Details([
            html.Summary("Driving and ownership", style=det_sum),
            html.Label("Daily driving distance (km)", style=lbl),
            dcc.Input(id="m1-daily-km", type="number", debounce=True, value=50,
                      min=1, max=500, style=inp),
            dcc.Slider(id="m1-daily-km-slider", min=1, max=500, step=1, value=50,
                       marks={1: "1", 100: "100", 250: "250", 500: "500"},
                       tooltip={"placement": "bottom", "always_visible": False}),
            html.P("Kingston commuters typically drive 20–80 km/day. Taxis much higher.", style=hint),
            html.Label("Ownership period (years)", style=lbl),
            dcc.Input(id="m1-years", type="number", debounce=True, value=5,
                      min=1, max=20, style=inp),
            dcc.Slider(id="m1-years-slider", min=1, max=20, step=1, value=5,
                       marks={1: "1", 5: "5", 10: "10", 15: "15", 20: "20"},
                       tooltip={"placement": "bottom", "always_visible": False}),
            html.P("Longer periods show the full benefit of lower EV running costs.", style=hint),
        ], open=True, style=det_style),

        html.Details([
            html.Summary("Charging location", style=det_sum),
            dcc.RadioItems(
                id="m1-charging-location",
                options=[
                    {"label": " Home only",   "value": "home"},
                    {"label": " Public only", "value": "public"},
                    {"label": " Mix of both", "value": "mix"},
                ],
                value="home",
                labelStyle={"display": "block", "fontSize": "13px", "marginBottom": "6px"},
            ),
            html.Div(id="m1-charging-mix-inputs", children=[
                html.Label("% charged at home",
                           style={"fontSize": "12px", "fontWeight": "500", "display": "block",
                                  "marginTop": "10px", "marginBottom": "4px"}),
                dcc.Input(id="m1-home-charge-pct", type="number", debounce=True,
                          value=70, min=0, max=100, step=1,
                          style={"width": "100px", "padding": "6px 8px", "fontSize": "13px",
                                 "border": "1px solid #ccc", "borderRadius": "4px"}),
                html.Span(" % (rest at public rate)",
                          style={"fontSize": "12px", "color": "#888", "marginLeft": "8px"}),
            ], style={"display": "none"}),
            html.P("Home rate and public rate are set in Global settings above.", style=hint),
        ], open=True, style=det_style),

        html.Div(id="m1-summary-cards"),

        html.P(
            "ICE prices: Toyota Jamaica (toyotajamaica.com, June 2026), converted at J$158.53/USD. "
            "EV prices: not publicly listed by the authorized dealer in Jamaica — enter a confirmed dealer quote. "
            "Consumption figures are estimates for Jamaican driving conditions.",
            style={"fontSize": "11px", "color": "#999", "marginTop": "8px",
                   "borderTop": "1px solid #eee", "paddingTop": "10px"}),
    ], style={"width": "38%", "minWidth": "300px", "flexShrink": "0"})

    right_panel = html.Div([
        html.P(
            "Enter all required fields to see the Total Cost of Ownership chart.",
            id="m1-tco-placeholder",
            style={"color": "#aaa", "fontSize": "13px", "marginTop": "40px",
                   "textAlign": "center"},
        ),
        dcc.Graph(id="m1-tco-fig", style={"display": "none"},
                  config={"displayModeBar": False}),
    ], style={
        "flex": "1", "minWidth": "300px",
        "position": "sticky", "top": "20px", "alignSelf": "flex-start",
    })

    return html.Div([
        html.Div([left_panel, right_panel],
                 style={"display": "flex", "gap": "24px", "alignItems": "flex-start"}),
    ])

# ── Callbacks ─────────────────────────────────────────────────────
@app.callback(
    Output("markup-custom-input-wrapper", "style"),
    Input("markup-station-select", "value"),
)
def toggle_custom_markup_input(station_idx):
    if station_idx is None:
        return {"display": "none"}
    if KINGSTON_STATION_MARKUPS[station_idx]["markup"] == "custom":
        return {"display": "block"}
    return {"display": "none"}


@app.callback(
    Output("effective-fuel-price-store", "data"),
    Output("effective-fuel-price-display", "children"),
    Input("fuel-grade-select", "value"),
    Input("markup-station-select", "value"),
    Input("markup-custom-input", "value"),
)
def compute_effective_fuel_price(grade, station_idx, custom_markup):
    if grade is None:
        return None, ""
    ref_price = latest_prices.get(grade)
    if ref_price is None:
        return None, ""

    if station_idx is None:
        markup = KINGSTON_RETAIL_MARKUP_AVG.get(grade, 34)
        markup_source = "Kingston average"
    else:
        station = KINGSTON_STATION_MARKUPS[station_idx]
        if station["markup"] is None:
            markup = KINGSTON_RETAIL_MARKUP_AVG.get(grade, 34)
            markup_source = "Kingston average"
        elif station["markup"] == "custom":
            if custom_markup is not None and custom_markup > 0:
                implied_markup = custom_markup - ref_price
                markup = implied_markup
                effective = round(custom_markup, 2)
                display = (
                    f"Full retail price J${effective:.2f}/L "
                    f"(implies markup of J${implied_markup:.2f}/L above Petrojam reference)"
                )
                return effective, display
            markup = 0
            markup_source = "custom (no price entered)"
        else:
            markup = station["markup"]
            markup_source = station["label"]

    effective = round(ref_price + markup, 2)
    display = f"Petrojam J${ref_price:.2f} + markup J${markup:.2f} = J${effective:.2f}/L ({markup_source})"
    return effective, display


@app.callback(
    Output("global-settings-summary", "children"),
    Input("effective-fuel-price-store", "data"),
    Input("electricity-rate-slider", "value"),
)
def update_global_settings_summary(effective_price, electricity_rate):
    fuel_display = f"J${effective_price}/L" if effective_price else "not set"
    return html.P([
        html.Strong("Active global settings: "),
        f"Fuel price = {fuel_display}",
        f"   |   Electricity rate = J${electricity_rate}/kWh",
    ], style={"fontSize": "13px", "color": "#444", "margin": "0"})


@app.callback(
    Output("m6-fuel-price-prompt", "children"),
    Input("effective-fuel-price-store", "data"),
)
def show_fuel_price_prompt(effective_price):
    if effective_price is None:
        return html.Div([
            html.P("Select a fuel grade in Global settings to enable Module 1, 5, and 6 calculations.",
                   style={"margin": "0", "fontSize": "13px", "color": "#856404"}),
        ], style={
            "backgroundColor": "#FFF9E6",
            "border": "1px solid #E0A106",
            "borderLeft": "4px solid #E0A106",
            "borderRadius": "6px",
            "padding": "10px 16px",
            "margin": "0 32px 12px",
        })
    return None


@app.callback(
    Output("m1-ice-price", "value"),
    Input("m1-ice-dropdown", "value")
)
def update_ice_inputs(model_key):
    return ICE_VEHICLES[model_key]["price_jmd"]


@app.callback(
    Output("m1-ev-note",  "children"),
    Output("m1-ev-price", "value"),
    Input("m1-ev-dropdown", "value")
)
def update_ev_inputs(model_key):
    v = BEV_VEHICLES[model_key]
    price = v.get("price_jmd")
    source = v.get("price_source")
    if price is not None and source:
        note = html.Div([
            html.P(
                f"Range: {v.get('range_km_nedc')} km (NEDC). "
                f"Price auto-filled from {source}. "
                "You may override this with a negotiated price.",
                style={"fontSize": "11px", "color": "#2d8a2d",
                       "marginTop": "2px", "marginBottom": "10px"},
            ),
        ])
    else:
        note = html.P(
            f"Range: {v.get('range_km_nedc')} km (NEDC). "
            "Price not publicly listed — enter a confirmed dealer quote.",
            style={"fontSize": "11px", "color": "#888",
                   "marginTop": "2px", "marginBottom": "10px"},
        )
    return note, price


@app.callback(
    Output("m1-charging-mix-inputs", "style"),
    Input("m1-charging-location", "value")
)
def toggle_charging_mix_input(location):
    if location == "mix":
        return {"display": "block"}
    return {"display": "none"}


@app.callback(
    Output("m5-ice-consumption", "value"),
    Input("m5-ice-dropdown", "value")
)
def m5_update_ice(model_key):
    return ICE_VEHICLES[model_key]["consumption_per_100km"]


@app.callback(
    Output("m5-ev-consumption", "value"),
    Input("m5-ev-dropdown", "value")
)
def m5_update_ev(model_key):
    return BEV_VEHICLES[model_key]["consumption_per_100km"]


@app.callback(
    Output("m5-cards",   "children"),
    Output("m5-co2-fig", "figure"),
    Input("m5-ice-dropdown", "value"),
    Input("m5-ice-consumption", "value"),
    Input("m5-ev-dropdown", "value"),
    Input("m5-ev-consumption", "value"),
    Input("m5-daily-km", "value"),
    Input("m5-years", "value"),
    Input("m5-grid-scenario", "value"),
)
def calculate_module5(ice_key, ice_consumption, ev_key, ev_consumption,
                      daily_km, years, grid_scenario):
    empty_fig = go.Figure()
    empty_fig.update_layout(
        plot_bgcolor="#ffffff", paper_bgcolor="#ffffff",
        xaxis={"visible": False}, yaxis={"visible": False},
        annotations=[{"text": "Fill in inputs to see the CO2 chart.",
                      "xref": "paper", "yref": "paper", "x": 0.5, "y": 0.5,
                      "showarrow": False, "font": {"size": 13, "color": "#aaa"}}],
    )
    if not all([ice_consumption, ev_consumption, daily_km, years, grid_scenario]):
        return (html.P("Enter all inputs to see results.",
                       style={"color": "#888", "fontSize": "13px"}),
                empty_fig)

    years = int(years)
    grid = GRID_SCENARIOS[grid_scenario]
    intensity = grid["intensity_kg_per_kwh"]
    annual_km = daily_km * 365.0

    annual_co2_ice = (ice_consumption / 100) * annual_km * CO2_PER_LITRE_PETROL
    annual_co2_ev  = (ev_consumption  / 100) * annual_km * intensity

    mfg_premium_t  = BEV_MANUFACTURING_CO2_PREMIUM.get(ev_key, 8.0)
    mfg_premium_kg = mfg_premium_t * 1000

    lifetime_co2_ice = annual_co2_ice * years
    lifetime_co2_ev  = annual_co2_ev  * years + mfg_premium_kg

    annual_saving = annual_co2_ice - annual_co2_ev
    if annual_saving <= 0:
        carbon_payback_yrs = None
        payback_text = "BEV emits more per km at this grid mix"
        payback_col  = "#C0392B"
    else:
        carbon_payback_yrs = mfg_premium_kg / annual_saving
        if carbon_payback_yrs <= 20:
            payback_text = f"{carbon_payback_yrs:.1f} years"
            payback_col  = "#2d8a2d"
        else:
            payback_text = f"{carbon_payback_yrs:.1f} years (beyond 20yr horizon)"
            payback_col  = "#E07B22"

    card = {
        "backgroundColor": "#ffffff", "border": "1px solid #e0e0e0",
        "borderRadius": "6px", "padding": "12px 14px",
        "flex": "1", "minWidth": "130px", "textAlign": "center",
    }
    big  = {"fontSize": "18px", "fontWeight": "700", "margin": "4px 0"}
    tiny = {"fontSize": "12px", "color": "#777", "margin": "0"}

    cards = html.Div([
        html.Div([html.P("Annual ICE CO2", style=tiny),
                  html.P(f"{annual_co2_ice/1000:.2f} t",
                         style={**big, "color": "#C55A11"})], style=card),
        html.Div([html.P("Annual BEV CO2", style=tiny),
                  html.P(f"{annual_co2_ev/1000:.2f} t",
                         style={**big, "color": "#1A7A6E"})], style=card),
        html.Div([html.P("Annual CO2 saving", style=tiny),
                  html.P(f"{(annual_co2_ice - annual_co2_ev)/1000:.2f} t",
                         style={**big, "color": "#2d8a2d"
                                if annual_co2_ice > annual_co2_ev else "#C0392B"})],
                 style=card),
        html.Div([html.P(f"Lifetime ICE ({years} yr)", style=tiny),
                  html.P(f"{lifetime_co2_ice/1000:.1f} t",
                         style={**big, "color": "#C55A11"})], style=card),
        html.Div([html.P("Lifetime BEV incl. mfg", style=tiny),
                  html.P(f"{lifetime_co2_ev/1000:.1f} t",
                         style={**big, "color": "#1A7A6E"})], style=card),
        html.Div([html.P("Carbon payback", style=tiny),
                  html.P(payback_text,
                         style={**big, "color": payback_col, "fontSize": "14px"})],
                 style=card),
    ], style={"display": "flex", "gap": "8px", "flexWrap": "wrap", "marginTop": "12px"})

    year_list      = list(range(0, years + 1))
    ice_cumulative = [annual_co2_ice * y / 1000 for y in year_list]
    ev_cumulative  = [annual_co2_ev  * y / 1000 + mfg_premium_kg / 1000
                      for y in year_list]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=year_list, y=ice_cumulative, mode="lines+markers",
        name="ICE cumulative CO2",
        line=dict(color="#C55A11", width=2), marker=dict(size=6),
    ))
    fig.add_trace(go.Scatter(
        x=year_list, y=ev_cumulative, mode="lines+markers",
        name="BEV cumulative CO2 (incl. manufacturing)",
        line=dict(color="#1A7A6E", width=2), marker=dict(size=6),
    ))
    if carbon_payback_yrs is not None and 0 < carbon_payback_yrs <= years:
        fig.add_vline(
            x=carbon_payback_yrs,
            line_dash="dash", line_color="#2d8a2d",
            annotation_text=f"Carbon payback: {carbon_payback_yrs:.1f} yrs",
            annotation_position="top right",
            annotation_font_color="#2d8a2d",
            annotation_font_size=11,
        )
    fig.update_layout(
        title={"text": f"Cumulative CO2 Emissions over {years} Years (tonnes)",
               "font": {"size": 14}},
        xaxis=dict(title="Year of ownership", dtick=1),
        yaxis=dict(title="Cumulative CO2 (tonnes)"),
        plot_bgcolor="#ffffff",
        paper_bgcolor="#ffffff",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        hovermode="x unified",
        height=440,
        margin=dict(l=60, r=40, t=70, b=50),
    )

    return cards, fig


@app.callback(
    Output("m1-summary-cards", "children"),
    Output("m1-tco-fig", "figure"),
    Output("m1-tco-fig", "style"),
    Output("m1-tco-placeholder", "style"),
    Input("m1-ice-price", "value"),
    Input("m1-ice-consumption", "value"),
    Input("m1-ev-price", "value"),
    Input("m1-ev-consumption", "value"),
    Input("m1-daily-km", "value"),
    Input("effective-fuel-price-store", "data"),
    Input("electricity-rate-slider", "value"),
    Input("m1-years", "value"),
    Input("m1-ice-dropdown", "value"),
    Input("m1-ev-dropdown", "value"),
    Input("public-charging-rate", "value"),
    Input("m1-charging-location", "value"),
    Input("m1-home-charge-pct", "value"),
)
def calculate_module1(ice_price, ice_consumption, ev_price, ev_consumption,
                      daily_km, fuel_price, electricity_rate, years,
                      ice_model_key, ev_model_key,
                      public_rate, charging_location, home_charge_pct):
    hide_chart = {"display": "none"}
    show_chart = {"display": "block"}
    show_ph    = {}
    hide_ph    = {"display": "none"}
    empty_fig  = go.Figure()

    if not all([ice_consumption, ev_consumption, daily_km, fuel_price, electricity_rate]):
        msg = html.P(
            "Enter all required values (fuel price in Global settings, consumption, daily distance) to see results.",
            style={"color": "#888", "fontSize": "13px"},
        )
        return msg, empty_fig, hide_chart, show_ph

    if charging_location == "public":
        effective_ev_rate = public_rate if public_rate else electricity_rate
    elif charging_location == "mix":
        home_pct = (home_charge_pct if home_charge_pct is not None else 70) / 100
        pub_r = public_rate if public_rate else electricity_rate
        effective_ev_rate = electricity_rate * home_pct + pub_r * (1 - home_pct)
    else:
        effective_ev_rate = electricity_rate

    cost_km_ice = (ice_consumption / 100) * fuel_price
    cost_km_ev  = (ev_consumption  / 100) * effective_ev_rate
    annual_km   = daily_km * 365
    annual_ice  = cost_km_ice * annual_km
    annual_ev   = cost_km_ev  * annual_km
    savings     = annual_ice - annual_ev

    rc = {
        "backgroundColor": "#ffffff", "border": "1px solid #e0e0e0",
        "borderRadius": "6px", "padding": "12px 14px",
        "flex": "1", "minWidth": "130px", "textAlign": "center",
    }
    big  = {"fontSize": "15px", "fontWeight": "700", "margin": "4px 0"}
    tiny = {"fontSize": "12px", "color": "#777", "margin": "0"}

    summary_cards = html.Div([
        html.Div([html.P("ICE fuel cost/km", style=tiny),
                  html.P(f"J${cost_km_ice:.2f}", style={**big, "color": "#C55A11"})], style=rc),
        html.Div([html.P("EV energy cost/km", style=tiny),
                  html.P(f"J${cost_km_ev:.2f}", style={**big, "color": "#1A7A6E"})], style=rc),
        html.Div([html.P("Annual savings", style=tiny),
                  html.P(
                      f"J${savings:,.0f}" if savings >= 0 else f"-J${abs(savings):,.0f}",
                      style={**big, "color": "#2E75B6" if savings >= 0 else "#C00000"}
                  )], style=rc),
    ], style={"display": "flex", "gap": "8px", "flexWrap": "wrap",
              "marginTop": "12px", "marginBottom": "4px"})

    if not ev_price:
        return summary_cards, empty_fig, hide_chart, show_ph

    years = int(years) if years else 5
    ice_annual_fuel  = (ice_consumption / 100) * fuel_price * daily_km * 365
    ev_annual_energy = (ev_consumption  / 100) * effective_ev_rate * daily_km * 365

    ice_v = ICE_VEHICLES[ice_model_key]
    ev_v  = BEV_VEHICLES[ev_model_key]
    ice_dep_y1, ice_dep_sub, ice_maint = (
        ice_v["depreciation_y1"], ice_v["depreciation_subsequent"], ice_v["annual_maintenance_jmd"]
    )
    ev_dep_y1, ev_dep_sub, ev_maint = (
        ev_v["depreciation_y1"], ev_v["depreciation_subsequent"], ev_v["annual_maintenance_jmd"]
    )

    ice_cum = [0.0]
    ev_cum  = [0.0]
    for y in range(1, years + 1):
        ice_val = ice_price * (1 - ice_dep_y1) * (1 - ice_dep_sub) ** (y - 1)
        ice_cum.append((ice_price - ice_val) + (ice_annual_fuel + ice_maint) * y)
        ev_val  = ev_price  * (1 - ev_dep_y1)  * (1 - ev_dep_sub)  ** (y - 1)
        ev_cum.append((ev_price - ev_val) + (ev_annual_energy + ev_maint) * y)

    x_yrs = list(range(0, years + 1))
    crossover = None
    for i in range(len(x_yrs) - 1):
        d0, d1 = ice_cum[i] - ev_cum[i], ice_cum[i + 1] - ev_cum[i + 1]
        if d0 * d1 < 0:
            crossover = i + d0 / (d0 - d1)
            break

    fig_tco = go.Figure()
    fig_tco.add_trace(go.Scatter(
        x=x_yrs, y=[v / 1_000_000 for v in ice_cum],
        mode="lines+markers", name="ICE Total Cost",
        line={"color": "#C55A11", "width": 2}, marker={"size": 6},
    ))
    fig_tco.add_trace(go.Scatter(
        x=x_yrs, y=[v / 1_000_000 for v in ev_cum],
        mode="lines+markers", name="EV Total Cost",
        line={"color": "#1A7A6E", "width": 2}, marker={"size": 6},
    ))
    if crossover is not None:
        fig_tco.add_vline(
            x=crossover, line_dash="dash", line_color="#888",
            annotation_text=f"Payback ~{crossover:.1f} yrs",
            annotation_position="top right",
        )
    fig_tco.update_layout(
        title="Total Cost of Ownership",
        xaxis_title="Year",
        yaxis_title="Cumulative Cost (J$ millions)",
        plot_bgcolor="#ffffff",
        paper_bgcolor="#ffffff",
        hovermode="x unified",
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.02,
                "xanchor": "right", "x": 1},
        margin={"t": 60, "b": 40, "l": 60, "r": 20},
        height=420,
    )
    return summary_cards, fig_tco, show_chart, hide_ph


@app.callback(
    Output("m1-ice-consumption", "value"),
    Output("m1-ice-consumption-slider", "value"),
    Input("m1-ice-consumption", "value"),
    Input("m1-ice-consumption-slider", "value"),
    Input("m1-ice-dropdown", "value"),
    prevent_initial_call=True,
)
def sync_m1_ice_consumption(inp_val, slider_val, model_key):
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update, dash.no_update
    tid = ctx.triggered[0]["prop_id"].split(".")[0]
    if tid == "m1-ice-dropdown":
        v = ICE_VEHICLES[model_key]["consumption_per_100km"]
        return v, v
    if tid == "m1-ice-consumption":
        return dash.no_update, inp_val
    return slider_val, dash.no_update


@app.callback(
    Output("m1-ev-consumption", "value"),
    Output("m1-ev-consumption-slider", "value"),
    Input("m1-ev-consumption", "value"),
    Input("m1-ev-consumption-slider", "value"),
    Input("m1-ev-dropdown", "value"),
    prevent_initial_call=True,
)
def sync_m1_ev_consumption(inp_val, slider_val, model_key):
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update, dash.no_update
    tid = ctx.triggered[0]["prop_id"].split(".")[0]
    if tid == "m1-ev-dropdown":
        v = BEV_VEHICLES[model_key]["consumption_per_100km"]
        return v, v
    if tid == "m1-ev-consumption":
        return dash.no_update, inp_val
    return slider_val, dash.no_update


@app.callback(
    Output("m1-daily-km", "value"),
    Output("m1-daily-km-slider", "value"),
    Input("m1-daily-km", "value"),
    Input("m1-daily-km-slider", "value"),
    prevent_initial_call=True,
)
def sync_m1_daily_km(inp_val, slider_val):
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update, dash.no_update
    tid = ctx.triggered[0]["prop_id"].split(".")[0]
    if tid == "m1-daily-km":
        return dash.no_update, inp_val
    return slider_val, dash.no_update


@app.callback(
    Output("m1-years", "value"),
    Output("m1-years-slider", "value"),
    Input("m1-years", "value"),
    Input("m1-years-slider", "value"),
    prevent_initial_call=True,
)
def sync_m1_years(inp_val, slider_val):
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update, dash.no_update
    tid = ctx.triggered[0]["prop_id"].split(".")[0]
    if tid == "m1-years":
        return dash.no_update, inp_val
    return slider_val, dash.no_update


MODULE_INFO = {
    "tab-1": ("EV vs. ICE Calculator",   "Week 2",   "#2E75B6"),
    "tab-2": ("Route Cost Map",                    "Week 3",   "#2E75B6"),
    "tab-3": ("Gas & Energy Price Tracker",        "Week 2",   "#2E75B6"),
    "tab-4": ("Fleet Penetration Simulator",       "Week 3",   "#2E75B6"),
    "tab-5": ("Emissions Impact Calculator",       "Week 3",   "#1A7A6E"),
    "tab-6": ("Taxi Feasibility Tool",             "Week 3",   "#1A7A6E"),
    "tab-7": ("Fiscal Policy & Duty Tracker",      "Week 4",   "#C55A11"),
    "tab-8": ("Caribbean Regional Comparison",     "Week 3-4", "#C55A11"),
}

ALL_CONTENT_IDS = ["content-home"] + [f"content-{k}" for k in MODULE_INFO.keys()]


@app.callback(
    [Output(cid, "style") for cid in ALL_CONTENT_IDS],
    Input("active-tab-store", "data"),
)
def toggle_module_visibility(active_tab):
    target = f"content-{active_tab}"
    return [
        ({"display": "block"} if cid == target else {"display": "none"})
        for cid in ALL_CONTENT_IDS
    ]


def module5_layout():
    lbl = {"fontSize": "12px", "fontWeight": "600", "color": "#555",
           "marginBottom": "4px", "display": "block"}
    inp = {
        "width": "100%", "padding": "6px 8px", "fontSize": "13px",
        "border": "1px solid #ccc", "borderRadius": "4px",
        "marginBottom": "14px", "boxSizing": "border-box",
    }
    det_style = {"backgroundColor": "#fff", "border": "1px solid #e0e0e0",
                 "borderRadius": "6px", "padding": "14px 16px", "marginBottom": "10px"}

    ice_opts  = [{"label": v["label"], "value": k} for k, v in ICE_VEHICLES.items()]
    ev_opts   = [{"label": v["label"], "value": k} for k, v in BEV_VEHICLES.items()]
    grid_opts = [{"label": v["label"], "value": k} for k, v in GRID_SCENARIOS.items()]

    d_ice  = "toyota-yaris-new"
    d_ev   = "byd-yuan-pro-new"
    d_grid = "current_2022"

    left_panel = html.Div([
        html.Div([
            html.H4("ICE Vehicle", style={"color": "#C55A11",
                    "marginTop": "0", "marginBottom": "12px"}),
            html.Label("Select model", style=lbl),
            dcc.Dropdown(id="m5-ice-dropdown", options=ice_opts,
                         value=d_ice, clearable=False,
                         style={"fontSize": "13px", "marginBottom": "14px"}),
            html.Label("Fuel consumption (L/100km)", style=lbl),
            dcc.Input(id="m5-ice-consumption", type="number", debounce=True,
                      value=ICE_VEHICLES[d_ice]["consumption_per_100km"],
                      step=0.1, style=inp),
        ], style=det_style),

        html.Div([
            html.H4("Electric Vehicle", style={"color": "#1A7A6E",
                    "marginTop": "0", "marginBottom": "12px"}),
            html.Label("Select model", style=lbl),
            dcc.Dropdown(id="m5-ev-dropdown", options=ev_opts,
                         value=d_ev, clearable=False,
                         style={"fontSize": "13px", "marginBottom": "14px"}),
            html.Label("Energy consumption (kWh/100km)", style=lbl),
            dcc.Input(id="m5-ev-consumption", type="number", debounce=True,
                      value=BEV_VEHICLES[d_ev]["consumption_per_100km"],
                      step=0.1, style=inp),
        ], style=det_style),

        html.Div([
            html.H4("Driving and Grid", style={"color": "#2E75B6",
                    "marginTop": "0", "marginBottom": "12px"}),
            html.Label("Daily driving distance (km)", style=lbl),
            dcc.Input(id="m5-daily-km", type="number", debounce=True,
                      value=50, min=1, max=500, step=1, style=inp),
            html.Label("Ownership period (years)", style=lbl),
            dcc.Input(id="m5-years", type="number", debounce=True,
                      value=5, min=1, max=20, step=1, style=inp),
            html.Label("Grid scenario", style=lbl),
            dcc.Dropdown(id="m5-grid-scenario", options=grid_opts,
                         value=d_grid, clearable=False,
                         style={"fontSize": "13px", "marginBottom": "4px"}),
            html.P("Source: METT 2022 Jamaica IRP (Cabinet approved, Aug 2023).",
                   style={"fontSize": "10px", "color": "#888", "marginTop": "4px"}),
        ], style=det_style),

        html.Div(id="m5-cards"),

        html.P([
            "Petrol CO2: 2.31 kg CO2/litre (90 octane combustion chemistry). ",
            "Grid CO2 intensities derived from METT (2023) 2022 Jamaica Integrated "
            "Resource Plan: 2022 actual (2.1 Mt CO2 / 4,425 GWh); 2030 IRP target "
            "(1.29 Mt CO2 / 4,688 GWh). BEV manufacturing CO2 premium estimates "
            "from IEA lifecycle analysis literature. All figures are estimates."
        ], style={"fontSize": "11px", "color": "#999", "marginTop": "12px",
                  "borderTop": "1px solid #eee", "paddingTop": "10px"}),
    ], style={"width": "40%", "minWidth": "300px", "flexShrink": "0"})

    right_panel = html.Div([
        dcc.Graph(id="m5-co2-fig", style={"height": "480px"},
                  config={"displayModeBar": False}),
    ], style={
        "flex": "1",
        "minWidth": "300px",
        "position": "sticky",
        "top": "20px",
        "alignSelf": "flex-start",
        "backgroundColor": "#ffffff",
        "border": "1px solid #e0e0e0",
        "borderRadius": "8px",
        "padding": "16px",
        "overflowY": "auto",
        "maxHeight": "90vh",
    })

    return html.Div([
        html.Div([left_panel, right_panel],
                 style={"display": "flex", "gap": "20px",
                        "alignItems": "flex-start", "flexWrap": "wrap"}),
    ])


def module4_layout():
    banner = {
        "backgroundColor": "#E1F5EE", "color": "#0E2A24",
        "fontWeight": "700", "fontSize": "15px",
        "padding": "10px 16px", "marginBottom": "12px",
        "marginTop": "8px", "borderRadius": "6px",
        "borderLeft": "3px solid #1A9E75",
    }
    lbl = {"fontSize": "12px", "fontWeight": "600", "color": "#555",
           "marginBottom": "4px", "display": "block"}
    inp = {"width": "100%", "padding": "6px 8px", "fontSize": "13px",
           "border": "1px solid #ccc", "borderRadius": "4px",
           "marginBottom": "10px", "boxSizing": "border-box"}

    btn_base = {
        "padding": "7px 14px", "fontSize": "12px", "fontWeight": "600",
        "border": "1px solid #1A9E75", "borderRadius": "4px",
        "cursor": "pointer", "backgroundColor": "#ffffff", "color": "#1A9E75",
        "transition": "background-color 0.15s",
    }

    def stream_controls(stream_key):
        b = FLEET_BASELINES[stream_key]
        s = SCURVE_DEFAULTS[stream_key]
        preset_note_default = SCURVE_PRESETS[stream_key]["base"]["note"]

        return html.Div([
            html.Div([
                html.H4(b["label"],
                        style={"color": "#1A9E75", "marginTop": "0", "marginBottom": "4px"}),
                html.P(
                    f"2030 target: {b['target_pct_2030']}% EV penetration "
                    "(National EV Policy 2023)",
                    style={"fontSize": "12px", "color": "#666", "marginBottom": "14px"},
                ),

                html.Label("Choose a scenario", style=lbl),
                html.Div([
                    html.Button(
                        "Conservative",
                        id=f"m4-{stream_key}-preset-conservative",
                        n_clicks=0,
                        style=btn_base,
                    ),
                    html.Button(
                        "Base case",
                        id=f"m4-{stream_key}-preset-base",
                        n_clicks=0,
                        style=btn_base,
                    ),
                    html.Button(
                        "Optimistic",
                        id=f"m4-{stream_key}-preset-optimistic",
                        n_clicks=0,
                        style=btn_base,
                    ),
                ], style={"display": "flex", "gap": "8px",
                          "marginBottom": "10px", "flexWrap": "wrap"}),

                html.P(
                    id=f"m4-{stream_key}-preset-note",
                    children=preset_note_default,
                    style={
                        "fontSize": "11px", "color": "#444",
                        "backgroundColor": "#f4faf8",
                        "padding": "8px 12px", "borderRadius": "4px",
                        "borderLeft": "3px solid #1A9E75",
                        "marginBottom": "14px",
                    },
                ),

                html.Details([
                    html.Summary(
                        "Fine-tune the S-curve (advanced)",
                        style={
                            "fontSize": "12px", "cursor": "pointer",
                            "color": "#777", "padding": "4px 0",
                            "marginBottom": "10px",
                        },
                    ),
                    html.P(
                        "Steepness: how sharply adoption accelerates once it starts. "
                        "Midpoint: the year when 50% of the stream's target penetration is reached. "
                        "Clicking a preset above updates these values automatically.",
                        style={"fontSize": "11px", "color": "#888", "marginBottom": "10px"},
                    ),
                    html.Label(
                        "S-curve steepness  (0.1 = slow gradual ramp,  1.5 = sharp rapid ramp)",
                        style=lbl,
                    ),
                    dcc.Slider(
                        id=f"m4-{stream_key}-steepness",
                        min=0.1, max=1.5, step=0.05, value=s["steepness"],
                        marks={0.1: "slow", 0.5: "", 0.8: "medium", 1.2: "", 1.5: "sharp"},
                        tooltip={"placement": "bottom", "always_visible": True},
                    ),
                    html.Div(style={"height": "10px"}),
                    html.Label(
                        "Midpoint year  (year when 50% of the target penetration is reached)",
                        style=lbl,
                    ),
                    dcc.Slider(
                        id=f"m4-{stream_key}-midpoint",
                        min=2027, max=2045, step=1, value=s["midpoint_year"],
                        marks={
                            2027: "2027", 2030: "2030", 2035: "2035",
                            2040: "2040", 2045: "2045",
                        },
                        tooltip={"placement": "bottom", "always_visible": True},
                    ),
                    html.Div(style={"height": "10px"}),
                ], style={"marginBottom": "12px"}),

                html.Hr(style={"margin": "10px 0", "borderColor": "#eee"}),

                html.Label("Current fleet size (vehicles)", style=lbl),
                dcc.Input(
                    id=f"m4-{stream_key}-fleet-size", type="number", debounce=True,
                    value=b["current_estimate"], min=100, max=10_000_000, step=100,
                    style=inp,
                ),
                html.P(
                    b["current_source"],
                    style={"fontSize": "10px", "color": "#C0392B",
                           "marginTop": "-6px", "marginBottom": "10px"},
                ),

                html.Label("Avg annual km per vehicle", style=lbl),
                dcc.Input(
                    id=f"m4-{stream_key}-km-per-year", type="number", debounce=True,
                    value=b["km_per_year_avg"], min=1000, max=100000, step=1000,
                    style=inp,
                ),

                html.Label("Avg ICE consumption (L/100km)", style=lbl),
                dcc.Input(
                    id=f"m4-{stream_key}-consumption", type="number", debounce=True,
                    value=b["avg_consumption_l_per_100km"], min=3, max=25, step=0.1,
                    style=inp,
                ),

            ], style={
                "backgroundColor": "#fff", "border": "1px solid #e0e0e0",
                "borderRadius": "6px", "padding": "16px", "marginBottom": "16px",
            }),
        ])

    left_children = [

        html.Div(
            "Fleet Penetration Simulator -- Jamaica 2030 EV Targets",
            style=banner,
        ),
        html.P([
            "This module projects EV adoption across three fleet streams against Jamaica's "
            "National EV Policy 2023 targets. Use the scenario presets for each stream to "
            "choose Conservative, Base case, or Optimistic assumptions, then expand "
            "'Fine-tune' if you want to adjust the S-curve shape manually. "
            "The chart below updates immediately."
        ], style={"fontSize": "13px", "color": "#444", "marginBottom": "16px"}),

        html.P([
            html.Strong("Important on data confidence: "),
            "Only the private-stream 2015 baseline (190,000 vehicles) is from a published "
            "international source. All three current fleet sizes are PLACEHOLDERS pending "
            "institutional confirmation from METT, STATIN, and the Transport Authority. "
            "The S-curve shape is a modelling assumption, not a forecast."
        ], style={
            "fontSize": "11px", "color": "#666",
            "borderLeft": "3px solid #E0A106",
            "padding": "10px 14px", "backgroundColor": "#FFF9E6",
            "marginBottom": "16px", "borderRadius": "4px",
        }),

        html.Div("Global projection settings", style=banner),
        html.Div([
            html.Div([
                html.Label("Projection horizon (years from today)", style=lbl),
                dcc.Slider(
                    id="m4-horizon", min=5, max=25, step=1, value=15,
                    marks={5: "5", 10: "10", 15: "15", 20: "20", 25: "25"},
                    tooltip={"placement": "bottom", "always_visible": False},
                ),
                html.Div(style={"height": "16px"}),
                html.Label("Grid CO2 intensity scenario", style=lbl),
                dcc.Dropdown(
                    id="m4-grid-scenario",
                    options=[{"label": v["label"], "value": k}
                             for k, v in GRID_SCENARIOS.items()],
                    value="irp_2026", clearable=False,
                    style={"fontSize": "13px", "marginBottom": "12px"},
                ),
                html.P(
                    "Same grid scenarios as Module 5. Affects the CO2 avoided figures only.",
                    style={"fontSize": "11px", "color": "#888"},
                ),
            ], style={
                "flex": "1", "minWidth": "300px",
                "backgroundColor": "#fff", "border": "1px solid #e0e0e0",
                "borderRadius": "6px", "padding": "16px",
            }),
        ], style={"marginBottom": "16px"}),

        html.Div("Fleet stream parameters", style=banner),

        html.Details([
            html.Summary(
                "Private Vehicle Fleet  (2030 target: 12%)",
                style={"cursor": "pointer", "fontWeight": "600",
                       "fontSize": "14px", "padding": "8px"},
            ),
            stream_controls("private"),
        ], open=True, style={
            "backgroundColor": "#fafafa", "borderRadius": "6px",
            "padding": "8px", "marginBottom": "8px",
        }),

        html.Details([
            html.Summary(
                "Public Transport Fleet  (2030 target: 16%)",
                style={"cursor": "pointer", "fontWeight": "600",
                       "fontSize": "14px", "padding": "8px"},
            ),
            stream_controls("public"),
        ], open=False, style={
            "backgroundColor": "#fafafa", "borderRadius": "6px",
            "padding": "8px", "marginBottom": "8px",
        }),

        html.Details([
            html.Summary(
                "GOJ Fleet  (2030 target: 100%)",
                style={"cursor": "pointer", "fontWeight": "600",
                       "fontSize": "14px", "padding": "8px"},
            ),
            stream_controls("goj"),
        ], open=False, style={
            "backgroundColor": "#fafafa", "borderRadius": "6px",
            "padding": "8px", "marginBottom": "16px",
        }),

        html.Div(id="m4-summary-cards"),

        html.P([
            "Sources: 2030 targets from National EV Policy (Government of Jamaica, 2023). "
            "Private fleet 2015 anchor from CEIC/OICA. "
            "Grid CO2 intensity from METT 2022 Integrated Resource Plan. "
            "Import duty structure from Jamaica Customs Agency FAQ (jca.gov.jm). "
            "All current-fleet-size defaults are PLACEHOLDERS."
        ], style={
            "fontSize": "11px", "color": "#999", "marginTop": "16px",
            "borderTop": "1px solid #eee", "paddingTop": "12px",
        }),
    ]

    right_panel_style = {
        "flex": "1",
        "minWidth": "300px",
        "position": "sticky",
        "top": "20px",
        "alignSelf": "flex-start",
        "backgroundColor": "#ffffff",
        "border": "1px solid #e0e0e0",
        "borderRadius": "8px",
        "padding": "16px",
        "overflowY": "auto",
        "maxHeight": "90vh",
    }

    right_panel = html.Div([
        dcc.Graph(id="m4-penetration-fig", style={"height": "320px"},
                  config={"displayModeBar": False}),
        dcc.Graph(id="m4-co2-fig",         style={"height": "250px"},
                  config={"displayModeBar": False}),
        dcc.Graph(id="m4-revenue-fig",     style={"height": "250px"},
                  config={"displayModeBar": False}),
    ], style=right_panel_style)

    left_panel = html.Div(left_children,
                          style={"width": "40%", "minWidth": "300px", "flexShrink": "0"})

    return html.Div([
        html.Div([left_panel, right_panel],
                 style={"display": "flex", "gap": "20px",
                        "alignItems": "flex-start", "flexWrap": "wrap"}),
    ])


def module6_layout():
    lbl  = {"fontSize": "12px", "fontWeight": "600", "color": "#555",
            "marginBottom": "4px", "display": "block"}
    inp  = {"width": "100%", "padding": "6px 8px", "fontSize": "13px",
            "border": "1px solid #ccc", "borderRadius": "4px",
            "marginBottom": "6px", "boxSizing": "border-box"}
    hint = {"fontSize": "11px", "color": "#888", "marginBottom": "10px", "marginTop": "2px"}
    det_sum = {"cursor": "pointer", "fontWeight": "600", "fontSize": "13px",
               "padding": "6px 0", "marginBottom": "8px"}
    det_style = {"backgroundColor": "#fff", "border": "1px solid #e0e0e0",
                 "borderRadius": "6px", "padding": "14px 16px", "marginBottom": "10px"}
    veh_det = {"backgroundColor": "#fafafa", "border": "1px solid #e0e0e0",
               "borderRadius": "4px", "padding": "10px 14px", "marginBottom": "8px"}

    def loan_block(prefix, label, default_dp, default_rate, default_term):
        return html.Details([
            html.Summary(label, style={**det_sum, "fontSize": "12px"}),
            html.Label("Down payment (%)", style=lbl),
            dcc.Input(id=f"m6-{prefix}-downpayment", type="number", debounce=True,
                      value=default_dp, min=0, max=100, step=5, style=inp),
            html.Label("Loan interest rate (% APR)", style=lbl),
            dcc.Input(id=f"m6-{prefix}-loan-rate", type="number", debounce=True,
                      value=default_rate, min=1, max=30, step=0.1, style=inp),
            dcc.Slider(id=f"m6-{prefix}-loan-rate-slider", min=1, max=30, step=0.1,
                       value=default_rate,
                       marks={1: "1%", 10: "10%", 20: "20%", 30: "30%"},
                       tooltip={"placement": "bottom", "always_visible": False}),
            html.Label("Loan term (years)", style={**lbl, "marginTop": "8px"}),
            dcc.Input(id=f"m6-{prefix}-loan-term", type="number", debounce=True,
                      value=default_term, min=0.5, max=10, step=0.5, style=inp),
            dcc.Slider(id=f"m6-{prefix}-loan-term-slider", min=0.5, max=10, step=0.5,
                       value=default_term,
                       marks={0.5: "0.5", 3: "3", 6: "6", 10: "10"},
                       tooltip={"placement": "bottom", "always_visible": False}),
        ], open=True, style=veh_det)

    left_panel = html.Div([
        html.Details([
            html.Summary("Trip volume and revenue", style=det_sum),
            html.Label("Trips per day", style=lbl),
            dcc.Input(id="m6-trips-per-day", type="number", debounce=True,
                      value=40, min=5, max=150, step=1, style=inp),
            dcc.Slider(id="m6-trips-per-day-slider", min=5, max=150, step=1, value=40,
                       marks={5: "5", 40: "40", 80: "80", 150: "150"},
                       tooltip={"placement": "bottom", "always_visible": False}),
            html.P("Typical Kingston route taxi: 30–60 short trips per day.", style=hint),
            html.Label("Total fare per trip (J$)", style=lbl),
            dcc.Input(id="m6-fare", type="number", debounce=True,
                      value=DEFAULT_FARE_PER_TRIP, min=50, max=2000, step=10, style=inp),
            html.P("Full amount collected per completed trip.", style=hint),
            html.Label("Average distance per trip (km)", style=lbl),
            dcc.Input(id="m6-trip-km", type="number", debounce=True,
                      value=DEFAULT_TRIP_KM, min=1, max=30, step=0.5, style=inp),
            html.P("Kingston short routes average 3–7 km.", style=hint),
            html.Label("Working days per week", style=lbl),
            dcc.Input(id="m6-days-per-week", type="number", debounce=True,
                      value=6, min=1, max=7, step=1, style=inp),
            html.P("Most Kingston operators work 6 days.", style=hint),
            html.Label("Ownership horizon (years)", style=lbl),
            dcc.Input(id="m6-ownership-years", type="number", debounce=True,
                      value=5, min=1, max=15, step=0.5, style=inp),
            dcc.Slider(id="m6-ownership-years-slider", min=1, max=15, step=0.5, value=5,
                       marks={1: "1", 5: "5", 10: "10", 15: "15"},
                       tooltip={"placement": "bottom", "always_visible": False}),
            html.P("Longer horizons show the full benefit of EV loan payoff.", style=hint),
        ], open=True, style=det_style),

        html.Details([
            html.Summary("EV charging scenario", style=det_sum),
            dcc.RadioItems(
                id="m6-charging-scenario",
                options=[
                    {"label": " Public only — J$96/kWh (Evergo confirmed)", "value": "public"},
                    {"label": " Fleet HQ — J$60/kWh (estimated commercial rate)", "value": "fleet_hq"},
                    {"label": " Mix: 60% fleet HQ, 40% public", "value": "mix"},
                    {"label": " Custom rate", "value": "custom"},
                ],
                value="public",
                labelStyle={"display": "block", "fontSize": "12px", "marginBottom": "6px"},
            ),
            html.Div(id="m6-custom-rate-wrapper", children=[
                html.Label("Custom charging rate (J$/kWh)", style={**lbl, "marginTop": "8px"}),
                dcc.Input(id="m6-custom-rate", type="number", debounce=True,
                          value=None, min=10, max=200, step=0.5,
                          placeholder="J$/kWh",
                          style={"width": "160px", "padding": "6px 8px", "fontSize": "13px",
                                 "border": "1px solid #ccc", "borderRadius": "4px"}),
            ], style={"display": "none"}),
            html.P("Public rate is confirmed. Fleet HQ rate is a project estimate for "
                   "commercial JPS tariff pending confirmed data.",
                   style={**hint, "marginTop": "8px"}),
        ], open=True, style=det_style),

        html.Details([
            html.Summary("Loan financing — per vehicle", style=det_sum),
            loan_block("probox", "Toyota Probox",     default_dp=20, default_rate=11.0, default_term=3),
            loan_block("yuan",   "BYD Yuan Plus 2024", default_dp=10, default_rate=9.0,  default_term=5),
            loan_block("leaf",   "Nissan Leaf (used)", default_dp=20, default_rate=13.0, default_term=4),
            html.P("Rates from ScoopRate summary of Jamaica lender rates, 2026.",
                   style=hint),
        ], open=True, style=det_style),

        html.Div(id="m6-vehicle-cards"),

        html.P([
            "Sources: Probox real-world consumption from inCarDoc (1NZ-FE 1.5L, urban 10.7 L/100km). "
            "BYD Yuan Plus 16.3 kWh/100km from field data across 16 Kingston route legs. "
            "Public charging rate J$96/kWh confirmed by Evergo, June 2026. "
            "Probox price from Jacars.net asking prices (not confirmed sales). "
            "BYD Yuan Plus price is a placeholder pending confirmed dealer quote."
        ], style={"fontSize": "11px", "color": "#999", "marginTop": "8px",
                  "borderTop": "1px solid #eee", "paddingTop": "10px"}),
    ], style={"width": "40%", "minWidth": "300px", "flexShrink": "0"})

    right_panel = html.Div([
        html.P(
            "Fill in the inputs to see cumulative income chart and crossover analysis.",
            id="m6-chart-placeholder",
            style={"color": "#aaa", "fontSize": "13px", "marginTop": "40px",
                   "textAlign": "center"},
        ),
        dcc.Graph(id="m6-income-fig", style={"display": "none"},
                  config={"displayModeBar": False}),
        html.Div(id="m6-crossover-cards"),
    ], style={
        "flex": "1",
        "minWidth": "300px",
        "position": "sticky",
        "top": "20px",
        "alignSelf": "flex-start",
        "backgroundColor": "#ffffff",
        "border": "1px solid #e0e0e0",
        "borderRadius": "8px",
        "padding": "16px",
        "overflowY": "auto",
        "maxHeight": "90vh",
    })

    return html.Div([
        html.Div([left_panel, right_panel],
                 style={"display": "flex", "gap": "20px",
                        "alignItems": "flex-start", "flexWrap": "wrap"}),
    ])


NAV_ICONS = {
    "tab-1": "fa-solid fa-calculator",
    "tab-2": "fa-solid fa-route",
    "tab-3": "fa-solid fa-gas-pump",
    "tab-4": "fa-solid fa-chart-line",
    "tab-5": "fa-solid fa-leaf",
    "tab-6": "fa-solid fa-taxi",
    "tab-7": "fa-solid fa-scale-balanced",
    "tab-8": "fa-solid fa-globe",
}


def homepage_layout():
    card_style = {
        "backgroundColor": "var(--card-bg)", "border": "1px solid var(--card-border)",
        "borderRadius": "12px", "padding": "20px", "cursor": "pointer",
        "boxShadow": "var(--shadow-card)", "transition": "transform 0.1s ease",
    }
    cards = []
    for tab_id, (name, target, colour) in MODULE_INFO.items():
        cards.append(
            html.Div([
                html.I(className=NAV_ICONS.get(tab_id, "fa-solid fa-circle"),
                       style={"fontSize": "22px", "color": "var(--accent)", "marginBottom": "10px"}),
                html.H4(name, style={"margin": "0 0 6px", "fontSize": "15px", "color": "var(--text-primary)"}),
                html.P(f"Build target: {target}", style={"margin": "0", "fontSize": "12px", "color": "var(--text-muted)"}),
            ], id={"type": "home-card", "index": tab_id}, n_clicks=0, style=card_style)
        )
    return html.Div([
        html.H2("Jamaica EV Dashboard", style={"color": "var(--text-primary)", "marginBottom": "4px"}),
        html.P("Select a module below to get started.", style={"color": "var(--text-secondary)", "marginBottom": "24px", "fontSize": "13px"}),
        html.Div(cards, style={"display": "grid", "gridTemplateColumns": "repeat(auto-fill, minmax(220px, 1fr))", "gap": "16px"}),
    ])


@app.callback(
    Output("sidebar-nav-container", "children"),
    Input("active-tab-store", "data")
)
def render_sidebar_nav(active_tab):
    links = [
        html.Div([
            html.I(className="fa-solid fa-house", style={"width": "18px", "fontSize": "13px"}),
            html.Span("Home", style={"fontSize": "13px"}),
        ], id={"type": "nav-link", "index": "home"},
           className="sidebar-nav-link" + (" active" if active_tab == "home" else ""),
           n_clicks=0)
    ]
    for tab_id, (name, _, _) in MODULE_INFO.items():
        is_active = tab_id == active_tab
        links.append(
            html.Div([
                html.I(className=NAV_ICONS.get(tab_id, "fa-solid fa-circle"),
                       style={"width": "18px", "fontSize": "13px"}),
                html.Span(name, style={"fontSize": "13px"}),
            ], id={"type": "nav-link", "index": tab_id},
               className="sidebar-nav-link" + (" active" if is_active else ""),
               n_clicks=0)
        )
    return links


@app.callback(
    Output("active-tab-store", "data"),
    Input({"type": "nav-link", "index": dash.ALL}, "n_clicks"),
    Input({"type": "home-card", "index": dash.ALL}, "n_clicks"),
    prevent_initial_call=True
)
def update_active_tab(nav_clicks, card_clicks):
    import json
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update
    triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]
    tab_id = json.loads(triggered_id)["index"]
    return tab_id


@app.callback(
    Output("page-header", "children"),
    Input("active-tab-store", "data"),
)
def update_page_header(tab):
    if tab == "home":
        return None
    name, target, colour = MODULE_INFO[tab]
    return html.Div([
        html.H2(name, style={"color": "#1F3864", "marginTop": "0"}),
        html.Div([
            html.Span("Build target: ", style={"fontWeight": "600", "color": "#555"}),
            html.Span(target, style={"color": colour, "fontWeight": "600"}),
        ], style={
            "backgroundColor": "#ffffff",
            "border": f"1px solid {colour}",
            "borderLeft": f"4px solid {colour}",
            "padding": "12px 16px",
            "borderRadius": "4px",
            "marginBottom": "20px",
            "fontSize": "14px"
        }),
    ])


import math


def logistic_curve(year, current_year, midpoint_year, steepness, target_max):
    years_from_midpoint = year - midpoint_year
    exponent = -steepness * years_from_midpoint
    if exponent > 500:
        return 0.0
    return target_max / (1 + math.exp(exponent))


def hex_to_rgba(hex_color, alpha=0.5):
    """Convert a #RRGGBB hex string to rgba(r,g,b,a) for Plotly."""
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"


@app.callback(
    Output("m4-summary-cards",   "children"),
    Output("m4-penetration-fig", "figure"),
    Output("m4-co2-fig",         "figure"),
    Output("m4-revenue-fig",     "figure"),
    Input("m4-horizon", "value"),
    Input("m4-grid-scenario", "value"),
    Input("m4-private-fleet-size", "value"),
    Input("m4-private-km-per-year", "value"),
    Input("m4-private-consumption", "value"),
    Input("m4-private-steepness", "value"),
    Input("m4-private-midpoint", "value"),
    Input("m4-public-fleet-size", "value"),
    Input("m4-public-km-per-year", "value"),
    Input("m4-public-consumption", "value"),
    Input("m4-public-steepness", "value"),
    Input("m4-public-midpoint", "value"),
    Input("m4-goj-fleet-size", "value"),
    Input("m4-goj-km-per-year", "value"),
    Input("m4-goj-consumption", "value"),
    Input("m4-goj-steepness", "value"),
    Input("m4-goj-midpoint", "value"),
)
def calculate_module4(horizon, grid_scenario,
                      priv_size, priv_km, priv_cons, priv_steep, priv_mid,
                      pub_size, pub_km, pub_cons, pub_steep, pub_mid,
                      goj_size, goj_km, goj_cons, goj_steep, goj_mid):

    empty_fig = go.Figure()
    empty_fig.update_layout(
        plot_bgcolor="#ffffff", paper_bgcolor="#ffffff",
        xaxis={"visible": False}, yaxis={"visible": False},
        annotations=[{"text": "Adjust all inputs to see projections.",
                      "xref": "paper", "yref": "paper", "x": 0.5, "y": 0.5,
                      "showarrow": False, "font": {"size": 13, "color": "#aaa"}}],
    )
    required = [horizon, grid_scenario, priv_size, priv_km, priv_cons, priv_steep, priv_mid,
                pub_size, pub_km, pub_cons, pub_steep, pub_mid,
                goj_size, goj_km, goj_cons, goj_steep, goj_mid]
    if not all(x is not None for x in required):
        return None, empty_fig, empty_fig, empty_fig

    from datetime import datetime
    current_year = datetime.now().year
    years = list(range(current_year, current_year + int(horizon) + 1))

    grid_intensity = GRID_SCENARIOS[grid_scenario]["intensity_kg_per_kwh"]

    streams = {
        "private": {"size": priv_size, "km": priv_km, "cons": priv_cons,
                    "steep": priv_steep, "mid": priv_mid,
                    "target": FLEET_BASELINES["private"]["target_pct_2030"],
                    "label": "Private", "color": "#2E75B6"},
        "public":  {"size": pub_size, "km": pub_km, "cons": pub_cons,
                    "steep": pub_steep, "mid": pub_mid,
                    "target": FLEET_BASELINES["public"]["target_pct_2030"],
                    "label": "Public Transport", "color": "#C55A11"},
        "goj":     {"size": goj_size, "km": goj_km, "cons": goj_cons,
                    "steep": goj_steep, "mid": goj_mid,
                    "target": FLEET_BASELINES["goj"]["target_pct_2030"],
                    "label": "GOJ", "color": "#1A9E75"},
    }

    for key, s in streams.items():
        s["penetration"] = [logistic_curve(y, current_year, s["mid"], s["steep"], s["target"])
                            for y in years]
        s["ev_count"] = [s["size"] * (p / 100) for p in s["penetration"]]
        ice_co2_per_veh = s["km"] * (s["cons"] / 100) * CO2_PER_LITRE_PETROL
        ev_kwh_per_year = s["km"] * (16.0 / 100)
        ev_co2_per_veh = ev_kwh_per_year * grid_intensity
        co2_saved_per_veh = ice_co2_per_veh - ev_co2_per_veh
        s["annual_co2_saved_t"] = [(ev * co2_saved_per_veh) / 1000 for ev in s["ev_count"]]
        s["revenue_impact"] = [0]
        for i in range(1, len(years)):
            new_evs = s["ev_count"][i] - s["ev_count"][i - 1]
            s["revenue_impact"].append(new_evs * (ICE_IMPORT_REVENUE_PER_VEHICLE_JMD - EV_IMPORT_REVENUE_PER_VEHICLE_JMD))

    target_year = 2030
    idx_2030 = years.index(target_year) if target_year in years else None

    card = {"backgroundColor": "#ffffff", "border": "1px solid #e0e0e0",
            "borderRadius": "6px", "padding": "16px 20px",
            "flex": "1", "minWidth": "180px", "textAlign": "center"}
    big  = {"fontSize": "22px", "fontWeight": "700", "margin": "6px 0"}
    tiny = {"fontSize": "12px", "color": "#777", "margin": "0"}
    section_banner = {"backgroundColor": "#E1F5EE", "color": "#0E2A24",
                      "fontWeight": "700", "fontSize": "14px",
                      "padding": "8px 16px", "marginBottom": "12px",
                      "marginTop": "20px", "borderRadius": "6px",
                      "borderLeft": "3px solid #1A9E75"}

    target_cards = []
    for key, s in streams.items():
        if idx_2030 is not None:
            projected = s["penetration"][idx_2030]
            gap = s["target"] - projected
            gap_text = f"{gap:+.1f} pp" if gap >= 0 else f"{gap:.1f} pp"
            gap_color = "#C0392B" if gap > 0.5 else "#2d8a2d"
            proj_text = f"{projected:.1f}%"
        else:
            gap_text = "beyond horizon"
            gap_color = "#888"
            proj_text = "--"
        target_cards.append(html.Div([
            html.P(s["label"], style=tiny),
            html.P(f"Target {s['target']}% | Projected {proj_text}",
                   style={"fontSize": "13px", "margin": "6px 0", "color": "#333"}),
            html.P(gap_text, style={**big, "color": gap_color, "fontSize": "20px"}),
            html.P("gap to 2030 target", style={"fontSize": "10px", "color": "#888"}),
        ], style=card))

    fig_pen = go.Figure()
    for key, s in streams.items():
        fig_pen.add_trace(go.Scatter(
            x=years, y=s["penetration"], mode="lines+markers",
            name=f"{s['label']} projected",
            line=dict(color=s["color"], width=2), marker=dict(size=5),
        ))
        fig_pen.add_hline(y=s["target"], line_dash="dot", line_color=s["color"],
                          annotation_text=f"{s['label']} 2030 target ({s['target']}%)",
                          annotation_position="right",
                          annotation_font_size=10, annotation_font_color=s["color"])
    fig_pen.add_vline(x=2030, line_dash="dash", line_color="#888",
                      annotation_text="2030", annotation_position="top")
    fig_pen.update_layout(
        title={"text": "EV Penetration Projection by Fleet Stream", "font": {"size": 14}},
        xaxis=dict(title="Year"),
        yaxis=dict(title="EV share of fleet (%)", ticksuffix="%"),
        plot_bgcolor="#ffffff", paper_bgcolor="#ffffff",
        legend=dict(orientation="h", yanchor="top", y=-0.25, xanchor="center", x=0.5, font=dict(size=10)),
        height=380, margin=dict(l=60, r=20, t=60, b=80),
        hovermode="x unified",
    )

    fig_co2 = go.Figure()
    for key, s in streams.items():
        cum, running = [], 0
        for v in s["annual_co2_saved_t"]:
            running += v
            cum.append(running)
        fig_co2.add_trace(go.Scatter(
            x=years, y=cum, mode="lines",
            name=f"{s['label']} cumulative",
            stackgroup="one",
            line=dict(color=s["color"], width=0),
            fillcolor=hex_to_rgba(s["color"], 0.5),
        ))
    fig_co2.update_layout(
        title={"text": "Cumulative CO2 Avoided (tonnes)", "font": {"size": 14}},
        xaxis=dict(title="Year"),
        yaxis=dict(title="Cumulative CO2 avoided (t)"),
        plot_bgcolor="#ffffff", paper_bgcolor="#ffffff",
        legend=dict(orientation="h", yanchor="top", y=-0.3, xanchor="center", x=0.5, font=dict(size=10)),
        height=340, margin=dict(l=70, r=20, t=60, b=80),
        hovermode="x unified",
    )

    fig_rev = go.Figure()
    for key, s in streams.items():
        cum_rev, running = [], 0
        for v in s["revenue_impact"]:
            running += v
            cum_rev.append(running / 1_000_000_000)
        fig_rev.add_trace(go.Scatter(
            x=years, y=cum_rev, mode="lines+markers",
            name=f"{s['label']} cumulative revenue lost",
            line=dict(color=s["color"], width=2), marker=dict(size=5),
        ))
    fig_rev.update_layout(
        title={"text": "Cumulative Government Revenue Foregone (J$ billions)", "font": {"size": 14}},
        xaxis=dict(title="Year"),
        yaxis=dict(title="Cumulative revenue foregone (J$ bn)"),
        plot_bgcolor="#ffffff", paper_bgcolor="#ffffff",
        legend=dict(orientation="h", yanchor="top", y=-0.3, xanchor="center", x=0.5, font=dict(size=10)),
        height=340, margin=dict(l=70, r=20, t=60, b=80),
        hovermode="x unified",
    )

    # ── Plain-English summary ─────────────────────────────────────────────
    summary_lines = []
    all_on_track = True
    for key, s in streams.items():
        if idx_2030 is not None:
            proj = s["penetration"][idx_2030]
            gap  = s["target"] - proj
            if gap > 0.5:
                all_on_track = False
                summary_lines.append(
                    f"{s['label']}: {proj:.1f}% by 2030 "
                    f"({gap:.1f} pp short of {s['target']}% target)"
                )
            else:
                summary_lines.append(
                    f"{s['label']}: {proj:.1f}% by 2030 "
                    f"(on track for {s['target']}% target)"
                )

    if summary_lines:
        if all_on_track:
            summary_intro  = "At current settings, all streams are on track for 2030:"
            summary_bg     = "#E8F8F5"
            summary_border = "#1A9E75"
            summary_color  = "#0E2A24"
        else:
            summary_intro  = "At current settings, one or more streams fall short of 2030 targets:"
            summary_bg     = "#FEF9E7"
            summary_border = "#E0A106"
            summary_color  = "#7D6608"
        plain_english = html.Div([
            html.P(summary_intro,
                   style={"fontWeight": "600", "margin": "0 0 6px",
                          "fontSize": "13px", "color": summary_color}),
            html.Ul(
                [html.Li(line, style={"fontSize": "13px", "color": summary_color})
                 for line in summary_lines],
                style={"margin": "0", "paddingLeft": "18px"},
            ),
        ], style={
            "backgroundColor": summary_bg,
            "border": f"1px solid {summary_border}",
            "borderLeft": f"4px solid {summary_border}",
            "padding": "12px 16px", "borderRadius": "4px",
            "marginBottom": "20px",
        })
    else:
        plain_english = html.P(
            "Extend the projection horizon to include 2030 to see the target gap summary.",
            style={"fontSize": "13px", "color": "#888", "marginBottom": "16px"},
        )

    summary_cards = html.Div([
        plain_english,
        html.Div("2030 target gap", style={**section_banner, "marginTop": "4px"}),
        html.Div(target_cards, style={"display": "flex", "gap": "12px",
                                      "flexWrap": "wrap", "marginBottom": "8px"}),
    ])

    return summary_cards, fig_pen, fig_co2, fig_rev


@app.callback(
    Output("tab3-fuel-chart", "figure"),
    Input("effective-fuel-price-store", "data"),
)
def update_tab3_chart(fuel_price):
    fig = px.line(
        fuel_df,
        x="Date",
        y=["Gasolene 87", "Gasolene 90", "Auto Diesel"],
        title="Petrojam Weekly Pump Prices — Jamaica (J$/litre)",
        labels={"value": "Price (J$/litre)", "variable": "Fuel Type"},
        color_discrete_map={
            "Gasolene 87":  "#2E75B6",
            "Gasolene 90":  "#1A7A6E",
            "Auto Diesel":  "#C55A11",
        }
    )
    if fuel_price is not None:
        fig.add_hline(
            y=fuel_price,
            line_dash="dash",
            line_color="#888",
            annotation_text=f"Current input: J${fuel_price}",
            annotation_position="top left"
        )
    fig.update_layout(
        plot_bgcolor="#ffffff",
        paper_bgcolor="#ffffff",
        legend_title_text="",
        hovermode="x unified",
        margin={"t": 50, "b": 40, "l": 60, "r": 20},
    )
    return fig


@app.callback(
    Output("m6-income-fig",        "figure"),
    Output("m6-income-fig",        "style"),
    Output("m6-chart-placeholder", "style"),
    Output("m6-vehicle-cards",     "children"),
    Output("m6-crossover-cards",   "children"),
    Input("m6-trips-per-day",      "value"),
    Input("m6-trip-km",            "value"),
    Input("m6-fare",               "value"),
    Input("m6-days-per-week",      "value"),
    Input("m6-ownership-years",    "value"),
    Input("m6-charging-scenario",  "value"),
    Input("m6-custom-rate",        "value"),
    Input("m6-probox-downpayment", "value"),
    Input("m6-probox-loan-rate",   "value"),
    Input("m6-probox-loan-term",   "value"),
    Input("m6-yuan-downpayment",   "value"),
    Input("m6-yuan-loan-rate",     "value"),
    Input("m6-yuan-loan-term",     "value"),
    Input("m6-leaf-downpayment",   "value"),
    Input("m6-leaf-loan-rate",     "value"),
    Input("m6-leaf-loan-term",     "value"),
    Input("effective-fuel-price-store", "data"),
    Input("public-charging-rate",  "value"),
)
def calculate_module6(
    trips_per_day, trip_km, fare, days_per_week, ownership_years,
    charging_scenario, custom_rate,
    probox_dp, probox_rate, probox_term,
    yuan_dp, yuan_rate, yuan_term,
    leaf_dp, leaf_rate, leaf_term,
    fuel_price, public_rate,
):

    no_chart  = {"display": "none"}
    show_chart = {"display": "block"}
    show_ph   = {"color": "#aaa", "fontSize": "13px", "marginTop": "40px", "textAlign": "center"}
    hide_ph   = {"display": "none"}

    required = [trips_per_day, trip_km, fare, days_per_week, fuel_price, public_rate]
    if not all(r is not None for r in required):
        return go.Figure(), no_chart, show_ph, None, None

    # Annual volumes
    km_per_year      = trips_per_day * trip_km * days_per_week * 52
    trips_per_year   = trips_per_day * days_per_week * 52
    revenue_per_year = trips_per_year * fare

    # EV effective charging rate
    if charging_scenario == "public":
        ev_rate = public_rate
        charging_note = f"Public charging only at J${public_rate}/kWh."
    elif charging_scenario == "fleet_hq":
        ev_rate = FLEET_HQ_CHARGE_RATE_JMD_PER_KWH
        charging_note = f"Fleet HQ install at J${FLEET_HQ_CHARGE_RATE_JMD_PER_KWH}/kWh estimated."
    elif charging_scenario == "custom":
        ev_rate = custom_rate if custom_rate else public_rate
        charging_note = f"Custom rate J${ev_rate}/kWh."
    else:
        ev_rate = 0.6 * FLEET_HQ_CHARGE_RATE_JMD_PER_KWH + 0.4 * public_rate
        charging_note = f"Mix: 60% fleet HQ + 40% public = J${ev_rate:.0f}/kWh blended."

    # Per-vehicle loan params
    loan_params = {
        "probox":    (probox_dp or 20, probox_rate or 11.0, probox_term or 3),
        "yuan_plus": (yuan_dp   or 10, yuan_rate   or 9.0,  yuan_term   or 5),
        "leaf":      (leaf_dp   or 20, leaf_rate   or 13.0, leaf_term   or 4),
    }

    def pmt(principal, annual_rate_pct, term_years):
        if not term_years:
            return 0
        r = (annual_rate_pct / 100) / 12
        n = int(term_years * 12)
        if r > 0 and n > 0:
            return principal * r * (1 + r)**n / ((1 + r)**n - 1)
        return principal / max(n, 1)

    # Per-vehicle calculations
    results = {}
    for key, v in TAXI_VEHICLES.items():
        price = v.get("price_jmd") or v.get("price_estimate_jmd")
        dp_pct, lr, lt = loan_params[key]
        downpayment     = price * (dp_pct / 100)
        monthly_payment = pmt(price - downpayment, lr, lt)

        if v["type"] == "ICE":
            energy_cost_per_km = (v["consumption_urban"] / 100) * fuel_price
        else:
            energy_cost_per_km = (v["consumption_measured"] / 100) * ev_rate

        results[key] = {
            "label": v["label"],
            "price": price,
            "downpayment": downpayment,
            "monthly_payment": monthly_payment,
            "annual_loan_payment": monthly_payment * 12,
            "annual_energy_cost": energy_cost_per_km * km_per_year,
            "annual_maintenance": v["annual_maintenance_jmd"],
            "energy_cost_per_km": energy_cost_per_km,
            "type": v["type"],
            "notes": v["notes"],
            "loan_term_years": lt,
        }

    # ── Vehicle summary cards ──
    card = {"backgroundColor": "#ffffff", "border": "1px solid #e0e0e0",
            "borderRadius": "6px", "padding": "12px 14px",
            "flex": "1", "minWidth": "130px", "textAlign": "center"}
    big  = {"fontSize": "18px", "fontWeight": "700", "margin": "4px 0"}
    tiny = {"fontSize": "12px", "color": "#777", "margin": "0"}

    vehicle_rows = []
    for key in ["probox", "yuan_plus", "leaf"]:
        r = results[key]
        annual_net = revenue_per_year - (r["annual_energy_cost"] + r["annual_maintenance"] + r["annual_loan_payment"])
        net_color  = "#1A9E75" if annual_net > 0 else "#C0392B"
        type_color = "#C55A11" if r["type"] == "ICE" else "#1A9E75"
        vehicle_rows.append(html.Div([
            html.Div([
                html.Span(r["label"], style={"fontWeight": "700", "fontSize": "13px", "color": type_color}),
                html.Span(f"  {r['notes']}", style={"fontSize": "11px", "color": "#888"}),
            ], style={"marginBottom": "8px"}),
            html.Div([
                html.Div([html.P("Purchase price", style=tiny),
                          html.P(f"J${r['price']:,.0f}", style={**big, "color": "#1F3864"})], style=card),
                html.Div([html.P("Monthly loan", style=tiny),
                          html.P(f"J${r['monthly_payment']:,.0f}", style={**big, "color": "#C55A11"})], style=card),
                html.Div([html.P("Energy/km", style=tiny),
                          html.P(f"J${r['energy_cost_per_km']:.2f}", style={**big, "color": type_color})], style=card),
                html.Div([html.P("Net annual income", style=tiny),
                          html.P(f"J${annual_net:,.0f}" if annual_net >= 0 else f"-J${abs(annual_net):,.0f}",
                                 style={**big, "color": net_color})], style=card),
            ], style={"display": "flex", "gap": "8px", "flexWrap": "wrap", "marginBottom": "10px"}),
        ], style={"backgroundColor": "#fff", "border": "1px solid #e0e0e0",
                  "borderRadius": "6px", "padding": "12px 16px", "marginBottom": "8px"}))

    vehicle_cards = html.Div([
        html.P(
            f"Revenue: J${revenue_per_year:,.0f}/yr  ·  "
            f"{trips_per_day:.0f} trips/day  ·  "
            f"{km_per_year:,.0f} km/yr  ·  {charging_note}",
            style={"fontSize": "12px", "color": "#555", "marginBottom": "10px"},
        ),
        *vehicle_rows,
    ])

    # ── Multi-year cumulative income chart ──
    years     = int(ownership_years) if ownership_years else 5
    year_list = list(range(0, years + 1))
    fig       = go.Figure()
    colors    = {"probox": "#C55A11", "yuan_plus": "#1A9E75", "leaf": "#2E75B6"}
    trajectories = {}

    for key in ["probox", "yuan_plus", "leaf"]:
        r  = results[key]
        lt = r["loan_term_years"]
        cumulative_net = []
        running = -r["downpayment"]
        for y in year_list:
            if y == 0:
                cumulative_net.append(running)
                continue
            annual_cost = r["annual_energy_cost"] + r["annual_maintenance"]
            if y <= lt:
                annual_cost += r["annual_loan_payment"]
            running += revenue_per_year - annual_cost
            cumulative_net.append(running)
        trajectories[key] = cumulative_net
        fig.add_trace(go.Scatter(
            x=year_list, y=[v / 1_000_000 for v in cumulative_net],
            mode="lines+markers", name=results[key]["label"],
            line=dict(color=colors[key], width=2), marker=dict(size=6),
        ))

    def find_crossover(ev_traj, ice_traj):
        for i in range(1, len(year_list)):
            prev_diff = ev_traj[i-1] - ice_traj[i-1]
            curr_diff = ev_traj[i]   - ice_traj[i]
            if prev_diff < 0 and curr_diff >= 0:
                frac = prev_diff / (prev_diff - curr_diff)
                return (i - 1) + frac
        return None

    yuan_crossover = find_crossover(trajectories["yuan_plus"], trajectories["probox"])
    leaf_crossover = find_crossover(trajectories["leaf"],      trajectories["probox"])

    for label, cross, color in [("Yuan Plus overtakes", yuan_crossover, "#1A9E75"),
                                 ("Leaf overtakes",      leaf_crossover, "#2E75B6")]:
        if cross is not None and cross <= years:
            fig.add_vline(x=cross, line_dash="dash", line_color=color,
                          annotation_text=label, annotation_position="top",
                          annotation_font_color=color, annotation_font_size=10)

    fig.add_hline(y=0, line_dash="dot", line_color="#888",
                  annotation_text="Break-even", annotation_position="top left",
                  annotation_font_size=10)
    fig.update_layout(
        title={"text": f"Cumulative driver net income over {years} years (J$ millions)",
               "font": {"size": 14}},
        xaxis=dict(title="Year", dtick=1),
        yaxis=dict(title="Cumulative net income (J$ millions)"),
        plot_bgcolor="#ffffff", paper_bgcolor="#ffffff",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="top", y=-0.2, xanchor="center", x=0.5, font=dict(size=10)),
        height=440, margin=dict(l=60, r=20, t=60, b=100),
    )

    # ── Crossover cards ──
    def crossover_card(label, crossover_years, ev_color):
        if crossover_years is None:
            value_text = "Does not overtake"
            sub_text   = f"Within the {years}-year horizon. Extend ownership to check further."
            value_color = "#C0392B"
        else:
            yrs    = int(crossover_years)
            months = int(round((crossover_years - yrs) * 12))
            if months == 12:
                yrs += 1; months = 0
            value_text  = (f"{months} months" if yrs == 0 else
                           f"{yrs} years"     if months == 0 else
                           f"{yrs} yr, {months} mo")
            sub_text    = "EV cumulative net income first exceeds the Probox baseline."
            value_color = ev_color
        return html.Div([
            html.P(label,      style={"fontSize": "12px", "color": "#777", "margin": "0 0 4px"}),
            html.P(value_text, style={"fontSize": "20px", "fontWeight": "700",
                                      "color": value_color, "margin": "4px 0"}),
            html.P(sub_text,   style={"fontSize": "11px", "color": "#888", "margin": "4px 0 0"}),
        ], style={"backgroundColor": "#ffffff", "border": "1px solid #e0e0e0",
                  "borderRadius": "6px", "padding": "14px 18px",
                  "flex": "1", "minWidth": "200px", "textAlign": "center"})

    crossover_cards = html.Div([
        html.P("When does the EV overtake the Probox?",
               style={"fontWeight": "700", "fontSize": "14px", "marginBottom": "8px",
                      "color": "#0E2A24"}),
        html.Div([
            crossover_card("BYD Yuan Plus vs Probox", yuan_crossover, "#1A9E75"),
            crossover_card("Nissan Leaf vs Probox",   leaf_crossover, "#2E75B6"),
        ], style={"display": "flex", "gap": "10px", "flexWrap": "wrap"}),
        html.P("Crossover is when cumulative EV net income first exceeds the ICE baseline.",
               style={"fontSize": "11px", "color": "#888", "marginTop": "8px"}),
    ])

    return fig, show_chart, hide_ph, vehicle_cards, crossover_cards


@app.callback(
    Output("m6-custom-rate-wrapper", "style"),
    Input("m6-charging-scenario", "value"),
)
def toggle_m6_custom_rate(scenario):
    if scenario == "custom":
        return {"display": "block"}
    return {"display": "none"}


@app.callback(
    Output("m6-trips-per-day",        "value"),
    Output("m6-trips-per-day-slider", "value"),
    Input("m6-trips-per-day",         "value"),
    Input("m6-trips-per-day-slider",  "value"),
    prevent_initial_call=True,
)
def sync_m6_trips(inp_val, slider_val):
    ctx = dash.callback_context
    tid = ctx.triggered[0]["prop_id"].split(".")[0]
    if tid == "m6-trips-per-day":
        return dash.no_update, inp_val
    return slider_val, dash.no_update


@app.callback(
    Output("m6-ownership-years",        "value"),
    Output("m6-ownership-years-slider", "value"),
    Input("m6-ownership-years",         "value"),
    Input("m6-ownership-years-slider",  "value"),
    prevent_initial_call=True,
)
def sync_m6_ownership(inp_val, slider_val):
    ctx = dash.callback_context
    tid = ctx.triggered[0]["prop_id"].split(".")[0]
    if tid == "m6-ownership-years":
        return dash.no_update, inp_val
    return slider_val, dash.no_update


@app.callback(
    Output("m6-probox-loan-rate",        "value"),
    Output("m6-probox-loan-rate-slider", "value"),
    Input("m6-probox-loan-rate",         "value"),
    Input("m6-probox-loan-rate-slider",  "value"),
    prevent_initial_call=True,
)
def sync_m6_probox_rate(inp_val, slider_val):
    ctx = dash.callback_context
    tid = ctx.triggered[0]["prop_id"].split(".")[0]
    if tid == "m6-probox-loan-rate":
        return dash.no_update, inp_val
    return slider_val, dash.no_update


@app.callback(
    Output("m6-probox-loan-term",        "value"),
    Output("m6-probox-loan-term-slider", "value"),
    Input("m6-probox-loan-term",         "value"),
    Input("m6-probox-loan-term-slider",  "value"),
    prevent_initial_call=True,
)
def sync_m6_probox_term(inp_val, slider_val):
    ctx = dash.callback_context
    tid = ctx.triggered[0]["prop_id"].split(".")[0]
    if tid == "m6-probox-loan-term":
        return dash.no_update, inp_val
    return slider_val, dash.no_update


@app.callback(
    Output("m6-yuan-loan-rate",        "value"),
    Output("m6-yuan-loan-rate-slider", "value"),
    Input("m6-yuan-loan-rate",         "value"),
    Input("m6-yuan-loan-rate-slider",  "value"),
    prevent_initial_call=True,
)
def sync_m6_yuan_rate(inp_val, slider_val):
    ctx = dash.callback_context
    tid = ctx.triggered[0]["prop_id"].split(".")[0]
    if tid == "m6-yuan-loan-rate":
        return dash.no_update, inp_val
    return slider_val, dash.no_update


@app.callback(
    Output("m6-yuan-loan-term",        "value"),
    Output("m6-yuan-loan-term-slider", "value"),
    Input("m6-yuan-loan-term",         "value"),
    Input("m6-yuan-loan-term-slider",  "value"),
    prevent_initial_call=True,
)
def sync_m6_yuan_term(inp_val, slider_val):
    ctx = dash.callback_context
    tid = ctx.triggered[0]["prop_id"].split(".")[0]
    if tid == "m6-yuan-loan-term":
        return dash.no_update, inp_val
    return slider_val, dash.no_update


@app.callback(
    Output("m6-leaf-loan-rate",        "value"),
    Output("m6-leaf-loan-rate-slider", "value"),
    Input("m6-leaf-loan-rate",         "value"),
    Input("m6-leaf-loan-rate-slider",  "value"),
    prevent_initial_call=True,
)
def sync_m6_leaf_rate(inp_val, slider_val):
    ctx = dash.callback_context
    tid = ctx.triggered[0]["prop_id"].split(".")[0]
    if tid == "m6-leaf-loan-rate":
        return dash.no_update, inp_val
    return slider_val, dash.no_update


@app.callback(
    Output("m6-leaf-loan-term",        "value"),
    Output("m6-leaf-loan-term-slider", "value"),
    Input("m6-leaf-loan-term",         "value"),
    Input("m6-leaf-loan-term-slider",  "value"),
    prevent_initial_call=True,
)
def sync_m6_leaf_term(inp_val, slider_val):
    ctx = dash.callback_context
    tid = ctx.triggered[0]["prop_id"].split(".")[0]
    if tid == "m6-leaf-loan-term":
        return dash.no_update, inp_val
    return slider_val, dash.no_update


@app.callback(
    Output("module-instructions", "children"),
    Input("active-tab-store", "data"),
)
def update_module_instructions(active_tab):
    if not active_tab or active_tab == "home":
        return None

    instructions = {
        "tab-1": {
            "title": "EV vs. ICE Total Cost of Ownership Calculator",
            "summary": (
                "Compares the full cost of owning a petrol car versus an electric vehicle over your "
                "chosen ownership period, including purchase price, fuel or electricity, and maintenance. "
                "The crossover point is the year when cumulative EV costs drop below the ICE baseline."
            ),
            "how": (
                "Select vehicles from the dropdowns, enter a confirmed dealer price for the EV, "
                "then adjust daily driving distance and ownership years. "
                "The fuel price comes from the global settings sidebar."
            ),
        },
        "tab-2": {
            "title": "Route Cost Map",
            "summary": "Maps operating cost per kilometre across Kingston route-taxi corridors.",
            "how": "Select a route and vehicle type to see the per-km cost breakdown on the map.",
        },
        "tab-3": {
            "title": "Gas & Energy Price Tracker",
            "summary": (
                "Tracks Petrojam published pump prices and JPS electricity tariffs over time, "
                "showing how the fuel-cost gap between ICE and EV has shifted."
            ),
            "how": "Use the date range selector to zoom in on a period of interest.",
        },
        "tab-4": {
            "title": "Fleet Penetration Simulator (S-Curve)",
            "summary": (
                "Projects how quickly Jamaica's private, public, and government EV fleets could grow "
                "using a logistic S-curve model. Choose a scenario preset or fine-tune the steepness "
                "and midpoint year to build your own projection."
            ),
            "how": (
                "Click Conservative, Base, or Optimistic for each fleet stream to load a calibrated "
                "scenario, or open the Fine-tune section to set your own steepness and midpoint. "
                "The 2030 gap summary updates automatically."
            ),
        },
        "tab-5": {
            "title": "Emissions Impact Calculator",
            "summary": (
                "Calculates lifetime CO₂ savings of switching from an ICE vehicle to an EV, "
                "accounting for Jamaica's grid carbon intensity and the manufacturing emissions "
                "premium of producing a new battery pack."
            ),
            "how": (
                "Select vehicles and enter annual mileage. The carbon payback line shows when the "
                "EV's lifetime emissions fall below the ICE baseline. "
                "Adjust the grid mix slider to test cleaner or dirtier electricity scenarios."
            ),
        },
        "tab-6": {
            "title": "Taxi Feasibility Tool",
            "summary": (
                "Simulates the financial position of a Kingston route-taxi driver operating a "
                "Toyota Probox (ICE baseline), BYD Yuan Plus 2024, or used Nissan Leaf, "
                "showing net annual income and the year the EV overtakes the Probox."
            ),
            "how": (
                "Enter trips per day, fare per trip, and trip distance. "
                "Adjust the loan terms for each vehicle separately under Loan financing. "
                "The crossover cards update automatically as you change inputs."
            ),
        },
        "tab-7": {
            "title": "Fiscal Policy & Duty Tracker",
            "summary": (
                "Tracks Jamaica's import duty, GCT, and SCT concessions on EVs relative to "
                "ICE vehicles, and shows how the tax gap has changed since the Vision 2030 "
                "policy package was introduced."
            ),
            "how": "Use the toggle to switch between landed-cost view and effective-tax-rate view.",
        },
        "tab-8": {
            "title": "Caribbean Regional Comparison",
            "summary": (
                "Compares EV adoption, fuel prices, grid carbon intensity, and policy incentives "
                "across Caribbean island states, contextualising Jamaica's position in the region."
            ),
            "how": "Select countries to include in the comparison and choose a metric from the dropdown.",
        },
    }

    if active_tab not in instructions:
        return None

    info = instructions[active_tab]
    return html.Div([
        html.P(info["title"],
               style={"fontSize": "17px", "fontWeight": "700", "color": "#0E2A24",
                      "margin": "0 0 4px"}),
        html.P(info["summary"],
               style={"fontSize": "13px", "color": "#444", "margin": "0 0 4px",
                      "lineHeight": "1.5"}),
        html.P(["How to use: ", html.Em(info["how"])],
               style={"fontSize": "12px", "color": "#666", "margin": "0",
                      "fontStyle": "italic"}),
    ], style={
        "backgroundColor": "#F0F7F4",
        "border": "1px solid #BEE0D6",
        "borderRadius": "6px",
        "padding": "12px 16px",
        "marginBottom": "16px",
    })


def make_preset_callback(stream_key):
    @app.callback(
        Output(f"m4-{stream_key}-steepness", "value"),
        Output(f"m4-{stream_key}-midpoint", "value"),
        Output(f"m4-{stream_key}-preset-note", "children"),
        Input(f"m4-{stream_key}-preset-conservative", "n_clicks"),
        Input(f"m4-{stream_key}-preset-base", "n_clicks"),
        Input(f"m4-{stream_key}-preset-optimistic", "n_clicks"),
        prevent_initial_call=True,
    )
    def _set_preset(cons, base, opt, _key=stream_key):
        ctx = dash.callback_context
        if not ctx.triggered:
            return dash.no_update, dash.no_update, dash.no_update
        btn_id = ctx.triggered[0]["prop_id"].split(".")[0]
        if "conservative" in btn_id:
            level = "conservative"
        elif "optimistic" in btn_id:
            level = "optimistic"
        else:
            level = "base"
        p = SCURVE_PRESETS[_key][level]
        return p["steepness"], p["midpoint_year"], p["note"]

for _stream in ["private", "public", "goj"]:
    make_preset_callback(_stream)


# ── Run ───────────────────────────────────────────────────────────
app.layout = serve_layout

if __name__ == "__main__":
    app.run(debug=True, port=8050)
