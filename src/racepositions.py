import fastf1
import matplotlib.pyplot as plt
import streamlit as st

def racepositions_plt(session , selected_drivers):
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