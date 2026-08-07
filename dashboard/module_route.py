"""
Route Cost Map. Layout and callbacks.

Kept out of app.py, which is already 4,800 lines, following the precedent set
by module7_policy.py.

WHAT THIS MODULE DOES NOT DO
----------------------------
It does not compute energy. That comes from EVRange, an external physics model
calibrated on the joint data collection runs. See routing_client.py for why the
call is cache first and how stub data is prevented from reaching the report.

The vehicle list here is deliberately short. EVRange's terrain correction was
calibrated on BYD Yuan Plus runs, so a Yuan Plus result is as good as the model
gets and anything else inherits a correction fitted on a different car. Rather
than offer eleven vehicles at varying and undocumented quality, this offers the
calibrated ones and says so on the page.
"""

from __future__ import annotations

from dash import dcc, html

import routes as route_data
import route_costs
from routing_client import calculate_route, cache_status

# EVRange model identifiers. Rohan supplies these from /api/ev-models once the
# host is live; until then they are placeholders and every lookup falls through
# to the stub, which is the intended behaviour rather than a failure.
EV_SPEC_IDS = {
    "byd-yuan-plus-new": None,   # calibration vehicle for the terrain correction
    "nissan-leaf-used":  None,   # present in EVRange, calibration status unconfirmed
}

CALIBRATION_NOTE = {
    "byd-yuan-plus-new": (
        "Calibration vehicle. The EVRange terrain correction was fitted on "
        "measured runs of this car on Jamaican roads, so its figures carry the "
        "least model uncertainty of anything on offer."
    ),
    "nissan-leaf-used": (
        "Present in EVRange but not the calibration vehicle. Mass and drag "
        "terms differ, while the terrain correction is inherited from the Yuan "
        "Plus. Treat as indicative."
    ),
}

DRIVING_MODES = [
    {"label": "Eco, 0.93x consumption",    "value": "eco"},
    {"label": "Normal, 1.00x",             "value": "normal"},
    {"label": "Sport, 1.10x consumption",  "value": "sport"},
]

lbl = {"fontSize": "15px", "fontWeight": "600", "color": "#555",
       "marginBottom": "4px", "display": "block"}
inp = {"width": "100%", "padding": "6px 8px", "fontSize": "16px",
       "border": "1px solid #ccc", "borderRadius": "4px",
       "marginBottom": "14px", "boxSizing": "border-box"}
det_style = {"backgroundColor": "#fff", "border": "1px solid #e0e0e0",
             "borderRadius": "6px", "padding": "14px 16px", "marginBottom": "10px"}


def source_banner(source: str, note: str):
    """
    Always visible, never dismissible. A reader must be able to tell at a
    glance whether the numbers on this page came from the model or from a
    placeholder, because everything else on the page looks identical either way.
    """
    if source in ("live", "disk", "memory"):
        text = ("Figures from EVRange." +
                (" Served from the local cache." if source != "live"
                 else " Fetched live."))
        style = {"backgroundColor": "#EAF4EF", "border": "1px solid #B9DCC9",
                 "color": "#1A5E43"}
    else:
        text = ("PLACEHOLDER DATA. The EVRange host is not reachable"
                + (f" ({note})" if note else "") +
                ", so the figures below are synthetic and must not be quoted. "
                "They exist so the page can be built and checked.")
        style = {"backgroundColor": "#FDECEA", "border": "1px solid #F5B7B1",
                 "color": "#922B21"}
    style.update({"padding": "10px 14px", "borderRadius": "6px",
                  "fontSize": "14px", "marginBottom": "14px",
                  "fontWeight": "600", "lineHeight": "1.5"})
    return html.Div(text, style=style)


