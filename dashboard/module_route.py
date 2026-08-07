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


def _route_availability_note() -> str:
    """
    States plainly how much of the measured set is currently usable, rather
    than leaving a short dropdown looking like the whole dataset.
    """
    st = route_data.coordinate_status()
    base = ("Only corridors actually driven during data collection are "
            "offered, so every result here can be checked against a recorded "
            "run. ")
    if st["places_done"] < st["places_total"]:
        return base + (
            f"{st['runs_total']} measured Kingston runs exist but "
            f"{st['runs_total'] - st['runs_routable']} of them cannot be shown "
            f"yet, because {st['places_total'] - st['places_done']} of "
            f"{st['places_total']} endpoint coordinates are still missing.")
    return base + f"All {st['runs_total']} measured Kingston runs are available."


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
            html.P(_route_availability_note(),
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
            # The petrol side is a single fixed figure while the electric side
            # varies with terrain, gradient and speed through EVRange. That
            # asymmetry is route dependent and cannot be resolved from the data
            # this project holds, so the number is exposed rather than buried.
            html.Label("Petrol comparison, L/100km", style=lbl),
            dcc.Input(id="mr-ice-consumption", type="number", debounce=True,
                      value=7.6, min=3, max=25, step=0.1, style=inp),
            html.P("Toyota Probox 1.5L, the route-taxi incumbent. 7.6 combined, "
                   "10.7 urban, both from inCarDoc user data for the 1NZ-FE. "
                   "Use the urban figure for a city corridor. Unlike the "
                   "electric side, this one value applies to the whole route "
                   "whatever the terrain does.",
                   style={"fontSize": "12px", "color": "#8A9E97",
                          "margin": "-8px 0 14px", "lineHeight": "1.45"}),
            html.Label("Where you charge", style=lbl),
            dcc.RadioItems(
                id="mr-charging-location",
                options=[
                    {"label": " Home only",   "value": "home"},
                    {"label": " Public only", "value": "public"},
                ],
                value="home",
                labelStyle={"display": "block", "fontSize": "16px",
                            "marginBottom": "6px"},
            ),
            html.P("Both rates, and the pump price the petrol comparison uses, "
                   "come from Global settings at the top of the page. That is "
                   "deliberate: the same trip must not cost different amounts "
                   "in this module and in the calculator.",
                   style={"fontSize": "13px", "color": "#5B7A70",
                          "margin": "10px 0 0", "lineHeight": "1.5"}),
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


def best_geometry(route_key: str, api_result: dict):
    """
    Pick the best available line to draw, and say where it came from.

    Order: EVRange's own geometry when the result is real, then the cached
    OSRM road geometry, then the straight line the stub produces.

    The middle case matters and needs care. A real road line drawn under stub
    costs looks far more finished than it is, so the caller must keep the
    placeholder banner on the numbers regardless of what the map shows. The map
    being right says nothing about the figures beside it.
    """
    leg = (api_result.get("routes") or [{}])[0]
    geom = leg.get("geometry")
    real_result = api_result.get("source") in ("live", "disk", "memory") \
        and not api_result.get("stub")
    if real_result and geom and len(geom.get("coordinates", [])) > 2:
        return geom, False, ""
    cached = route_data.road_geometry(route_key)
    if cached and len(cached.get("coordinates", [])) > 2:
        return cached, False, (
            "Road shape from OpenStreetMap. The figures beside it are not from "
            "the same source.")
    return geom, True, ""


def build_map_figure(geometry, label, *, is_placeholder: bool = False):
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

    # A two-point geometry is a straight line between the endpoints, which is
    # what the stub produces. Drawn solid and green it looks like a routed path
    # that happens to be direct. Drawn thin, grey and captioned, it reads as
    # what it is: no route data yet.
    straight = is_placeholder or len(coords) <= 2
    fig.add_trace(go.Scattermap(
        lat=lats, lon=lons, mode="lines",
        line=({"width": 2, "color": "#B0B0B0"} if straight
              else {"width": 4, "color": "#1A7A6E"}),
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
    if straight:
        fig.add_annotation(
            text=("Straight line between the endpoints, not the road taken. "
                  "The routed path comes from EVRange."),
            xref="paper", yref="paper", x=0.5, y=0.02, showarrow=False,
            font={"size": 12, "color": "#666"},
            bgcolor="rgba(255,255,255,0.85)", borderpad=4,
        )
    return fig


def fetch_route(route_key, vehicle_key, *, soc, passengers, cargo, temp,
                mode, return_trip):
    """One call, with the UI's inputs mapped onto the EVRange request shape."""
    r = route_data.resolve_route(route_key)
    if r is None:
        raise KeyError(f"unknown route {route_key!r}")
    spec_id = EV_SPEC_IDS.get(vehicle_key) or f"PENDING:{vehicle_key}"
    return calculate_route(
        spec_id, r["start"], r["end"],
        currentSocPct=soc, passengerCount=passengers, cargoKg=cargo,
        ambientTempC=temp, drivingMode=mode, returnTrip=bool(return_trip),
    )


def _card(title, value, sub, colour):
    return html.Div([
        html.P(title, style={"margin": "0 0 4px", "fontSize": "13px",
                             "color": "#777", "fontWeight": "600",
                             "textTransform": "uppercase",
                             "letterSpacing": "0.3px"}),
        html.P(value, style={"margin": "0", "fontSize": "22px",
                             "fontWeight": "700", "color": colour}),
        html.P(sub, style={"margin": "4px 0 0", "fontSize": "12px",
                           "color": "#8A9E97", "lineHeight": "1.4"}),
    ], style={"backgroundColor": "#fff", "border": "1px solid #e0e0e0",
              "borderRadius": "6px", "padding": "12px 14px", "flex": "1",
              "minWidth": "150px"})


def build_cards(leg, ev, ice, cmp_):
    """Summary row. Energy and battery from EVRange, money and CO2 from us."""
    saving = cmp_["saving_jmd"]
    win_colour = "#1A7A6E" if saving > 0 else "#C55A11"
    pct = f"{cmp_['saving_pct']:.0f}% cheaper" if cmp_["saving_pct"] is not None else ""
    cards = [
        _card("Distance", f"{leg['distanceKm']:,.1f} km",
              f"About {leg.get('durationMin', 0):,.0f} minutes", "#2E75B6"),
        _card("Electric", f"J${ev.total_cost:,.0f}",
              f"J${ev.cost_per_km:,.2f}/km at {leg['avgWhkm']:,.0f} Wh/km",
              "#1A7A6E"),
        _card("Petrol", f"J${ice.total_cost:,.0f}",
              f"J${ice.cost_per_km:,.2f}/km, {ice.litres:,.1f} litres",
              "#C55A11"),
        _card("Saving per trip", f"J${saving:,.0f}", pct, win_colour),
        _card("Battery used", f"{leg.get('socNeededPct', 0):,.1f}%",
              f"{leg.get('socAfterTripPct', 0):,.1f}% left on arrival",
              "#2E75B6"),
        _card("CO2 avoided", f"{cmp_['co2_saving_kg']:,.1f} kg",
              (f"{cmp_['co2_saving_pct']:.0f}% less than petrol"
               if cmp_["co2_saving_pct"] is not None else ""), "#1A7A6E"),
    ]
    return html.Div(cards, style={"display": "flex", "gap": "10px",
                                  "flexWrap": "wrap"})


def build_basis(ev, ice):
    """
    Every figure above, shown as the arithmetic that produced it.

    This is not decoration. The module joins someone else's energy model to
    this project's prices, and a reader has to be able to see which half a
    number came from.
    """
    items = [html.Li(t, style={"marginBottom": "5px"})
             for t in (ev.basis + [b for b in ice.basis if b not in ev.basis])]
    return html.Details([
        html.Summary("How these figures were calculated",
                     style={"fontSize": "14px", "fontWeight": "600",
                            "cursor": "pointer", "color": "#2E75B6"}),
        html.Ul(items, style={"fontSize": "13px", "color": "#5B7A70",
                              "lineHeight": "1.55", "marginTop": "10px",
                              "paddingLeft": "20px"}),
    ], style={"borderTop": "1px solid #eee", "paddingTop": "10px"})


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
