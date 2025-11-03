import streamlit as st
import fastf1
import fastf1.plotting
import matplotlib.pyplot as plt
import pandas as pd

st.set_page_config(page_title="F1 Dashboard", layout="wide")

st.title("🏎️ F1 Race Dashboard")

# --- Sidebar controls ---
year = st.sidebar.selectbox("Select Year", list(range(2018, 2025))[::-1], index=1)
event = st.sidebar.text_input("Enter Grand Prix name (e.g. Hungary, Bahrain, Japan)", "Hungary")
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

        stints = laps[["Driver", "Stint", "Compound", "LapNumber"]]
        stints = stints.groupby(["Driver", "Stint", "Compound"]).count().reset_index()
        stints = stints.rename(columns={"LapNumber": "StintLength"})

        fig1, ax1 = plt.subplots(figsize=(6, 10))
        for driver in drivers:
            driver_stints = stints.loc[stints["Driver"] == driver]
            previous_stint_end = 0
            for _, row in driver_stints.iterrows():
                compound_color = fastf1.plotting.get_compound_color(row["Compound"], session=session)
                ax1.barh(
                    y=driver,
                    width=row["StintLength"],
                    left=previous_stint_end,
                    color=compound_color,
                    edgecolor="black"
                )
                previous_stint_end += row["StintLength"]

        ax1.set_title(f"{year} {event} Grand Prix Strategies")
        ax1.set_xlabel("Lap Number")
        ax1.invert_yaxis()
        ax1.spines['top'].set_visible(False)
        ax1.spines['right'].set_visible(False)
        ax1.spines['left'].set_visible(False)
        ax1.grid(False)
        st.pyplot(fig1)

    # --- TAB 2: Position Chart ---
    with tab2:
        st.subheader("Driver Race Positions by Lap")

        # Load FastF1's color scheme
        fastf1.plotting.setup_mpl(mpl_timedelta_support=False, color_scheme='fastf1')

        fig2, ax2 = plt.subplots(figsize=(8.0, 4.9))
        for drv in session.drivers:
            drv_laps = session.laps.pick_drivers(drv)
            abb = drv_laps['Driver'].iloc[0]
            style = fastf1.plotting.get_driver_style(identifier=abb,
                                                     style=['color', 'linestyle'],
                                                     session=session)
            ax2.plot(drv_laps['LapNumber'], drv_laps['Position'],
                     label=abb, **style)

        ax2.set_ylim([20.5, 0.5])
        ax2.set_yticks([1, 5, 10, 15, 20])
        ax2.set_xlabel('Lap')
        ax2.set_ylabel('Position')
        ax2.legend(bbox_to_anchor=(1.0, 1.02))
        plt.tight_layout()
        st.pyplot(fig2)

except Exception as e:
    st.error(f"⚠️ Could not load session: {e}")
