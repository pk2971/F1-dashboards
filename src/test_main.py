import fastf1.plotting
import streamlit as st
import matplotlib.pyplot as plt
from data_loader import load_session 
from plot_functions import racepositions_plt , tyre_strategies , lap_time

st.set_page_config(page_title="F1 Dashboard", layout="wide")

st.title("🏎️💨 F1 Race Dashboard ")

# --- Sidebar controls ---
year = st.sidebar.selectbox("Select Year", list(range(2020, 2026))[::-1], index=1)
races= [
    "Bahrain", "Saudi Arabia", "Australia", "Azerbaijan", "Miami",
    "Emilia Romagna", "Monaco", "Spain", "Canada", "Austria",
    "Britain", "Hungary", "Belgium", "Netherlands", "Italy",
    "Singapore", "Japan", "Qatar", "USA", "Mexico",
    "Brazil", "Las Vegas", "Abu Dhabi"
]
event = st.sidebar.selectbox("Select Grand Prix", options=races, index=races.index("Australia"))
session_type = st.sidebar.selectbox("Session Type", ["R", "Q"], index=0)

try:
    session = load_session(year, event, session_type)
    laps = session.laps
    drivers = session.drivers
    drivers = [session.get_driver(drv)["Abbreviation"] for drv in drivers]

    st.success(f"Loaded {year} {event} GP {session_type} successfully")

    tab1 , tab2 , tab3 = st.tabs(["Race Positions", "Tyre Strategies",  "Lap Time"])

    with tab1:
        st.subheader("Race Positions and Track Status")
        selected_drivers = st.multiselect(
            "Choose Driver:", 
            drivers, 
            default=drivers,
            key="race_positions"
        )
        
        if not selected_drivers:
            st.warning("Please select at least one driver")
        else:
            racepositions_plt(session , selected_drivers)
    
    with tab2:
        st.subheader("Tyre Strategies")        
        # --- Drivers selectbox ---
        selected_drivers = st.multiselect("Choose Driver:", drivers, default=drivers , key = "Tyre_stints")
        
        if not selected_drivers:
            st.warning("Please select at least one driver")
        else:
            tyre_strategies(session , selected_drivers , laps , year , event)

    with tab3:
        st.subheader("Lap Time Analysis")
        fastf1.plotting.setup_mpl(mpl_timedelta_support=True, color_scheme='fastf1')
        
        selected_drivers = st.multiselect("Choose Driver:", drivers, default=drivers[:3] , key = "Lap_time")  # Default to first 3 drivers

        if not selected_drivers:
            st.warning("Please select at least one driver")
        else:
            lap_time(session , selected_drivers)
    
    
except Exception as e:
    st.error(f"⚠️ Could not load session: {e}")
    import traceback
    st.code(traceback.format_exc())