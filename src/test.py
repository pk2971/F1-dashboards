import fastf1.plotting
import streamlit as st
import matplotlib.pyplot as plt

from data_loader import load_session , load_telemetry_session

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
    session_telemetry = load_telemetry_session(year, event, session_type)
    laps = session.laps
    drivers = session.drivers
    drivers = [session.get_driver(drv)["Abbreviation"] for drv in drivers]

    st.success(f"Loaded {year} {event} GP {session_type} successfully")

    tab, = st.tabs(["Telemetry Comparision"])   
    with tab:
        st.subheader("Telemetry Comparision") 
        driver_1 = st.selectbox(
                "Select Driver 1:", 
                drivers,
                index=1,
                key="Driver_1"
            )  
        driver_2 = st.selectbox(
                "Select Driver 2:", 
                drivers,
                index=1,
                key="Driver_2"
            )  
        ver_lap = session.laps.pick_drivers(driver_1).pick_fastest()
        ham_lap = session.laps.pick_drivers(driver_2).pick_fastest()
        ver_tel = ver_lap.get_car_data().add_distance()
        ham_tel = ham_lap.get_car_data().add_distance()
        rbr_color = fastf1.plotting.get_team_color(ver_lap['Team'], session=session)
        mer_color = fastf1.plotting.get_team_color(ham_lap['Team'], session=session)

        fig, ax = plt.subplots()
        ax.plot(ver_tel['Distance'], ver_tel['Speed'], color=rbr_color, label=driver_1)
        ax.plot(ham_tel['Distance'], ham_tel['Speed'], color=mer_color, label=driver_2)

        ax.set_xlabel('Distance in m')
        ax.set_ylabel('Speed in km/h')
        ax.legend()
        plt.suptitle(f"Fastest Lap Comparison \n"
                    f"{session.event['EventName']} {session.event.year} Qualifying")

        # Use Streamlit to display the figure
        st.pyplot(fig)
        



except Exception as e:
    st.error(f"⚠️ Could not load session: {e}")
    import traceback
    st.code(traceback.format_exc())