def route_map_layout():
    route_opts = route_data.selectable_routes()
    default_route = route_opts[0]["value"] if route_opts else None
    veh_opts = [
        {"label": "BYD Yuan Plus 2024 (calibration vehicle)",
         "value": "byd-yuan-plus-new"},
        {"label": "Nissan Leaf, used", "value": "nissan-leaf-used"},
    ]

    left_panel = html.Div([
        html.Div([
            html.H4("Route", style={"color": "#2E75B6", "marginTop": "0",
                                    "marginBottom": "12px"}),
            html.Label("Corridor", style=lbl),
            dcc.Dropdown(id="mr-route", options=route_opts, value=default_route,
                         clearable=False,
                         style={"fontSize": "16px", "marginBottom": "8px"}),
            html.P(
                "Only corridors that were actually driven during data "
                "collection are offered, so every result on this page can be "
                "checked against a recorded run. "
                f"{len(route_data.PENDING_ROUTES)} further route-taxi corridors "
                "are named in the report but have not been surveyed.",
                style={"fontSize": "12px", "color": "#8A9E97",
                       "margin": "0 0 12px", "lineHeight": "1.45"}),
            dcc.Checklist(
                id="mr-return-trip",
                options=[{"label": " Return trip", "value": "yes"}],
                value=[], style={"fontSize": "15px"}),
        ], style=det_style),

        html.Div([
            html.H4("Vehicle", style={"color": "#1A7A6E", "marginTop": "0",
                                      "marginBottom": "12px"}),
            dcc.Dropdown(id="mr-vehicle", options=veh_opts,
                         value="byd-yuan-plus-new", clearable=False,
                         style={"fontSize": "16px", "marginBottom": "8px"}),
            html.Div(id="mr-calibration-note", style={
                "fontSize": "12px", "color": "#8A9E97", "lineHeight": "1.45",
                "marginBottom": "10px"}),
            html.Label("Battery charge at the start (%)", style=lbl),
            # Debounced per Rohan: without it a drag fires a request per tick
            # and blows through the 20 per minute limit in seconds.
            dcc.Slider(id="mr-soc", min=10, max=100, step=5, value=80,
                       marks={10: "10", 50: "50", 100: "100"},
                       tooltip={"placement": "top", "always_visible": False},
                       updatemode="mouseup"),
        ], style=det_style),

        html.Details([
            html.Summary("Conditions", style={"fontSize": "16px",
                                              "fontWeight": "600",
                                              "cursor": "pointer",
                                              "color": "#2E75B6"}),
            html.Div([
                html.Label("Passengers", style=lbl),
                dcc.Input(id="mr-passengers", type="number", debounce=True,
                          value=1, min=1, max=7, step=1, style=inp),
                html.Label("Cargo (kg)", style=lbl),
                dcc.Input(id="mr-cargo", type="number", debounce=True,
                          value=0, min=0, max=500, step=5, style=inp),
                html.Label("Ambient temperature (°C)", style=lbl),
                dcc.Input(id="mr-temp", type="number", debounce=True,
                          value=28, min=15, max=40, step=1, style=inp),
                html.P("HVAC load ramps from zero at 22°C to full cooling at "
                       "38°C in the EVRange model, so this moves consumption "
                       "more than it looks like it should.",
                       style={"fontSize": "12px", "color": "#8A9E97",
                              "margin": "-8px 0 12px", "lineHeight": "1.45"}),
                html.Label("Driving mode", style=lbl),
                dcc.Dropdown(id="mr-mode", options=DRIVING_MODES,
                             value="normal", clearable=False,
                             style={"fontSize": "16px", "marginBottom": "14px"}),
            ], style={"marginTop": "12px"}),
        ], style=det_style),

        html.Div([
            html.H4("Prices", style={"color": "#C55A11", "marginTop": "0",
                                     "marginBottom": "12px"}),
            html.P("Charging rate and pump price come from Global settings at "
                   "the top of the page, so this module agrees with the "
                   "calculator and the taxi tool.",
                   style={"fontSize": "13px", "color": "#5B7A70",
                          "margin": "0", "lineHeight": "1.5"}),
        ], style=det_style),
    ], style={"width": "38%", "minWidth": "300px", "flexShrink": "0"})

    right_panel = html.Div([
        html.Div(id="mr-banner"),
        dcc.Graph(id="mr-map", style={"height": "380px"},
                  config={"displayModeBar": False}),
        html.Div(id="mr-cards", style={"marginTop": "14px"}),
        html.Div(id="mr-basis", style={"marginTop": "12px"}),
    ], style={
        "flex": "1", "minWidth": "320px", "backgroundColor": "#ffffff",
        "border": "1px solid #e0e0e0", "borderRadius": "8px", "padding": "16px",
    })

    return html.Div([
        html.Div([left_panel, right_panel],
                 style={"display": "flex", "gap": "20px",
                        "alignItems": "flex-start", "flexWrap": "wrap"}),
    ])


