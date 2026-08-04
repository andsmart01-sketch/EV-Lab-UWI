"""
Module 7: EV Policy & 2030 Target Progress Tracker
Jamaica National EV Policy (June 2023)
EV Lab Research Project -- UWI Mona, 2026

Parts:
  A: Visual tracker of Jamaica's three 2030 targets.
     Current values are PENDING -- set DATA_PENDING = False and fill
     TARGETS[*]["current_pct"] once METT registration data arrives.
  B: Colour-coded table of every implementation action in ACTIONS.
     NOTE: ACTIONS currently holds 23 entries while the chart titles used
     to say 22. Counts are now derived from len(ACTIONS) so they cannot
     drift, but check against the policy document which figure is right.
  C: Gap summary panel.

Source:
  Government of Jamaica. (2023). National electric vehicle policy.
  Ministry of Energy, Telecommunications and Transport (METT).
  NOTE: the URL below still uses the old msettjamaica.gov.jm domain.
  Verify it resolves before citing it in the report.
  https://msettjamaica.gov.jm/electric-vehicle-policy/
"""

from dash import dcc, html
import plotly.graph_objects as go

# -----------------------------------------------------------------------
# TOGGLE: set to False once METT data is received and current_pct filled
# -----------------------------------------------------------------------
DATA_PENDING = True

# -----------------------------------------------------------------------
# DATA: 2030 Targets
# current_pct: leave as None while DATA_PENDING = True.
# Fill in real figures from METT and set DATA_PENDING = False.
# -----------------------------------------------------------------------

# METT did not respond to the data request, so current_pct stays None. Rather
# than three empty bars, each target now carries the strongest SECONDARY
# evidence obtainable, plus a plain statement of why a percentage still cannot
# be computed. In every case the blocker is the DENOMINATOR, not the numerator:
# Jamaica publishes no current fleet totals by category.
#
# Do not fill current_pct from these. They are numerators without denominators,
# and inventing a denominator to get a percentage would be worse than a blank.

TARGETS = [
    {
        "label": "Private EV Fleet",
        "target_pct": 12,
        "current_pct": None,
        "unit": "% of privately owned fleet",
        "source": "METT fleet registry -- no response to data request",
        "known": "6,606 vehicles imported Jul 2022-Jun 2023, up from 2,854 the "
                 "year before. 951 in July 2023 alone, the highest month on record.",
        "known_caveat": "NOT a fleet count and NOT all electric. This is a 12-month "
                        "IMPORT flow, and the STATIN series is explicitly 'electric "
                        "vehicles including hybrids'. Hybrids are out of scope here, "
                        "so the true BEV number is materially lower and unknown.",
        "known_source": "STATIN data obtained by the Jamaica Observer, 24 Jan 2024",
        "known_url": "https://www.jamaicaobserver.com/2024/01/24/ev-imports-soar-9-b-year-govt-incentive/",
        "blocker": "No confirmed current total of privately registered vehicles. "
                   "The nearest anchors are ~190,000 (CEIC/OICA, 2015) and a "
                   "reported ~536,000 registered motor cars (TAJ, 2018), which are "
                   "not on the same basis and cannot be reconciled without help "
                   "from TAJ or the Island Traffic Authority.",
    },
    {
        "label": "Public Transport EV Fleet",
        "target_pct": 16,
        "current_pct": None,
        "unit": "% of public transport fleet",
        "source": "METT / Transport Authority -- no response to data request",
        "known": "JUTC operates 5 electric buses, of which 4 are in service.",
        "known_caveat": "Against a JUTC operable fleet of roughly 350-450 buses this "
                        "is about 1%, but JUTC is only the formal bus operator. "
                        "Minibuses and route taxis carry a large share of public "
                        "transport and are not counted in that denominator at all.",
        "known_source": "Jamaica Gleaner, Jul 2025; Dr L.-R. Harris, pers. comm., Jul 2026",
        "known_url": None,
        "blocker": "No published total for public passenger vehicles including "
                   "minibuses and route taxis. The Transport Authority licenses "
                   "these and is the only body that can supply the denominator.",
    },
    {
        "label": "GOJ Fleet",
        "target_pct": 100,
        "current_pct": None,
        "unit": "% of Government of Jamaica fleet",
        "source": "METT -- no response to data request",
        "known": "No confirmed count of electric vehicles in the government fleet "
                 "was obtained from any source, primary or secondary.",
        "known_caveat": "This is the most ambitious of the three targets and the "
                        "least publicly evidenced. Absence of reporting is itself a "
                        "finding worth stating in the report.",
        "known_source": None,
        "known_url": None,
        "blocker": "Neither the numerator nor the denominator is public. The Ministry "
                   "of Finance and the Public Service holds government fleet records.",
    },
]

# -----------------------------------------------------------------------
# DATA: 22 Policy Implementation Actions
# -----------------------------------------------------------------------

