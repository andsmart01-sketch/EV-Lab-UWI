import dash
from dash import dcc, html, Input, Output, State, ALL, MATCH
from data_loader import load_fuel_prices, get_latest_prices, get_live_exchange_rate
import plotly.express as px
import plotly.graph_objects as go
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'data'))
from vehicles import (ICE_VEHICLES, BEV_VEHICLES,
                      get_ice_dropdown_options, get_bev_dropdown_options,
                      bev_manufacturing_premium_tonnes,
                      bev_manufacturing_premium_note,
                      BATTERY_PRODUCTION_CO2_KG_PER_KWH)
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


# ── Static layout cache ───────────────────────────────────────────
#
# serve_layout() runs on EVERY page load and rebuilds all eight modules.
# Measured at 86 ms, of which the Caribbean module alone was 24 ms because it
# rebuilds two DataFrames and two figures from a dictionary that never changes.
#
# Three modules take no user input and render identically every time: the
# policy tracker, the Caribbean comparison, and the fuel price chart. Building
# them once and reusing the result removes that work from every subsequent
# request. Dash serialises the layout to JSON per request and does not mutate
# the component tree, so sharing these objects across requests is safe.
#
# If you ever make one of these depend on user state, remove it from here.
_STATIC_LAYOUT_CACHE = {}


def cached_layout(key, builder):
    """Build a user-independent layout once, then reuse it."""
    if key not in _STATIC_LAYOUT_CACHE:
        _STATIC_LAYOUT_CACHE[key] = builder()
    return _STATIC_LAYOUT_CACHE[key]


# ── Chart layout helper ───────────────────────────────────────────
#
# WHY THIS EXISTS
#
# Overlapping text in the charts had one root cause. Plotly measures legend
# position (`y`) as a fraction of the PLOT AREA height, but margins are set in
# PIXELS. Every chart had a hand-tuned fraction like y=-0.3, which meant the
# clearance in pixels changed with each chart's height and margins. On tall
# charts the legend floated too far down; on short ones it landed on top of the
# x-axis title. Legends placed above the plot at y=1.02 collided with the title
# for the same reason.
#
# This helper works the other way round. Pick the clearance in PIXELS, then
# solve for the fraction. Legends always sit below the plot, always clear of the
# axis title, at any height.

_TITLE_BAND_PX   = 76    # room above the plot for the chart title
_AXIS_TITLE_PX   = 57    # room below the plot for tick labels plus the x-axis title
_NO_AXIS_TITLE_PX = 32   # same, when there is no x-axis title
_LEGEND_ROW_PX   = 22    # height of one wrapped row of legend entries
_BOTTOM_PAD_PX   = 17


_ROTATED_TICK_PX = 42    # extra clearance when x tick labels are angled
_CHAR_PX         = 8.9   # approx px per character of a rotated axis title

# Axis furniture. Dark enough to read as a real axis, light enough not to
# compete with the data. Gridlines sit well below both.
_AXIS_LINE_COLOUR = "#5B7A70"
_AXIS_LINE_WIDTH  = 1.5
_GRID_COLOUR      = "#EDF3F1"

# ── Series colours ────────────────────────────────────────────────
#
# Dr Harris flagged that blue and green look too similar on the charts. He is
# right, and the audit shows why: the two most used series colours in the whole
# dashboard were #2E75B6 (blue, hue 209) and #1A7A6E (teal, hue 172). Teal
# reads as green, and at line width 2 on a white background the pair is genuinely
# hard to separate, more so for the roughly 8% of men with red-green colour
# vision deficiency, for whom the distinction is carried almost entirely by
# lightness.
#
# THE RULE: never put "blue" and "green"/"teal" in the same chart. Reach for
# purple, amber or red as the second series instead. Blue against orange is the
# safest pair available and is used wherever there are only two series.
#
# The two identity colours are fixed and must not be reassigned, because they
# mean the same thing on every chart in the dashboard:
#     ICE  = orange
#     EV   = green
SERIES_COLOURS = {
    "ice":    "#C55A11",   # orange, ICE everywhere
    "ev":     "#1A9E75",   # green, EV everywhere
    "blue":   "#2E75B6",
    "purple": "#7B3FA0",
    "amber":  "#E0A106",
    "red":    "#C0392B",
    "navy":   "#1F3864",
    "brown":  "#8B4513",
    "teal":   "#1A7A6E",   # safe only when no blue is present in the chart
    "grey":   "#8A9E97",
}

# Ordered fallback for charts with several series. Deliberately alternates hue
# families so that adjacent entries never sit in the blue/green trap.
SERIES_CYCLE = [
    SERIES_COLOURS["blue"], SERIES_COLOURS["orange"] if "orange" in SERIES_COLOURS
    else SERIES_COLOURS["ice"], SERIES_COLOURS["purple"], SERIES_COLOURS["ev"],
    SERIES_COLOURS["amber"], SERIES_COLOURS["red"], SERIES_COLOURS["navy"],
    SERIES_COLOURS["brown"],
]
SERIES_COLOURS["orange"] = SERIES_COLOURS["ice"]
SERIES_COLOURS["green"]  = SERIES_COLOURS["ev"]
_MIN_PLOT_PX     = 160


def chart_layout(title, height, xtitle=None, ytitle=None, y2title=None,
                 legend_rows=1, left=70, right=20, show_legend=True,
                 title_size=14, tickangle=0):
    """
    Consistent, non-overlapping Plotly layout.

    Two rules make this reliable, both learned from charts that overlapped:

    1. The figure GROWS to fit its furniture. It never squeezes the plot area.
       A rotated y-axis title is laid out along the plot height, and if the
       title is longer than the plot area Plotly lets it overflow upward into
       the chart title. Reserving legend rows out of a fixed height caused
       exactly that. So the required plot area is computed first and the height
       is raised to meet it.

    2. The chart title is anchored to the PLOT area, not the figure container.
       With xref "container" the title starts at the far left edge, on top of
       the rotated y-axis title. With xref "paper" it starts where the plot
       starts, which is always clear of it.

    legend_rows is how many rows the legend is expected to wrap onto, since the
    right-hand panel is narrow and long series names wrap.
    """
    clearance = _AXIS_TITLE_PX if xtitle else _NO_AXIS_TITLE_PX
    if tickangle:
        clearance += _ROTATED_TICK_PX

    if show_legend:
        bottom = clearance + (_LEGEND_ROW_PX * legend_rows) + _BOTTOM_PAD_PX
    else:
        bottom = clearance + _BOTTOM_PAD_PX

    # Rule 1: the plot area must be tall enough for any rotated axis title.
    needed_plot = max(
        _MIN_PLOT_PX,
        len(ytitle or "") * _CHAR_PX,
        len(y2title or "") * _CHAR_PX,
    )
    height = max(height, int(_TITLE_BAND_PX + bottom + needed_plot))
    plot_height = height - _TITLE_BAND_PX - bottom

    # Rule 3: every chart shows a visible x and y axis line.
    #
    # Plotly draws no axis line by default. On a white background with no
    # gridlines that leaves a bar chart floating with nothing to sit on, which
    # is what Dr Harris saw in the Module 2 country comparison. Setting this
    # here rather than per chart means it cannot be forgotten on the next one.
    #
    # zeroline is switched OFF deliberately. Plotly's zero line is drawn INSIDE
    # the plot at y=0, so on a chart whose axis starts at zero you get two
    # lines a pixel apart, and on a chart with negative values you get a stray
    # line through the middle that reads as an axis but is not one.
    axis_line = dict(
        showline=True,
        linecolor=_AXIS_LINE_COLOUR,
        linewidth=_AXIS_LINE_WIDTH,
        ticks="outside",
        tickcolor=_AXIS_LINE_COLOUR,
        ticklen=5,
        zeroline=False,
        showgrid=True,
        gridcolor=_GRID_COLOUR,
        gridwidth=1,
    )

    x_axis = dict(axis_line, tickangle=tickangle)
    if xtitle:
        x_axis["title"] = xtitle
    # Vertical gridlines add clutter on categorical axes and rarely help.
    x_axis["showgrid"] = False

    y_axis = dict(axis_line)
    if ytitle:
        y_axis["title"] = ytitle

    layout = dict(
        # Rule 2: anchor the title to the plot area, not the container.
        title={"text": title, "font": {"size": title_size},
               "x": 0, "xanchor": "left", "xref": "paper"},
        xaxis=x_axis,
        yaxis=y_axis,
        plot_bgcolor="#ffffff",
        paper_bgcolor="#ffffff",
        hovermode="x unified",
        height=height,
        margin=dict(l=left, r=right, t=_TITLE_BAND_PX, b=bottom),
        showlegend=show_legend,
    )
    if y2title:
        layout["yaxis2"] = dict(
            axis_line, title=y2title, overlaying="y", side="right",
            showgrid=False,
        )
    if show_legend:
        # Solve the fraction from the pixel clearance we actually want.
        layout["legend"] = dict(
            orientation="h", yanchor="top",
            y=-(clearance / plot_height),
            xanchor="center", x=0.5,
            font=dict(size=12),
        )
    return layout

# ── Layout ────────────────────────────────────────────────────────
def placeholder_layout():
    return html.P(
        "Module content will be built in accordance with the project timeline.",
        style={"color": "#777", "fontSize": "16px", "marginTop": "20px"}
    )


