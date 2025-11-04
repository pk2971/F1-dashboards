import streamlit as st
import fastf1
import fastf1.plotting
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import Patch
from fastf1 import plotting



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
    session.load(telemetry=True, weather=True)
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
        st.info("Coming soon...")
        
        # --- Drivers selectbox ---
        # selected_drivers = st.multiselect("Choose Driver:", drivers, default=drivers)
        
        # if not selected_drivers:
        #     st.warning("Please select at least one driver")
        # else:
        #     # --- Laps slider ---
        #     min_lap = int(laps['LapNumber'].min())
        #     max_lap = int(laps['LapNumber'].max())
        #     selected_laps = st.select_slider(
        #         "Choose lap numbers:",
        #         options=list(range(min_lap, max_lap + 1)),
        #         value=(min_lap, max_lap)  # default: full range
        #     )
            
        #     # Filter laps for selected drivers and selected lap range
        #     driver_laps = laps[
        #         (laps['Driver'].isin(selected_drivers)) &
        #         (laps['LapNumber'] >= selected_laps[0]) &
        #         (laps['LapNumber'] <= selected_laps[1])
        #     ].copy()
            
        #     if len(driver_laps) == 0:
        #         st.warning("No data available for the selected filters")
        #     else:
        #         # Get weather data and join with laps
        #         weather_data = session.laps.get_weather_data()
        #         laps_reset = laps.reset_index(drop=True)
        #         weather_reset = weather_data.reset_index(drop=True)
        #         joined = pd.concat([laps_reset, weather_reset.loc[:, ~(weather_reset.columns == 'Time')]], axis=1)
                
        #         # Filter joined data for selected lap range
        #         joined_filtered = joined[
        #             (joined['LapNumber'] >= selected_laps[0]) &
        #             (joined['LapNumber'] <= selected_laps[1])
        #         ]
                
        #         # Build stints summary for selected drivers and laps
        #         stints = driver_laps.groupby(["Driver", "Stint", "Compound"]).size().reset_index(name='StintLength')
                
        #         # Plot
        #         fig1, ax1 = plt.subplots(figsize=(15, max(4, len(selected_drivers) * 0.6)))
                
        #         for driver in selected_drivers:
        #             driver_stints = stints[stints["Driver"] == driver].sort_values("Stint")
        #             previous_stint_end = selected_laps[0] - 1  # Start from the beginning of selected range
                    
        #             for _, row in driver_stints.iterrows():
        #                 compound_color = fastf1.plotting.get_compound_color(row["Compound"], session=session)
        #                 ax1.barh(
        #                     y=driver,
        #                     width=row["StintLength"],
        #                     left=previous_stint_end,
        #                     color=compound_color,
        #                     edgecolor="black",
        #                     linewidth=1.5,
        #                     fill=True
        #                 )
        #                 previous_stint_end += row["StintLength"]
                
        #         # Add rain overlay
        #         for i, row in joined_filtered.iterrows():
        #             if row['Rainfall']:
        #                 ax1.axvspan(row['LapNumber'] - 0.5, row['LapNumber'] + 0.5,
        #                         color='skyblue', alpha=0.3, zorder=0)
                
        #         # Configure axes
        #         ax1.set_title(f"{year} {event} Grand Prix - Tyre Strategies", fontsize=14, fontweight='bold')
        #         ax1.set_xlabel("Lap Number", fontsize=12)
        #         ax1.set_ylabel("Driver", fontsize=12)
        #         ax1.set_xlim(selected_laps[0] - 1, selected_laps[1] + 1)
                
        #         # Set x-axis ticks based on range
        #         lap_range = selected_laps[1] - selected_laps[0] + 1
        #         if lap_range <= 20:
        #             ax1.set_xticks(range(selected_laps[0], selected_laps[1] + 1))
        #         else:
        #             # Show fewer ticks for larger ranges
        #             step = max(1, lap_range // 20)
        #             ax1.set_xticks(range(selected_laps[0], selected_laps[1] + 1, step))
                
        #         ax1.grid(axis='x', linestyle='-', alpha=0.3)
        #         ax1.invert_yaxis()
        #         ax1.spines['top'].set_visible(False)
        #         ax1.spines['right'].set_visible(False)
        #         ax1.spines['left'].set_visible(False)
                
        #         # Create legend
        #         compounds_used = stints['Compound'].unique()
        #         compound_patches = [Patch(facecolor=fastf1.plotting.get_compound_color(compound, session=session),
        #                                 edgecolor='black', label=compound) 
        #                         for compound in compounds_used]
                
        #         # Add rain to legend if there was any rainfall
        #         if joined_filtered['Rainfall'].any():
        #             rain_patch = Patch(facecolor='skyblue', alpha=0.3, label='Rain')
        #             legend_elements = compound_patches + [rain_patch]
        #         else:
        #             legend_elements = compound_patches
                
        #         ax1.legend(handles=legend_elements, loc='lower right', title='Tire Compounds & Conditions')
                
        #         plt.tight_layout()
        #         st.pyplot(fig1)


    with tab2:
        st.subheader("Lap Time Analysis")
        selected_drivers = st.multiselect("Choose Driver:", drivers, default=drivers)
        fig, ax = plt.subplots(figsize=(8, 5))
        for driver in selected_drivers:
            laps = session.laps.pick_drivers(driver).pick_quicklaps().reset_index()
            style = plotting.get_driver_style(identifier=driver,
                                      style=['color', 'linestyle'],
                                      session=session)
            ax.plot(laps['LapTime'], **style, label=driver)
        ax.set_xlabel("Lap Number")
        ax.set_ylabel("Lap Time")
        ax.legend()
        

except Exception as e:
    st.error(f"⚠️ Could not load session: {e}")
    import traceback
    st.code(traceback.format_exc())