ACTIONS = [
    # Goal 1
    {"goal": 1, "action": "Set technical requirements to import EVs",
     "agencies": "METT, TBL", "timeline": "< 6 months", "deadline": "Dec 2023",
     "status": "Partial",
     "notes": "Section 1.1.1 of the policy defines this action mainly as setting an "
              "age limit: electric cars, motorcycles, light commercial vehicles, "
              "trucks, buses and similar should not exceed three years, measured as "
              "36 months from manufacture. A three-year threshold is operative, "
              "because only EVs under three years old qualify for the reduced 10% "
              "import duty. It is not clear whether it was also adopted as an import "
              "restriction, since the general motor vehicle age limit of six years "
              "still applies. The section's other elements, battery verification, "
              "right-hand drive and active thermal management, are written as "
              "recommendations rather than requirements, and battery verification "
              "depends on the information standard below, which is not in place. "
              "The three-year rule has since been written into law for another "
              "vehicle class: the Road Traffic (Licence Duties) Order 2024, passed "
              "by the Senate on 13 December 2024, cut e-bike import duty from 20% "
              "to 10% and exempted e-bikes from annual licence fees, in both cases "
              "only for units three years old or less, running to 31 March 2029.",
     "evidence_url": "https://www.jamaicaobserver.com/2024/01/24/ev-imports-soar-9-b-year-govt-incentive/"},
    {"goal": 1, "action": "Standardise technical information requirements for EV import",
     "agencies": "METT, TBL", "timeline": "< 6 months", "deadline": "Dec 2023",
     "status": "Not confirmed", "notes": ""},
    {"goal": 1, "action": "Develop battery labelling system",
     "agencies": "METT, NEPA, MIIC", "timeline": "1 year", "deadline": "Jun 2024",
     "status": "Not confirmed",
     "notes": "Requested but not delivered. In June 2024, the deadline month, the "
              "ministry's Chief Technical Director said the ministry 'intends to "
              "collaborate' with the Bureau of Standards Jamaica and had 'asked the "
              "Ministry of Industry, Investment and Commerce to facilitate the "
              "development of a quality-control standard for lithium-ion batteries'. "
              "That is a request to begin work, made in the month the action was due. "
              "No standard has since been traced.",
     "evidence_url": "https://www.jamaicaobserver.com/2024/06/03/govt-moves-prevent-influx-substandard-lithium-ion-batteries/"},
    {"goal": 1, "action": "Publish EV import guidelines",
     "agencies": "METT, Jamaica Customs, TBL, MIIC", "timeline": "< 6 months",
     "deadline": "Dec 2023", "status": "Partial",
     "notes": "Some official guidance exists but not the document the policy asks "
              "for. Jamaica Customs confirms electric vehicles are exempt from "
              "General Consumption Tax and publishes the clearance code to use, "
              "Additional National Code V14. However Section 1.1.2 requires a "
              "National Electric Vehicle Import Guideline, developed with the "
              "Ministry of Industry, Investment and Commerce, to serve as a single "
              "reference for importers. No such guideline was found, and the Customs "
              "motor vehicle pages an importer would normally consult carry no "
              "EV-specific guidance and defer age limits to the Trade Board.",
     "evidence_url": "https://jca.gov.jm/faq/are-electric-motor-vehicles-exempt-from-payment-of-general-consumption-tax-gct/"},
    {"goal": 1, "action": "Update EV inspection procedures",
     "agencies": "METT, TBL, MIIC", "timeline": "1 year", "deadline": "Jun 2024",
     "status": "Not confirmed", "notes": ""},
    {"goal": 1, "action": "Update private EV registration procedures",
     "agencies": "METT", "timeline": "1 year", "deadline": "Jun 2024",
     "status": "Partial", "notes": "TAJ processes EVs but no EV-specific fields confirmed."},
    # Goal 2
    {"goal": 2, "action": "Develop national EV charging deployment plan",
     "agencies": "METT, OUR", "timeline": "1-3 years", "deadline": "Jun 2026",
     "status": "Not confirmed",
     "notes": "The OUR ran a public consultation on EVs with a formal JPS response on record, but that process dates from 2021 and predates the 2023 policy. No post-2023 national charging deployment plan was traced. Network growth is happening commercially rather than under a published national plan.",
     "evidence_url": "https://our.org.jm/wp-content/uploads/2021/06/JPS-Response-to-EV-Consultation-Document.pdf"},
    {"goal": 2, "action": "Grid readiness assessment with JPS",
     "agencies": "METT, JPS", "timeline": "1-3 years", "deadline": "Jun 2026",
     "status": "Not confirmed",
     "notes": "No published joint METT and JPS grid readiness assessment was traced. JPS is clearly doing internal planning, having expanded Charge n Go to roughly 39 stations across six parishes by December 2025, but commercial rollout is not the same as the published assessment the policy calls for.",
     "evidence_url": "https://www.jpsco.com/jps-to-roll-out-6-new-ev-charging-locations-this-year/"},
    {"goal": 2, "action": "Publish EVSE technical and safety standards",
     "agencies": "METT, BSJ", "timeline": "1-3 years", "deadline": "Jun 2026",
     "status": "Not confirmed", "notes": "BSJ website does not list EV-specific standard."},
    {"goal": 2, "action": "Create public charging location information platform",
     "agencies": "METT", "timeline": "1-3 years", "deadline": "Jun 2026",
     "status": "Partial",
     "notes": "Platforms exist but none is national or government-run. JPS operates Charge n Go with its availability shown through the third-party ChargeLab app plus an RFID card; Evergo runs a separate network with its own app. A driver must therefore consult two private apps to see where they can charge. The policy action is for METT to create a single information platform, and no such platform was traced. Secondary source, Gleaner December 2025.",
     "evidence_url": "https://jamaica-gleaner.com/article/news/20251202/growth-jobs-powering-jamaicas-e-mobility-future-inside-charge-n-go-revolution"},
    # Goal 3
    {"goal": 3, "action": "Publish EVSE operating guidelines",
     "agencies": "METT, OUR", "timeline": "1-5 years", "deadline": "Jun 2028",
     "status": "Not confirmed",
     "notes": "The OUR has regulatory authority over electricity rates and consulted on EVs in 2021, producing preliminary recommendations and an accompanying analysis. No operating guidelines for charging equipment have been issued since the 2023 policy. Deadline is June 2028, so this is not yet overdue.",
     "evidence_url": "https://our.org.jm/wp-content/uploads/2021/07/OURs-EV-Article-Val-Fagan-2021-June.pdf"},
    {"goal": 3, "action": "Establish EVSE interoperability standard",
     "agencies": "METT, BSJ", "timeline": "1-5 years", "deadline": "Jun 2028",
     "status": "Not confirmed", "notes": "Multiple private networks; compatibility unconfirmed."},
    # Goal 4
    {"goal": 4, "action": "Battery collection and transport regulation",
     "agencies": "METT, NEPA, NSWMA", "timeline": "1-3 years", "deadline": "Jun 2026",
     "status": "Partial",
     "notes": "A transport control now exists, though it came from an international "
              "treaty rather than the EV policy. From 1 January 2025 anyone exporting "
              "electrical and electronic waste from Jamaica must go through the Prior "
              "Informed Consent procedure, under the 2022 Basel Convention amendment. "
              "NEPA must obtain approval from transit and importing states before "
              "issuing a permit, and the scope covers batteries used in motor "
              "vehicles. This regulates movement out of the country, not domestic "
              "collection, and it is not EV-specific.",
     "evidence_url": "https://www.nepa.gov.jm/sites/default/files/2025-01/Jamaica_to_strengthen_control_of_e_waste_exports.pdf"},
    {"goal": 4, "action": "Battery re-use and repurposing guidelines",
     "agencies": "METT, NEPA, NSWMA", "timeline": "1-3 years", "deadline": "Jun 2026",
     "status": "Not confirmed",
     "notes": "No guidelines traced. A 2024 study at UWI Mona reviewing Jamaica's "
              "legislation found no Act currently classifies electric vehicle "
              "batteries as hazardous waste. The National Solid Waste Management "
              "Act 2001 is the closest instrument but contains no provision for "
              "them, so there is no legal basis on which re-use or second-life "
              "rules could yet sit."},
    {"goal": 4, "action": "Battery recycling and disposal procedures",
     "agencies": "METT, NEPA, NSWMA", "timeline": "1-3 years", "deadline": "Jun 2026",
     "status": "Not confirmed",
     "notes": "No national procedure, but a working private route exists. The draft "
              "Green Paper on hazardous waste management, covering e-waste and EV "
              "batteries, went to Cabinet in December 2020 and was never finalised; "
              "the operative instrument is still the 2018 hazardous waste policy, "
              "which predates the EV policy. Meanwhile Tropical Battery Company has "
              "collected spent lithium batteries from consumer electronics and "
              "electric vehicles since early 2022, using receptacles at its six "
              "locations and a 5% in-store discount to encourage returns, then "
              "exporting them to an international recycler that recovers about 95% "
              "of the elements. That is a company programme, not a national one.",
     "evidence_url": "https://jamaica-gleaner.com/article/business/20211119/tropical-battery-recycle-ev-solar-batteries"},
    {"goal": 4, "action": "Establish Authorised Treatment Facilities (ATFs)",
     "agencies": "METT, MEGJC, NEPA, NSWMA", "timeline": "1-3 years", "deadline": "Jun 2026",
     "status": "Not confirmed",
     "notes": "REFINED: general e-waste ATFs do exist. NEPA authorises exactly two entities to collect and store e-waste, INET Jamaica Ltd (Marcus Garvey Drive, Kingston) and NSWMA (Riverton); NSWMA cannot export and partners with INET to do so. But neither is an EV-battery-specific treatment facility, and no EV battery ATF has been identified. The gap is narrower than first recorded but still real. Secondary source, JIS/Gleaner June 2025.",
     "evidence_url": "https://jis.gov.jm/use-nepa-authorised-facilities-only-for-disposal-of-e-waste/"},
    {"goal": 4, "action": "Battery status assessment system",
     "agencies": "METT, NEPA, NSWMA", "timeline": "3-5 years", "deadline": "Jun 2028",
     "status": "Not started (est.)", "notes": ""},
    # Goal 5
    {"goal": 5, "action": "Certification programme for EV mechanics and technicians",
     "agencies": "METT, MEGJC, MOEY, Universities", "timeline": "< 6 months",
     "deadline": "Dec 2023", "status": "Confirmed",
     "notes": "DELIVERED, but not by METT. JPS Foundation / IDB Lab Project eDrive runs two NVQ-J programmes through HEART/NSTA Trust: Electric-Hybrid Vehicle Routine Maintenance Level 2 (12 months) and System Repair and Replacement Level 3 (18 months), for 200 technicians. 15 instructors gained UK Institute of the Motor Industry certifications via a 2022 Train-the-Trainer with EINTAC Ltd. Jamaica was first in the Caribbean to establish an IMI-certified EV training programme. Secondary source. Delivery is by a utility foundation and a development bank, not the ministry named in the policy.",
     "evidence_url": "https://www.jpsco.com/200-persons-to-be-trained-as-ev-technicians-applications-now-open-for-jps-foundations-project-edrive-electric-vehicle-training/"},
    {"goal": 5, "action": "First responder EV certification (police, firefighters)",
     "agencies": "METT, MEGJC, MOEY, Universities", "timeline": "2-3 years",
     "deadline": "Jun 2026", "status": "In progress",
     "notes": "Upskilling 200 first responders is a stated objective of Project eDrive (JPS Foundation / IDB Lab) alongside the 200 technicians. Reported by the Gleaner, March 2023. Secondary source; completion numbers NOT verified and the June 2026 deadline has now passed without a published outcome.",
     "evidence_url": "https://jamaica-gleaner.com/article/news/20230307/growth-jobs-heartnsta-trust-gets-boost-ev-training"},
    {"goal": 5, "action": "Establish EV Skill Centers",
     "agencies": "METT, MEGJC", "timeline": "1-3 years", "deadline": "Jun 2026",
     "status": "Partial",
     "notes": "Three HEART/NSTA Trust campuses are equipped for and delivering EV training: the Jamaican-German Automotive School (Kingston), Southwest TVET Institute Derrick Rochester Campus (St Elizabeth) and Port Maria Vocational Training Centre (St Mary). Equipment valued over J$4M within a J$13M Project eDrive investment. These are existing TVET campuses hosting EV training, NOT purpose-built EV Skill Centres as the policy describes. Secondary source.",
     "evidence_url": "https://jamaica-gleaner.com/article/news/20230307/growth-jobs-heartnsta-trust-gets-boost-ev-training"},
    # Goal 6
    {"goal": 6, "action": "National EV awareness communication campaigns",
     "agencies": "METT, MOEY, Universities", "timeline": "1-3 years", "deadline": "Jun 2026",
     "status": "Partial", "notes": "Some METT social media. No formal campaign confirmed."},
    {"goal": 6, "action": "Parking incentives for EV users",
     "agencies": "METT, MFPS", "timeline": "< 6 months", "deadline": "Dec 2023",
     "status": "Not confirmed", "notes": "Some informal reserved bays at private locations."},
    # The policy's three headline 2030 fleet targets. They are objectives rather
    # than implementation actions, but they belong in this table so the tracker
    # covers the whole policy. Goal 6 is the adoption goal, so they sit here.
    {"goal": 6, "action": "Reach 12% electric share of the private vehicle fleet",
     "agencies": "METT", "timeline": "By 2030", "deadline": "2030",
     "status": "Not confirmed",
     "notes": "Partly measurable. 575,041 vehicles were certified fit to use the "
              "roads in 2022, of which 34,928 were public passenger vehicles, "
              "leaving about 540,000 private, commercial and government vehicles "
              "combined. Jamaica does not separate private cars from that total, "
              "and no count of fully electric cars exists, so a precise share "
              "still cannot be given.",
     "evidence_url": "https://www.jamaicaobserver.com/2024/01/24/ev-imports-soar-9-b-year-govt-incentive/"},
    {"goal": 6, "action": "Reach 16% electric share of the public transport fleet",
     "agencies": "METT, Transport Authority", "timeline": "By 2030", "deadline": "2030",
     "status": "Not confirmed",
     "notes": "Now measurable. Jamaica licensed 34,928 public passenger vehicles "
              "in 2022. The state bus company JUTC runs 5 electric buses, 4 of "
              "them in service. That is roughly 0.01% of the licensed fleet "
              "against a 16% target. Even measured against JUTC's own 350 buses "
              "it is about 1.4%.",
     "evidence_url": "https://jamaica-gleaner.com/article/news/20230813/jamaica-records-26-jump-motor-vehicle-imports-2022"},
    {"goal": 6, "action": "Reach 100% electric share of the government fleet",
     "agencies": "METT, Ministry of Finance", "timeline": "By 2030", "deadline": "2030",
     "status": "Not confirmed",
     "notes": "The most ambitious of the three targets and the least reported. "
              "No public figure was found for how many government vehicles are "
              "electric, nor for the size of the government fleet."},
    {"goal": 6, "action": "Designate Low Emission Zones",
     "agencies": "METT", "timeline": "1 year", "deadline": "Jun 2024",
     "status": "Not implemented", "notes": "No gazette notice found. Deadline missed."},
]