def serve_layout():
    return html.Div([

    dcc.Store(id="active-tab-store", data="home"),
    dcc.Store(id="effective-fuel-price-store", data=None),

    html.Div([

        # Sidebar -- navigation
        html.Div([
            html.Div([
                html.H2("Jamaica EV Dashboard", style={"color": "#fff", "fontSize": "20px", "margin": "0 0 2px"}),
                html.P("UWI Mona -- EV Lab 2026", style={"color": "var(--sidebar-text)", "fontSize": "14px", "margin": "0"}),
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
                    "fontSize": "16px", "fontWeight": "500",
                    "color": "var(--text-secondary)",
                    "cursor": "pointer", "padding": "12px 20px",
                }),
                html.Div([
                    html.Div([
                        html.Label("Fuel grade", style={
                            "fontSize": "15px", "fontWeight": "500",
                            "display": "block", "marginBottom": "4px",
                        }),
                        dcc.Dropdown(
                            id="fuel-grade-select",
                            options=[{"label": "87 octane", "value": "g87"},
                                     {"label": "90 octane", "value": "g90"}],
                            value="g90", clearable=False,
                            style={"width": "160px", "fontSize": "16px", "marginBottom": "8px"},
                        ),
                    ], style={"marginRight": "32px"}),
                    html.Div([
                        html.Label("Home charging, JPS residential (J$/kWh)", style={
                            "fontSize": "15px", "fontWeight": "500",
                            "display": "block", "marginBottom": "4px",
                        }),
                        dcc.Input(
                            id="electricity-rate-slider", type="number",
                            value=42, min=1, max=200, step=0.01, debounce=True,
                            style={"width": "160px", "padding": "6px 8px",
                                   "fontSize": "16px",
                                   "border": "1px solid var(--card-border)",
                                   "borderRadius": "6px"},
                        ),
                    ], style={"marginRight": "32px"}),
                    html.Div([
                        html.Label("Public charging network", style={
                            "fontSize": "15px", "fontWeight": "500",
                            "display": "block", "marginBottom": "4px",
                        }),
                        dcc.Dropdown(
                            id="charging-network-select",
                            options=[{"label": v["label"], "value": k}
                                     for k, v in CHARGING_NETWORKS.items()],
                            value=DEFAULT_CHARGING_NETWORK,
                            clearable=False,
                            style={"width": "260px", "fontSize": "15px"},
                        ),
                        html.Div(id="charging-network-note", style={
                            "fontSize": "12px", "marginTop": "4px",
                            "maxWidth": "260px",
                        }),
                    ], style={"marginRight": "32px"}),
                    html.Div([
                        # Label is set by the network selector callback so it always
                        # names the operator whose rate is actually in the box.
                        html.Label(id="public-charging-rate-label",
                                   children="Evergo rate (J$/kWh)", style={
                            "fontSize": "15px", "fontWeight": "500",
                            "display": "block", "marginBottom": "4px",
                        }),
                        dcc.Input(
                            id="public-charging-rate", type="number",
                            value=96, min=1, max=200, step=0.01, debounce=True,
                            style={"width": "160px", "padding": "6px 8px",
                                   "fontSize": "16px",
                                   "border": "1px solid var(--card-border)",
                                   "borderRadius": "6px"},
                        ),
                    ], style={"marginRight": "32px"}),
                    # Feedback item 6. The price you actually pay is the primary
                    # control. The survey-derived sources (Kingston average and
                    # the 11 named stations) are kept but collapsed, because a
                    # station markup measured over three dates in June-July 2026
                    # goes stale while a price you read off the pump does not.
                    # Nothing was deleted; the field survey is still selectable.
                    html.Div([
                        html.Div(id="markup-custom-input-wrapper", children=[
                            html.Label("Fuel price you pay (J$/L)", style={
                                "fontSize": "15px", "fontWeight": "500",
                                "display": "block", "marginBottom": "4px",
                            }),
                            dcc.Input(
                                id="markup-custom-input", type="number",
                                placeholder="Enter the pump price you pay at your station",
                                # Step 0.1: Jamaican pump prices are quoted to the
                                # tenth of a dollar, so 0.5 could not express them.
                                value=None, min=50, max=600, step=0.1, debounce=True,
                                style={"width": "240px", "padding": "6px 8px",
                                       "fontSize": "16px",
                                       "border": "1px solid var(--card-border)",
                                       "borderRadius": "6px"},
                            ),
                        ]),
                        html.Div(id="effective-fuel-price-display",
                                 style={"fontSize": "14px", "color": "var(--text-muted)",
                                        "marginTop": "6px", "maxWidth": "260px"}),

                        html.Details([
                            html.Summary("Other price sources (field survey)", style={
                                "fontSize": "14px", "cursor": "pointer",
                                "color": "var(--text-muted)", "marginBottom": "6px",
                            }),
                            html.Label("Retail markup source", style={
                                "fontSize": "15px", "fontWeight": "500",
                                "display": "block", "marginBottom": "4px",
                            }),
                            dcc.Dropdown(
                                id="markup-station-select",
                                options=[{"label": s["label"], "value": i}
                                         for i, s in enumerate(KINGSTON_STATION_MARKUPS)],
                                # Custom is the default: the price you actually pay
                                # beats any survey average. Falls back to the Kingston
                                # average until a price is entered.
                                value=CUSTOM_MARKUP_INDEX,
                                clearable=False,
                                style={"width": "260px", "fontSize": "15px",
                                       "marginBottom": "8px"},
                            ),
                            html.P(
                                "Retail = Petrojam reference + markup. The Petrojam price "
                                "already includes Special Consumption Tax. Markups come from a "
                                "Kingston field survey across three dates in June-July 2026 "
                                "(J$29 for 87, J$34 for 90, J$48 for diesel on average). "
                                "Station markups change over time, so your own pump price is "
                                "the more reliable input. When you fill up, check for the "
                                "orange verification sticker on the pump. It shows the "
                                "National Compliance and Regulatory Authority has inspected "
                                "the dispenser for accuracy, and gives the period the check "
                                "remains valid.",
                                style={"fontSize": "12px", "color": "var(--text-muted)",
                                       "marginTop": "0", "maxWidth": "260px"},
                            ),
                        ], open=False, style={"marginTop": "10px"}),
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
                "borderRadius": "4px", "fontSize": "16px",
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
                # These two take no user input, so they are built once and reused.
                html.Div(cached_layout("m7", build_module7_layout), id="content-tab-7"),
                html.Div(cached_layout("m8", module8_layout),       id="content-tab-8"),
            ], id="tab-content", style={"padding": "0 32px 28px"}),

        ], style={"flex": "1", "overflow": "auto", "backgroundColor": "var(--page-bg)"}),

    ], style={"display": "flex", "flex": "1", "overflow": "hidden"}),

], style={"display": "flex", "flexDirection": "column", "height": "100vh"})

USD_TO_JMD = get_live_exchange_rate(fallback=156.0)
# Printed once per import. In debug mode Dash restarts on every file save, so
# repeated lines here mean the reloader is doing its job, not that anything is
# looping. The source is included so a stale cache or a silent fallback to the
# hardcoded rate is visible rather than looking like a normal startup.
import data_loader as _dl
print(f"[startup] USD/JMD = {USD_TO_JMD:.4f}  (source: {_dl.LAST_RATE_SOURCE})")

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

# Index of the custom entry, derived rather than hardcoded so the dropdown
# default survives any reordering of the station list above.
CUSTOM_MARKUP_INDEX = next(
    i for i, s in enumerate(KINGSTON_STATION_MARKUPS) if s["markup"] == "custom"
)

# ── Public charging networks ──────────────────────────────────────
#
# Jamaica has TWO public charging networks, not one. This project previously
# modelled only Evergo, which understated the options available to a driver.
#
#   Evergo            J$96/kWh FLAT. Same price on every charger, every hour,
#                     every level. Confirmed directly by Delano Mighty, Senior
#                     Engineer, Evergo, June 2026. 71 chargers (52 L2, 19 L3+).
#
#   JPS Charge 'n Go  TIME OF USE, three price bands. Full schedule below, read
#                     from the ChargeLab app rate card, July 2026.
#
# THIS IS THE MOST IMPORTANT PRICING FINDING IN THE PROJECT.
#
# Evergo charges J$96/kWh at any hour. JPS ranges from J$50.11 to J$130.63
# depending on when you plug in. So:
#   - JPS overnight is 48% CHEAPER than Evergo.
#   - JPS daytime   is 36% cheaper than Evergo.
#   - JPS evening   is 36% MORE EXPENSIVE than Evergo.
# A driver charging at 7pm pays 2.6x what the same driver pays at 2am on the
# same network. Time of day now matters more than which network you choose,
# and no module modelled that before.
#
# It also retires a placeholder: FLEET_HQ_CHARGE_RATE_JMD_PER_KWH was a guessed
# J$60 "commercial rate". The real published off-peak public rate is J$50.11,
# cheaper than the guess, so an overnight-charging fleet no longer needs an
# invented number at all.
#
# Source: JPS Charge 'n Go rate card, ChargeLab app, read July 2026.

JPS_TOU_SCHEDULE = {
    "weekday": [
        ("00:00-06:00", 50.11),
        ("06:00-18:00", 61.33),
        ("18:00-22:00", 130.63),
        ("22:00-24:00", 50.11),
    ],
    "weekend": [
        ("00:00-18:00", 50.11),
        ("18:00-22:00", 61.33),
        ("22:00-24:00", 50.11),
    ],
}

JPS_OFFPEAK_RATE = 50.11
JPS_DAY_RATE     = 61.33
JPS_PEAK_RATE    = 130.63

CHARGING_NETWORKS = {
    "evergo": {
        "label": "Evergo - J$96/kWh flat, any hour",
        "rate": 96.0,
        "verified": True,
        "note": "Flat rate on all chargers, hours and levels. Confirmed by "
                "Evergo (D. Mighty, Senior Engineer), June 2026.",
    },
    "jps_offpeak": {
        "label": f"JPS Charge 'n Go - overnight J${JPS_OFFPEAK_RATE}/kWh",
        "rate": JPS_OFFPEAK_RATE,
        "verified": True,
        "note": "Weeknights 22:00-06:00 and most of the weekend. Cheapest public "
                "charging in Jamaica, 48% below Evergo. JPS rate card, July 2026.",
    },
    "jps_day": {
        "label": f"JPS Charge 'n Go - daytime J${JPS_DAY_RATE}/kWh",
        "rate": JPS_DAY_RATE,
        "verified": True,
        "note": "Weekdays 06:00-18:00, and weekend evenings 18:00-22:00. "
                "JPS rate card, July 2026.",
    },
    "jps_peak": {
        "label": f"JPS Charge 'n Go - evening peak J${JPS_PEAK_RATE}/kWh",
        "rate": JPS_PEAK_RATE,
        "verified": True,
        "note": "Weekday evenings 18:00-22:00. The most expensive way to charge "
                "in Jamaica, 36% above Evergo and 2.6x JPS overnight. "
                "JPS rate card, July 2026.",
    },
}

# JPS Charge 'n Go sites confirmed from the operator's own bulletin of
# 22 July 2026. This is NOT the whole network; JPS reported roughly 39 charging
# points across six parishes in December 2025, and this bulletin lists only the
# two new sites plus five it chose to highlight. Treat as a verified partial
# inventory, not a total. The same bulletin states that some plugs across the
# network are out of service, so nameplate plug counts overstate availability.
JPS_STATIONS_CONFIRMED = [
    # (site, parish, plugs, kW, commissioned)
    ("Total Energies, Salem, Runaway Bay (by KFC)", "St Ann",       4, 240, "Jul 2026"),
    ("Harbour City Mall, Montego Bay",              "St James",     4, 160, "Jul 2026"),
    ("Afresh (S-Foods) Supermarket",                "St Andrew",    4, None, "pre-Jul 2026"),
    ("Total Energies, Portmore Parkway",            "St Catherine", 4, None, "pre-Jul 2026"),
    ("Total Energies, Old Harbour (Toll Road)",     "St Catherine", 2, None, "pre-Jul 2026"),
    ("Total Energies, Discovery Bay",               "St Ann",       4, None, "pre-Jul 2026"),
    ("Total Energies, Yallahs",                     "St Thomas",    2, None, "pre-Jul 2026"),
]

DEFAULT_CHARGING_NETWORK = "evergo"


def charging_network_rate(key, fallback):
    """Rate for a named network, or the fallback if that rate is not yet known."""
    net = CHARGING_NETWORKS.get(key)
    if net is None or net["rate"] is None:
        return fallback
    return net["rate"]


# ── Module 6: Taxi Feasibility constants ──────────────────────────
#
# Module 6 previously carried its own hardcoded three-vehicle dict that
# duplicated data/vehicles.py at DIFFERENT values (Yuan Plus 16.3 here versus
# 14.0 there). The vehicle set is now built FROM vehicles.py so there is one
# price, one battery capacity and one maintenance figure per vehicle, with
# consumption deliberately overridden because taxi duty is not private duty.
#
# CONSUMPTION BASIS
#
# Every figure in Module 6 is URBAN-basis, because Kingston route taxi work is
# stop-and-go by definition. data/vehicles.py is combined-basis, because that is
# what the private-buyer modules compare on. The two must not be mixed.
#
# Where a real urban measurement exists it is used directly. Where none exists,
# the combined figure is scaled by an uplift factor derived from the vehicles
# that DO have both numbers:
#
#   ICE uplift 10.7 / 7.6 = 1.41, from inCarDoc Probox 1NZ-FE data.
#   EV uplift, mean of two observations:
#       BYD Yuan Plus 16.3 / 14.0 = 1.16  (own field data, 16 Kingston legs)
#       Nissan Leaf     18.0 / 16.0 = 1.13  (project estimate)
#     giving 1.15.
#
# THESE UPLIFTS ARE ASSUMPTIONS, not measurements. The ICE factor rests on a
# single vehicle. Any vehicle whose consumption is derived rather than measured
# is flagged as such in the interface and should be treated as indicative until
# field data replaces it. Priority for the next field trip: an urban figure for
# the Nissan Tiida, which is the second most common route taxi after the Probox.

TAXI_ICE_URBAN_UPLIFT = 10.7 / 7.6    # 1.408
TAXI_EV_URBAN_UPLIFT  = ((16.3 / 14.0) + (18.0 / 16.0)) / 2    # 1.145

# Measured or directly-estimated urban figures. These override the uplift.
TAXI_FIELD_CONSUMPTION = {
    "toyota-probox-used": (10.7, "inCarDoc user data, 1NZ-FE 1.5L, urban cycle"),
    "byd-yuan-plus-new":  (16.3, "own field measurement, 16 Kingston route legs, July 2026"),
    "nissan-leaf-used":   (18.0, "project estimate for Jamaican urban conditions with AC"),
}

# Realistic urban range for EVs, where it differs from the vehicles.py
# real-world figure because taxi duty runs the AC continuously.
TAXI_RANGE_OVERRIDE = {
    "byd-yuan-plus-new": 340,
    "nissan-leaf-used":  180,
}

# Vehicles offered in Module 6, in display order.
TAXI_CANDIDATE_KEYS = [
    "toyota-probox-used",     # ICE baseline
    "toyota-probox-late",     # same vehicle, fresh import, for old vs new ICE
    "nissan-tiida-used",      # second ICE baseline
    "byd-yuan-plus-new",
    "nissan-leaf-used",
    "byd-yuan-pro-new",
    "byd-seal-new",
    "byd-sealion7-new",
    "byd-atto8-new",
    "hyundai-kona-ev-used",
    "kia-soul-ev-used",
    "tesla-model3-used",
]

# Default comparison set when the module first loads.
TAXI_DEFAULT_SELECTION = [
    "toyota-probox-used", "nissan-tiida-used",
    "byd-yuan-plus-new", "nissan-leaf-used",
]

# Loan terms differ by vehicle class. Jamaican lenders price used-vehicle and
# EV paper differently. Source: ScoopRate summary of Jamaica lender rates, 2026.
TAXI_LOAN_DEFAULTS = {
    ("ICE", "used"): (20, 11.0, 3),
    ("ICE", "new"):  (20, 10.0, 5),
    ("EV",  "new"):  (10,  9.0, 5),
    ("EV",  "used"): (20, 13.0, 4),
}

TAXI_PALETTE = ["#C55A11", "#8B4513", "#A0522D", "#1A9E75", "#2E75B6", "#7B3FA0",
                "#0F6B5C", "#B8860B", "#4A6FA5", "#9E4A3F", "#3C8D8D", "#6A5ACD"]

# Distinct marker shape per vehicle, so the chart stays readable in greyscale,
# when printed for a poster, and for anyone who cannot separate the colours.
# Colour alone is not enough once more than about four vehicles are selected.
TAXI_SYMBOLS = ["circle", "square", "diamond", "triangle-up", "cross",
                "x", "star", "triangle-down", "pentagon", "hexagon",
                "star-diamond", "triangle-left"]


def _build_taxi_vehicles():
    """Assemble the Module 6 vehicle set from data/vehicles.py."""
    out = {}
    for i, key in enumerate(TAXI_CANDIDATE_KEYS):
        src = ICE_VEHICLES.get(key) or BEV_VEHICLES.get(key)
        if src is None:
            continue
        is_ev = key in BEV_VEHICLES
        vtype = "EV" if is_ev else "ICE"
        condition = src.get("condition", "used")

        if key in TAXI_FIELD_CONSUMPTION:
            consumption, csource = TAXI_FIELD_CONSUMPTION[key]
            measured = True
        else:
            uplift = TAXI_EV_URBAN_UPLIFT if is_ev else TAXI_ICE_URBAN_UPLIFT
            consumption = round(src["consumption_per_100km"] * uplift, 1)
            csource = (f"derived: {src['consumption_per_100km']} combined "
                       f"x {uplift:.2f} urban uplift. NOT measured.")
            measured = False

        out[key] = {
            "label": src["label"],
            "type": vtype,
            "condition": condition,
            "price_jmd": src.get("price_jmd"),
            "price_verified": src.get("price_verified", False),
            "price_source": src.get("price_source", ""),
            "consumption_urban": consumption,
            "consumption_source": csource,
            "consumption_measured": measured,
            "battery_kwh": src.get("battery_kwh"),
            "range_km_realistic": TAXI_RANGE_OVERRIDE.get(key,
                                                          src.get("range_km_realworld")),
            "annual_maintenance_jmd": src["annual_maintenance_jmd"],
            "loan_defaults": TAXI_LOAN_DEFAULTS[(vtype, condition)],
            "colour": TAXI_PALETTE[i % len(TAXI_PALETTE)],
            "symbol": TAXI_SYMBOLS[i % len(TAXI_SYMBOLS)],
            "notes": src.get("notes", ""),
        }
    return out


TAXI_VEHICLES = _build_taxi_vehicles()

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
# FLEET_HQ_CHARGE_RATE_JMD_PER_KWH removed July 2026. It was a guessed J$60/kWh
# "commercial rate" never confirmed with JPS, and the depot-charging scenario it
# supported is now covered by the real JPS overnight rate of J$50.11/kWh.

# ── Module 4: Fleet Penetration Simulator ────────────────────────
FLEET_BASELINES = {
    "private": {
        "label": "Private Vehicle Fleet",
        "size_2015": 190_000,   # CEIC / OICA, Dec 2015 (published anchor, oldest solid data point)
        # 540,113 = 575,041 fit-certified vehicles MINUS 34,928 licensed public
        # passenger vehicles. Both figures are from the Economic and Social Survey
        # Jamaica 2022 (Planning Institute of Jamaica), reported by the Gleaner on
        # 13 August 2023. This replaces a 240,000 placeholder extrapolated from a
        # 2015 anchor, and is more than double it.
        #
        # UPPER BOUND, not a private-car count. The remainder still contains
        # commercial goods vehicles and the government fleet, neither of which
        # Jamaica publishes separately. The true private figure is lower.
        "current_estimate": 540_113,
        "current_source": "Economic and Social Survey Jamaica 2022 (PIOJ): 575,041 "
                          "vehicles certified fit by the Island Traffic Authority, "
                          "less 34,928 licensed public passenger vehicles. Upper "
                          "bound: still includes commercial and government vehicles.",
        "target_pct_2030": 12,
        "km_per_year_avg": 12_000,
        "km_source": "PLACEHOLDER: international average for private vehicles, no Jamaica-specific figure",
        "avg_consumption_l_per_100km": 8.0,
        "avg_ev_consumption_kwh_per_100km": 16.0,
        "ev_consumption_source": "Mid-range of the BEV models in data/vehicles.py "
                                 "(14.0 to 20.0 kWh/100km), consistent with the "
                                 "16.3 kWh/100km measured on the BYD Yuan Plus.",
        "avg_purchase_price_jmd": 4_500_000,
        "annual_ev_imports_2023": 280,   # MSTT via Jamaica Observer
    },
    "public": {
        "label": "Public Transport Fleet",
        "size_2015": None,
        # JUTC operable fleet after the June 2025 delivery of 63 CNG and 30 diesel
        # coaches. Daily roll-out is lower still, around 250, against a stated
        # KMTR requirement of 450-500 buses to deliver 31,000 seats a day.
        # For scale, the ESSJ 2022 recorded an average of just 179 buses operating
        # monthly in the KMTR, the fifth consecutive year of decline.
        #
        # SCOPE: this stream models JUTC buses only, because the energy and
        # emissions parameters below are bus parameters. The policy's 16% public
        # transport target plausibly covers the whole licensed public passenger
        # fleet, which the ESSJ 2022 puts at 34,928 vehicles and which is
        # dominated by route taxis and minibuses, not buses. Route taxis are
        # modelled separately in the taxi module.
        "current_estimate": 350,
        "current_source": "JUTC operable fleet approximately 350 buses after the "
                          "June 2025 CNG and diesel delivery. Daily roll-out around "
                          "250. JUTC buses only; the wider licensed public passenger "
                          "fleet is 34,928 vehicles (ESSJ 2022, PIOJ).",
        "target_pct_2030": 16,
        "km_per_year_avg": 40_000,
        "km_source": "PLACEHOLDER: taxi/bus estimate based on Kingston route data",
        # BOTH figures below were passenger-car values and are now bus values.
        #
        # Diesel: 10 L/100km is what a car uses. A 12-metre city transit bus uses
        # roughly five times that. 55.5 L/100km is derived from Gao et al. (2017),
        # who report diesel FUEL energy of 5.52 kWh/km at 32.5% engine efficiency
        # on real Knoxville Area Transit routes; at a diesel LHV of 9.94 kWh/L
        # that is 0.555 L/km.
        #
        # Electric: 135 kWh/100km is the same study's real-world average of
        # 1.35 kWh/km. Standardized drive cycles span 1.24 to 2.48 kWh/km, so
        # 124 to 248 kWh/100km is the defensible range. JUTC's pilot unit is a
        # Golden Dragon NAV12, 35 seated plus 20 standing, which is the same
        # 12-metre transit class the study models.
        #
        # Source: Gao, Z., Lin, Z., LaClair, T. J., Liu, C., Li, J.-M., Birky,
        # A. K., & Ward, J. (2017). Battery capacity and recharging needs for
        # electric buses in city transit service. Energy, 122, 588-600.
        # https://doi.org/10.1016/j.energy.2017.01.101
        "avg_consumption_l_per_100km": 55.5,
        "avg_ev_consumption_kwh_per_100km": 135.0,
        "ev_consumption_source": "Gao et al. (2017), Oak Ridge National Laboratory, "
                                 "real-world city transit average. Range across "
                                 "standardized drive cycles is 124 to 248 kWh/100km. "
                                 "JUTC has not published figures for its own buses.",
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
        "avg_ev_consumption_kwh_per_100km": 17.0,
        "ev_consumption_source": "Mid-range passenger car and light SUV figure from "
                                 "data/vehicles.py, slightly above the private fleet to "
                                 "reflect a heavier average government vehicle.",
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

# ── Caribbean Regional Comparison Data ─────────────────────────────
# (displayed as module 2; the tab-8 id is historical, see MODULE_INFO)
#
# Sources:
#   IEA Global EV Outlook 2026 (iea.org, May 2026)
#   OLADE EV Fleet Report 2024 (olade.org)
#   Jamaica Gleaner (2023) for Jamaica fleet figures
#   CARICOM EV Month webinar series (November 2025)
#   UNEP (2025). Caribbean leading the charge to electric mobility.
#     https://www.unep.org/technical-highlight/caribbean-leading-charge-electric-mobility
#   Per-country policy sources are on each record in source_url.
#
# FUEL PRICES
#
# All Caribbean fuel prices are US$/litre for May 2026 from a single consistent
# source: the Energy Chamber of Trinidad and Tobago's compilation of
# GlobalPetrolPrices.com data across eleven CARICOM markets.
#   https://energynow.tt/blog/gasoline-prices-rise-across-most-of-caricom
# Using one compilation for all of them matters more than using each country's
# own national statistics, because pump prices are only comparable if they were
# collected on the same date on the same basis.
#
# CORRECTED July 2026: Trinidad & Tobago was on record here at US$0.40/litre.
# The verified May 2026 figure is US$1.14. The old value was stale by years and
# supported a false conclusion, that T&T has near-free fuel that cancels out its
# zero EV duty. It does not. Guyana at US$1.00 is the cheapest CARICOM market;
# T&T sits below the regional average of US$1.41 but not dramatically so.
# Jamaica was also stale at US$1.27 and is US$1.46.
#
# Grenada, Belize and Suriname are in that compilation but only as percentage
# changes, with no absolute stated, so their prices remain None rather than
# being back-derived.
#
# CARIBBEAN GRID EMISSION FACTORS (2015)
#
# Source: Perez Martin, D., Desgain, D., Relova Delgado, I., Hinostroza, M. L.,
# & Carrera Doral, W. (2015). Analysis of grid emission factors for the
# electricity sector in Caribbean countries. UNEP DTU Partnership, with OLADE
# and the UNFCCC Regional Collaboration Centre for the Caribbean.
# https://backend.orbit.dtu.dk/ws/files/128107251/2015_10_Caribbean_Grid_Emission_04.pdf
#
# ***DO NOT PLUG THESE INTO THE EMISSIONS MODULE ALONGSIDE JAMAICA'S 0.474.***
#
# They are NOT the same quantity. Jamaica's 0.474 kg CO2/kWh is an AVERAGE grid
# intensity: total system emissions divided by total generation, from the 2022
# IRP. The figures below are CDM combined margin (CM) factors, and the study
# states plainly that with no build margin data available it set CM equal to the
# operating margin, so "the CM emission factors calculated in this study are
# probably overestimated". Operating margin weights dispatchable thermal plant
# and does not credit renewables the way an average intensity does.
#
# Mixing the two would manufacture a fake decline. Use these for RANKING which
# grids are dirtier, not for arithmetic against Jamaica's 0.474.

CARIBBEAN_GRID_EF_2015_TCO2_PER_MWH = {
    "Guyana":             0.9483,
    "Grenada":            0.8027,   # highest CM, wholly fossil-fuelled
    "Barbados":           0.7906,   # wholly fossil-fuelled in 2015
    "Jamaica":            0.7324,
    "Bahamas":            0.7230,
    "Trinidad & Tobago":  0.6660,
    "Dominica":           0.4711,   # lowest, low fossil dependence
    # Reported only as a group range, not individually, so not assigned:
    #   Antigua & Barbuda, St Kitts & Nevis, Saint Lucia: 0.6526 to 0.6943
    #   St Vincent & the Grenadines, Haiti:               0.5493 to 0.5537
}

# WHY THIS MATTERS TO THE RETROSPECTIVE IN THE FLEET EMISSIONS SECTION
#
# That section holds Jamaica's grid flat at the 2022 value of 0.474 back to
# 2015, and the code already warns this makes CO2 avoided an optimistic bound.
# This study puts Jamaica at 0.7324 in 2015 on an OM basis. Even allowing that
# OM overstates an average, the gap is large and is consistent with a real
# decline driven by the Old Harbour LNG conversion rather than by renewables.
# So the flat-line assumption is not mildly optimistic, it is substantially so.
#
# ACTION: source Jamaica's actual historical average grid intensity year by year
# from the IRP annexes, PCJ or the OUR, and replace the flat line. Until then,
# the retrospective CO2 figures should be presented as an upper bound and said
# to be so out loud.

# ON MISSING VALUES
#
# Fields are None where this project has NOT found a figure it can attribute to
# a source. They are not zeros and they are not estimates. Six of the Caribbean
# entries have policy detail but no fleet count, because small-island vehicle
# registries do not publish EV counts separately. Filling those with plausible
# numbers would make the charts look complete and the analysis worthless.
#
# Known gaps worth chasing, in order of usefulness to this project:
#   1. Trinidad & Tobago fleet count. Figures near 3,000 are quoted in secondary
#      reporting but were not traceable to a registry source. T&T matters most
#      because it isolates the fuel-price variable: identical 0% duty to Guyana
#      and Grenada, but the cheapest pump fuel in the region.
#   2. Cayman Islands fleet count. The 75 on record is from 2021 and is stale.
#   3. Barbados EV sales share. Fleet and bus data are good, sales share is not.
#   4. Aruba, Curacao and Bonaire. Only general vehicle import duty rates were
#      found (27%, 22%, 25%) from a commercial source, with no EV-specific
#      policy, so they are excluded rather than entered on weak sourcing.

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
        "country": "Chile",
        "region": "Latin America",
        "ev_sales_share_pct": None,
        "ev_fleet_total": None,
        "charging_stations": None,
        "key_policy": "THE ELECTRIC TAXI BENCHMARK. Two state programmes, Mi Taxi "
                      "Electrico and Mas Transporte Electrico, run by the Agencia de "
                      "Sostenibilidad Energetica with the Ministry of Energy and GEF "
                      "funding, have put 405 electric vehicles into small-scale public "
                      "transport across 10 regions. Reported outcomes: average saving "
                      "of over 3 million Chilean pesos a year per driver from lower "
                      "running costs, and more than 3,900 tonnes of CO2 avoided a year "
                      "across the replaced fleet, about 9.6 t per vehicle. The study "
                      "also names four barriers, all of which apply to Jamaica: slow "
                      "utility response times connecting residential chargers, driver "
                      "distrust of the technology, digital exclusion in the application "
                      "process given driver age, and no local training for charging "
                      "installers.",
        "import_duty_ev_pct": None,
        "fuel_price_usd_per_litre": None,
        "source_year": 2026,
        "source_url": "https://cmsostenible.org/wp-content/uploads/2026/03/vf2_Electromovilidad_en_el_transporte_publico_menor.pdf",
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
        # DEALER-REPORTED, NOT REGISTRY DATA. Two Barbadian dealer groups gave
        # figures to Barbados Today (16 July 2026):
        #   Christopher Yearwood, GM, Caribbean Automotive Retailers (CAR)
        #     Barbados: EV uptake "from ten per cent in 2025 to 20 per cent in
        #     2026 year to date, with HEV remaining more or less consistent".
        #   Justin Inniss, Inchcape Barbados: in H1 2026 "72 per cent of the new
        #     vehicles sold were hybrid and electric, and of that 21 per cent
        #     were actually full EV".
        # The Inniss phrasing is ambiguous: "of that 21 per cent" could mean 21%
        # of the 72% (about 15% of all sales) or 21% of all sales. Yearwood's
        # independent 20% figure supports the second reading, so 20.0 is used as
        # the conservative point estimate of the two.
        # CAVEAT for the report: this is new-vehicle sales through two dealer
        # networks, not national registrations, and Barbados has a substantial
        # used-import channel. It is not strictly the same measure as the IEA
        # sales-share figures used for Uruguay, Costa Rica, Colombia and Brazil.
        "ev_sales_share_pct": 20.0,
        "ev_fleet_total": 600,
        "charging_stations": 100,
        "key_policy": "10% import duty on new AND used battery-electric cars, a four-year "
                      "excise tax and VAT holiday extended to 31 March 2029 (2026 Budget), "
                      "accelerated tax write-offs for company EV purchases, interest-free "
                      "loans for eligible public officers, and a low-interest revolving fund "
                      "for public service vehicle operators. NOTE FOR MODULE 6: Barbados "
                      "already levies an 'alternate fuel levy' of BBD$25 a month on "
                      "low-emission vehicles, introduced 2023, explicitly to recover fuel tax "
                      "revenue lost as drivers switch. That is a working implementation of the "
                      "revenue-foregone problem this dashboard models. Dealers report EV share "
                      "of new sales rising 10% (2025) to about 20% (2026 YTD), with hybrids "
                      "and EVs together at 72% of new sales in H1 2026, up from 26% in 2023. "
                      "Public transit is 89% electric: 59 electric buses, 61 more planned, "
                      "cutting about US$4M a year in diesel. Carbon neutral target 2030.",
        "import_duty_ev_pct": 10.0,
        "fuel_price_usd_per_litre": 1.85,
        "source_year": 2026,
        "source_url": "https://barbadostoday.bb/2026/07/16/evs-hybrids-gain-traction-with-consumers-dealers/",
    },
    {
        "country": "Jamaica",
        "region": "Caribbean",
        "ev_sales_share_pct": 3.0,
        # CORRECTED July 2026. This was recorded as 6,606 "EV fleet total". That
        # number is neither a fleet total nor purely electric. It is the count of
        # vehicles IMPORTED in the twelve months July 2022 to June 2023, and the
        # STATIN dataset the Jamaica Observer obtained is explicitly "electric
        # vehicles INCLUDING HYBRIDS". Hybrids are out of scope for this project.
        # Using it as a BEV stock figure overstated Jamaica's fleet by an unknown
        # but large factor and made the Module 2 comparison unreliable.
        # No confirmed BEV stock figure for Jamaica has been obtained.
        "ev_fleet_total": None,
        "ev_imports_incl_hybrids_2022_23": 6606,
        "charging_stations": 100,
        "key_policy": "National EV Policy 2023: 12% private, 16% public transport, 100% govt fleet by 2030; duty cut from 30% to 10%",
        "import_duty_ev_pct": 10.0,
        "fuel_price_usd_per_litre": 1.46,
        "source_year": 2024,
        "source_url": "https://www.iea.org/reports/global-ev-outlook-2026",
    },
    {
        "country": "Trinidad & Tobago",
        "region": "Caribbean",
        "ev_sales_share_pct": None,
        # Reports of roughly 3,000 registered EVs circulate but this project has
        # not traced them to a primary source. Left blank rather than guessed.
        "ev_fleet_total": None,
        "charging_stations": None,
        "key_policy": "CORRECTION: previously recorded here as having minimal EV policy. It "
                      "does not. All customs duty, motor vehicle tax and VAT were removed on "
                      "battery electric vehicle imports from 1 January 2022, with an age limit "
                      "on used imports, and duty, VAT and Online Purchase Tax on EV chargers "
                      "and parts were exempted from 1 January 2025. Pump price is fixed by the "
                      "state and a subsidy absorbs the gap to wholesale, so the price barely "
                      "moved through the 2025-26 global spike while Jamaica's rose 16.8%. The "
                      "2025-26 Budget cut Super gasoline a further TT$1/litre. So T&T combines "
                      "zero duty with an insulated, below-regional-average pump price.",
        "import_duty_ev_pct": 0.0,
        "fuel_price_usd_per_litre": 1.14,
        "source_year": 2025,
        "source_url": "https://caricom.org/tt-removes-taxes-and-import-duties-on-electric-vehicles-caricom-business/",
    },
    {
        "country": "Cayman Islands",
        "region": "Caribbean",
        "ev_sales_share_pct": None,
        # STALE: 75 units is a 2021 count and no newer figure was found. Treat as
        # a floor, not a current value.
        "ev_fleet_total": 75,
        "charging_stations": None,
        "key_policy": "Zero import duty on EVs valued up to CI$29,999 for personal use, in "
                      "place since 2019, with a National Energy Policy proposal to extend 0% "
                      "to all EVs for five years. Policy target is for all drivers to be "
                      "electric by 2045. Caribbean Utilities Company operates free public "
                      "charging across Grand Cayman and installs paid strata chargers. "
                      "Fleet count is a stale 2021 figure and needs refreshing from the "
                      "Cayman Islands Vehicle Licensing Department.",
        "import_duty_ev_pct": 0.0,
        "fuel_price_usd_per_litre": 1.60,
        "source_year": 2021,
        "source_url": "https://www.radiocayman.gov.ky/news/zero-customs-duties-for-electric-vehicles",
    },
    {
        "country": "St Kitts & Nevis",
        "region": "Caribbean",
        "ev_sales_share_pct": None,
        "ev_fleet_total": None,
        "charging_stations": None,
        "key_policy": "Import duty on fully electric vehicles under four years old cut from "
                      "45% to 10%, effective 1 May 2026, announced alongside the SOLARISE and "
                      "DRIVE programmes. Closely parallels Jamaica's own 30% to 10% cut, which "
                      "makes it the most directly comparable policy event in the region. "
                      "UNEP/GEF-supported e-mobility sits inside the national energy "
                      "transition strategy, targeting a 61% cut in CO2 by 2030.",
        "import_duty_ev_pct": 10.0,
        "fuel_price_usd_per_litre": None,
        "source_year": 2026,
        "source_url": "https://www.sknis.gov.kn/2026/04/30/saint-kitts-and-nevis-government-slashes-import-duties-for-fully-electric-vehicles/",
    },
    {
        "country": "Grenada",
        "region": "Caribbean",
        "ev_sales_share_pct": None,
        "ev_fleet_total": None,
        "charging_stations": None,
        "key_policy": "100% duty and tax concession on EV imports and on charging stations, "
                      "granted in the 2024 Budget. Strongest headline incentive in the "
                      "Eastern Caribbean, with a stated aim that all new vehicle purchases in "
                      "2025 be electric or hybrid. Transport accounts for 39% of national "
                      "greenhouse gas emissions.",
        "import_duty_ev_pct": 0.0,
        "fuel_price_usd_per_litre": None,
        "source_year": 2024,
        "source_url": "https://www.finance.gd/docs/2023/Budget%20Statement%202024_1.pdf",
    },
    {
        "country": "Saint Lucia",
        "region": "Caribbean",
        "ev_sales_share_pct": None,
        "ev_fleet_total": None,
        "charging_stations": None,
        "key_policy": "Third Nationally Determined Contribution commits to 30% of new vehicle "
                      "sales being electric by 2030, backed by fiscal incentives and "
                      "infrastructure investment. Directly comparable in ambition to Jamaica's "
                      "12% private target, and notably more aggressive.",
        "import_duty_ev_pct": None,
        "fuel_price_usd_per_litre": 1.30,
        "source_year": 2026,
        "source_url": "https://unfccc.int/sites/default/files/2025-02/Saint%20Lucias%20Third%20Nationally%20Determined%20Contribution.pdf",
    },
    {
        "country": "Antigua & Barbuda",
        "region": "Caribbean",
        "ev_sales_share_pct": None,
        "ev_fleet_total": None,
        "charging_stations": None,
        "key_policy": "Nine electric minibuses in public transport trials, bought with a "
                      "US$560,000 GEF grant under the UNEP-led Sustainable Low-Carbon Island "
                      "Management project. Government aims to transition from internal "
                      "combustion to electric by 2040, including planned import restrictions "
                      "on conventional vehicles, and to electrify its own 180-vehicle fleet. "
                      "The clearest regional precedent for electrifying public transport.",
        "import_duty_ev_pct": None,
        "fuel_price_usd_per_litre": None,
        "source_year": 2025,
        "source_url": "https://www.unep.org/technical-highlight/caribbean-leading-charge-electric-mobility",
    },
    {
        "country": "Dominica",
        "region": "Caribbean",
        "ev_sales_share_pct": None,
        "ev_fleet_total": None,
        "charging_stations": None,
        "key_policy": "Regulated fuel pricing rather than EV-specific fiscal incentive. New "
                      "regulated prices were set in March 2026 in response to global "
                      "volatility, with gasoline at EC$15.57 per gallon. Pump price fell 4.5% "
                      "over 2025-26 while most of the region rose. No EV duty regime traced "
                      "by this project.",
        "import_duty_ev_pct": None,
        "fuel_price_usd_per_litre": 1.27,
        "source_year": 2026,
        "source_url": "https://energynow.tt/blog/gasoline-prices-rise-across-most-of-caricom",
    },
    {
        "country": "Haiti",
        "region": "Caribbean",
        "ev_sales_share_pct": None,
        "ev_fleet_total": None,
        "charging_stations": None,
        "key_policy": "Largest CARICOM pump price increase over 2025-26, up 29.5% to US$1.46 "
                      "per litre. Included as the region's low-income, high-fuel-price case: "
                      "it shows that a high pump price on its own does not drive EV adoption "
                      "when purchasing power and grid reliability are the binding constraints. "
                      "No EV policy framework traced by this project.",
        "import_duty_ev_pct": None,
        "fuel_price_usd_per_litre": 1.46,
        "source_year": 2026,
        "source_url": "https://energynow.tt/blog/gasoline-prices-rise-across-most-of-caricom",
    },
    {
        "country": "Bermuda",
        "region": "Caribbean",
        "ev_sales_share_pct": None,
        "ev_fleet_total": None,
        "charging_stations": None,
        "key_policy": "Electric vehicles have been duty free since the 2011/12 budget and EV "
                      "batteries since 2017, making this the longest-running zero-duty regime "
                      "in the region. Parts for EV charging stations are also duty free. A "
                      "National Electric Vehicle Policy and Strategy has been out for public "
                      "consultation. Useful as a long-run test of what duty removal alone "
                      "achieves over more than a decade.",
        "import_duty_ev_pct": 0.0,
        "fuel_price_usd_per_litre": None,
        "source_year": 2025,
        "source_url": "https://www.gov.bm/articles/duty-free%C2%A0parts-electric-vehicle-charging-stations-and-accessories",
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
        "fuel_price_usd_per_litre": 1.46,
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
        "fuel_price_usd_per_litre": 1.0,
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
#   BEV manufacturing CO2 premium is derived in data/vehicles.py from battery
#     capacity and the battery supply-chain intensity in Bieker, G. (2021).
#     A global comparison of the life-cycle greenhouse gas emissions of
#     combustion engine and electric passenger cars. ICCT.
#     https://theicct.org/publication/a-global-comparison-of-the-life-cycle-greenhouse-gas-emissions-of-combustion-engine-and-electric-passenger-cars/

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

# BEV manufacturing CO2 premium above an equivalent ICE vehicle.
#
# The hardcoded dict that used to live here has been REMOVED. Its values were
# labelled "premium above ICE" but were consistently 2.2 to 2.4 times the
# battery production emissions implied by Bieker (2021), which means they were
# cradle-to-gate vehicle totals, not premiums. Charging a full vehicle total as
# a premium roughly doubled the carbon payback period reported by Module 5.
#
# Premiums are now derived in data/vehicles.py from battery capacity and the
# published supply-chain intensity. Call bev_manufacturing_premium_tonnes(key).
# See that file for the method, its glider-parity assumption, and the citation.


# Fields a country needs before it can appear on every chart in this module.
REGIONAL_FIELDS = [
    ("ev_sales_share_pct",       "BEV sales share"),
    ("ev_fleet_total",           "EV fleet total"),
    ("charging_stations",        "charging stations"),
    ("import_duty_ev_pct",       "EV import duty"),
    ("fuel_price_usd_per_litre", "retail fuel price"),
]


def regional_data_gaps(row):
    """Which of the comparison fields this country has no figure for."""
    return [label for key, label in REGIONAL_FIELDS if row.get(key) is None]


def build_regional_footnotes():
    """
    Per-country note on what data exists and what does not.

    Dr Harris asked for footnotes saying whether each country has data
    available. This is worth more than a tidy chart, because the gaps are the
    finding: only 5 of the 19 countries here have a complete set, and 14 are
    missing at least one field. A reader who sees Chile absent from a chart
    should be able to learn that it is absent because no figure was obtainable,
    not because Chile has no EVs.

    Countries are grouped by how complete they are rather than alphabetically,
    so the pattern is visible at a glance.
    """
    complete, partial, none_at_all = [], [], []
    for r in sorted(REGIONAL_DATA, key=lambda x: x["country"]):
        gaps = regional_data_gaps(r)
        if not gaps:
            complete.append((r, gaps))
        elif len(gaps) == len(REGIONAL_FIELDS):
            none_at_all.append((r, gaps))
        else:
            partial.append((r, gaps))

    note = {"fontSize": "14px", "color": "#5B7A70", "margin": "0 0 6px 0",
            "textAlign": "justify", "lineHeight": "1.5"}

    def block(title, items, describe):
        if not items:
            return None
        lines = []
        for r, gaps in items:
            yr = r.get("source_year")
            lines.append(html.Li([
                html.B(r["country"]),
                f"  (data year {yr}). " if yr else ". ",
                describe(gaps),
            ], style=note))
        return html.Div([
            html.Div(f"{title} ({len(items)})", style={
                "fontWeight": "700", "fontSize": "15px",
                "color": "#0E2A24", "marginTop": "10px", "marginBottom": "4px"}),
            html.Ul(lines, style={"marginTop": "0", "paddingLeft": "20px"}),
        ])

    return html.Div([
        html.Div("Data availability by country", style={
            "backgroundColor": "#E1F5EE", "color": "#0E2A24",
            "fontWeight": "700", "fontSize": "18px", "padding": "10px 18px",
            "marginBottom": "10px", "marginTop": "20px", "borderRadius": "2px"}),
        html.P(
            "Figures come from different years and different national sources, "
            "so a country missing from a chart is missing because no figure "
            "could be obtained, not because the value is zero. Comparisons "
            "across countries should be read with the data year in mind.",
            style={**note, "marginBottom": "10px"},
        ),
        block("Complete data", complete,
              lambda g: "All five comparison fields available."),
        block("Partial data", partial,
              lambda g: f"No figure obtained for: {', '.join(g)}."),
        block("No comparison data", none_at_all,
              lambda g: ("Listed for regional context only. No figure was "
                         "obtained for any comparison field, so this country "
                         "does not appear on the charts above.")),
    ])


def module8_layout():
    import pandas as pd

    df = pd.DataFrame(REGIONAL_DATA)

    # ── Chart 1: Horizontal bar chart of EV sales share ──────────────
    df_bar = df[df["ev_sales_share_pct"].notna()].sort_values(
        "ev_sales_share_pct", ascending=True
    )
    # Jamaica was blue and the rest of the Caribbean teal, the same blue/green
    # pairing as the scatter. Jamaica is now orange in both charts, so the eye
    # finds it in the same colour wherever it appears in this module.
    bar_colors = [
        SERIES_COLOURS["ice"] if c == "Jamaica" else
        SERIES_COLOURS["blue"] if r == "Caribbean" else
        SERIES_COLOURS["grey"]
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
    # "most recent year" told the reader nothing. The figures come from
    # different years per country, which matters when comparing them, so the
    # actual span is stated and each bar carries its own year on hover.
    bar_years = sorted({r["source_year"] for r in REGIONAL_DATA
                        if r["ev_sales_share_pct"] is not None and r.get("source_year")})
    year_span = (f"{bar_years[0]}" if len(bar_years) == 1
                 else f"{bar_years[0]} to {bar_years[-1]}")
    fig_bar.update_layout(**chart_layout(
        f"BEV New Car Sales Share by Country (%, data years {year_span})",
        height=340, xtitle="BEV New Car Sales Share (%)",
        show_legend=False, left=120, right=80,
    ))
    fig_bar.update_traces(
        customdata=df_bar["source_year"],
        hovertemplate="%{y}: %{x:.1f}% (data year %{customdata})<extra></extra>",
    )
    fig_bar.update_xaxes(range=[0, 40], ticksuffix="%")

    # ── Chart 2: Scatter plot fuel price vs EV adoption ──────────────
    df_scatter = df[
        df["ev_sales_share_pct"].notna() &
        df["fuel_price_usd_per_litre"].notna()
    ].copy()
    # Cross-country comparisons stay in USD. The source data is natively USD and
    # converting it into JMD to compare Uruguay against Brazil added a Jamaican
    # exchange rate to a chart that has nothing to do with Jamaica's currency,
    # and made every point move whenever the JMD rate moved. Supervisor feedback
    # item 11: display USD for all cross-country comparisons.
    fig_scatter = go.Figure()

    df_jamaica = df_scatter[df_scatter["country"] == "Jamaica"]
    df_others  = df_scatter[df_scatter["country"] != "Jamaica"]

    fig_scatter.add_trace(go.Scatter(
        x=df_others["fuel_price_usd_per_litre"],
        y=df_others["ev_sales_share_pct"],
        mode="markers+text",
        # Was teal #1A7A6E against Jamaica's blue #2E75B6. Blue and teal are
        # the pairing Dr Harris flagged, and here they carried the single most
        # important distinction on the chart: which point is Jamaica. The
        # comparison countries are now muted blue and Jamaica is orange, the
        # strongest separation available and one that survives greyscale
        # printing because the two also differ in lightness.
        marker=dict(color=SERIES_COLOURS["blue"], size=14, opacity=0.75),
        text=df_others["country"],
        textposition="top center",
        textfont=dict(size=14),
        name="Other countries",
    ))
    fig_scatter.add_trace(go.Scatter(
        x=df_jamaica["fuel_price_usd_per_litre"],
        y=df_jamaica["ev_sales_share_pct"],
        mode="markers+text",
        marker=dict(color=SERIES_COLOURS["ice"], size=18,
                    line=dict(color="#0E2A24", width=2), symbol="diamond"),
        text=df_jamaica["country"],
        textposition="top center",
        textfont=dict(size=15, color=SERIES_COLOURS["ice"]),
        name="Jamaica",
    ))

    import numpy as np
    if len(df_scatter) >= 2:
        z = np.polyfit(df_scatter["fuel_price_usd_per_litre"], df_scatter["ev_sales_share_pct"], 1)
        trend_x = [df_scatter["fuel_price_usd_per_litre"].min(), df_scatter["fuel_price_usd_per_litre"].max()]
        trend_y = [z[0] * x + z[1] for x in trend_x]
        fig_scatter.add_trace(go.Scatter(
            x=trend_x, y=trend_y,
            mode="lines",
            line=dict(color="#B0B0B0", width=1.5, dash="dot"),
            name="Trend",
            hoverinfo="skip",
        ))

    fig_scatter.update_layout(**chart_layout(
        "Retail Fuel Price vs BEV Adoption Rate",
        height=380,
        xtitle="Retail Fuel Price (US$/litre)",
        ytitle="BEV New Car Sales Share (%)",
        legend_rows=1, left=60, right=40,
    ))
    fig_scatter.update_xaxes(tickprefix="US$")
    fig_scatter.update_yaxes(ticksuffix="%")

    # ── Summary table ─────────────────────────────────────────────────
    banner = {
        "backgroundColor": "#E1F5EE",
        "color": "#0E2A24",
        "fontWeight": "700",
        "fontSize": "18px",
        "padding": "10px 18px",
        "marginBottom": "12px",
        "marginTop": "20px",
        "borderRadius": "2px",
    }
    th = {
        "backgroundColor": "#1A9E75",
        "color": "white",
        "fontWeight": "600",
        "fontSize": "15px",
        "padding": "8px 12px",
        "textAlign": "left",
        "border": "1px solid #cccccc",
    }

    def td_style(country):
        base = {
            "padding": "7px 12px",
            "fontSize": "15px",
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
               "fontSize": "15px"}
    )

    return html.Div([
        html.Div("BEV Adoption by Country", style=banner),
        dcc.Graph(figure=fig_bar, config={"displayModeBar": False}),

        html.Div("Fuel Price vs BEV Adoption Rate", style=banner),
        dcc.Graph(figure=fig_scatter, config={"displayModeBar": False}),
        html.P(
            "Each point is one country. The x-axis is retail fuel price in US$ per litre, "
            "kept in USD because converting international prices into Jamaican dollars adds "
            "an exchange rate that has nothing to do with the comparison. Caribbean prices "
            "are May 2026 from one source for consistency. The y-axis is BEV share of new "
            "car sales, not fleet stock. "
            "Only 7 of the 16 countries appear. Nine are missing because Caribbean vehicle "
            "registries do not publish EV sales share, not because those markets have none. "
            "The dotted trend line is fitted to those 7 points only and should be read as "
            "indicative at best. "
            "Read the two points at US$1.46 together: Jamaica and The Bahamas face an almost "
            "identical pump price, yet Bahamian BEV share is roughly four times Jamaica's. "
            "Whatever separates them is not the price of fuel. That single pair is stronger "
            "evidence than the trend line.",
            style={"fontSize": "16px", "color": "#444", "textAlign": "justify",
                   "lineHeight": "1.5",
                   "marginTop": "8px", "marginBottom": "20px"}
        ),

        html.Div("Regional Comparison Summary Table", style=banner),
        table,

        build_regional_footnotes(),
    ], style={"padding": "4px"})


def module1_layout():
    lbl = {"fontSize": "15px", "fontWeight": "600", "color": "#555",
           "marginBottom": "4px", "display": "block"}
    inp = {"width": "100%", "padding": "6px 8px", "fontSize": "16px",
           "border": "1px solid #ccc", "borderRadius": "4px",
           "marginBottom": "6px", "boxSizing": "border-box"}
    hint = {"fontSize": "14px", "color": "#888", "marginBottom": "10px", "marginTop": "2px"}
    det_sum = {"cursor": "pointer", "fontWeight": "600", "fontSize": "16px",
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
                         clearable=False, style={"fontSize": "16px", "marginBottom": "10px"}),
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
                         clearable=False, style={"fontSize": "16px", "marginBottom": "10px"}),
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
                labelStyle={"display": "block", "fontSize": "16px", "marginBottom": "6px"},
            ),
            html.Div(id="m1-charging-mix-inputs", children=[
                html.Label("% charged at home",
                           style={"fontSize": "15px", "fontWeight": "500", "display": "block",
                                  "marginTop": "10px", "marginBottom": "4px"}),
                dcc.Input(id="m1-home-charge-pct", type="number", debounce=True,
                          value=70, min=0, max=100, step=1,
                          style={"width": "100px", "padding": "6px 8px", "fontSize": "16px",
                                 "border": "1px solid #ccc", "borderRadius": "4px"}),
                html.Span(" % (rest at public rate)",
                          style={"fontSize": "15px", "color": "#888", "marginLeft": "8px"}),
            ], style={"display": "none"}),
            html.P("Home rate and public rate are set in Global settings above.", style=hint),
        ], open=True, style=det_style),

        html.Div(id="m1-summary-cards"),

        html.P(
            "ICE prices: Toyota Jamaica (toyotajamaica.com, June 2026), converted at J$158.53/USD. "
            "EV prices: not publicly listed by the authorized dealer in Jamaica — enter a confirmed dealer quote. "
            "Consumption figures are estimates for Jamaican driving conditions.",
            style={"fontSize": "14px", "color": "#999", "marginTop": "8px",
                   "borderTop": "1px solid #eee", "paddingTop": "10px"}),
    ], style={"width": "38%", "minWidth": "300px", "flexShrink": "0"})

    right_panel = html.Div([
        html.P(
            "Enter all required fields to see the Total Cost of Ownership chart.",
            id="m1-tco-placeholder",
            style={"color": "#aaa", "fontSize": "16px", "marginTop": "40px",
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
            # Custom is the default selection, so this branch runs on first load
            # before the user has typed anything. It previously set markup = 0,
            # which handed every module the bare Petrojam wholesale price as if
            # it were a pump price and understated fuel cost by roughly J$34/L.
            # Fall back to the surveyed Kingston average instead, and say so.
            markup = KINGSTON_RETAIL_MARKUP_AVG.get(grade, 34)
            markup_source = "Kingston average, enter your own pump price above"
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
    ], style={"fontSize": "16px", "color": "#444", "margin": "0"})


@app.callback(
    Output("m6-fuel-price-prompt", "children"),
    Input("effective-fuel-price-store", "data"),
)
def show_fuel_price_prompt(effective_price):
    if effective_price is None:
        return html.Div([
            html.P("Select a fuel grade in Global settings to enable Module 1, 5, and 6 calculations.",
                   style={"margin": "0", "fontSize": "16px", "color": "#856404"}),
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
                style={"fontSize": "14px", "color": "#2d8a2d",
                       "marginTop": "2px", "marginBottom": "10px"},
            ),
        ])
    else:
        note = html.P(
            f"Range: {v.get('range_km_nedc')} km (NEDC). "
            "Price not publicly listed — enter a confirmed dealer quote.",
            style={"fontSize": "14px", "color": "#888",
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
                      "showarrow": False, "font": {"size": 16, "color": "#aaa"}}],
    )
    if not all([ice_consumption, ev_consumption, daily_km, years, grid_scenario]):
        return (html.P("Enter all inputs to see results.",
                       style={"color": "#888", "fontSize": "16px"}),
                empty_fig)

    years = int(years)
    grid = GRID_SCENARIOS[grid_scenario]
    intensity = grid["intensity_kg_per_kwh"]
    annual_km = daily_km * 365.0

    annual_co2_ice = (ice_consumption / 100) * annual_km * CO2_PER_LITRE_PETROL
    annual_co2_ev  = (ev_consumption  / 100) * annual_km * intensity

    # Manufacturing premium derived from battery capacity, not hardcoded.
    # If the selected BEV has no battery capacity on record we surface that
    # rather than silently substituting an invented default.
    mfg_premium_t = bev_manufacturing_premium_tonnes(ev_key)
    if mfg_premium_t is None:
        return (html.P("No battery capacity on record for the selected BEV, so the "
                       "manufacturing CO2 premium cannot be derived. Add battery_kwh "
                       "to this vehicle in data/vehicles.py.",
                       style={"color": "#C0392B", "fontSize": "16px"}),
                empty_fig)
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
    big  = {"fontSize": "22px", "fontWeight": "700", "margin": "4px 0"}
    tiny = {"fontSize": "15px", "color": "#777", "margin": "0"}

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
                         style={**big, "color": payback_col, "fontSize": "17px"})],
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
    fig.update_layout(**chart_layout(
        f"Cumulative CO2 Emissions over {years} Years (tonnes)",
        height=440,
        xtitle="Year of ownership",
        ytitle="Cumulative CO2 (tonnes)",
        legend_rows=2,   # "BEV cumulative CO2 (incl. manufacturing)" wraps
        left=60, right=40,
    ))
    fig.update_xaxes(dtick=1)

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
            style={"color": "#888", "fontSize": "16px"},
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
    big  = {"fontSize": "18px", "fontWeight": "700", "margin": "4px 0"}
    tiny = {"fontSize": "15px", "color": "#777", "margin": "0"}

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
        **chart_layout(
            "Total Cost of Ownership",
            height=420, xtitle="Year", ytitle="Cumulative Cost (J$ millions)",
            legend_rows=1, left=60,
        )
    )
    # Feedback item 20: state the crossover in words, not only as a chart
    # annotation. The chart line is easy to miss and impossible to quote.
    if crossover is None:
        if ev_cum[-1] < ice_cum[-1]:
            verdict_text = f"The EV is already cheaper, and stays cheaper for all {years} years."
            verdict_sub = "It never falls behind within this ownership period."
            verdict_col = "#1A7A6E"
        else:
            verdict_text = f"The EV does not overtake within {years} years."
            verdict_sub = ("Try a longer ownership period, more daily driving, "
                           "or a higher share of home charging.")
            verdict_col = "#C0392B"
    else:
        yrs = int(crossover)
        months = int(round((crossover - yrs) * 12))
        if months == 12:
            yrs, months = yrs + 1, 0
        when = (f"{months} months" if yrs == 0 else
                f"{yrs} years" if months == 0 else
                f"{yrs} years, {months} months")
        verdict_text = f"The EV becomes the cheaper vehicle after {when}."
        verdict_sub = ("Before this point the petrol car has cost you less overall. "
                       "After it, the EV is ahead and the gap keeps widening.")
        verdict_col = "#1A7A6E"

    verdict_box = html.Div([
        html.P("When does the EV overtake?",
               style={"fontSize": "15px", "color": "#777", "margin": "0 0 4px"}),
        html.P(verdict_text,
               style={"fontSize": "21px", "fontWeight": "700",
                      "color": verdict_col, "margin": "0 0 4px"}),
        html.P(verdict_sub,
               style={"fontSize": "14px", "color": "#888", "margin": "0"}),
    ], style={"backgroundColor": "#ffffff", "border": f"1px solid {verdict_col}",
              "borderRadius": "6px", "padding": "12px 16px", "marginTop": "10px"})

    return (html.Div([summary_cards, verdict_box]),
            fig_tco, show_chart, hide_ph)


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


