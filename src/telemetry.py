import streamlit as st
from fastf1 import plotting
from matplotlib import pyplot as plt
from matplotlib.pyplot import figure
plotting.setup_mpl()
def telemetry_plots(session , driver_1 , driver_2 ):
    fastest_driver_1 = session.laps.pick_drivers("VER").pick_fastest()
    fastest_driver_2 = session.laps.pick_drivers("GAS").pick_fastest()

    # Get telemetry from fastest laps
    telemetry_driver_1 = fastest_driver_1.get_car_data().add_distance()
    telemetry_driver_2 = fastest_driver_2.get_car_data().add_distance()
    st.header(telemetry_driver_1)
    st.header(telemetry_driver_2)

    