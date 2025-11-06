# Dashboards.py
import fastf1.plotting
import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
from data_loader import load_session
from plot_functions import (
    racepositions_plt, tyre_strategies, lap_time,
    speed_comparison, gear_analysis, fastest_lap_comparison
)

st.set_page_config(page_title="F1 Dashboard", layout="wide")

st.title("🏎️💨 F1 Race Dashboard")

# --- Sidebar controls ---
year = st.sidebar.selectbox("Select Year", list(range(2020, 2026))[::-1], index=1)
races = [
    "Bahrain", "Saudi Arabia", "Australia", "Azerbaijan", "Miami",
    "Emilia Romagna", "Monaco", "Spain", "Canada", "Austria",
    "Britain", "Hungary", "Belgium", "Netherlands", "Italy",
    "Singapore", "Japan", "Qatar", "Texas", "Mexico",
    "Brazil", "Las Vegas", "Abu Dhabi"
]
event = st.sidebar.selectbox("Select Grand Prix", options=races, index=races.index("Australia"))
session_type = st.sidebar.selectbox("Session Type", ["Race", "Qualifying"], index=0)

st.sidebar.markdown("---")
st.sidebar.info("💡 **Tip:** Basic dashboards load fast. Telemetry dashboards may take longer.")

# Tab selection
tab_names = [
    "📊 Overview",
    "📈 Race Positions", 
    "🏁 Tyre Strategies", 
    "⏱️ Lap Time",
    "🚀 Speed Comparison",
    "⚙️ Gear Analysis",
    "🔥 Fastest Lap"
]

# Map tabs to loading requirements
TELEMETRY_TABS = ["🚀 Speed Comparison", "⚙️ Gear Analysis", "🔥 Fastest Lap"]
WEATHER_TABS = ["🏁 Tyre Strategies"]

# Create tabs
tabs = st.tabs(tab_names)

# Determine what data to load based on active tab
# Note: Streamlit doesn't tell us which tab is active, so we load on-demand within each tab

with tabs[0]:  # Overview
    st.subheader("Race Overview")
    
    try:
        with st.spinner("Loading session data..."):
            session = load_session(year, event, session_type, mode='basic')
            laps = session.laps
            drivers = session.drivers
            drivers = [session.get_driver(drv)["Abbreviation"] for drv in drivers]
        
        st.success(f"✅ Loaded {year} {event} GP {session_type}")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Laps", int(laps['LapNumber'].max()))
            st.metric("Drivers", len(drivers))
        
        with col2:
            if session_type == "Race" and 'Position' in laps.columns:
                final_laps = laps[laps['LapNumber'] == laps['LapNumber'].max()]
                if not final_laps.empty:
                    winner_data = final_laps[final_laps['Position'] == 1]
                    if not winner_data.empty:
                        winner = winner_data.iloc[0]['Driver']
                        st.metric("Winner", winner)
        
        with col3:
            fastest_lap = laps.pick_fastest()
            if fastest_lap is not None and not (isinstance(fastest_lap, pd.DataFrame) and fastest_lap.empty):
                st.metric("Fastest Lap Driver", f"{fastest_lap['Driver']}")
                lap_time_str = str(fastest_lap['LapTime']).split(' ')[-1] if pd.notna(fastest_lap['LapTime']) else 'N/A'
                st.metric("Time", lap_time_str)
        
        # Quick stats table
        st.subheader("Driver Summary")
        driver_stats = []
        for driver in drivers:
            driver_laps = laps.pick_drivers(driver)
            if not driver_laps.empty:
                fastest = driver_laps['LapTime'].min()
                avg = driver_laps['LapTime'].mean()
                driver_stats.append({
                    'Driver': driver,
                    'Laps': len(driver_laps),
                    'Fastest': str(fastest).split(' ')[-1] if pd.notna(fastest) else 'N/A',
                    'Average': str(avg).split(' ')[-1] if pd.notna(avg) else 'N/A'
                })
        
        st.dataframe(pd.DataFrame(driver_stats), use_container_width=True, hide_index=True)
        
    except Exception as e:
        st.error(f"⚠️ Could not load session: {e}")

with tabs[1]:  # Race Positions
    st.subheader("Race Positions and Track Status")
    
    try:
        with st.spinner("Loading session data..."):
            session = load_session(year, event, session_type, mode='basic')
            drivers = [session.get_driver(drv)["Abbreviation"] for drv in session.drivers]
        
        selected_drivers = st.multiselect(
            "Choose Driver:", 
            drivers, 
            default=drivers,
            key="race_positions"
        )
        
        if not selected_drivers:
            st.warning("Please select at least one driver")
        else:
            racepositions_plt(session, selected_drivers)
            
    except Exception as e:
        st.error(f"⚠️ Could not load session: {e}")

