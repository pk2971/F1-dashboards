import streamlit as st
import fastf1
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from one_data_loader import load_session_light , load_session_weather

def racepositions_plt(year , event , session_type):
    """
    Plot race positions and track status for selected drivers with lap selection.
    """
    fastf1.plotting.setup_mpl(color_scheme='fastf1')
    session = load_session_light(year, event, session_type)
    drivers = session.drivers
    drivers = [session.get_driver(drv)["Abbreviation"] for drv in drivers]
    selected_drivers = st.multiselect(
            "Choose Driver:", 
            drivers, 
            default=drivers,
            key="race_positions"
        )
    
        
    if not selected_drivers:
        st.warning("Please select at least one driver")

    else:
        # --- Lap selection slider ---
        min_lap = int(session.laps['LapNumber'].min())
        max_lap = int(session.laps['LapNumber'].max())
        selected_laps = st.select_slider(
            "Choose lap numbers:",
            options=list(range(min_lap, max_lap + 1)),
            value=(min_lap, max_lap) , key= "race_position"
        )

        # Filter laps for selected range
        laps_filtered = session.laps[
            (session.laps['LapNumber'] >= selected_laps[0]) &
            (session.laps['LapNumber'] <= selected_laps[1])
        ].copy()

        fig, ax = plt.subplots(figsize=(20, 11))

        # Track status flags
        flag_legend_added = {'red': False, 'yellow': False, 'orange': False}

        for lap_num in laps_filtered['LapNumber'].unique():
            lap_data = laps_filtered[laps_filtered['LapNumber'] == lap_num].iloc[0]

            if 'TrackStatus' in lap_data and pd.notna(lap_data['TrackStatus']):
                track_status = str(lap_data['TrackStatus'])

                if '5' in track_status:
                    label = 'Red Flag' if not flag_legend_added['red'] else None
                    ax.axvspan(lap_num - 0.5, lap_num + 0.5, color='red', alpha=0.2, label=label)
                    flag_legend_added['red'] = True
                elif '4' in track_status:
                    label = 'Safety Car' if not flag_legend_added['yellow'] else None
                    ax.axvspan(lap_num - 0.5, lap_num + 0.5, color='yellow', alpha=0.3, label=label)
                    flag_legend_added['yellow'] = True
                elif '6' in track_status:
                    label = 'VSC' if not flag_legend_added['orange'] else None
                    ax.axvspan(lap_num - 0.5, lap_num + 0.5, color='orange', alpha=0.2, label=label)
                    flag_legend_added['orange'] = True

        # Plot driver positions
        for drv in selected_drivers:
            drv_laps = laps_filtered.pick_drivers(drv)
            if len(drv_laps) == 0:
                continue
            abb = drv_laps['Driver'].iloc[0]
            style = fastf1.plotting.get_driver_style(identifier=abb, style=['color', 'linestyle'], session=session)
            ax.plot(drv_laps['LapNumber'], drv_laps['Position'], label=abb, **style)

        # y-axis (positions for selected drivers only)
        all_positions = []
        for drv in selected_drivers:
            drv_laps = laps_filtered.pick_drivers(drv)
            if len(drv_laps) > 0:
                all_positions.extend(drv_laps['Position'].tolist())

        if all_positions:
            min_pos = min(all_positions)
            max_pos = max(all_positions)
        else:
            min_pos, max_pos = 1, len(session.drivers)

        ax.set_ylim([max_pos + 0.5, min_pos - 0.5])
        ax.set_yticks(range(int(min_pos), int(max_pos) + 1))

        # x-axis (laps)
        ax.set_xlim(selected_laps[0] - 0.5, selected_laps[1] + 0.5)
        ax.set_xticks(range(selected_laps[0], selected_laps[1] + 1))

        ax.set_xlabel('Lap', fontsize=12)
        ax.set_ylabel('Position', fontsize=12)
        ax.set_title('Race Position Changes', fontsize=14)
        ax.grid(True, alpha=0.3)

        ax.legend(bbox_to_anchor=(1.0, 1.02), loc='upper left', framealpha=0.9)

        plt.tight_layout()
        st.pyplot(fig)