STATUS_DEFINITIONS = {
    "Confirmed":          "fully achieved",
    "In progress":        "mostly achieved",
    "Partial":            "somewhat achieved",
    "Not confirmed":      "little achieved",
    "Not implemented":    "same as or worse than baseline",
    "Not started (est.)": "missing score",
    "Pending data":       "missing score",
}

# Achievement scale colours. The six tiers below are the scale; the internal
# status names are just the labels this file happens to use for them.
STATUS_COLORS = {
    "Confirmed":          "#1B5E20",   # Deep forest green  - fully achieved
    "In progress":        "#29B6F6",   # Bright sky blue    - mostly achieved
    "Partial":            "#FFCA28",   # Warm amber         - somewhat achieved
    "Not confirmed":      "#F57C00",   # Dark orange        - little achieved
    "Not implemented":    "#D32F2F",   # Crimson red        - worse than baseline
    "Not started (est.)": "#9E9E9E",   # Neutral grey       - missing score
    "Pending data":       "#9E9E9E",   # Neutral grey       - missing score
}

# Human-readable tier name for each status, used in the colour key so the
# legend can never drift out of step with STATUS_COLORS again.
STATUS_TIER_LABELS = [
    ("Confirmed",          "Confirmed / Fully achieved"),
    ("In progress",        "In progress / Mostly achieved"),
    ("Partial",            "Partial / Somewhat achieved"),
    ("Not confirmed",      "Not confirmed / Little achieved"),
    ("Not implemented",    "Not implemented / Same as or worse than baseline"),
    ("Not started (est.)", "Not started / Missing score"),
]

