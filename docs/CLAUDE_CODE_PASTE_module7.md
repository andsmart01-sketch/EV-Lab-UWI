You are helping with an active research project. Here is all the context you need.

---

## PROJECT CONTEXT

- Repo root: C:\Users\Andrew Smart\ev-lab-repo
- Python environment: conda EVlab (Python 3.11)
- Framework: Dash 4.2.0
- Run command: python dashboard/app.py (from repo root, in CMD with conda activate EVlab)
- Dashboard at http://localhost:8050
- Import rule: in app.py, use `from data_loader import ...` NOT `from dashboard.data_loader import ...`
  because running `python dashboard/app.py` adds dashboard/ to sys.path directly.

Existing dashboard structure:
- dashboard/app.py -- main Dash app, already has Module 1 (BEV vs ICE Calculator)
  and Module 3 (Price Tracker) built. Uses dcc.Tabs for navigation.
- dashboard/data_loader.py -- exposes load_fuel_prices() and get_latest_prices()
- data/vehicles.py -- vehicle database

---

## TASK

Integrate Module 7 (EV Policy and 2030 Target Progress Tracker) into the dashboard.

### Step 1: Create the file

Create a new file at:
  dashboard/module7_policy.py

Paste the following content exactly into that file:

```python
"""
Module 7: EV Policy & 2030 Target Progress Tracker
Jamaica National EV Policy (June 2023)
EV Lab Research Project -- UWI Mona, 2026

Parts:
  A: Visual tracker of Jamaica's three 2030 targets.
     Current values are PENDING -- set DATA_PENDING = False and fill
     TARGETS[*]["current_pct"] once MSETT registration data arrives.
  B: Colour-coded table of all 22 implementation actions.
  C: Gap summary panel.

Source:
  Government of Jamaica. (2023). National electric vehicle policy. MSETT.
  https://msettjamaica.gov.jm/electric-vehicle-policy/
"""

from dash import dcc, html
import plotly.graph_objects as go

# -----------------------------------------------------------------------
# TOGGLE: set to False once MSETT data is received and current_pct filled
# -----------------------------------------------------------------------
DATA_PENDING = True

# -----------------------------------------------------------------------
# DATA: 2030 Targets
# current_pct: leave as None while DATA_PENDING = True.
# Fill in real figures from MSETT and set DATA_PENDING = False.
# -----------------------------------------------------------------------

TARGETS = [
    {
        "label": "Private EV Fleet",
        "target_pct": 12,
        "current_pct": None,
        "unit": "% of privately owned fleet",
        "source": "MSETT fleet registry -- data request pending"
    },
    {
        "label": "Public Transport EV Fleet",
        "target_pct": 16,
        "current_pct": None,
        "unit": "% of public transport fleet",
        "source": "MSETT / Transport Authority -- data request pending"
    },
    {
        "label": "GOJ Fleet",
        "target_pct": 100,
        "current_pct": None,
        "unit": "% of Government of Jamaica fleet",
        "source": "MSETT -- data request pending"
    },
]

# -----------------------------------------------------------------------
# DATA: 22 Policy Implementation Actions
# -----------------------------------------------------------------------

ACTIONS = [
    # Goal 1
    {"goal": 1, "action": "Set technical requirements to import EVs",
     "agencies": "MSETT, TBL", "timeline": "< 6 months", "deadline": "Dec 2023",
     "status": "Not confirmed", "notes": "No published standard located."},
    {"goal": 1, "action": "Standardise technical information requirements for EV import",
     "agencies": "MSETT, TBL", "timeline": "< 6 months", "deadline": "Dec 2023",
     "status": "Not confirmed", "notes": ""},
    {"goal": 1, "action": "Develop battery labelling system",
     "agencies": "MSETT, NEPA, MIIC", "timeline": "1 year", "deadline": "Jun 2024",
     "status": "Not confirmed", "notes": "No MSETT announcement found."},
    {"goal": 1, "action": "Publish EV import guidelines",
     "agencies": "MSETT, Jamaica Customs, TBL, MIIC", "timeline": "< 6 months",
     "deadline": "Dec 2023", "status": "Not confirmed", "notes": ""},
    {"goal": 1, "action": "Update EV inspection procedures",
     "agencies": "MSETT, TBL, MIIC", "timeline": "1 year", "deadline": "Jun 2024",
     "status": "Not confirmed", "notes": ""},
    {"goal": 1, "action": "Update private EV registration procedures",
     "agencies": "MSETT", "timeline": "1 year", "deadline": "Jun 2024",
     "status": "Partial", "notes": "TAJ processes EVs but no EV-specific fields confirmed."},
    # Goal 2
    {"goal": 2, "action": "Develop national EV charging deployment plan",
     "agencies": "MSETT, OUR", "timeline": "1-3 years", "deadline": "Jun 2026",
     "status": "Not confirmed", "notes": "No published national charging plan located."},
    {"goal": 2, "action": "Grid readiness assessment with JPS",
     "agencies": "MSETT, JPS", "timeline": "1-3 years", "deadline": "Jun 2026",
     "status": "Not confirmed", "notes": "JPS data request pending."},
    {"goal": 2, "action": "Publish EVSE technical and safety standards",
     "agencies": "MSETT, BSJ", "timeline": "1-3 years", "deadline": "Jun 2026",
     "status": "Not confirmed", "notes": "BSJ website does not list EV-specific standard."},
    {"goal": 2, "action": "Create public charging location information platform",
     "agencies": "MSETT", "timeline": "1-3 years", "deadline": "Jun 2026",
     "status": "Not confirmed", "notes": "No centralised official platform found."},
    # Goal 3
    {"goal": 3, "action": "Publish EVSE operating guidelines",
     "agencies": "MSETT, OUR", "timeline": "1-5 years", "deadline": "Jun 2028",
     "status": "Not confirmed", "notes": ""},
    {"goal": 3, "action": "Establish EVSE interoperability standard",
     "agencies": "MSETT, BSJ", "timeline": "1-5 years", "deadline": "Jun 2028",
     "status": "Not confirmed", "notes": "Multiple private networks; compatibility unconfirmed."},
    # Goal 4
    {"goal": 4, "action": "Battery collection and transport regulation",
     "agencies": "MSETT, NEPA, NSWMA", "timeline": "1-3 years", "deadline": "Jun 2026",
     "status": "Not confirmed", "notes": "NSWMA mandate does not list EV batteries."},
    {"goal": 4, "action": "Battery re-use and repurposing guidelines",
     "agencies": "MSETT, NEPA, NSWMA", "timeline": "1-3 years", "deadline": "Jun 2026",
     "status": "Not confirmed", "notes": ""},
    {"goal": 4, "action": "Battery recycling and disposal procedures",
     "agencies": "MSETT, NEPA, NSWMA", "timeline": "1-3 years", "deadline": "Jun 2026",
     "status": "Not confirmed", "notes": ""},
    {"goal": 4, "action": "Establish Authorised Treatment Facilities (ATFs)",
     "agencies": "MSETT, MEGJC, NEPA, NSWMA", "timeline": "1-3 years", "deadline": "Jun 2026",
     "status": "Not confirmed", "notes": "No certified ATF identified. Critical gap."},
    {"goal": 4, "action": "Battery status assessment system",
     "agencies": "MSETT, NEPA, NSWMA", "timeline": "3-5 years", "deadline": "Jun 2028",
     "status": "Not started (est.)", "notes": ""},
    # Goal 5
    {"goal": 5, "action": "Certification programme for EV mechanics and technicians",
     "agencies": "MSETT, MEGJC, MOEY, Universities", "timeline": "< 6 months",
     "deadline": "Dec 2023", "status": "Not confirmed",
     "notes": "HEART/NSTA does not list EV programme."},
    {"goal": 5, "action": "First responder EV certification (police, firefighters)",
     "agencies": "MSETT, MEGJC, MOEY, Universities", "timeline": "2-3 years",
     "deadline": "Jun 2026", "status": "Not confirmed", "notes": ""},
    {"goal": 5, "action": "Establish EV Skill Centers",
     "agencies": "MSETT, MEGJC", "timeline": "1-3 years", "deadline": "Jun 2026",
     "status": "Not confirmed", "notes": ""},
    # Goal 6
    {"goal": 6, "action": "National EV awareness communication campaigns",
     "agencies": "MSETT, MOEY, Universities", "timeline": "1-3 years", "deadline": "Jun 2026",
     "status": "Partial", "notes": "Some MSETT social media. No formal campaign confirmed."},
    {"goal": 6, "action": "Parking incentives for EV users",
     "agencies": "MSETT, MFPS", "timeline": "< 6 months", "deadline": "Dec 2023",
     "status": "Not confirmed", "notes": "Some informal reserved bays at private locations."},
    {"goal": 6, "action": "Designate Low Emission Zones",
     "agencies": "MSETT", "timeline": "1 year", "deadline": "Jun 2024",
     "status": "Not implemented", "notes": "No gazette notice found. Deadline missed."},
]

STATUS_COLORS = {
    "Confirmed":          "#2ecc71",
    "Partial":            "#f39c12",
    "Not confirmed":      "#e74c3c",
    "Not started (est.)": "#95a5a6",
    "Not implemented":    "#c0392b",
    "In progress":        "#3498db",
    "Pending data":       "#bdc3c7",
}


def build_progress_bars():
    fig = go.Figure()
    y_labels = [t["label"] for t in TARGETS]
    targets   = [t["target_pct"] for t in TARGETS]
    currents  = [t["current_pct"] for t in TARGETS]

    fig.add_trace(go.Bar(
        name="2030 Target",
        y=y_labels,
        x=targets,
        orientation="h",
        marker_color="rgba(52, 152, 219, 0.25)",
        marker_line=dict(color="rgba(52, 152, 219, 0.8)", width=2),
        text=[f"{t}% target" for t in targets],
        textposition="outside",
    ))

    if DATA_PENDING:
        fig.add_trace(go.Bar(
            name="Current (data pending)",
            y=y_labels,
            x=[0.0, 0.0, 0.0],
            orientation="h",
            marker_color="rgba(189, 195, 199, 0.6)",
            marker_line=dict(color="#95a5a6", width=1),
            text=["Pending MSETT data"] * 3,
            textposition="outside",
        ))
        note = (
            "Current penetration figures are PENDING. "
            "Set DATA_PENDING = False in module7_policy.py and fill current_pct "
            "once MSETT registration data is received."
        )
    else:
        fig.add_trace(go.Bar(
            name="Estimated Current",
            y=y_labels,
            x=currents,
            orientation="h",
            marker_color="rgba(46, 204, 113, 0.85)",
            text=[f"~{c}%" for c in currents],
            textposition="inside",
        ))
        note = "Source: MSETT fleet registry. Verify against STATIN transport data."

    fig.update_layout(
        title={"text": "Jamaica 2030 EV Fleet Penetration Targets vs Current Progress",
               "font": {"size": 15}},
        barmode="overlay",
        xaxis=dict(title="Percentage of Fleet", range=[0, 115], ticksuffix="%"),
        yaxis=dict(title=""),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        height=320,
        margin=dict(l=200, r=80, t=80, b=70),
        annotations=[dict(
            text=note, xref="paper", yref="paper",
            x=0, y=-0.25, showarrow=False,
            font=dict(size=11, color="#888888"), align="left"
        )]
    )
    return fig


def build_actions_table():
    cell_colors = [STATUS_COLORS.get(a["status"], "#cccccc") for a in ACTIONS]
    fig = go.Figure(data=[go.Table(
        columnwidth=[25, 200, 90, 130, 110, 170],
        header=dict(
            values=["<b>Goal</b>", "<b>Action</b>", "<b>Deadline</b>",
                    "<b>Agencies</b>", "<b>Status</b>", "<b>Notes</b>"],
            fill_color="#2c3e50",
            font=dict(color="white", size=12),
            align="left", height=36
        ),
        cells=dict(
            values=[
                [a["goal"]     for a in ACTIONS],
                [a["action"]   for a in ACTIONS],
                [a["deadline"] for a in ACTIONS],
                [a["agencies"] for a in ACTIONS],
                [a["status"]   for a in ACTIONS],
                [a["notes"]    for a in ACTIONS],
            ],
            fill_color=[
                ["#f8f9fa"] * len(ACTIONS),
                ["#f8f9fa"] * len(ACTIONS),
                ["#f8f9fa"] * len(ACTIONS),
                ["#f8f9fa"] * len(ACTIONS),
                cell_colors,
                ["#f8f9fa"] * len(ACTIONS),
            ],
            font=dict(color="#2c3e50", size=11),
            align="left", height=30
        )
    )])
    fig.update_layout(
        title={"text": "Policy Implementation Action Tracker (22 Actions)",
               "font": {"size": 14}},
        height=800, margin=dict(l=10, r=10, t=50, b=10)
    )
    return fig


def build_status_pie():
    from collections import Counter
    counts = Counter(a["status"] for a in ACTIONS)
    labels = list(counts.keys())
    values = list(counts.values())
    colors = [STATUS_COLORS.get(l, "#cccccc") for l in labels]
    fig = go.Figure(data=[go.Pie(
        labels=labels, values=values,
        marker=dict(colors=colors),
        hole=0.4, textinfo="label+value", hoverinfo="label+percent"
    )])
    fig.update_layout(
        title={"text": "Action Status Summary (22 Actions)", "font": {"size": 13}},
        height=320, margin=dict(l=10, r=10, t=50, b=10), showlegend=False
    )
    return fig


def build_module7_layout():
    pending_banner = html.Div(
        "DATA PENDING -- Current fleet penetration figures not yet available. "
        "Update DATA_PENDING in module7_policy.py once MSETT data is received.",
        style={
            "backgroundColor": "#ffeeba", "border": "1px solid #ffc107",
            "borderRadius": "4px", "padding": "10px 16px",
            "marginBottom": "18px", "fontSize": "13px", "color": "#856404"
        }
    ) if DATA_PENDING else html.Div()

    return html.Div([
        html.H4("Module 7: EV Policy and 2030 Target Progress Tracker",
                style={"marginBottom": "4px"}),
        html.P(
            "Source: Government of Jamaica. (2023). National electric vehicle policy. "
            "MSETT. https://msettjamaica.gov.jm/electric-vehicle-policy/",
            style={"fontSize": "11px", "color": "#888", "marginBottom": "14px"}
        ),
        pending_banner,
        html.H5("2030 Fleet Penetration Targets"),
        dcc.Graph(id="m7-progress-bars", figure=build_progress_bars(),
                  config={"displayModeBar": False}),
        html.Hr(),
        html.H5("Overall Implementation Status"),
        html.Div([
            dcc.Graph(id="m7-status-pie", figure=build_status_pie(),
                      config={"displayModeBar": False},
                      style={"width": "46%", "display": "inline-block",
                             "verticalAlign": "top"}),
            html.Div([
                html.H6("Colour Key", style={"marginBottom": "8px"}),
                html.Ul([
                    html.Li([
                        html.Span(style={
                            "display": "inline-block", "width": "13px", "height": "13px",
                            "backgroundColor": color, "marginRight": "8px",
                            "borderRadius": "2px", "verticalAlign": "middle"
                        }),
                        label
                    ], style={"listStyle": "none", "marginBottom": "5px", "fontSize": "12px"})
                    for label, color in STATUS_COLORS.items()
                ], style={"paddingLeft": "0"})
            ], style={"width": "50%", "display": "inline-block",
                      "verticalAlign": "top", "paddingLeft": "24px"})
        ]),
        html.Hr(),
        html.H5("All Policy Implementation Actions"),
        html.P(
            "Status reflects publicly available information as of June 2026. "
            "Table updates when institutional responses arrive.",
            style={"fontSize": "11px", "color": "#888", "marginBottom": "8px"}
        ),
        dcc.Graph(id="m7-actions-table", figure=build_actions_table(),
                  config={"displayModeBar": False}),
        html.Hr(),
        html.H5("Identified Policy Gaps"),
        html.Ul([
            html.Li("No publicly available Policy Implementation Plan (due September 2023)."),
            html.Li("No confirmed Authorised Treatment Facility for EV battery disposal."),
            html.Li("No national charging deployment plan published."),
            html.Li("No EVSE interoperability standard issued by the Bureau of Standards Jamaica."),
            html.Li("No Low Emission Zone designated -- 1-year deadline of June 2024 missed."),
            html.Li("No framework for used EV imports or minimum battery health thresholds."),
            html.Li("No producer responsibility scheme for battery end-of-life cost recovery."),
            html.Li("No public GOJ fleet electrification procurement schedule or budget line."),
            html.Li("No grid emissions disclosure requirement on JPS."),
        ], style={"lineHeight": "2.0", "fontSize": "13px"}),
        html.P("Full analysis: docs/ev_policy_gap_analysis.md",
               style={"fontSize": "11px", "color": "#888"})
    ], style={"padding": "20px"})
```

