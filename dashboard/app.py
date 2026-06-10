import dash
from dash import dcc, html, Input, Output

app = dash.Dash(
    __name__,
    title="Jamaica EV Dashboard — UWI Mona",
    suppress_callback_exceptions=True
)
server = app.server  # Expose the Flask server for deployment on UWI server

# ── Layout ────────────────────────────────────────────────────────
app.layout = html.Div([

    # Header
    html.Div([
        html.H1("Jamaica EV & Hybrid Vehicle Dashboard",
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

            html.Label("Fuel price (J$/litre)", style={"fontSize": "13px", "fontWeight": "500"}),
            dcc.Slider(
                id="fuel-price-slider",
                min=150, max=280, step=5, value=210,
                marks={150: "150", 210: "210", 280: "280"},
                tooltip={"placement": "bottom", "always_visible": False}
            ),
            html.Div(id="fuel-price-display",
                     style={"fontSize": "12px", "color": "#555", "marginBottom": "20px"}),

            html.Label("JPS electricity rate (J$/kWh)", style={"fontSize": "13px", "fontWeight": "500"}),
            dcc.Slider(
                id="electricity-rate-slider",
                min=30, max=80, step=1, value=50,
                marks={30: "30", 50: "50", 80: "80"},
                tooltip={"placement": "bottom", "always_visible": False}
            ),
            html.Div(id="electricity-rate-display",
                     style={"fontSize": "12px", "color": "#555", "marginBottom": "20px"}),

            html.Hr(style={"borderColor": "#ddd"}),
            html.P("These controls update all modules simultaneously.",
                   style={"fontSize": "11px", "color": "#888", "marginTop": "8px"}),

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


MODULE_INFO = {
    "tab-1": ("EV / Hybrid vs. ICE Calculator",   "Week 2",   "#2E75B6"),
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
            "fontSize": "13px"
        }),
        html.P(
            "Module content will be built in accordance with the project timeline. "
            "Use the sidebar sliders to verify that global state is working correctly — "
            "the active settings panel above should update across all tabs.",
            style={"color": "#777", "fontSize": "13px", "marginTop": "20px"}
        )
    ])


# ── Run ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=True, port=8050)
