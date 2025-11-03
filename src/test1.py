import streamlit as st
import fastf1
import fastf1.plotting
import matplotlib.pyplot as plt
import pandas as pd

st.set_page_config(page_title="F1 Dashboard", layout="wide")

st.title("🏎️ F1 Race Dashboard")

# --- Sidebar controls ---
year = st.sidebar.selectbox("Select Year", list(range(2018, 2026))[::-1], index=1)
races_2025 = [
    "Bahrain", "Saudi Arabia", "Australia", "Azerbaijan", "Miami",
    "Emilia Romagna", "Monaco", "Spain", "Canada", "Austria",
    "Britain", "Hungary", "Belgium", "Netherlands", "Italy",
    "Singapore", "Japan", "Qatar", "USA", "Mexico",
    "Brazil", "Las Vegas", "Abu Dhabi"
]
event = st.sidebar.selectbox("Select Grand Prix", options=races_2025, index=races_2025.index("Australia"))
session_type = st.sidebar.selectbox("Session Type", ["R", "Q", "FP1", "FP2", "FP3"], index=0)

@st.cache_data(show_spinner=True)
def load_session(year, event, session_type):
    session = fastf1.get_session(year, event, session_type)
    session.load(telemetry=False, weather=False)
    return session

try:
    session = load_session(year, event, session_type)
    laps = session.laps
    drivers = session.drivers
    drivers = [session.get_driver(drv)["Abbreviation"] for drv in drivers]

    st.success(f"Loaded {year} {event} GP {session_type} successfully ✅")

    # --- Tabs ---
    tab1, tab2 = st.tabs(["📊 Tyre Strategies", "📈 Race Positions"])

    # --- TAB 1: Tyre Stints ---
    with tab1:

        st.subheader("Tyre Strategies")
        
        # --- Drivers selectbox ---
        selected_driver = st.multiselect("Choose Driver:", drivers , default=drivers)
        
        # --- Laps slider ---
        min_lap = int(laps['LapNumber'].min())
        max_lap = int(laps['LapNumber'].max())
        selected_laps = st.select_slider(
            "Choose lap numbers:",
            options=list(range(min_lap, max_lap + 1)),
            value=(min_lap, max_lap)  # default: full range
        )
        
        # Filter laps for selected driver and selected lap range
        driver_laps = laps[(laps['Driver'] == selected_driver) &
                        (laps['LapNumber'] >= selected_laps[0]) &
                        (laps['LapNumber'] <= selected_laps[1])]
        
        # Build stints summary
        stints = driver_laps.groupby(["Driver", "Stint", "Compound"]).count().reset_index()
        stints = stints.rename(columns={"LapNumber": "StintLength"})
        
        # Plot
        fig1, ax1 = plt.subplots(figsize=(10, 2))  # horizontal bar
        previous_stint_end = 0
        for _, row in stints.iterrows():
            compound_color = fastf1.plotting.get_compound_color(row["Compound"], session=session)
            ax1.barh(
                y=row["Driver"],
                width=row["StintLength"],
                left=previous_stint_end,
                color=compound_color,
                edgecolor="black"
            )
            previous_stint_end += row["StintLength"]
        
        ax1.set_title(f"{year} {event} Grand Prix Tyre Strategies")
        ax1.set_xlabel("Lap Number")
        ax1.invert_yaxis()
        ax1.spines['top'].set_visible(False)
        ax1.spines['right'].set_visible(False)
        ax1.spines['left'].set_visible(False)
        ax1.grid(False)
        st.pyplot(fig1)


    with tab2:
        st.subheader("whatever")

except Exception as e:
    st.error(f"⚠️ Could not load session: {e}")