with tabs[2]:  # Tyre Strategies
    st.subheader("Tyre Strategies")
    
    try:
        with st.spinner("Loading session with weather data..."):
            session = load_session(year, event, session_type, mode='weather')
            laps = session.laps
            drivers = [session.get_driver(drv)["Abbreviation"] for drv in session.drivers]
        
        selected_drivers = st.multiselect("Choose Driver:", drivers, default=drivers, key="Tyre_stints")
        
        if not selected_drivers:
            st.warning("Please select at least one driver")
        else:
            tyre_strategies(session, selected_drivers, laps, year, event)
            
    except Exception as e:
        st.error(f"⚠️ Could not load session: {e}")

with tabs[3]:  # Lap Time
    st.subheader("Lap Time Analysis")
    
    try:
        with st.spinner("Loading session data..."):
            session = load_session(year, event, session_type, mode='basic')
            drivers = [session.get_driver(drv)["Abbreviation"] for drv in session.drivers]
        
        fastf1.plotting.setup_mpl(mpl_timedelta_support=True, color_scheme='fastf1')
        
        selected_drivers = st.multiselect("Choose Driver:", drivers, default=drivers[:3], key="Lap_time")

        if not selected_drivers:
            st.warning("Please select at least one driver")
        else:
            lap_time(session, selected_drivers)
            
    except Exception as e:
        st.error(f"⚠️ Could not load session: {e}")

with tabs[4]:  # Speed Comparison
    st.subheader("Speed Comparison")
    st.info("💡 Select 2-3 drivers for best comparison. This uses telemetry data and may take longer to load.")
    
    try:
        with st.spinner("⏳ Loading telemetry data (this may take 30-60 seconds)..."):
            session = load_session(year, event, session_type, mode='full')
            drivers = [session.get_driver(drv)["Abbreviation"] for drv in session.drivers]
        
        selected_drivers = st.multiselect("Choose Driver:", drivers, default=drivers[:2], key="speed_comp")
        
        if len(selected_drivers) < 2:
            st.warning("Please select at least 2 drivers")
        else:
            speed_comparison(session, selected_drivers)
            
    except Exception as e:
        st.error(f"⚠️ Could not load telemetry: {e}")
        import traceback
        with st.expander("Show error details"):
            st.code(traceback.format_exc())

with tabs[5]:  # Gear Analysis
    st.subheader("Gear Analysis")
    st.info("💡 Analyze gear shifts, throttle, and brake application for a driver's fastest lap.")
    
    try:
        with st.spinner("⏳ Loading telemetry data (this may take 30-60 seconds)..."):
            session = load_session(year, event, session_type, mode='full')
            drivers = [session.get_driver(drv)["Abbreviation"] for drv in session.drivers]
        
        selected_driver = st.selectbox("Choose Driver:", drivers, key="gear_analysis")
        
        if selected_driver:
            gear_analysis(session, selected_driver)
            
    except Exception as e:
        st.error(f"⚠️ Could not load telemetry: {e}")
        import traceback
        with st.expander("Show error details"):
            st.code(traceback.format_exc())

with tabs[6]:  # Fastest Lap Comparison
    st.subheader("Fastest Lap Telemetry Comparison")
    st.info("💡 Compare speed, throttle, and brake application across drivers' fastest laps.")
    
    try:
        with st.spinner("⏳ Loading telemetry data (this may take 30-60 seconds)..."):
            session = load_session(year, event, session_type, mode='full')
            drivers = [session.get_driver(drv)["Abbreviation"] for drv in session.drivers]
        
        selected_drivers = st.multiselect("Choose Driver:", drivers, default=drivers[:2], key="fastest_lap")
        
        if len(selected_drivers) < 2:
            st.warning("Please select at least 2 drivers")
        else:
            fastest_lap_comparison(session, selected_drivers)
            
    except Exception as e:
        st.error(f"⚠️ Could not load telemetry: {e}")
        import traceback
        with st.expander("Show error details"):
            st.code(traceback.format_exc())

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("### About")
st.sidebar.markdown("Data powered by FastF1")
st.sidebar.markdown(f"Current session: **{year} {event} {session_type}**")