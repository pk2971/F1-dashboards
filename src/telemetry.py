import streamlit as st
import fastf1
from fastf1 import plotting
from matplotlib import pyplot as plt

plotting.setup_mpl()

def telemetry_plots(session, driver_1, driver_2, selected_laps):
    # Use session.laps (already loaded with telemetry=True)
    laps = session.laps

    # Filter laps for selected drivers
    laps_driver_1 = laps.pick_driver(driver_1)
    laps_driver_2 = laps.pick_driver(driver_2)

    # Pick fastest lap or specific lap
    if selected_laps == "Fastest lap":
        lap_driver_1 = laps_driver_1.pick_fastest()
        lap_driver_2 = laps_driver_2.pick_fastest()
        title_suffix = "Fastest Lap Comparison"
    else:
        lap_driver_1 = laps_driver_1[laps_driver_1['LapNumber'] == selected_laps].iloc[0]
        lap_driver_2 = laps_driver_2[laps_driver_2['LapNumber'] == selected_laps].iloc[0]
        title_suffix = f"Lap {selected_laps} Comparison"

    # Get telemetry data (with distance added)
    telemetry_driver_1 = lap_driver_1.get_car_data().add_distance()
    telemetry_driver_2 = lap_driver_2.get_car_data().add_distance()

    # Plot setup
    fig, ax = plt.subplots(3, figsize=(10, 8))
    fig.suptitle(f"{driver_1} vs {driver_2} – {title_suffix}", fontsize=14, fontweight='bold')

    # Speed
    ax[0].plot(telemetry_driver_1['Distance'], telemetry_driver_1['Speed'], label=driver_1)
    ax[0].plot(telemetry_driver_2['Distance'], telemetry_driver_2['Speed'], label=driver_2)
    ax[0].set_ylabel('Speed (km/h)')
    ax[0].legend(loc="lower right")

    # Throttle
    ax[1].plot(telemetry_driver_1['Distance'], telemetry_driver_1['Throttle'], label=driver_1)
    ax[1].plot(telemetry_driver_2['Distance'], telemetry_driver_2['Throttle'], label=driver_2)
    ax[1].set_ylabel('Throttle (%)')

    # Brake
    ax[2].plot(telemetry_driver_1['Distance'], telemetry_driver_1['Brake'], label=driver_1)
    ax[2].plot(telemetry_driver_2['Distance'], telemetry_driver_2['Brake'], label=driver_2)
    ax[2].set_ylabel('Brake')
    ax[2].set_xlabel('Distance (m)')

    for a in ax.flat:
        a.label_outer()
        a.grid(True, alpha=0.3)

    plt.tight_layout()
    st.pyplot(fig)