# ── Module order and numbering ────────────────────────────────────
#
# MODULE_INFO is an ordered dict and it is the SINGLE source of display order.
# The sidebar, the homepage cards and the page header all iterate over it, so
# reordering these lines reorders the whole dashboard. Nothing else needs to
# change.
#
# The tab-N keys are INTERNAL IDS ONLY. They are the original build order and
# they no longer match the position on screen. Do not read them as module
# numbers. They are deliberately left alone because they are wired into the
# content div ids, the icon map, the instruction map and every callback; the
# displayed number is derived from position instead, by module_number() below.
#
# Current display order, set July 2026 on supervisor feedback:
#   policy context, then regional context, then private consumer, then taxi,
#   then routes, then fleet, then emissions, then fuel prices.

# (name, accent colour). The build-week field that used to sit between them has
# been removed: it described the project schedule, not the module, and meant
# nothing to anyone using the dashboard.
MODULE_INFO = {
    "tab-7": ("Fiscal Policy & Duty Tracker",      "#C55A11"),
    "tab-8": ("Caribbean Regional Comparison",     "#C55A11"),
    "tab-1": ("EV vs. ICE Calculator",             "#2E75B6"),
    "tab-6": ("Taxi Feasibility Tool",             "#1A7A6E"),
    "tab-2": ("Route Cost Map",                    "#2E75B6"),
    "tab-4": ("Fleet Penetration Simulator",       "#2E75B6"),
    "tab-5": ("Emissions Impact Calculator",       "#1A7A6E"),
    "tab-3": ("Gas & Energy Price Tracker",        "#2E75B6"),
}

