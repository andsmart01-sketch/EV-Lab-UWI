import dash
from dash import dcc, html, Input, Output
from data_loader import load_fuel_prices, get_latest_prices
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
# ── Data ──────────────────────────────────────────────────────────
fuel_df = load_fuel_prices()
latest_prices = get_latest_prices()
server = app.server  # Expose the Flask server for deployment on UWI server

# ── Layout ────────────────────────────────────────────────────────
app.layout = html.Div([

    # Header
    html.Div([
        html.H1("Jamaica EV Vehicle Dashboard",
                style={"margin": "0", "color": "#1F3864", "fontSize": "28px"}),
        html.P("University of the West Indies, Mona Campus — EV Lab Research Project, 2026",
               style={"margin": "4px 0 0", "color": "#555", "fontSize": "13px"}),
    ], style={
        "padding": "20px 30px 16px",
        "borderBottom": "3px solid #2E75B6",
        "backgroundColor": "#ffffff"
    }),

    # Body: sidebar + main content
    html.Div([

        # Sidebar — global controls
html.Div([
    html.H3("Global Controls", style={"color": "#1F3864", "fontSize": "15px", "marginBottom": "16px"}),

    html.Label("90 Octane fuel price (J$/litre)", style={"fontSize": "13px", "fontWeight": "500"}),
    dcc.Input(
        id="fuel-price-slider",
        type="number",
        value=round(latest_prices["g90"]),
        min=50,
        max=500,
        step=0.01,
        debounce=True,
        style={"width": "100%", "padding": "6px 8px", "fontSize": "13px",
               "border": "1px solid #ccc", "borderRadius": "4px", "marginBottom": "4px"}
    ),
    html.Div(id="fuel-price-display",
             style={"fontSize": "11px", "color": "#888", "marginBottom": "20px"}),

    html.Label("JPS electricity rate (J$/kWh)", style={"fontSize": "13px", "fontWeight": "500"}),
    dcc.Input(
        id="electricity-rate-slider",
        type="number",
        value=50,
        min=1,
        max=200,
        step=0.01,
        debounce=True,
        style={"width": "100%", "padding": "6px 8px", "fontSize": "13px",
               "border": "1px solid #ccc", "borderRadius": "4px", "marginBottom": "4px"}
    ),
    html.Div(id="electricity-rate-display",
             style={"fontSize": "11px", "color": "#888", "marginBottom": "20px"}),

    html.Hr(style={"borderColor": "#ddd"}),
    html.P(f"Fuel price sourced from Petrojam ({latest_prices['date']}).",
           style={"fontSize": "11px", "color": "#888", "marginTop": "8px"}),
    html.P("These controls update all modules simultaneously.",
           style={"fontSize": "11px", "color": "#888"}),

], style={
    "width": "220px",
    "minWidth": "220px",
    "padding": "20px 16px",
    "backgroundColor": "#f7f9fc",
    "borderRight": "1px solid #e0e0e0",
    "overflowY": "auto",
}),

        # Main content — tabs
        html.Div([
            dcc.Tabs(
                id="main-tabs",
                value="tab-1",
                children=[
                    dcc.Tab(label="1 · EV vs ICE",       value="tab-1"),
                    dcc.Tab(label="2 · Route Map",        value="tab-2"),
                    dcc.Tab(label="3 · Price Tracker",    value="tab-3"),
                    dcc.Tab(label="4 · Fleet Simulator",  value="tab-4"),
                    dcc.Tab(label="5 · Emissions",        value="tab-5"),
                    dcc.Tab(label="6 · Taxi Feasibility", value="tab-6"),
                    dcc.Tab(label="7 · Policy & Duties",  value="tab-7"),
                    dcc.Tab(label="8 · Caribbean",        value="tab-8"),
                ],
                style={"fontSize": "13px"}
            ),
            html.Div(id="tab-content", style={"padding": "24px"}),
        ], style={"flex": "1", "overflow": "auto"}),

    ], style={"display": "flex", "flex": "1", "overflow": "hidden"}),

], style={
    "fontFamily": "Arial, sans-serif",
    "display": "flex",
    "flexDirection": "column",
    "height": "100vh",
    "backgroundColor": "#f0f2f5"
})

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
]


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
    scatter_colors = [
        "#2E75B6" if c == "Jamaica" else "#1A7A6E"
        for c in df_scatter["country"]
    ]
    fig_scatter = go.Figure()
    fig_scatter.add_trace(go.Scatter(
        x=df_scatter["fuel_price_usd_per_litre"],
        y=df_scatter["ev_sales_share_pct"],
        mode="markers+text",
        marker=dict(color=scatter_colors, size=12),
        text=df_scatter["country"],
        textposition="top center",
        textfont=dict(size=11),
    ))
    fig_scatter.update_layout(
        title={"text": "Retail Fuel Price vs BEV Adoption Rate",
               "font": {"size": 14}},
        xaxis=dict(title="Retail Fuel Price (USD/litre)",
                   tickprefix="$"),
        yaxis=dict(title="BEV New Car Sales Share (%)",
                   ticksuffix="%"),
        plot_bgcolor="#ffffff",
        paper_bgcolor="#ffffff",
        height=380,
        margin=dict(l=60, r=40, t=60, b=60),
        showlegend=False,
        annotations=[dict(
            text="Higher fuel prices correlate with faster BEV adoption. "
                 "Trinidad and Tobago excluded (no adoption rate data). "
                 "Sources: IEA Global EV Outlook 2026; OLADE (2024).",
            xref="paper", yref="paper",
            x=0, y=-0.18, showarrow=False,
            font=dict(size=10, color="#888888"), align="left"
        )]
    )

    # ── Summary table ─────────────────────────────────────────────────
    banner = {
        "backgroundColor": "#F5C400",
        "color": "#1a1a1a",
        "fontWeight": "700",
        "fontSize": "15px",
        "padding": "10px 18px",
        "marginBottom": "12px",
        "marginTop": "20px",
        "borderRadius": "2px",
    }
    th = {
        "backgroundColor": "#B8860B",
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
               "Import Duty on EVs", "Key Policy Note", "Data Year"]

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
            "Higher fuel prices correlate with faster BEV adoption across the region. "
            "Jamaica's relatively moderate fuel price and the absence of full import "
            "duty exemptions help explain its lower adoption rate compared to Uruguay "
            "and Costa Rica.",
            style={"fontSize": "13px", "color": "#444",
                   "marginTop": "8px", "marginBottom": "20px"}
        ),

        html.Div("Regional Comparison Summary Table", style=banner),
        table,
        html.P(
            "Sources: IEA Global EV Outlook 2026 (iea.org); OLADE EV Fleet Report 2024 "
            "(olade.org); CARILEC (2025); Jamaica Gleaner (2023); OUR Jamaica (2021). "
            "Sales share figures refer to new car sales in the most recent reported year. "
            "Jamaica 2030 targets from MSETT National Electric Vehicle Policy (2023).",
            style={"fontSize": "11px", "color": "#999",
                   "marginTop": "14px", "borderTop": "1px solid #eee",
                   "paddingTop": "10px"}
        ),
    ], style={"padding": "4px"})


