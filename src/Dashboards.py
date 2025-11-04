import fastf1
import pandas as pd
import fastf1.plotting
import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.patches import Patch



st.set_page_config(page_title="F1 Dashboard", layout="wide")

st.title("🏎️💨 F1 Race Dashboard")

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

@st.cache_data(show_spinner=True)
def load_session(year, event, session_type):
    session = fastf1.get_session(year, event, session_type)
    session.load(telemetry=False, weather=True)
    return session

try:
    session = load_session(year, event, session_type)
    laps = session.laps
    drivers = session.drivers
    drivers = [session.get_driver(drv)["Abbreviation"] for drv in drivers]

    st.success(f"Loaded {year} {event} GP {session_type} successfully")

    # --- Tabs ---
    tab1, tab2, tab3 = st.tabs(["Race Positions", "Tyre Strategies",  "Lap Time"])
    # -- TAB 1: Race Positions --
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
            fig, ax = plt.subplots(figsize=(20.0, 11))
            
            # Add colored background spans for flags/safety car 
            flag_legend_added = {'red': False, 'yellow': False, 'orange': False}
            
            for lap_num in session.laps['LapNumber'].unique():
                lap_data = session.laps[session.laps['LapNumber'] == lap_num].iloc[0]
                
                # Check for flags
                if 'TrackStatus' in lap_data and pd.notna(lap_data['TrackStatus']):
                    track_status = str(lap_data['TrackStatus'])
                    
                    # Red flag
                    if '5' in track_status:
                        label = 'Red Flag' if not flag_legend_added['red'] else None
                        ax.axvspan(lap_num - 0.5, lap_num + 0.5, color='red', alpha=0.2, label=label)
                        flag_legend_added['red'] = True
                    
                    # Yellow flag / Safety Car
                    elif '4' in track_status:
                        label = 'Safety Car' if not flag_legend_added['yellow'] else None
                        ax.axvspan(lap_num - 0.5, lap_num + 0.5, color='yellow', alpha=0.3, label=label)
                        flag_legend_added['yellow'] = True
                    
                    # Virtual Safety Car
                    elif '6' in track_status:
                        label = 'VSC' if not flag_legend_added['orange'] else None
                        ax.axvspan(lap_num - 0.5, lap_num + 0.5, color='orange', alpha=0.2, label=label)
                        flag_legend_added['orange'] = True
            
            # Plot driver positions 
            for drv in selected_drivers:
                drv_laps = session.laps.pick_drivers(drv)
                 # Skipping drivers with no lap data
                if len(drv_laps) == 0:
                    continue 
                abb = drv_laps['Driver'].iloc[0]
                style = fastf1.plotting.get_driver_style(identifier=abb,
                                                        style=['color', 'linestyle'],
                                                        session=session)
                ax.plot(drv_laps['LapNumber'], drv_laps['Position'],
                        label=abb, **style)
            
            # y-axis (positions) 
            num_drivers = len(session.drivers)
            ax.set_ylim([num_drivers + 0.5, 0.5])
            ax.set_yticks(range(1, num_drivers + 1))
            
            # x-axis (laps) 
            max_lap = session.laps['LapNumber'].max()
            ax.set_xticks(range(1, int(max_lap) + 1))
            
            ax.set_xlabel('Lap', fontsize=12)
            ax.set_ylabel('Position', fontsize=12)
            ax.set_title('Race Position Changes', fontsize=14)
            ax.grid(True, alpha=0.3)
            
            # Legend with drivers and track status
            ax.legend(bbox_to_anchor=(1.0, 1.02), loc='upper left', framealpha=0.9)
            
            plt.tight_layout()
            st.pyplot(fig)
            
    # --- TAB 2: Tyre Stints ---
    with tab2:
        st.subheader("Tyre Strategies")
        
        # --- Drivers selectbox ---
        selected_drivers = st.multiselect("Choose Driver:", drivers, default=drivers , key = "Tyre_stints")
        
        if not selected_drivers:
            st.warning("Please select at least one driver")
        else:
            # --- Laps slider ---
            min_lap = int(laps['LapNumber'].min())
            max_lap = int(laps['LapNumber'].max())
            selected_laps = st.select_slider(
                "Choose lap numbers:",
                options=list(range(min_lap, max_lap + 1)),
                value=(min_lap, max_lap)  # default: full range
            )
            
            # Filter laps for selected drivers and selected lap range
            driver_laps = laps[
                (laps['Driver'].isin(selected_drivers)) &
                (laps['LapNumber'] >= selected_laps[0]) &
                (laps['LapNumber'] <= selected_laps[1])
            ].copy()
            
            if len(driver_laps) == 0:
                st.warning("No data available for the selected filters")
            else:
                # Get weather data and join with laps
                weather_data = session.laps.get_weather_data()
                laps_reset = laps.reset_index(drop=True)
                weather_reset = weather_data.reset_index(drop=True)
                joined = pd.concat([laps_reset, weather_reset.loc[:, ~(weather_reset.columns == 'Time')]], axis=1)
                
                # Filter joined data for selected lap range
                joined_filtered = joined[
                    (joined['LapNumber'] >= selected_laps[0]) &
                    (joined['LapNumber'] <= selected_laps[1])
                ]
                
                # Build stints summary for selected drivers and laps
                stints = driver_laps.groupby(["Driver", "Stint", "Compound"]).size().reset_index(name='StintLength')
                
                # Plot
                fig1, ax1 = plt.subplots(figsize=(15, max(4, len(selected_drivers) * 0.6)))
                
                for driver in selected_drivers:
                    driver_stints = stints[stints["Driver"] == driver].sort_values("Stint")
                    previous_stint_end = selected_laps[0] - 1  # Start from the beginning of selected range
                    
                    for _, row in driver_stints.iterrows():
                        compound_color = fastf1.plotting.get_compound_color(row["Compound"], session=session)
                        ax1.barh(
                            y=driver,
                            width=row["StintLength"],
                            left=previous_stint_end,
                            color=compound_color,
                            edgecolor="black",
                            linewidth=1.5,
                            fill=True
                        )
                        previous_stint_end += row["StintLength"]
                
                # Add rain overlay
                for i, row in joined_filtered.iterrows():
                    if row['Rainfall']:
                        ax1.axvspan(row['LapNumber'] - 0.5, row['LapNumber'] + 0.5,
                                color='skyblue', alpha=0.3, zorder=0)
                
                # Configure axes
                ax1.set_title(f"{year} {event} Grand Prix - Tyre Strategies", fontsize=14, fontweight='bold')
                ax1.set_xlabel("Lap Number", fontsize=12)
                ax1.set_ylabel("Driver", fontsize=12)
                ax1.set_xlim(selected_laps[0] - 1, selected_laps[1] + 1)
                
                # Set x-axis ticks based on range
                lap_range = selected_laps[1] - selected_laps[0] + 1
                if lap_range <= 20:
                    ax1.set_xticks(range(selected_laps[0], selected_laps[1] + 1))
                else:
                    # Show fewer ticks for larger ranges
                    step = max(1, lap_range // 20)
                    ax1.set_xticks(range(selected_laps[0], selected_laps[1] + 1, step))
                
                ax1.grid(axis='x', linestyle='-', alpha=0.3)
                ax1.invert_yaxis()
                ax1.spines['top'].set_visible(False)
                ax1.spines['right'].set_visible(False)
                ax1.spines['left'].set_visible(False)
                
                # Legend
                compounds_used = stints['Compound'].unique()
                compound_patches = [Patch(facecolor=fastf1.plotting.get_compound_color(compound, session=session),
                                        edgecolor='black', label=compound) 
                                for compound in compounds_used]
                
                # Adding rain to legend if there was any rainfall
                if joined_filtered['Rainfall'].any():
                    rain_patch = Patch(facecolor='skyblue', alpha=0.3, label='Rain')
                    legend_elements = compound_patches + [rain_patch]
                else:
                    legend_elements = compound_patches
                
                ax1.legend(handles=legend_elements, loc='lower right', title='Tire Compounds & Conditions')
                
                plt.tight_layout()
                st.pyplot(fig1)

    # -- TAB 3: Lap Time Analysis
    with tab3:
        st.subheader("Lap Time Analysis")
        fastf1.plotting.setup_mpl(mpl_timedelta_support=True, color_scheme='fastf1')
        
        selected_drivers = st.multiselect("Choose Driver:", drivers, default=drivers[:3])  # Default to first 3 drivers
        
        if not selected_drivers:
            st.warning("Please select at least one driver")
        else:
            fig, ax = plt.subplots(figsize=(12, 6))
            
            for driver in selected_drivers:
                driver_laps = session.laps.pick_drivers(driver).pick_quicklaps().reset_index()
                
                if not driver_laps.empty:
                    style = fastf1.plotting.get_driver_style(
                        identifier=driver,
                        style=['color', 'linestyle'],
                        session=session
                    )
                    # Plot LapNumber on x-axis and LapTime on y-axis
                    ax.plot(driver_laps['LapNumber'], driver_laps['LapTime'], **style, label=driver)
            
            ax.set_xlabel("Lap Number", fontsize=12)
            ax.set_ylabel("Lap Time", fontsize=12)
            ax.set_title("Lap Time Progression", fontsize=14)
            ax.legend(loc='best')
            ax.grid(True, alpha=0.3)
            
            plt.tight_layout()
            st.pyplot(fig)
        

except Exception as e:
    st.error(f"⚠️ Could not load session: {e}")
    import traceback
    st.code(traceback.format_exc())