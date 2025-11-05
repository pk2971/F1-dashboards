import streamlit as st
def telemetry_plots(session , driver_1 , driver_2 , laps):
    min_lap = int(laps['LapNumber'].min())
    max_lap = int(laps['LapNumber'].max())
    options =  ["Fastest lap"] + list(range(min_lap, max_lap + 1))
    selected_laps = st.selectbox("Choose lap: ", options , index = 1)
    print(selected_laps)
    # lap_options = ["Fastest lap"] + selected_laps
    