def module1_layout():
    card = {
        "backgroundColor": "#ffffff", "border": "1px solid #e0e0e0",
        "borderRadius": "6px", "padding": "20px", "flex": "1", "minWidth": "260px",
    }
    lbl = {"fontSize": "12px", "fontWeight": "600", "color": "#555", "marginBottom": "4px"}
    inp = {
        "width": "100%", "padding": "6px 8px", "fontSize": "13px",
        "border": "1px solid #ccc", "borderRadius": "4px",
        "marginBottom": "14px", "boxSizing": "border-box",
    }
    note = {"fontSize": "11px", "color": "#888", "marginTop": "-10px", "marginBottom": "14px"}

    ice_opts = get_ice_dropdown_options()
    ev_opts  = get_bev_dropdown_options()
    d_ice, d_ev = "toyota-yaris-new", "byd-yuan-pro-new"

    return html.Div([
        html.Div([
            # ICE column
            html.Div([
                html.H4("ICE Vehicle", style={"color": "#C55A11", "marginTop": "0", "marginBottom": "16px"}),
                html.Label("Select model", style=lbl),
                dcc.Dropdown(id="m1-ice-dropdown", options=ice_opts, value=d_ice,
                             clearable=False, style={"fontSize": "13px", "marginBottom": "14px"}),
                html.Label("Purchase price (J$)", style=lbl),
                dcc.Input(id="m1-ice-price", type="number", debounce=True,
                          value=ICE_VEHICLES[d_ice]["price_jmd"], style=inp),
                html.Label("Fuel consumption (L/100km)", style=lbl),
                dcc.Input(id="m1-ice-consumption", type="number", debounce=True,
                          value=ICE_VEHICLES[d_ice]["consumption_per_100km"], step=0.1, style=inp),
                html.P("Real-world estimates for Jamaican driving. Adjust as needed.", style=note),
            ], style=card),

            html.Div(style={"width": "20px"}),

            # EV column
            html.Div([
                html.H4("Electric Vehicle", style={"color": "#1A7A6E", "marginTop": "0", "marginBottom": "16px"}),
                html.Label("Select model", style=lbl),
                dcc.Dropdown(id="m1-ev-dropdown", options=ev_opts, value=d_ev,
                             clearable=False, style={"fontSize": "13px", "marginBottom": "14px"}),
                html.Label("Purchase price (J$)", style=lbl),
                dcc.Input(id="m1-ev-price", type="number", debounce=True,
                          placeholder="Enter dealer quote", value=None, style=inp),
                html.Div(id="m1-ev-note",
                         children=html.P(
                             f"Range: {BEV_VEHICLES[d_ev]['range_km_nedc']} km (NEDC). "
                             "ATL Automotive does not publish BYD prices — enter dealer quote.",
                             style=note)),
                html.Label("Energy consumption (kWh/100km)", style=lbl),
                dcc.Input(id="m1-ev-consumption", type="number", debounce=True,
                          value=BEV_VEHICLES[d_ev]["consumption_per_100km"], step=0.1, style=inp),
                html.P("Estimated from battery capacity and NEDC range. Adjust as needed.", style=note),
            ], style=card),
        ], style={"display": "flex", "gap": "20px", "marginBottom": "20px", "flexWrap": "wrap"}),

        html.Div([
            html.Label("Daily driving distance",
                       style={"fontSize": "12px", "fontWeight": "600", "color": "#555", "marginRight": "12px"}),
            dcc.Input(id="m1-daily-km", type="number", debounce=True, value=50, min=1, max=500,
                      style={"width": "100px", "padding": "6px 8px", "fontSize": "13px",
                             "border": "1px solid #ccc", "borderRadius": "4px"}),
            html.Span(" km per day", style={"fontSize": "13px", "color": "#555", "marginLeft": "8px"}),
        ], style={"backgroundColor": "#fff", "border": "1px solid #e0e0e0",
                  "borderRadius": "6px", "padding": "14px 20px", "marginBottom": "20px"}),

        html.Div([
            html.Label("Ownership period (years)",
                       style={"fontSize": "12px", "fontWeight": "600", "color": "#555", "marginRight": "12px"}),
            dcc.Input(id="m1-years", type="number", debounce=True, value=5, min=1, max=20,
                      style={"width": "80px", "padding": "6px 8px", "fontSize": "13px",
                             "border": "1px solid #ccc", "borderRadius": "4px"}),
            html.Span(" years", style={"fontSize": "13px", "color": "#555", "marginLeft": "8px"}),
        ], style={"backgroundColor": "#fff", "border": "1px solid #e0e0e0",
                  "borderRadius": "6px", "padding": "14px 20px", "marginBottom": "20px"}),

        html.Div(id="m1-results"),

        html.P(
            "ICE prices: Toyota Jamaica (toyotajamaica.com, June 2026), converted at J$158.53/USD "
            "(exchange-rates.org, June 15, 2026). EV prices: not publicly listed by ATL Automotive / "
            "BYD Jamaica (byd.atlautomotive.com). Consumption figures are estimates for Jamaican "
            "driving conditions.",
            style={"fontSize": "11px", "color": "#999", "marginTop": "16px",
                   "borderTop": "1px solid #eee", "paddingTop": "12px"}),
    ])

