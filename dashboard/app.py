import streamlit as st

st.set_page_config(
    page_title="Jamaica EV Dashboard — UWI Mona",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("Jamaica EV & Hybrid Vehicle Dashboard")
st.caption("University of the West Indies, Mona Campus — EV Lab Research Project, 2026")

st.sidebar.header("Global Controls")
fuel_price = st.sidebar.slider(
    "Current fuel price (J$/litre)",
    min_value=150, max_value=280, value=210, step=5,
    help="Updates all modules simultaneously"
)
electricity_rate = st.sidebar.slider(
    "JPS electricity rate (J$/kWh)",
    min_value=30, max_value=80, value=50, step=1,
    help="Used in EV charging cost calculations"
)

tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
    "1 EV vs ICE", "2 Route Map", "3 Price Tracker",
    "4 Fleet Sim", "5 Emissions", "6 Taxi", "7 Policy", "8 Caribbean"
])

modules = [
    (tab1, "EV / Hybrid vs. ICE Calculator", "Week 2"),
    (tab2, "Route Cost Map", "Week 3"),
    (tab3, "Gas & Energy Price Tracker", "Week 2"),
    (tab4, "Fleet Penetration Simulator", "Week 3"),
    (tab5, "Emissions Impact Calculator", "Week 3"),
    (tab6, "Taxi Feasibility Tool", "Week 3"),
    (tab7, "Fiscal Policy & Duty Tracker", "Week 4"),
    (tab8, "Caribbean Regional Comparison", "Week 3-4"),
]

for tab, name, target in modules:
    with tab:
        st.header(name)
        st.info(f"Build target: {target}")
