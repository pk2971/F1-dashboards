import fastf1.plotting
import streamlit as st

from data_loader import load_session
from racepositions import racepositions_plt
from tyrestrategies import tyre_strategies
from laptime import lap_time
from telemetry import telemetry_plots

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

    tab1 , tab2 , tab3 , tab4 = st.tabs(["Race Positions", "Tyre Strategies",  "Lap Time" , "Telemetry Comparision"])

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
    
    with tab4:
        st.subheader("Telemetry Comparision") 
        results = session.results.sort_values('Position')
        p1_driver = results.iloc[0]['Abbreviation']
        p2_driver = results.iloc[1]['Abbreviation']
        # Create two columns
        col1, col2 = st.columns(2)

        with col1:
            driver_1 = st.selectbox(
                "Select Driver 1:", 
                drivers,
                index=drivers.index(p1_driver) if p1_driver in drivers else 0,
                key="Driver_1"
            )

        with col2:
            driver_2 = st.selectbox(
                "Select Driver 2:", 
                drivers,
                index=drivers.index(p2_driver) if p2_driver in drivers else 1,
                key="Driver_2"
            )  
        min_lap = int(laps['LapNumber'].min())
        max_lap = int(laps['LapNumber'].max())
        lap_options =  ["Fastest lap"] + list(range(min_lap, max_lap + 1))
        selected_laps = st.selectbox("Choose lap: ", lap_options , index = 0)    
        fastest_driver_1 = session.laps.pick_drivers("VER").pick_fastest()
        fastest_driver_2 = session.laps.pick_drivers("GAS").pick_fastest()

        # Get telemetry from fastest laps
        telemetry_driver_1 = fastest_driver_1.get_car_data().add_distance()
        telemetry_driver_2 = fastest_driver_2.get_car_data().add_distance()
        st.subheader(telemetry_driver_1)
        # telemetry_plots(session , driver_1 , driver_2 )


except Exception as e:
    st.error(f"⚠️ Could not load session: {e}")
    import traceback
    st.code(traceback.format_exc())