# ── Callbacks ─────────────────────────────────────────────────────
@app.callback(
    Output("fuel-price-display", "children"),
    Input("fuel-price-slider", "value")
)
def update_fuel_display(value):
    return f"Current: J${value}/litre"


@app.callback(
    Output("electricity-rate-display", "children"),
    Input("electricity-rate-slider", "value")
)
def update_electricity_display(value):
    return f"Current: J${value}/kWh"
@app.callback(
    Output("m1-ice-price", "value"),
    Output("m1-ice-consumption", "value"),
    Input("m1-ice-dropdown", "value")
)
def update_ice_inputs(model_key):
    v = ICE_VEHICLES[model_key]
    return v["price_jmd"], v["consumption_per_100km"]


@app.callback(
    Output("m1-ev-consumption", "value"),
    Output("m1-ev-note", "children"),
    Input("m1-ev-dropdown", "value")
)
def update_ev_inputs(model_key):
    v = BEV_VEHICLES[model_key]
    note = html.P(
        f"Range: {v['range_km_nedc']} km (NEDC). ATL Automotive does not publish prices — enter dealer quote.",
        style={"fontSize": "11px", "color": "#888", "marginTop": "-10px", "marginBottom": "14px"}
    )
    return v["consumption_per_100km"], note


@app.callback(
    Output("m1-results", "children"),
    Input("m1-ice-price", "value"),
    Input("m1-ice-consumption", "value"),
    Input("m1-ev-price", "value"),
    Input("m1-ev-consumption", "value"),
    Input("m1-daily-km", "value"),
    Input("fuel-price-slider", "value"),
    Input("electricity-rate-slider", "value"),
    Input("m1-years", "value"),
)
def calculate_module1(ice_price, ice_consumption, ev_price, ev_consumption,
                      daily_km, fuel_price, electricity_rate, years):
    if not all([ice_consumption, ev_consumption, daily_km, fuel_price, electricity_rate]):
        return html.P("Enter all required values to see results.",
                      style={"color": "#888", "fontSize": "13px"})

    cost_km_ice = (ice_consumption / 100) * fuel_price
    cost_km_ev  = (ev_consumption  / 100) * electricity_rate
    monthly_km  = daily_km * 30.44
    monthly_ice = cost_km_ice * monthly_km
    monthly_ev  = cost_km_ev  * monthly_km
    savings     = monthly_ice - monthly_ev

    rc = {
        "backgroundColor": "#ffffff", "border": "1px solid #e0e0e0",
        "borderRadius": "6px", "padding": "16px 20px",
        "flex": "1", "minWidth": "160px", "textAlign": "center",
    }
    big  = {"fontSize": "22px", "fontWeight": "700", "margin": "6px 0"}
    tiny = {"fontSize": "12px", "color": "#777", "margin": "0"}

    cards = [
        html.Div([html.P("ICE cost per km",     style=tiny),
                  html.P(f"J${cost_km_ice:.2f}", style={**big, "color": "#C55A11"})], style=rc),
        html.Div([html.P("EV cost per km",      style=tiny),
                  html.P(f"J${cost_km_ev:.2f}", style={**big, "color": "#1A7A6E"})], style=rc),
        html.Div([html.P("Monthly ICE fuel cost", style=tiny),
                  html.P(f"J${monthly_ice:,.0f}", style={**big, "color": "#C55A11"})], style=rc),
        html.Div([html.P("Monthly EV energy cost", style=tiny),
                  html.P(f"J${monthly_ev:,.0f}", style={**big, "color": "#1A7A6E"})], style=rc),
        html.Div([html.P("Monthly savings", style=tiny),
                  html.P(
                      f"J${savings:,.0f}" if savings >= 0 else f"-J${abs(savings):,.0f}",
                      style={**big, "color": "#2E75B6" if savings >= 0 else "#C00000"}
                  )], style=rc),
    ]

    if ice_price and ev_price and savings > 0:
        diff = ev_price - ice_price
        if diff <= 0:
            pb_text, pb_col = "EV is cheaper upfront", "#1A7A6E"
        else:
            months = diff / savings
            pb_text = f"{months:.0f} months ({months/12:.1f} years)"
            pb_col  = "#2E75B6"
        cards.append(html.Div([
            html.P("Fuel cost payback (running costs only)", style=tiny),
            html.P(pb_text, style={**big, "color": pb_col, "fontSize": "17px"}),
            html.P("Based on fuel vs energy savings only. See TCO chart for full economic crossover "
                   "including maintenance and depreciation.",
                   style={"fontSize": "11px", "color": "#888888", "margin": "4px 0 0"}),
        ], style=rc))
    elif not ev_price:
        cards.append(html.Div([
            html.P("Fuel cost payback (running costs only)", style=tiny),
            html.P("Enter EV price to calculate",
                   style={**big, "fontSize": "13px", "color": "#aaa"}),
            html.P("Based on fuel vs energy savings only. See TCO chart for full economic crossover "
                   "including maintenance and depreciation.",
                   style={"fontSize": "11px", "color": "#888888", "margin": "4px 0 0"}),
        ], style=rc))
    else:
        cards.append(html.Div([
            html.P("Fuel cost payback (running costs only)", style=tiny),
            html.P("EV running costs exceed ICE at current rates",
                   style={**big, "fontSize": "12px", "color": "#C00000"}),
            html.P("Based on fuel vs energy savings only. See TCO chart for full economic crossover "
                   "including maintenance and depreciation.",
                   style={"fontSize": "11px", "color": "#888888", "margin": "4px 0 0"}),
        ], style=rc))

    years = int(years) if years else 5

    if ev_price:
        ice_annual_fuel  = (ice_consumption / 100) * fuel_price * daily_km * 365
        ev_annual_energy = (ev_consumption  / 100) * electricity_rate * daily_km * 365

        ice_v = next(iter(ICE_VEHICLES.values()))
        ev_v  = next(iter(BEV_VEHICLES.values()))
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
            legend={"orientation": "h", "yanchor": "bottom", "y": 1.02, "xanchor": "right", "x": 1},
            margin={"t": 60, "b": 40, "l": 60, "r": 20},
        )
        tco_section = dcc.Graph(figure=fig_tco, style={"height": "400px", "marginTop": "24px"})
    else:
        tco_section = html.P(
            "Enter EV purchase price to enable TCO chart",
            style={"color": "#aaa", "fontSize": "13px", "marginTop": "20px"},
        )

    return html.Div([
        html.H4("Results", style={"color": "#1F3864", "marginBottom": "14px"}),
        html.Div(cards, style={"display": "flex", "gap": "12px", "flexWrap": "wrap"}),
        tco_section,
    ])
    


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


