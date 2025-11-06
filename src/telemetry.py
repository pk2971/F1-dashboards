import streamlit as st
from fastf1 import plotting
from matplotlib import pyplot as plt
from matplotlib.pyplot import figure
plotting.setup_mpl()
def telemetry_plots(session , driver_1 , driver_2 ):
    if not session.laps.pick_drivers(driver_1).pick_fastest().get_car_data()._car_data_loaded:
        session.load(telemetry=True)
    
    # Test for plot
    fastest_driver_1 = session.laps.pick_drivers(driver_1).pick_fastest()
    fastest_driver_2 = session.laps.pick_drivers(driver_2).pick_fastest()

    # Get telemetry from fastest laps
    telemetry_driver_1 = fastest_driver_1.get_car_data().add_distance()
    telemetry_driver_2 = fastest_driver_2.get_car_data().add_distance()

    # Create the plot
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(telemetry_driver_1['Distance'], telemetry_driver_1['Speed'], label=driver_1)
    ax.plot(telemetry_driver_2['Distance'], telemetry_driver_2['Speed'], label=driver_2)
    
    ax.set_xlabel("Distance (m)")
    ax.set_ylabel("Speed (km/h)")
    ax.set_title(f"Distance vs Speed: {driver_1} vs {driver_2}")
    ax.legend()
    
    # Display the plot in Streamlit
    st.pyplot(fig)

    