# Fills light enough to need dark text rather than white, checked for contrast.
LIGHT_STATUS_FILLS = {"#29B6F6", "#FFCA28", "#F57C00", "#9E9E9E"}


# -----------------------------------------------------------------------
# CHARTS
# -----------------------------------------------------------------------

def build_progress_bars():
    """Target bars only when data pending; fills in when DATA_PENDING = False."""
    fig = go.Figure()

    y_labels = [t["label"] for t in TARGETS]
    targets   = [t["target_pct"] for t in TARGETS]
    currents  = [t["current_pct"] for t in TARGETS]

    # Target bars always shown
    fig.add_trace(go.Bar(
        name="2030 Target",
        y=y_labels,
        x=targets,
        orientation="h",
        marker_color="rgba(245, 196, 0, 0.3)",
        marker_line=dict(color="#1A9E75", width=2),
        text=[f"{t}% target" for t in targets],
        textposition="outside",
    ))

    if DATA_PENDING:
        # Show a thin "pending" bar so the user knows the field exists
        fig.add_trace(go.Bar(
            name="Current (data pending)",
            y=y_labels,
            x=[0.0, 0.0, 0.0],
            orientation="h",
            marker_color="rgba(189, 195, 199, 0.6)",
            marker_line=dict(color="#95a5a6", width=1),
            text=["Pending METT data"] * 3,
            textposition="outside",
        ))
        pending_note = (
            "Current penetration figures are PENDING. "
            "Set DATA_PENDING = False in module7_policy.py and fill current_pct "
            "once METT registration data is received."
        )
    else:
        fig.add_trace(go.Bar(
            name="Estimated Current",
            y=y_labels,
            x=currents,
            orientation="h",
            marker_color="#2d8a2d",
            text=[f"~{c}%" for c in currents],
            textposition="inside",
        ))
        pending_note = "Verify figures against STATIN transport data."

    # Layout geometry mirrors chart_layout() in app.py. It is duplicated rather
    # than imported because app.py imports this module, so importing back would
    # create a circular import. Legend sits below the plot, clear of the x-axis
    # title, with the caveat note below the legend. Offsets are solved from
    # pixel clearances instead of being hand-tuned fractions, which is what
    # caused the overlap in the first place.
    _height, _top, _bottom = 380, 70, 118
    _plot_h = _height - _top - _bottom          # 192 px of plot area
    _axis_px, _legend_px = 46, 18               # clearance below plot, legend row

    fig.update_layout(
        title={"text": "Jamaica 2030 EV Fleet Penetration Targets vs Current Progress",
               "font": {"size": 15}, "x": 0, "xanchor": "left"},
        barmode="overlay",
        xaxis=dict(title="Percentage of Fleet", range=[0, 115], ticksuffix="%"),
        yaxis=dict(title=""),
        legend=dict(orientation="h", yanchor="top",
                    y=-(_axis_px / _plot_h),
                    xanchor="center", x=0.5, font=dict(size=10)),
        height=_height,
        margin=dict(l=200, r=80, t=_top, b=_bottom),
        annotations=[dict(
            text=pending_note,
            xref="paper", yref="paper",
            x=0, y=-((_axis_px + _legend_px + 10) / _plot_h),
            xanchor="left", yanchor="top", showarrow=False,
            font=dict(size=11, color="#888888"), align="left"
        )]
    )
    return fig