@app.callback(
    Output("tab-content", "children"),
    Input("main-tabs", "value"),
    Input("fuel-price-slider", "value"),
    Input("electricity-rate-slider", "value")
)
def render_tab(tab, fuel_price, electricity_rate):
    name, target, colour = MODULE_INFO[tab]

    header = html.Div([
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
        html.Div([
            html.P([
                html.Strong("Active global settings: "),
                f"Fuel price = J${fuel_price}/litre   |   "
                f"Electricity rate = J${electricity_rate}/kWh"
            ], style={"fontSize": "13px", "color": "#444", "margin": "0"})
        ], style={
            "backgroundColor": "#EBF5FB",
            "padding": "10px 16px",
            "borderRadius": "4px",
            "fontSize": "13px",
            "marginBottom": "20px"
        }),
    ])

    placeholder = html.P(
        "Module content will be built in accordance with the project timeline. "
        "Use the sidebar inputs to verify that global state is working correctly — "
        "the active settings panel above should update across all tabs.",
        style={"color": "#777", "fontSize": "13px", "marginTop": "20px"}
    )

    if tab == "tab-3":
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
        content = dcc.Graph(figure=fig, style={"height": "480px"})
    elif tab == "tab-1":
        content = module1_layout()
    elif tab == "tab-7":
        content = build_module7_layout()
    elif tab == "tab-8":
        content = module8_layout()
    else:
        content = placeholder
    return html.Div([header, content])

# ── Run ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=True, port=8050)