def build_map_figure(geometry, label):
    """
    Draw the route. EVRange returns [lon, lat] pairs, Plotly wants separate lat
    and lon lists, so the swap happens here and nowhere else.

    Uses go.Scattermap, which renders on OpenStreetMap tiles with no Mapbox
    token and no separate JavaScript library. Rohan suggested Mapbox GL JS;
    this achieves the same thing through Plotly, which is the natural fit for
    Dash. A Mapbox token can be added later purely to change the basemap.
    """
    import plotly.graph_objects as go

    coords = (geometry or {}).get("coordinates") or []
    lons = [c[0] for c in coords]
    lats = [c[1] for c in coords]
    fig = go.Figure()
    if not coords:
        fig.update_layout(
            annotations=[{"text": "No route geometry returned",
                          "xref": "paper", "yref": "paper", "x": 0.5, "y": 0.5,
                          "showarrow": False,
                          "font": {"size": 16, "color": "#aaa"}}])
        return fig

    fig.add_trace(go.Scattermap(
        lat=lats, lon=lons, mode="lines",
        line={"width": 4, "color": "#1A7A6E"},
        name=label, hoverinfo="skip",
    ))
    fig.add_trace(go.Scattermap(
        lat=[lats[0], lats[-1]], lon=[lons[0], lons[-1]], mode="markers",
        marker={"size": 12, "color": ["#2E75B6", "#C55A11"]},
        text=["Start", "End"], hoverinfo="text", name="",
        showlegend=False,
    ))
    fig.update_layout(
        map={"style": "open-street-map",
             "center": {"lat": sum(lats) / len(lats),
                        "lon": sum(lons) / len(lons)},
             "zoom": 9.5},
        margin={"l": 0, "r": 0, "t": 0, "b": 0},
        showlegend=False,
    )
    return fig


def fetch_route(route_key, vehicle_key, *, soc, passengers, cargo, temp,
                mode, return_trip):
    """One call, with the UI's inputs mapped onto the EVRange request shape."""
    r = route_data.MEASURED_ROUTES[route_key]
    spec_id = EV_SPEC_IDS.get(vehicle_key) or f"PENDING:{vehicle_key}"
    return calculate_route(
        spec_id, r["start"], r["end"],
        currentSocPct=soc, passengerCount=passengers, cargoKg=cargo,
        ambientTempC=temp, drivingMode=mode, returnTrip=bool(return_trip),
    )


def build_costs(api_result, *, charge_rate, rate_label, pump_price,
                price_label, ice_consumption, grid_intensity, co2_per_litre,
                return_trip):
    """Join the API's energy figures to this project's prices."""
    leg = api_result["routes"][0]
    toll, toll_basis = route_data.toll_cost_jmd(
        leg.get("hasTolls", False), return_trip=bool(return_trip))
    ev = route_costs.ev_route_cost(
        leg["distanceKm"], leg["avgWhkm"], charge_rate,
        grid_intensity_kg_per_kwh=grid_intensity,
        toll_jmd=toll, toll_basis=toll_basis, rate_label=rate_label)
    ice = route_costs.ice_route_cost(
        leg["distanceKm"], ice_consumption, pump_price,
        co2_kg_per_litre=co2_per_litre,
        toll_jmd=toll, toll_basis=toll_basis, price_label=price_label)
    return ev, ice, route_costs.compare(ev, ice), leg