def build_actions_table():
    """Colour-coded implementation action table."""
    cell_colors = [STATUS_COLORS.get(a["status"], "#cccccc") for a in ACTIONS]
    cell_text_colors = [
        "#2c3e50" if STATUS_COLORS.get(a["status"], "#cccccc") in LIGHT_STATUS_FILLS
        else "#ffffff"
        for a in ACTIONS
    ]

    fig = go.Figure(data=[go.Table(
        columnwidth=[25, 200, 90, 130, 110, 170],
        header=dict(
            values=["<b>Goal</b>", "<b>Action</b>", "<b>Deadline</b>",
                    "<b>Agencies</b>", "<b>Status</b>", "<b>Notes</b>"],
            fill_color="#1A9E75",
            font=dict(color="white", size=12),
            align="left",
            height=36
        ),
        cells=dict(
            values=[
                [a["goal"]     for a in ACTIONS],
                [a["action"]   for a in ACTIONS],
                [a["deadline"] for a in ACTIONS],
                [a["agencies"] for a in ACTIONS],
                [f'{a["status"]} ({STATUS_DEFINITIONS.get(a["status"], "")})' for a in ACTIONS],
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
            font=dict(
                color=[
                    ["#2c3e50"] * len(ACTIONS),  # Goal
                    ["#2c3e50"] * len(ACTIONS),  # Action
                    ["#2c3e50"] * len(ACTIONS),  # Deadline
                    ["#2c3e50"] * len(ACTIONS),  # Agencies
                    cell_text_colors,             # Status
                    ["#2c3e50"] * len(ACTIONS),  # Notes
                ],
                size=11
            ),
            align="left",
            height=30
        )
    )])
    fig.update_layout(
        title={"text": f"Policy Implementation Action Tracker ({len(ACTIONS)} Actions)",
               "font": {"size": 14}},
        height=800,
        margin=dict(l=10, r=10, t=50, b=10)
    )
    return fig


def build_status_pie():
    """Pie showing distribution of action statuses."""
    from collections import Counter
    counts = Counter(a["status"] for a in ACTIONS)
    labels = list(counts.keys())
    values = list(counts.values())
    colors = [STATUS_COLORS.get(l, "#cccccc") for l in labels]

    fig = go.Figure(data=[go.Pie(
        labels=labels, values=values,
        marker=dict(colors=colors),
        hole=0.4,
        textinfo="label+value",
        hoverinfo="label+percent"
    )])
    fig.update_layout(
        title={"text": f"Action Status Summary ({len(ACTIONS)} Actions)", "font": {"size": 13}},
        height=320,
        margin=dict(l=10, r=10, t=50, b=10),
        showlegend=False
    )
    return fig


# -----------------------------------------------------------------------
# LAYOUT
# -----------------------------------------------------------------------

def build_module7_layout():
    # METT did not supply fleet figures. Rather than a bare "data pending"
    # notice, show per-target what IS established from secondary sources and
    # exactly what is missing. In all three cases the missing piece is the
    # denominator, so a percentage cannot honestly be drawn.
    def _evidence_card(t):
        rows = [
            html.P(t["label"], style={
                "fontWeight": "700", "fontSize": "13px", "margin": "0 0 6px",
                "color": "#0E2A24"}),
            html.P([html.Span("Target: ", style={"fontWeight": "600"}),
                    f"{t['target_pct']}% of fleet by 2030"],
                   style={"fontSize": "12px", "margin": "0 0 6px", "color": "#444"}),
            html.P([html.Span("What is known: ", style={"fontWeight": "600"}),
                    t["known"]],
                   style={"fontSize": "12px", "margin": "0 0 6px", "color": "#444"}),
            html.P([html.Span("Caveat: ", style={"fontWeight": "600", "color": "#C0392B"}),
                    t["known_caveat"]],
                   style={"fontSize": "11px", "margin": "0 0 6px", "color": "#7B5A00"}),
            html.P([html.Span("Why no percentage: ", style={"fontWeight": "600"}),
                    t["blocker"]],
                   style={"fontSize": "11px", "margin": "0 0 6px", "color": "#666"}),
        ]
        if t.get("known_source"):
            src = (html.A(t["known_source"], href=t["known_url"], target="_blank",
                          style={"color": "#1A7A6E"})
                   if t.get("known_url") else
                   html.Span(t["known_source"], style={"color": "#888"}))
            rows.append(html.P(["Source: ", src],
                               style={"fontSize": "10px", "margin": "0", "color": "#888"}))
        return html.Div(rows, style={
            "backgroundColor": "#ffffff", "border": "1px solid #e0d5a8",
            "borderRadius": "4px", "padding": "10px 14px",
            "flex": "1", "minWidth": "260px"})

    pending_banner = html.Div([
        html.P("CURRENT PENETRATION NOT SHOWN. METT did not respond to the data "
               "request, so the bars below show the 2030 targets only.",
               style={"fontWeight": "700", "fontSize": "13px",
                      "margin": "0 0 4px", "color": "#856404"}),
        html.P("The obstacle is not the number of electric vehicles, it is the "
               "denominator. Jamaica does not publish current fleet totals by "
               "category, so a percentage cannot be calculated honestly from any "
               "public source. What each target's evidence does and does not "
               "support is set out below.",
               style={"fontSize": "12px", "margin": "0 0 12px", "color": "#856404"}),
        html.Div([_evidence_card(t) for t in TARGETS],
                 style={"display": "flex", "gap": "10px", "flexWrap": "wrap"}),
    ], style={
        "backgroundColor": "#fffbf0",
        "border": "1px solid #ffc107",
        "borderRadius": "4px",
        "padding": "12px 16px",
        "marginBottom": "18px",
    }) if DATA_PENDING else html.Div()

    return html.Div([

        # The module number and title are rendered by update_page_header() in
        # app.py, derived from position in MODULE_INFO. Do not hardcode a number
        # here; this module has moved position once already.
        #
        # The inline "Source:" line that used to sit here has been removed with
        # the others. It also cited the ministry as METT, which is wrong. The
        # correct attribution, for the module footer and the report, is:
        #   Government of Jamaica. (2023). National electric vehicle policy.
        #   Ministry of Energy, Telecommunications and Transport (METT).



        html.Div("Overall Implementation Status", style={
            "backgroundColor": "#E1F5EE",
            "color": "#0E2A24",
            "fontWeight": "700",
            "fontSize": "15px",
            "padding": "10px 18px",
            "marginBottom": "12px",
            "marginTop": "8px",
            "borderRadius": "2px",
            "letterSpacing": "0.3px",
        }),
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
                            "backgroundColor": STATUS_COLORS[key], "marginRight": "8px",
                            "borderRadius": "2px", "verticalAlign": "middle",
                            "border": "1px solid rgba(0,0,0,0.15)",
                        }),
                        label,
                    ], style={"listStyle": "none", "marginBottom": "5px", "fontSize": "12px"})
                    for key, label in STATUS_TIER_LABELS
                ], style={"paddingLeft": "0"})
            ], style={"width": "50%", "display": "inline-block",
                      "verticalAlign": "top", "paddingLeft": "24px"})
        ]),

        html.Hr(),

        html.Div("All Policy Implementation Actions", style={
            "backgroundColor": "#E1F5EE",
            "color": "#0E2A24",
            "fontWeight": "700",
            "fontSize": "15px",
            "padding": "10px 18px",
            "marginBottom": "12px",
            "marginTop": "8px",
            "borderRadius": "2px",
            "letterSpacing": "0.3px",
        }),
        html.P(
            "Status reflects publicly available information as of June 2026. "
            "Table updates when institutional responses arrive.",
            style={"fontSize": "11px", "color": "#888", "marginBottom": "8px"}
        ),
        dcc.Graph(id="m7-actions-table", figure=build_actions_table(),
                  config={"displayModeBar": False}),

        html.Hr(),

        html.Div("Identified Policy Gaps", style={
            "backgroundColor": "#E1F5EE",
            "color": "#0E2A24",
            "fontWeight": "700",
            "fontSize": "15px",
            "padding": "10px 18px",
            "marginBottom": "12px",
            "marginTop": "8px",
            "borderRadius": "2px",
            "letterSpacing": "0.3px",
        }),
        html.P("The pattern across these gaps is consistent. Where Jamaica has made "
               "real progress on electric vehicles, it has usually come from a "
               "utility, a development bank, a private company or an international "
               "treaty, rather than from the ministry the policy names.",
               style={"fontSize": "13px", "color": "#444", "marginBottom": "12px"}),

        html.P("Measurement", style={"fontWeight": "700", "fontSize": "13px",
                                     "margin": "0 0 4px"}),
        html.Ul([
            html.Li("Nobody publishes how many electric vehicles Jamaica has. Import "
                    "figures exist but the national statistics count hybrids together "
                    "with fully electric cars, so they cannot be used to measure a "
                    "target that excludes hybrids."),
            html.Li("Fleet totals are not broken down by category. 575,041 vehicles "
                    "were certified fit in 2022 and 34,928 of those were public "
                    "passenger vehicles, but private, commercial and government "
                    "vehicles are not separated, so the 12% private target cannot be "
                    "measured even if the EV count existed."),
            html.Li("The government fleet is the least reported of all. Neither the "
                    "number of vehicles nor the number that are electric is public, "
                    "against a 100% target."),
            html.Li("JUTC has not published energy consumption data from its electric "
                    "bus pilot, although measuring it was a stated aim of the trial."),
        ], style={"lineHeight": "1.9", "fontSize": "13px", "marginTop": "0"}),

        html.P("Standards and rules not yet issued",
               style={"fontWeight": "700", "fontSize": "13px", "margin": "10px 0 4px"}),
        html.Ul([
            html.Li("No quality standard for lithium-ion batteries. In June 2024, the "
                    "month this was due, the ministry had only just asked another "
                    "ministry to begin developing one."),
            html.Li("No battery health threshold for used electric vehicle imports. An "
                    "age limit of three years exists for the reduced duty, but nothing "
                    "governs the condition of the battery itself, which is what "
                    "actually determines whether a used EV is worth importing."),
            html.Li("No safety or technical standard for public charging equipment from "
                    "the Bureau of Standards Jamaica."),
            html.Li("No standard requiring different charging networks to work together, "
                    "though this is not due until 2028."),
            html.Li("No Low Emission Zone has been designated. This deadline passed in "
                    "June 2024."),
            html.Li("No publicly available plan for implementing the policy itself, "
                    "which was due in September 2023."),
        ], style={"lineHeight": "1.9", "fontSize": "13px", "marginTop": "0"}),

        html.P("Delivered by others, not by the state",
               style={"fontWeight": "700", "fontSize": "13px", "margin": "10px 0 4px"}),
        html.Ul([
            html.Li("Charging is being built commercially by JPS and Evergo. There is "
                    "no published national deployment plan, and no single place a "
                    "driver can look up every charger, because each operator runs its "
                    "own app."),
            html.Li("Technician and first-responder training was delivered by the JPS "
                    "Foundation and the Inter-American Development Bank through "
                    "HEART/NSTA, not by the ministries named in the policy."),
            html.Li("Battery recycling is being handled by a private company exporting "
                    "spent batteries abroad. There is still no producer responsibility "
                    "scheme making manufacturers or importers cover end-of-life costs. "
                    "A 2024 UWI Mona study of the legislation found the National Solid "
                    "Waste Management Act 2001 does not classify electric vehicle "
                    "batteries as hazardous waste, and that the Transport Authority "
                    "Act, Road Traffic Act and Public Health Act each address only a "
                    "small part of the problem."),
            html.Li("Two facilities are authorised to handle electronic waste, but "
                    "neither is set up specifically for electric vehicle batteries. "
                    "The one control that does now cover vehicle batteries came from "
                    "an international treaty obligation, not from this policy."),
        ], style={"lineHeight": "1.9", "fontSize": "13px", "marginTop": "0"}),

        html.P("Design limits worth noting",
               style={"fontWeight": "700", "fontSize": "13px", "margin": "10px 0 4px"}),
        html.Ul([
            html.Li("The reduced import duty was capped at 1,000 vehicles. A cap of "
                    "that size cannot deliver a 12% share of a fleet of several "
                    "hundred thousand, so the main incentive is limited by design."),
            html.Li("Importers have reported buying vehicles that turned out not to "
                    "qualify for the reduced duty, discovering this only on arrival. "
                    "That is what happens when the import guidelines the policy "
                    "promised have not been published."),
            html.Li("There is no requirement on JPS to publish the carbon intensity of "
                    "the electricity supply. Without it, no claim about how clean an "
                    "electric vehicle is in Jamaica can be independently checked, and "
                    "the same vehicle can look clean or dirty depending on which "
                    "assumption is used."),
        ], style={"lineHeight": "1.9", "fontSize": "13px", "marginTop": "0"}),
        html.P(
            "Full analysis: docs/ev_policy_gap_analysis.md",
            style={"fontSize": "11px", "color": "#888"}
        ),


    ], style={"padding": "20px"})