# Modules that render a placeholder rather than real content. Shown greyed with
# an "In development" tag so a demo viewer knows it is deliberate, not broken.
MODULES_IN_DEVELOPMENT = {"tab-2"}


def module_number(tab_id):
    """Displayed module number, derived from position in MODULE_INFO."""
    return list(MODULE_INFO).index(tab_id) + 1


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
    lbl = {"fontSize": "15px", "fontWeight": "600", "color": "#555",
           "marginBottom": "4px", "display": "block"}
    inp = {
        "width": "100%", "padding": "6px 8px", "fontSize": "16px",
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
                         style={"fontSize": "16px", "marginBottom": "14px"}),
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
                         style={"fontSize": "16px", "marginBottom": "14px"}),
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
                         style={"fontSize": "16px", "marginBottom": "4px"}),
        ], style=det_style),

        html.Div(id="m5-cards"),

        html.P(
            "The electric figure includes the emissions from building its battery, "
            "which is why the carbon payback is not immediate.",
            style={"fontSize": "14px", "color": "#999", "marginTop": "12px",
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
        "fontWeight": "700", "fontSize": "18px",
        "padding": "10px 16px", "marginBottom": "12px",
        "marginTop": "8px", "borderRadius": "6px",
        "borderLeft": "3px solid #1A9E75",
    }
    lbl = {"fontSize": "15px", "fontWeight": "600", "color": "#555",
           "marginBottom": "4px", "display": "block"}
    inp = {"width": "100%", "padding": "6px 8px", "fontSize": "16px",
           "border": "1px solid #ccc", "borderRadius": "4px",
           "marginBottom": "10px", "boxSizing": "border-box"}

    btn_base = {
        "padding": "7px 14px", "fontSize": "15px", "fontWeight": "600",
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
                    style={"fontSize": "15px", "color": "#666", "marginBottom": "14px"},
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
                        "fontSize": "14px", "color": "#444",
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
                            "fontSize": "15px", "cursor": "pointer",
                            "color": "#777", "padding": "4px 0",
                            "marginBottom": "10px",
                        },
                    ),
                    html.P(
                        "Steepness: how sharply adoption accelerates once it starts. "
                        "Midpoint: the year when 50% of the stream's target penetration is reached. "
                        "Clicking a preset above updates these values automatically.",
                        style={"fontSize": "14px", "color": "#888", "marginBottom": "10px"},
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
                    # step=1: fleet counts are exact numbers, not round hundreds.
                    # step=100 rejected both 540,113 and 350 as invalid.
                    # max 2,000,000: Jamaica certified 575,041 vehicles fit in 2022,
                    # so a 10,000,000 ceiling was meaningless.
                    value=b["current_estimate"], min=1, max=2_000_000, step=1,
                    style=inp,
                ),

                html.Label("Avg annual km per vehicle", style=lbl),
                dcc.Input(
                    id=f"m4-{stream_key}-km-per-year", type="number", debounce=True,
                    value=b["km_per_year_avg"], min=1000, max=100000, step=100,
                    style=inp,
                ),

                html.Label("Avg ICE consumption (L/100km)", style=lbl),
                dcc.Input(
                    id=f"m4-{stream_key}-consumption", type="number", debounce=True,
                    # max raised 25 -> 70. This one input serves cars (~8 L/100km)
                    # AND buses (~55 L/100km), so a car-sized ceiling made the
                    # public transport stream impossible to set correctly.
                    value=b["avg_consumption_l_per_100km"], min=3, max=70, step=0.1,
                    style=inp,
                ),

                html.Label("Avg EV consumption (kWh/100km)", style=lbl),
                dcc.Input(
                    id=f"m4-{stream_key}-ev-consumption", type="number", debounce=True,
                    value=b["avg_ev_consumption_kwh_per_100km"], min=5, max=300, step=0.1,
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
        ], style={"fontSize": "16px", "color": "#444", "marginBottom": "16px"}),


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
                    style={"fontSize": "16px", "marginBottom": "12px"},
                ),
                html.P(
                    "Same grid scenarios as Module 5. Affects the CO2 avoided figures only.",
                    style={"fontSize": "14px", "color": "#888"},
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
                       "fontSize": "17px", "padding": "8px"},
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
                       "fontSize": "17px", "padding": "8px"},
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
                       "fontSize": "17px", "padding": "8px"},
            ),
            stream_controls("goj"),
        ], open=False, style={
            "backgroundColor": "#fafafa", "borderRadius": "6px",
            "padding": "8px", "marginBottom": "16px",
        }),

        html.Div(id="m4-summary-cards"),

        # ── Private fleet emissions comparison ──────────────────────────
        html.Div("Private Fleet Emissions Comparison", style=banner),
        html.P(
            "The simulator above projects one penetration path, the S-curve. This "
            "section instead asks the counterfactual question directly: at any chosen "
            "level of private fleet electrification, what happens to emissions? "
            "Move the slider to any value from 0% to 100%.",
            style={"fontSize": "15px", "color": "#555", "marginBottom": "12px"},
        ),

        html.Div([
            html.Label("Direction", style=lbl),
            dcc.RadioItems(
                id="m4-fleet-emissions-mode",
                options=[
                    {"label": "  Retrospective: what emissions WOULD have been, "
                              "2015 to 2026", "value": "back"},
                    {"label": "  Forward: what emissions WILL be, 2026 to 2035",
                     "value": "forward"},
                ],
                value="back",
                labelStyle={"display": "block", "fontSize": "15px",
                            "marginBottom": "6px"},
            ),

            html.Label("Private fleet EV penetration (%)",
                       style={**lbl, "marginTop": "12px"}),
            dcc.Slider(
                id="m4-fleet-penetration", min=0, max=100, step=1, value=12,
                marks={0: "0%", 12: "12%", 25: "25%", 50: "50%",
                       75: "75%", 100: "100%"},
                tooltip={"placement": "bottom", "always_visible": True},
            ),
            html.P(
                "12% is the Government of Jamaica 2030 private vehicle target. "
                "Penetration is applied as a constant share across the whole period, "
                "which is the cleanest way to read the counterfactual. It is not a "
                "forecast of the adoption path.",
                style={"fontSize": "14px", "color": "#888", "marginTop": "8px"},
            ),

            html.Label("Include battery manufacturing emissions",
                       style={**lbl, "marginTop": "10px"}),
            dcc.RadioItems(
                id="m4-fleet-include-mfg",
                options=[
                    {"label": "  Yes, charge the battery production debt", "value": "yes"},
                    {"label": "  No, tailpipe and grid only", "value": "no"},
                ],
                value="yes",
                labelStyle={"display": "block", "fontSize": "15px",
                            "marginBottom": "6px"},
            ),
        ], style={
            "backgroundColor": "#fff", "border": "1px solid #e0e0e0",
            "borderRadius": "6px", "padding": "16px", "marginBottom": "16px",
        }),

        html.Div(id="m4-fleet-emissions-cards"),

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
        dcc.Graph(id="m4-fleet-emissions-fig", style={"height": "340px"},
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
    lbl  = {"fontSize": "15px", "fontWeight": "600", "color": "#555",
            "marginBottom": "4px", "display": "block"}
    inp  = {"width": "100%", "padding": "6px 8px", "fontSize": "16px",
            "border": "1px solid #ccc", "borderRadius": "4px",
            "marginBottom": "6px", "boxSizing": "border-box"}
    hint = {"fontSize": "14px", "color": "#888", "marginBottom": "10px", "marginTop": "2px"}
    det_sum = {"cursor": "pointer", "fontWeight": "600", "fontSize": "16px",
               "padding": "6px 0", "marginBottom": "8px"}
    det_style = {"backgroundColor": "#fff", "border": "1px solid #e0e0e0",
                 "borderRadius": "6px", "padding": "14px 16px", "marginBottom": "10px"}
    veh_det = {"backgroundColor": "#fafafa", "border": "1px solid #e0e0e0",
               "borderRadius": "4px", "padding": "10px 14px", "marginBottom": "8px"}

    # Loan blocks are rendered for EVERY candidate vehicle and shown or hidden
    # by CSS, matching the permanently-mounted-DOM pattern used elsewhere in
    # this dashboard. Dynamically creating and destroying them would reintroduce
    # the nonexistent-component callback errors that pattern was adopted to fix.
    # IDs are pattern-matching dicts so one MATCH callback serves all vehicles
    # instead of one pair of callbacks per vehicle.
    def loan_block(key, v):
        default_dp, default_rate, default_term = v["loan_defaults"]
        return html.Details([
            html.Summary(v["label"], style={**det_sum, "fontSize": "15px"}),
            html.Label("Down payment (%)", style=lbl),
            dcc.Input(id={"kind": "m6-dp", "veh": key}, type="number", debounce=True,
                      value=default_dp, min=0, max=100, step=5, style=inp),
            html.Label("Loan interest rate (% APR)", style=lbl),
            dcc.Input(id={"kind": "m6-rate", "veh": key}, type="number", debounce=True,
                      value=default_rate, min=1, max=30, step=0.1, style=inp),
            dcc.Slider(id={"kind": "m6-rate-slider", "veh": key}, min=1, max=30, step=0.1,
                       value=default_rate,
                       marks={1: "1%", 10: "10%", 20: "20%", 30: "30%"},
                       tooltip={"placement": "bottom", "always_visible": False}),
            html.Label("Loan term (years)", style={**lbl, "marginTop": "8px"}),
            dcc.Input(id={"kind": "m6-term", "veh": key}, type="number", debounce=True,
                      value=default_term, min=0.5, max=10, step=0.5, style=inp),
            dcc.Slider(id={"kind": "m6-term-slider", "veh": key}, min=0.5, max=10, step=0.5,
                       value=default_term,
                       marks={0.5: "0.5", 3: "3", 6: "6", 10: "10"},
                       tooltip={"placement": "bottom", "always_visible": False}),
        ], id={"kind": "m6-loan-wrap", "veh": key},
           open=(key in TAXI_DEFAULT_SELECTION), style=veh_det)

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
                    {"label": " Home charging, JPS residential (set in Global settings)",
                     "value": "home"},
                    {"label": " Public network rate (set in Global settings)", "value": "public"},
                    {"label": f" JPS overnight — J${JPS_OFFPEAK_RATE}/kWh (cheapest)",
                     "value": "jps_offpeak"},
                    {"label": f" JPS daytime — J${JPS_DAY_RATE}/kWh", "value": "jps_day"},
                    {"label": f" JPS evening peak — J${JPS_PEAK_RATE}/kWh (worst case)",
                     "value": "jps_peak"},
                    {"label": " Custom rate", "value": "custom"},
                ],
                value="public",
                labelStyle={"display": "block", "fontSize": "15px", "marginBottom": "6px"},
            ),
            html.Div(id="m6-custom-rate-wrapper", children=[
                html.Label("Custom charging rate (J$/kWh)", style={**lbl, "marginTop": "8px"}),
                dcc.Input(id="m6-custom-rate", type="number", debounce=True,
                          value=None, min=10, max=200, step=0.5,
                          placeholder="J$/kWh",
                          style={"width": "160px", "padding": "6px 8px", "fontSize": "16px",
                                 "border": "1px solid #ccc", "borderRadius": "4px"}),
            ], style={"display": "none"}),
            html.P("Public rate is confirmed. Fleet HQ rate is a project estimate for "
                   "commercial JPS tariff pending confirmed data.",
                   style={**hint, "marginTop": "8px"}),
        ], open=True, style=det_style),

        html.Details([
            html.Summary("Vehicles to compare", style=det_sum),
            dcc.Dropdown(
                id="m6-vehicle-select",
                options=[{"label": v["label"] + ("" if v["consumption_measured"]
                                                 else "  (consumption derived)"),
                          "value": k}
                         for k, v in TAXI_VEHICLES.items()],
                value=list(TAXI_DEFAULT_SELECTION),
                multi=True, clearable=False,
                style={"fontSize": "15px"},
            ),
            html.P("Pick any combination. At least one ICE vehicle is needed for a "
                   "crossover comparison. Vehicles marked 'consumption derived' have "
                   "no urban field measurement and use a scaled combined figure.",
                   style={**hint, "marginTop": "8px"}),
        ], open=True, style=det_style),

        html.Details([
            html.Summary("Loan financing — per vehicle", style=det_sum),
            html.Div([loan_block(k, v) for k, v in TAXI_VEHICLES.items()]),
            html.P("Rates from ScoopRate summary of Jamaica lender rates, 2026. "
                   "Used and EV paper are priced differently by Jamaican lenders, so "
                   "defaults vary by vehicle class.",
                   style=hint),
        ], open=True, style=det_style),

        html.Div(id="m6-vehicle-cards"),

    ], style={"width": "40%", "minWidth": "300px", "flexShrink": "0"})

    right_panel = html.Div([
        html.P(
            "Fill in the inputs to see cumulative income chart and crossover analysis.",
            id="m6-chart-placeholder",
            style={"color": "#aaa", "fontSize": "16px", "marginTop": "40px",
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
    for n, (tab_id, (name, colour)) in enumerate(MODULE_INFO.items(), start=1):
        in_dev = tab_id in MODULES_IN_DEVELOPMENT
        this_card = dict(card_style)
        if in_dev:
            this_card.update({"opacity": "0.6",
                              "borderStyle": "dashed"})
        cards.append(
            html.Div([
                html.I(className=NAV_ICONS.get(tab_id, "fa-solid fa-circle"),
                       style={"fontSize": "27px", "color": "var(--accent)", "marginBottom": "10px"}),
                html.H4(f"{n}. {name}",
                        style={"margin": "0 0 6px", "fontSize": "18px", "color": "var(--text-primary)"}),
                html.Span("In development", style={
                    "display": "inline-block", "marginTop": "8px",
                    "fontSize": "12px", "fontWeight": "700",
                    "letterSpacing": "0.4px", "textTransform": "uppercase",
                    "color": "#8A6D00", "backgroundColor": "#FFF4CC",
                    "border": "1px solid #E8D48A",
                    "borderRadius": "10px", "padding": "2px 8px",
                }) if in_dev else None,
            ], id={"type": "home-card", "index": tab_id}, n_clicks=0, style=this_card)
        )
    return html.Div([
        html.H2("Jamaica EV Dashboard", style={"color": "var(--text-primary)", "marginBottom": "4px"}),
        html.P("Select a module below to get started.", style={"color": "var(--text-secondary)", "marginBottom": "24px", "fontSize": "16px"}),
        html.Div(cards, style={"display": "grid", "gridTemplateColumns": "repeat(auto-fill, minmax(220px, 1fr))", "gap": "16px"}),
    ])


@app.callback(
    Output("sidebar-nav-container", "children"),
    Input("active-tab-store", "data")
)
def render_sidebar_nav(active_tab):
    links = [
        html.Div([
            html.I(className="fa-solid fa-house", style={"width": "18px", "fontSize": "16px"}),
            html.Span("Home", style={"fontSize": "16px"}),
        ], id={"type": "nav-link", "index": "home"},
           className="sidebar-nav-link" + (" active" if active_tab == "home" else ""),
           n_clicks=0)
    ]
    for n, (tab_id, (name, _)) in enumerate(MODULE_INFO.items(), start=1):
        is_active = tab_id == active_tab
        in_dev = tab_id in MODULES_IN_DEVELOPMENT
        links.append(
            html.Div([
                html.I(className=NAV_ICONS.get(tab_id, "fa-solid fa-circle"),
                       style={"width": "18px", "fontSize": "16px"}),
                html.Span(f"{n}. {name}",
                          style={"fontSize": "16px",
                                 "opacity": "0.55" if in_dev else "1"}),
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
    name, colour = MODULE_INFO[tab]
    # The build-week box that used to sit under the title has gone with the
    # field itself. The accent colour is still used, on the title.
    return html.Div([
        html.H2(f"{module_number(tab)}. {name}",
                style={"color": "#1F3864", "marginTop": "0",
                       "marginBottom": "20px",
                       "borderBottom": f"3px solid {colour}",
                       "paddingBottom": "8px", "display": "inline-block"}),
    ])


import math


# ── Module 4: private fleet emissions counterfactual ──────────────
#
# GRID INTENSITY OVER TIME
#
# The project has three sourced grid intensity points, all from the METT 2022
# Integrated Resource Plan: 0.474 kg CO2/kWh for the 2022 actual mix, 0.380 for
# the IRP 2026 projection and 0.275 for the 2030 target. There is NO published
# annual series for Jamaica before 2022 that this project has obtained.
#
# For the retrospective the 2022 figure is therefore held flat backwards to
# 2015. This is a stated simplification, not a measurement. Jamaica's renewable
# share was lower before 2022, so the true pre-2022 grid was probably dirtier
# than 0.474, which means the retrospective UNDERSTATES the emissions an EV
# fleet would have produced and therefore OVERSTATES the CO2 avoided. Treat the
# retrospective CO2 figures as an optimistic bound and say so in the report.
#
# Between sourced points the series is linearly interpolated.

GRID_INTENSITY_ANCHORS = {2022: 0.474, 2026: 0.380, 2030: 0.275}


def grid_intensity_for_year(year):
    """Interpolated grid CO2 intensity, flat outside the sourced range."""
    yrs = sorted(GRID_INTENSITY_ANCHORS)
    if year <= yrs[0]:
        return GRID_INTENSITY_ANCHORS[yrs[0]]
    if year >= yrs[-1]:
        return GRID_INTENSITY_ANCHORS[yrs[-1]]
    for a, b in zip(yrs, yrs[1:]):
        if a <= year <= b:
            f = (year - a) / (b - a)
            return (GRID_INTENSITY_ANCHORS[a]
                    + f * (GRID_INTENSITY_ANCHORS[b] - GRID_INTENSITY_ANCHORS[a]))
    return GRID_INTENSITY_ANCHORS[yrs[-1]]


def annual_petrojam_price(year, grade="Gasolene 90"):
    """
    Mean Petrojam ex-refinery price for a calendar year from the loaded series.
    Returns None if that year is not covered, so callers must handle the gap
    rather than silently extrapolating.
    """
    try:
        sub = fuel_df[fuel_df["Date"].dt.year == int(year)]
        if sub.empty:
            return None
        return float(sub[grade].mean())
    except Exception:
        return None


# Average battery pack size assumed for a private fleet BEV, used to price the
# manufacturing debt of a counterfactual fleet. Taken as the mean pack size of
# the BEVs in data/vehicles.py that are plausible private purchases.
FLEET_AVG_BATTERY_KWH = 55.0
FLEET_BATTERY_ORIGIN = "china"   # BYD is the dominant new EV brand in Jamaica


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
    Input("m4-private-ev-consumption", "value"),
    Input("m4-private-steepness", "value"),
    Input("m4-private-midpoint", "value"),
    Input("m4-public-fleet-size", "value"),
    Input("m4-public-km-per-year", "value"),
    Input("m4-public-consumption", "value"),
    Input("m4-public-ev-consumption", "value"),
    Input("m4-public-steepness", "value"),
    Input("m4-public-midpoint", "value"),
    Input("m4-goj-fleet-size", "value"),
    Input("m4-goj-km-per-year", "value"),
    Input("m4-goj-consumption", "value"),
    Input("m4-goj-ev-consumption", "value"),
    Input("m4-goj-steepness", "value"),
    Input("m4-goj-midpoint", "value"),
)
def calculate_module4(horizon, grid_scenario,
                      priv_size, priv_km, priv_cons, priv_ev_cons, priv_steep, priv_mid,
                      pub_size, pub_km, pub_cons, pub_ev_cons, pub_steep, pub_mid,
                      goj_size, goj_km, goj_cons, goj_ev_cons, goj_steep, goj_mid):

    empty_fig = go.Figure()
    empty_fig.update_layout(
        plot_bgcolor="#ffffff", paper_bgcolor="#ffffff",
        xaxis={"visible": False}, yaxis={"visible": False},
        annotations=[{"text": "Adjust all inputs to see projections.",
                      "xref": "paper", "yref": "paper", "x": 0.5, "y": 0.5,
                      "showarrow": False, "font": {"size": 16, "color": "#aaa"}}],
    )
    required = [horizon, grid_scenario,
                priv_size, priv_km, priv_cons, priv_ev_cons, priv_steep, priv_mid,
                pub_size, pub_km, pub_cons, pub_ev_cons, pub_steep, pub_mid,
                goj_size, goj_km, goj_cons, goj_ev_cons, goj_steep, goj_mid]
    if not all(x is not None for x in required):
        return None, empty_fig, empty_fig, empty_fig

    from datetime import datetime
    current_year = datetime.now().year
    years = list(range(current_year, current_year + int(horizon) + 1))

    grid_intensity = GRID_SCENARIOS[grid_scenario]["intensity_kg_per_kwh"]

    streams = {
        "private": {"size": priv_size, "km": priv_km, "cons": priv_cons,
                    "ev_cons": priv_ev_cons, "co2_per_litre": CO2_PER_LITRE_PETROL,
                    "steep": priv_steep, "mid": priv_mid,
                    "target": FLEET_BASELINES["private"]["target_pct_2030"],
                    "label": "Private", "color": "#2E75B6"},
        "public":  {"size": pub_size, "km": pub_km, "cons": pub_cons,
                    "ev_cons": pub_ev_cons, "co2_per_litre": CO2_PER_LITRE_DIESEL,
                    "steep": pub_steep, "mid": pub_mid,
                    "target": FLEET_BASELINES["public"]["target_pct_2030"],
                    "label": "Public Transport", "color": "#C55A11"},
        "goj":     {"size": goj_size, "km": goj_km, "cons": goj_cons,
                    "ev_cons": goj_ev_cons, "co2_per_litre": CO2_PER_LITRE_PETROL,
                    "steep": goj_steep, "mid": goj_mid,
                    "target": FLEET_BASELINES["goj"]["target_pct_2030"],
                    "label": "GOJ", "color": "#1A9E75"},
    }

    for key, s in streams.items():
        s["penetration"] = [logistic_curve(y, current_year, s["mid"], s["steep"], s["target"])
                            for y in years]
        s["ev_count"] = [s["size"] * (p / 100) for p in s["penetration"]]
        # BUG FIX: all three streams previously used petrol combustion chemistry.
        # The public transport stream is JUTC buses, which run on diesel at
        # 2.68 kg CO2/litre, not 2.31. This understated the ICE baseline for
        # buses by 16%.
        ice_co2_per_veh = s["km"] * (s["cons"] / 100) * s["co2_per_litre"]
        # BUG FIX: this previously hardcoded 16.0 kWh/100km for all three streams,
        # including the public transport stream, which is buses. A full-size
        # electric bus uses roughly six times a passenger car, so the old code
        # materially overstated public transport CO2 savings. Each stream now
        # carries its own EV consumption figure.
        ev_kwh_per_year = s["km"] * (s["ev_cons"] / 100)
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
    big  = {"fontSize": "27px", "fontWeight": "700", "margin": "6px 0"}
    tiny = {"fontSize": "15px", "color": "#777", "margin": "0"}
    section_banner = {"backgroundColor": "#E1F5EE", "color": "#0E2A24",
                      "fontWeight": "700", "fontSize": "17px",
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
                   style={"fontSize": "16px", "margin": "6px 0", "color": "#333"}),
            html.P(gap_text, style={**big, "color": gap_color, "fontSize": "25px"}),
            html.P("gap to 2030 target", style={"fontSize": "12px", "color": "#888"}),
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
    fig_pen.update_layout(**chart_layout(
        "EV Penetration Projection by Fleet Stream",
        height=380, xtitle="Year", ytitle="EV share of fleet (%)",
        legend_rows=1, left=60,
    ))
    fig_pen.update_yaxes(ticksuffix="%")

    fig_co2 = go.Figure()
    for key, s in streams.items():
        cum, running = [], 0
        for v in s["annual_co2_saved_t"]:
            running += v
            cum.append(running)
        fig_co2.add_trace(go.Scatter(
            x=years, y=cum, mode="lines",
            name=s["label"],
            stackgroup="one",
            line=dict(color=s["color"], width=0),
            fillcolor=hex_to_rgba(s["color"], 0.5),
        ))
    fig_co2.update_layout(**chart_layout(
        "Cumulative CO2 Avoided (tonnes)",
        height=340, xtitle="Year", ytitle="CO2 avoided (t)",
        legend_rows=2,   # three "<stream> cumulative" entries wrap in a narrow panel
    ))

    fig_rev = go.Figure()
    for key, s in streams.items():
        cum_rev, running = [], 0
        for v in s["revenue_impact"]:
            running += v
            cum_rev.append(running / 1_000_000_000)
        fig_rev.add_trace(go.Scatter(
            x=years, y=cum_rev, mode="lines+markers",
            name=s["label"],
            line=dict(color=s["color"], width=2), marker=dict(size=5),
        ))
    fig_rev.update_layout(**chart_layout(
        "Government Revenue Foregone (J$ billions, cumulative)",
        height=340, xtitle="Year", ytitle="Revenue foregone (J$ bn)",
        legend_rows=1,   # names shortened to the stream label, so one row
    ))

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
                          "fontSize": "16px", "color": summary_color}),
            html.Ul(
                [html.Li(line, style={"fontSize": "16px", "color": summary_color})
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
            style={"fontSize": "16px", "color": "#888", "marginBottom": "16px"},
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
            # Was blue #2E75B6 against teal #1A7A6E, which is the blue/green
            # pairing Dr Harris flagged as hard to tell apart. Purple replaces
            # the teal: it separates cleanly from both the blue and the orange,
            # including for the most common forms of colour blindness.
            "Gasolene 87":  SERIES_COLOURS["blue"],
            "Gasolene 90":  SERIES_COLOURS["purple"],
            "Auto Diesel":  SERIES_COLOURS["orange"],
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
    latest = fuel_df["Date"].max()
    earliest = fuel_df["Date"].min()
    fig.update_layout(
        **chart_layout(
            f"Petrojam Weekly Pump Prices, Jamaica "
            f"({earliest:%d %b %Y} to {latest:%d %b %Y})",
            height=430, xtitle="Week", ytitle="Price (J$/litre)",
            left=80,
        ),
        legend_title_text="",
    )
    # Explicit dates rather than Plotly's automatic label thinning, which on a
    # ten-year weekly series can show bare years and leave the reader unable to
    # tell which week a point belongs to.
    fig.update_xaxes(tickformat="%b %Y", hoverformat="%d %b %Y")
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
    Input("m6-vehicle-select",     "value"),
    Input({"kind": "m6-dp",   "veh": ALL}, "value"),
    Input({"kind": "m6-rate", "veh": ALL}, "value"),
    Input({"kind": "m6-term", "veh": ALL}, "value"),
    Input("effective-fuel-price-store", "data"),
    Input("public-charging-rate",  "value"),
    Input("electricity-rate-slider", "value"),
)
def calculate_module6(
    trips_per_day, trip_km, fare, days_per_week, ownership_years,
    charging_scenario, custom_rate,
    selected, dp_values, rate_values, term_values,
    fuel_price, public_rate, home_rate,
):

    no_chart  = {"display": "none"}
    show_chart = {"display": "block"}
    show_ph   = {"color": "#aaa", "fontSize": "16px", "marginTop": "40px", "textAlign": "center"}
    hide_ph   = {"display": "none"}

    required = [trips_per_day, trip_km, fare, days_per_week, fuel_price, public_rate]
    if not all(r is not None for r in required):
        return go.Figure(), no_chart, show_ph, None, None

    selected = [k for k in (selected or []) if k in TAXI_VEHICLES]
    if not selected:
        return (go.Figure(), no_chart,
                {**show_ph, "color": "#C0392B"},
                html.P("Select at least one vehicle to compare.",
                       style={"color": "#C0392B", "fontSize": "16px"}),
                None)

    # Recover the vehicle key for each pattern-matched input from the callback
    # context rather than assuming positional order matches TAXI_VEHICLES.
    def _by_veh(kind, values):
        out = {}
        for group in dash.callback_context.inputs_list:
            if not isinstance(group, list):
                continue
            for i, spec in enumerate(group):
                if isinstance(spec.get("id"), dict) and spec["id"].get("kind") == kind:
                    out[spec["id"]["veh"]] = spec.get("value")
        return out

    dp_by_veh   = _by_veh("m6-dp",   dp_values)
    rate_by_veh = _by_veh("m6-rate", rate_values)
    term_by_veh = _by_veh("m6-term", term_values)

    # Annual volumes
    km_per_year      = trips_per_day * trip_km * days_per_week * 52
    trips_per_year   = trips_per_day * days_per_week * 52
    revenue_per_year = trips_per_year * fare

    # EV effective charging rate
    if charging_scenario == "home":
        # Feedback item 18. An owner-driver who charges at home overnight pays
        # the JPS residential tariff, not a public network rate. This is the
        # cheapest option available to a single-vehicle operator and was missing
        # from this module entirely.
        ev_rate = home_rate if home_rate else public_rate
        charging_note = (f"Home charging at the JPS residential rate of "
                         f"J${ev_rate}/kWh. Assumes an owner-driver who can "
                         f"charge overnight at their own premises.")
    elif charging_scenario == "public":
        ev_rate = public_rate
        charging_note = f"Public charging only at J${public_rate}/kWh."
    elif charging_scenario in ("jps_offpeak", "jps_day", "jps_peak"):
        # JPS time-of-use. Overnight is how a depot-based taxi fleet would
        # actually charge; evening peak is the worst case a driver topping up
        # mid-shift would face.
        net = CHARGING_NETWORKS[charging_scenario]
        ev_rate = net["rate"]
        band = {"jps_offpeak": "overnight 22:00-06:00",
                "jps_day": "daytime 06:00-18:00",
                "jps_peak": "evening peak 18:00-22:00"}[charging_scenario]
        charging_note = (f"JPS Charge 'n Go {band} at J${ev_rate}/kWh "
                         f"({ev_rate / 96.0 - 1:+.0%} vs Evergo flat J$96).")
    else:
        # Covers "custom" and any unrecognised value. The old "Fleet HQ" and
        # "Mix" scenarios were removed: both were built on a guessed J$60/kWh
        # commercial rate that was never confirmed with JPS. The depot-charging
        # case they existed to model is now covered by JPS overnight at a real,
        # published J$50.11/kWh, which is cheaper than the guess anyway.
        ev_rate = custom_rate if custom_rate else public_rate
        charging_note = f"Custom rate J${ev_rate}/kWh."

    # Per-vehicle loan params, falling back to each vehicle's class defaults
    loan_params = {}
    for key in selected:
        d_dp, d_rate, d_term = TAXI_VEHICLES[key]["loan_defaults"]
        loan_params[key] = (
            dp_by_veh.get(key)   if dp_by_veh.get(key)   is not None else d_dp,
            rate_by_veh.get(key) if rate_by_veh.get(key) is not None else d_rate,
            term_by_veh.get(key) if term_by_veh.get(key) is not None else d_term,
        )

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
    for key in selected:
        v = TAXI_VEHICLES[key]
        price = v.get("price_jmd")
        if not price:
            continue
        dp_pct, lr, lt = loan_params[key]
        downpayment     = price * (dp_pct / 100)
        monthly_payment = pmt(price - downpayment, lr, lt)

        # Consumption is urban-basis for every vehicle in this module.
        rate = fuel_price if v["type"] == "ICE" else ev_rate
        energy_cost_per_km = (v["consumption_urban"] / 100) * rate

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
            "colour": v["colour"],
            "symbol": v["symbol"],
            "measured": v["consumption_measured"],
            "consumption_source": v["consumption_source"],
            "notes": v["notes"],
            "loan_term_years": lt,
        }

    if not results:
        return (go.Figure(), no_chart, show_ph,
                html.P("No price on record for the selected vehicles.",
                       style={"color": "#C0392B", "fontSize": "16px"}), None)

    ordered = [k for k in TAXI_VEHICLES if k in results]

    # ── Vehicle summary cards ──
    card = {"backgroundColor": "#ffffff", "border": "1px solid #e0e0e0",
            "borderRadius": "6px", "padding": "12px 14px",
            "flex": "1", "minWidth": "130px", "textAlign": "center"}
    big  = {"fontSize": "22px", "fontWeight": "700", "margin": "4px 0"}
    tiny = {"fontSize": "15px", "color": "#777", "margin": "0"}

    vehicle_rows = []
    for key in ordered:
        r = results[key]
        annual_net = revenue_per_year - (r["annual_energy_cost"] + r["annual_maintenance"] + r["annual_loan_payment"])
        net_color  = "#1A9E75" if annual_net > 0 else "#C0392B"
        type_color = r["colour"]
        vehicle_rows.append(html.Div([
            html.Div([
                html.Span(r["label"], style={"fontWeight": "700", "fontSize": "16px", "color": type_color}),
                html.Span("  consumption derived, not measured" if not r["measured"] else "",
                          style={"fontSize": "14px", "color": "#C0392B", "fontWeight": "600"}),
                html.Br(),
                html.Span(r["consumption_source"], style={"fontSize": "12px", "color": "#999"}),
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
            style={"fontSize": "15px", "color": "#555", "marginBottom": "10px"},
        ),
        *vehicle_rows,
    ])

    # ── Multi-year cumulative income chart ──
    years     = int(ownership_years) if ownership_years else 5
    year_list = list(range(0, years + 1))
    fig       = go.Figure()
    trajectories = {}

    for key in ordered:
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
            line=dict(color=r["colour"], width=2,
                      dash="solid" if r["measured"] else "dot"),
            marker=dict(size=9, symbol=r["symbol"],
                        line=dict(color="#FFFFFF", width=1)),
        ))

    def find_crossover(ev_traj, ice_traj):
        for i in range(1, len(year_list)):
            prev_diff = ev_traj[i-1] - ice_traj[i-1]
            curr_diff = ev_traj[i]   - ice_traj[i]
            if prev_diff < 0 and curr_diff >= 0:
                frac = prev_diff / (prev_diff - curr_diff)
                return (i - 1) + frac
        return None

    # The ICE baseline is the first selected ICE vehicle in display order.
    # Every selected EV is measured against it.
    ice_keys = [k for k in ordered if results[k]["type"] == "ICE"]
    ev_keys  = [k for k in ordered if results[k]["type"] == "EV"]
    baseline_key = ice_keys[0] if ice_keys else None

    crossovers = {}
    if baseline_key:
        for k in ev_keys:
            crossovers[k] = find_crossover(trajectories[k], trajectories[baseline_key])

        # Annotate only the earliest crossover to avoid the overlapping-label
        # problem that appears once more than two vehicles are selected.
        reached = {k: c for k, c in crossovers.items()
                   if c is not None and c <= years}
        if reached:
            first_k = min(reached, key=reached.get)
            fig.add_vline(
                x=reached[first_k], line_dash="dash",
                line_color=results[first_k]["colour"],
                annotation_text=f"{results[first_k]['label'].split('(')[0].strip()} overtakes",
                annotation_position="top",
                annotation_font_color=results[first_k]["colour"],
                annotation_font_size=10,
            )

    fig.add_hline(y=0, line_dash="dot", line_color="#888",
                  annotation_text="Break-even", annotation_position="top left",
                  annotation_font_size=10)
    fig.update_layout(
        # Vehicle labels are long and this module can plot up to eleven of them,
        # so the legend row count has to scale with the selection. Roughly two
        # labels fit per row in the right-hand panel.
        **chart_layout(
            f"Cumulative driver net income over {years} years (J$ millions)",
            height=440 + max(0, len(ordered) - 4) * 14,
            xtitle="Year", ytitle="Cumulative net income (J$ millions)",
            legend_rows=max(1, math.ceil(len(ordered) / 2)),
            left=60,
        )
    )
    fig.update_xaxes(dtick=1)

    # ── Crossover cards ──
    baseline_label = (results[baseline_key]["label"].split("(")[0].strip()
                      if baseline_key else "the ICE baseline")

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
            sub_text    = f"EV cumulative net income first exceeds {baseline_label}."
            value_color = ev_color
        return html.Div([
            html.P(label,      style={"fontSize": "15px", "color": "#777", "margin": "0 0 4px"}),
            html.P(value_text, style={"fontSize": "25px", "fontWeight": "700",
                                      "color": value_color, "margin": "4px 0"}),
            html.P(sub_text,   style={"fontSize": "14px", "color": "#888", "margin": "4px 0 0"}),
        ], style={"backgroundColor": "#ffffff", "border": "1px solid #e0e0e0",
                  "borderRadius": "6px", "padding": "14px 18px",
                  "flex": "1", "minWidth": "200px", "textAlign": "center"})

    if not baseline_key:
        crossover_cards = html.P(
            "Select at least one ICE vehicle to get a crossover comparison. "
            "Crossover is measured against an ICE baseline.",
            style={"fontSize": "15px", "color": "#C0392B", "marginTop": "8px"})
    elif not ev_keys:
        crossover_cards = html.P(
            "Select at least one EV to get a crossover comparison.",
            style={"fontSize": "15px", "color": "#C0392B", "marginTop": "8px"})
    else:
        crossover_cards = html.Div([
            html.P(f"When does each EV overtake the {baseline_label}?",
                   style={"fontWeight": "700", "fontSize": "17px", "marginBottom": "8px",
                          "color": "#0E2A24"}),
            html.Div([
                crossover_card(
                    results[k]["label"].split("(")[0].strip() + f" vs {baseline_label}",
                    crossovers[k], results[k]["colour"])
                for k in ev_keys
            ], style={"display": "flex", "gap": "10px", "flexWrap": "wrap"}),
            html.P(
                "Crossover is when cumulative EV net income first exceeds the ICE "
                "baseline. Where more than one ICE vehicle is selected, the first in "
                "the list is used as the baseline and the others are plotted for "
                "comparison. Dotted lines on the chart mark vehicles whose consumption "
                "is derived rather than measured.",
                style={"fontSize": "14px", "color": "#888", "marginTop": "8px"}),
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


def _m6_loan_wrap_style(visible):
    base = {"backgroundColor": "#fafafa", "border": "1px solid #e0e0e0",
            "borderRadius": "4px", "padding": "10px 14px", "marginBottom": "8px"}
    return base if visible else {**base, "display": "none"}


@app.callback(
    Output({"kind": "m6-loan-wrap", "veh": ALL}, "style"),
    Input("m6-vehicle-select", "value"),
)
def toggle_m6_loan_blocks(selected):
    """Show a vehicle's loan inputs only while it is in the comparison set."""
    selected = set(selected or [])
    return [_m6_loan_wrap_style(spec["id"]["veh"] in selected)
            for spec in dash.callback_context.outputs_list]


# Two MATCH callbacks replace the twelve per-vehicle sync callbacks that this
# module would otherwise need at eleven vehicles. MATCH fires once per vehicle
# whose input or slider changed, keeping the pair in step without knowing which
# vehicles exist.
@app.callback(
    Output({"kind": "m6-rate",        "veh": MATCH}, "value"),
    Output({"kind": "m6-rate-slider", "veh": MATCH}, "value"),
    Input({"kind": "m6-rate",         "veh": MATCH}, "value"),
    Input({"kind": "m6-rate-slider",  "veh": MATCH}, "value"),
    prevent_initial_call=True,
)
def sync_m6_rate(inp_val, slider_val):
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update, dash.no_update
    if '"kind":"m6-rate"' in ctx.triggered[0]["prop_id"].replace(" ", ""):
        return dash.no_update, inp_val
    return slider_val, dash.no_update


@app.callback(
    Output({"kind": "m6-term",        "veh": MATCH}, "value"),
    Output({"kind": "m6-term-slider", "veh": MATCH}, "value"),
    Input({"kind": "m6-term",         "veh": MATCH}, "value"),
    Input({"kind": "m6-term-slider",  "veh": MATCH}, "value"),
    prevent_initial_call=True,
)
def sync_m6_term(inp_val, slider_val):
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update, dash.no_update
    if '"kind":"m6-term"' in ctx.triggered[0]["prop_id"].replace(" ", ""):
        return dash.no_update, inp_val
    return slider_val, dash.no_update


@app.callback(
    Output("m4-fleet-emissions-cards", "children"),
    Output("m4-fleet-emissions-fig",   "figure"),
    Input("m4-fleet-emissions-mode",   "value"),
    Input("m4-fleet-penetration",      "value"),
    Input("m4-fleet-include-mfg",      "value"),
    Input("m4-private-fleet-size",     "value"),
    Input("m4-private-km-per-year",    "value"),
    Input("m4-private-consumption",    "value"),
    Input("m4-private-ev-consumption", "value"),
)
def calculate_m4_fleet_emissions(mode, penetration, include_mfg,
                                 fleet_now, km_per_year, ice_cons, ev_cons):
    """
    Counterfactual emissions for the Jamaican private vehicle fleet at an
    arbitrary EV penetration, looking either backwards or forwards.

    Backwards uses the real Petrojam 90-octane series to value the fuel that
    would not have been bought. Forwards holds the current real fuel price flat,
    because this project has no defensible fuel price forecast.
    """
    empty = go.Figure()
    empty.update_layout(
        plot_bgcolor="#ffffff", paper_bgcolor="#ffffff",
        xaxis={"visible": False}, yaxis={"visible": False},
        annotations=[{"text": "Adjust the inputs to see the counterfactual.",
                      "xref": "paper", "yref": "paper", "x": 0.5, "y": 0.5,
                      "showarrow": False, "font": {"size": 16, "color": "#aaa"}}],
    )
    if not all(x is not None for x in [mode, penetration, fleet_now,
                                       km_per_year, ice_cons, ev_cons]):
        return None, empty

    share = penetration / 100.0
    fleet_2015 = FLEET_BASELINES["private"]["size_2015"]

    if mode == "back":
        years = list(range(2015, 2027))
        # Linear interpolation between the 2015 CEIC/OICA anchor and the
        # current fleet estimate. The current estimate is itself a PLACEHOLDER.
        fleet_by_year = {
            y: fleet_2015 + (fleet_now - fleet_2015) * (y - 2015) / (2026 - 2015)
            for y in years
        }
        price_by_year = {y: annual_petrojam_price(y) for y in years}
        price_note = ("Fuel valued at the actual Petrojam 90-octane annual mean "
                      "for each year, ex-refinery.")
    else:
        years = list(range(2026, 2036))
        growth = 0.025   # same 2.5% assumption used for the current fleet estimate
        fleet_by_year = {y: fleet_now * ((1 + growth) ** (y - 2026)) for y in years}
        latest_price = annual_petrojam_price(2026) or latest_prices["g90"]
        price_by_year = {y: latest_price for y in years}
        price_note = (f"Fuel held flat at the 2026 Petrojam 90-octane mean of "
                      f"J${latest_price:,.2f}/litre. This project has no "
                      f"defensible fuel price forecast, so no trend is assumed.")

    # Per-year quantities
    ice_only_co2, mixed_co2, litres_saved, fuel_value_saved = [], [], [], []
    missing_price_years = []

    for y in years:
        fleet = fleet_by_year[y]
        gi = grid_intensity_for_year(y)

        litres_full = fleet * km_per_year * (ice_cons / 100.0)
        co2_full = litres_full * CO2_PER_LITRE_PETROL / 1000.0   # tonnes

        ev_count = fleet * share
        ice_count = fleet - ev_count
        co2_ice_part = (ice_count * km_per_year * (ice_cons / 100.0)
                        * CO2_PER_LITRE_PETROL / 1000.0)
        co2_ev_part = (ev_count * km_per_year * (ev_cons / 100.0)
                       * gi / 1000.0)

        ice_only_co2.append(co2_full)
        mixed_co2.append(co2_ice_part + co2_ev_part)

        l_saved = ev_count * km_per_year * (ice_cons / 100.0)
        litres_saved.append(l_saved)
        p = price_by_year[y]
        if p is None:
            missing_price_years.append(y)
            fuel_value_saved.append(0.0)
        else:
            fuel_value_saved.append(l_saved * p)

    # One-off manufacturing debt for the EV portion of the fleet, charged at the
    # start of the period. This is the full cradle-to-gate battery premium, not
    # the amortised used-vehicle figure, because these are vehicles being newly
    # built somewhere in the world to satisfy the counterfactual.
    intensity = BATTERY_PRODUCTION_CO2_KG_PER_KWH[FLEET_BATTERY_ORIGIN]
    ev_fleet_peak = max(fleet_by_year[y] for y in years) * share
    mfg_debt_t = ev_fleet_peak * FLEET_AVG_BATTERY_KWH * intensity / 1000.0
    if include_mfg != "yes":
        mfg_debt_t = 0.0

    cum_avoided = []
    running = -mfg_debt_t
    for i in range(len(years)):
        running += ice_only_co2[i] - mixed_co2[i]
        cum_avoided.append(running)

    total_gross_avoided = sum(a - b for a, b in zip(ice_only_co2, mixed_co2))
    total_net_avoided = total_gross_avoided - mfg_debt_t
    total_litres = sum(litres_saved)
    total_value = sum(fuel_value_saved)

    # Years to pay back the manufacturing debt
    payback_year = None
    for i, v in enumerate(cum_avoided):
        if v >= 0:
            payback_year = years[i]
            break

    # ── Cards ──
    card = {"backgroundColor": "#ffffff", "border": "1px solid #e0e0e0",
            "borderRadius": "6px", "padding": "14px 16px",
            "flex": "1", "minWidth": "160px", "textAlign": "center"}
    big  = {"fontSize": "25px", "fontWeight": "700", "margin": "6px 0"}
    tiny = {"fontSize": "15px", "color": "#777", "margin": "0"}

    period = f"{years[0]} to {years[-1]}"
    net_col = "#2d8a2d" if total_net_avoided > 0 else "#C0392B"

    cards = html.Div([
        html.P(
            f"At {penetration}% private fleet electrification over {period}: "
            f"{ev_fleet_peak:,.0f} electric vehicles at peak.",
            style={"fontSize": "15px", "color": "#555", "marginBottom": "10px"},
        ),
        html.Div([
            html.Div([html.P("Gross CO2 avoided", style=tiny),
                      html.P(f"{total_gross_avoided/1000:,.0f} kt",
                             style={**big, "color": "#1A7A6E"})], style=card),
            html.Div([html.P("Battery manufacturing debt", style=tiny),
                      html.P(f"{mfg_debt_t/1000:,.0f} kt",
                             style={**big, "color": "#C55A11"})], style=card),
            html.Div([html.P("Net CO2 avoided", style=tiny),
                      html.P(f"{total_net_avoided/1000:,.0f} kt",
                             style={**big, "color": net_col})], style=card),
            html.Div([html.P("Petrol not burned", style=tiny),
                      html.P(f"{total_litres/1e6:,.0f} M litres",
                             style={**big, "color": "#1F3864"})], style=card),
            html.Div([html.P("Fuel spend avoided", style=tiny),
                      html.P(f"J${total_value/1e9:,.1f} bn",
                             style={**big, "color": "#1F3864"})], style=card),
            html.Div([html.P("Manufacturing debt repaid", style=tiny),
                      html.P(str(payback_year) if payback_year else "not within period",
                             style={**big, "color": "#2d8a2d" if payback_year else "#C0392B",
                                    "fontSize": "20px"})], style=card),
        ], style={"display": "flex", "gap": "8px", "flexWrap": "wrap"}),
        html.P(
            price_note + " "
            + ("Jamaica's electricity was dirtier before 2022 than the figure used "
               "here, so the carbon dioxide avoided shown is towards the optimistic "
               "end. "
               if mode == "back" else
               "Electricity is assumed to get cleaner towards 2030, in line with the "
               "national target. ")
            + ("The emissions of building the batteries are included. "
               if include_mfg == "yes" else
               "Battery manufacturing is EXCLUDED, so these figures flatter the "
               "electric case. "),
            style={"fontSize": "14px", "color": "#888", "marginTop": "10px"},
        ),
    ])

    # ── Chart ──
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=years, y=[v / 1000 for v in ice_only_co2], mode="lines+markers",
        name="100% ICE fleet (baseline)",
        line=dict(color=SERIES_COLOURS["ice"], width=2), marker=dict(size=6),
    ))
    fig.add_trace(go.Scatter(
        x=years, y=[v / 1000 for v in mixed_co2], mode="lines+markers",
        # This chart previously ran teal, blue and a second green together.
        # The EV line now uses the standard EV green so it matches every other
        # module, and the two remaining series move to purple and amber, well
        # clear of both the green and each other.
        name=f"{penetration}% EV fleet",
        line=dict(color=SERIES_COLOURS["ev"], width=2), marker=dict(size=6),
        fill="tonexty", fillcolor="rgba(26,158,117,0.15)",
    ))
    fig.add_trace(go.Scatter(
        x=years, y=[v / 1000 for v in cum_avoided], mode="lines",
        name="Cumulative net avoided (incl. mfg)",
        line=dict(color=SERIES_COLOURS["purple"], width=2, dash="dash"),
        yaxis="y2",
    ))
    if payback_year and include_mfg == "yes":
        fig.add_vline(x=payback_year, line_dash="dot",
                      line_color=SERIES_COLOURS["amber"],
                      annotation_text=f"Battery debt repaid {payback_year}",
                      annotation_position="top left",
                      annotation_font_color=SERIES_COLOURS["amber"],
                      annotation_font_size=12)
    # dtick=1 forced all twelve year labels into a narrow panel, which made
    # Plotly angle them. Angled labels are taller than upright ones and pushed
    # the x-axis title down into the legend. Letting Plotly choose the tick
    # spacing keeps the labels upright and the spacing predictable.
    fig.update_layout(**chart_layout(
        f"Private fleet CO2 at {penetration}% electrification, {period}",
        height=380, xtitle="Year", ytitle="Annual fleet CO2 (kt)",
        y2title="Net avoided (kt)",
        legend_rows=3, left=60, right=60, tickangle=0,
    ))
    return cards, fig


# Short operator name per network key, used to label the rate box so it never
# says the generic "public charging rate" while holding one operator's price.
CHARGING_NETWORK_SHORT_NAME = {
    "evergo":      "Evergo",
    "jps_offpeak": "JPS Charge 'n Go, overnight",
    "jps_day":     "JPS Charge 'n Go, daytime",
    "jps_peak":    "JPS Charge 'n Go, evening peak",
}


@app.callback(
    Output("public-charging-rate", "value"),
    Output("public-charging-rate-label", "children"),
    Output("charging-network-note", "children"),
    Output("charging-network-note", "style"),
    Input("charging-network-select", "value"),
    prevent_initial_call=True,
)
def apply_charging_network(network_key):
    """
    Set the public charging rate and its label from the chosen network.

    Where a network's rate is not yet known, the rate box is left as the user
    left it and the note turns red asking for the figure, rather than silently
    substituting a made-up number.
    """
    net = CHARGING_NETWORKS.get(network_key)
    base = {"fontSize": "12px", "marginTop": "4px", "maxWidth": "260px"}
    short = CHARGING_NETWORK_SHORT_NAME.get(network_key, "Public")
    label = f"{short} rate (J$/kWh)"
    if net is None:
        return dash.no_update, label, "", base
    if net["rate"] is None:
        return (dash.no_update, label,
                "Rate not on file. " + net["note"],
                {**base, "color": "#C0392B", "fontWeight": "600"})
    return net["rate"], label, net["note"], {**base, "color": "#888"}


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
               style={"fontSize": "21px", "fontWeight": "700", "color": "#0E2A24",
                      "margin": "0 0 4px"}),
        html.P(info["summary"],
               style={"fontSize": "16px", "color": "#444", "margin": "0 0 4px",
                      "lineHeight": "1.5"}),
        html.P(["How to use: ", html.Em(info["how"])],
               style={"fontSize": "15px", "color": "#666", "margin": "0",
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
    # Debug mode is OFF unless you explicitly ask for it.
    #
    # This matters for more than speed. With debug=True Dash exposes an
    # interactive Python console on the error page, so anyone who can make the
    # app raise an exception can run arbitrary code on the host. That is fine
    # on your laptop and unacceptable on the UWI server.
    #
    #   Development (auto-reload on save, interactive errors):
    #       set EVLAB_DEBUG=1     (Windows)   then  python dashboard/app.py
    #       EVLAB_DEBUG=1 python dashboard/app.py        (macOS/Linux)
    #
    #   Production: do NOT run this file directly. Use a real WSGI server
    #   against the `server` object exposed at the top of this module:
    #       gunicorn -w 4 -b 0.0.0.0:8050 dashboard.app:server
    #   Four workers give roughly four times the throughput of this one.
    debug = os.environ.get("EVLAB_DEBUG", "").strip() in ("1", "true", "True")
    if debug:
        print("[startup] DEBUG MODE ON - do not use this on a public server")
    app.run(debug=debug, port=8050)
