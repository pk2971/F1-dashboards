import matplotlib.pyplot as plt
import fastf1
import streamlit as st

def lap_time(session, selected_drivers):
    
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