---

### Step 2: Wire it into app.py

Open dashboard/app.py. Make the following three changes.

**Change A -- add the import near the top of the file, with the other module imports:**
```python
from module7_policy import build_module7_layout
```

**Change B -- find the dcc.Tabs block where tabs are defined.**
It will look something like this (the exact label text may vary):
```python
dcc.Tab(label="Policy & Duties", value="tab-7"),
```
Make sure that tab exists. If it does not, add it to the tabs list in the same position as the other tabs.

**Change C -- find the tab content callback.**
It will have a pattern like:
```python
@app.callback(Output("tab-content", "children"), Input("tabs", "value"))
def render_tab(tab):
    if tab == "tab-1":
        return build_module1_layout()
    ...
```
Add this case to the if/elif chain:
```python
    elif tab == "tab-7":
        return build_module7_layout()
```

---

### Step 3: Verify

Run the dashboard:
```
python dashboard/app.py
```
Navigate to the Policy and Duties tab. You should see:
- A yellow "DATA PENDING" banner at the top
- A horizontal bar chart showing only the 2030 target bars (current bars show "Pending MSETT data")
- A pie chart showing action status distribution
- A colour-coded table of 22 implementation actions
- A gap summary list at the bottom

If you get an import error, check that module7_policy.py is in the dashboard/ folder,
not the repo root.

---

### When MSETT data arrives (future task)

Open dashboard/module7_policy.py and:
1. Set DATA_PENDING = False
2. Fill in current_pct for each entry in TARGETS with the real percentage figures
3. Save and restart the dashboard

The yellow banner will disappear and the progress bars will fill in automatically.

---

### Notes
- No em dashes anywhere in this codebase.
- All citation strings use APA 7th style where they appear in the UI.
- Do not import plotly.express in module7_policy.py -- it is not used and was removed.