def tyre_strategies(year , event , session_type):
    fastf1.plotting.setup_mpl(color_scheme='fastf1')
    session = load_session_weather(year, event, session_type)
    drivers = session.drivers
    laps = session.laps
    drivers = [session.get_driver(drv)["Abbreviation"] for drv in drivers]
    selected_drivers = st.multiselect(
            "Choose Driver:", 
            drivers, 
            default=drivers,
            key="tyre_strat_driver"
        )
    
    fastf1.plotting.setup_mpl(color_scheme='fastf1')

    # --- Lap selection slider ---
    min_lap = int(laps['LapNumber'].min())
    max_lap = int(laps['LapNumber'].max())
    selected_laps = st.select_slider(
        "Choose lap numbers:",
        options=list(range(min_lap, max_lap + 1)),
        value=(min_lap, max_lap),
        key="tyre_strat_laps"
    )

    # Filter laps for selected drivers and lap range
    driver_laps = laps[
        (laps['Driver'].isin(selected_drivers)) &
        (laps['LapNumber'] >= selected_laps[0]) &
        (laps['LapNumber'] <= selected_laps[1])
    ].copy()

    if len(driver_laps) == 0:
        st.warning("No data available for the selected filters")
        return

    # --- Weather join ---
    weather_data = session.laps.get_weather_data()
    laps_reset = laps.reset_index(drop=True)
    weather_reset = weather_data.reset_index(drop=True)
    joined = pd.concat([laps_reset, weather_reset.loc[:, ~(weather_reset.columns == 'Time')]], axis=1)
    joined_filtered = joined[
        (joined['LapNumber'] >= selected_laps[0]) &
        (joined['LapNumber'] <= selected_laps[1])
    ]

    # --- Build stints summary ---
    stints = driver_laps.groupby(["Driver", "Stint", "Compound"]).size().reset_index(name='StintLength')

    fig1, ax1 = plt.subplots(figsize=(15, max(4, len(selected_drivers) * 0.6)))

    # Map driver names to numeric y positions
    driver_positions = {drv: i for i, drv in enumerate(selected_drivers)}

    # --- Plot each driver's stints ---
    for driver in selected_drivers:
        driver_stints = stints[stints["Driver"] == driver].sort_values("Stint")
        previous_stint_end = selected_laps[0] - 1

        for _, row in driver_stints.iterrows():
            compound_color = fastf1.plotting.get_compound_color(row["Compound"], session=session)
            ax1.barh(
                y=driver_positions[driver],
                width=row["StintLength"],
                left=previous_stint_end,
                color=compound_color,
                edgecolor="black",
                linewidth=1.5
            )
            previous_stint_end += row["StintLength"]

    # --- Rain overlay ---
    if "Rainfall" in joined_filtered.columns:
        for _, row in joined_filtered.iterrows():
            if row.get('Rainfall', False):
                ax1.axvspan(row['LapNumber'] - 0.5, row['LapNumber'] + 0.5, color='skyblue', alpha=0.3, zorder=0)

    # --- Configure axes ---
    ax1.set_title(f"{year} {event} Grand Prix - Tyre Strategies", fontsize=14, fontweight='bold')
    ax1.set_xlabel("Lap Number", fontsize=12)
    ax1.set_ylabel("Driver", fontsize=12)
    ax1.set_xlim(selected_laps[0] - 1, selected_laps[1] + 1)

    # Label y-axis with driver abbreviations
    ax1.set_yticks(list(driver_positions.values()))
    ax1.set_yticklabels(list(driver_positions.keys()))
    ax1.invert_yaxis()  # top driver first

    # Show all lap numbers on x-axis
    ax1.set_xticks(range(selected_laps[0], selected_laps[1] + 1))
    ax1.set_xticklabels(range(selected_laps[0], selected_laps[1] + 1), rotation=90)

    ax1.grid(axis='x', linestyle='-', alpha=0.3)
    for spine in ['top', 'right', 'left']:
        ax1.spines[spine].set_visible(False)

    # --- Legend (tyre compounds + rain) ---
    compounds_used = stints['Compound'].unique()
    compound_patches = [
        Patch(facecolor=fastf1.plotting.get_compound_color(comp, session=session),
              edgecolor='black', label=comp)
        for comp in compounds_used
    ]

    legend_elements = compound_patches
    if "Rainfall" in joined_filtered.columns and joined_filtered['Rainfall'].any():
        legend_elements += [Patch(facecolor='skyblue', alpha=0.3, label='Rain')]

    ax1.legend(handles=legend_elements, loc='lower right', title='Tyre Compounds & Conditions')

    plt.tight_layout()
    st.pyplot(fig1)

def lap_time(year, event, session_type):
    fastf1.plotting.setup_mpl(color_scheme='fastf1')
    session = load_session_light(year, event, session_type)
    drivers = session.drivers
    drivers = [session.get_driver(drv)["Abbreviation"] for drv in drivers]
    selected_drivers = st.multiselect(
        "Choose Driver:", 
        drivers, 
        default=drivers[:3],
        key="lap_times"
    )
     
    fig, ax = plt.subplots(figsize=(12, 6))

    for driver in selected_drivers:
        driver_laps = session.laps.pick_drivers(driver).pick_quicklaps().reset_index()
        if not driver_laps.empty:
            style = fastf1.plotting.get_driver_style(
                identifier=driver,
                style=['color', 'linestyle'],
                session=session
            )
            ax.plot(driver_laps['LapNumber'], driver_laps['LapTime'], **style, label=driver)

    ax.set_xlabel("Lap Number", fontsize=12)
    ax.set_ylabel("Lap Time", fontsize=12)
    ax.set_title("Lap Time Progression", fontsize=14)
    ax.legend(loc='best')
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    st.pyplot(fig)
