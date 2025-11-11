import streamlit as st
import fastf1
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from one_data_loader import load_session_light 

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

        # y-axis (positions)
        num_drivers = len(session.drivers)
        ax.set_ylim([num_drivers + 0.5, 0.5])
        ax.set_yticks(range(1, num_drivers + 1))

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