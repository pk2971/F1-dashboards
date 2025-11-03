import streamlit as st
from matplotlib import pyplot as plt
import fastf1
import fastf1.plotting
import pandas as pd

st.set_page_config(page_title="F1 Tyre Strategies", layout="centered")

st.title("🏎️ F1 Tyre Strategy Visualization")
st.markdown("Visualize driver stint strategies for any F1 race using [FastF1](https://theoehrly.github.io/Fast-F1/).")

# --- Sidebar filters ---
year = st.sidebar.selectbox("Select Year", list(range(2018, 2025))[::-1], index=2)
event = st.sidebar.text_input("Enter Grand Prix name (e.g. Hungary, Monaco, Japan)", "Hungary")
session_type = st.sidebar.selectbox("Session Type", ["R", "Q", "FP1", "FP2", "FP3"], index=0)

st.sidebar.markdown("💡 Example: *2022, Hungary, Race (R)*")

# Cache the session load (to avoid reloading every time)
@st.cache_data(show_spinner=True)
def load_session(year, event, session_type):
    session = fastf1.get_session(year, event, session_type)
    session.load()
    return session

# --- Load Data ---
try:
    session = load_session(year, event, session_type)
    laps = session.laps
    drivers = session.drivers
    drivers = [session.get_driver(driver)["Abbreviation"] for driver in drivers]

    st.success(f"Loaded {year} {event} GP {session_type} session successfully ✅")

    # --- Prepare stint data ---
    stints = laps[["Driver", "Stint", "Compound", "LapNumber"]]
    stints = stints.groupby(["Driver", "Stint", "Compound"]).count().reset_index()
    stints = stints.rename(columns={"LapNumber": "StintLength"})

    # --- Plot ---
    fig, ax = plt.subplots(figsize=(6, 10))
    for driver in drivers:
        driver_stints = stints.loc[stints["Driver"] == driver]
        previous_stint_end = 0
        for _, row in driver_stints.iterrows():
            compound_color = fastf1.plotting.get_compound_color(row["Compound"], session=session)
            ax.barh(
                y=driver,
                width=row["StintLength"],
                left=previous_stint_end,
                color=compound_color,
                edgecolor="black"
            )
            previous_stint_end += row["StintLength"]

    ax.set_title(f"{year} {event} Grand Prix Strategies")
    ax.set_xlabel("Lap Number")
    ax.invert_yaxis()
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.grid(False)

    st.pyplot(fig)

except Exception as e:
    st.error(f"⚠️ Could not load session: {e}")
    st.stop()
