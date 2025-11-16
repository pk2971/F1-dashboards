import fastf1.plotting
import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.units as munits
import datetime
from one_plot_functions import *
from one_data_loader import get_race_schedule

munits.registry.clear()  # clear timple converter

st.set_page_config(page_title="F1 Dashboard", layout="wide")

st.title("🏎️💨 F1 Race Dashboard ")

# --- Sidebar controls ---
current_year = datetime.date.today().year
years = list(range(2023, current_year + 1))[::-1] 
default_index = years.index(current_year)
year = st.sidebar.selectbox("Select Year", years , index=default_index)

events = get_race_schedule(year)

# Optional: Map official race names to your desired display names if needed
display_names = [event for event in events]

event = st.sidebar.selectbox("Select Grand Prix", options=display_names, index = 0)

# session_type = st.sidebar.selectbox("Session Type", ["Race", "Qualifying"], index=0)
tab1 , tab2 , tab3 , tab4 , tab5 , tab6 = st.tabs(["Race Overview","Race Positions", "Tyre Strategies",  "Lap Time" , "Telemetry Comparison" , "Tyre Degradation" ])

with tab1:
    st.subheader("Race Overview")
    race_overview(year , event , "Race")
with tab2:
    st.subheader("Race Positions")
    racepositions_plt(year , event , "Race" )
with tab3:
    st.subheader("Tyre Strategies")
    tyre_strategies(year , event , "Race")
with tab4:
    st.subheader("Lap Times")
    lap_time(year , event , "Race")
with tab5:
    st.subheader("Telemetry Comparison")
    telemetry_driver_comparison(year , event , "Race")
with tab6:
    st.subheader("Tyre Degradation Analysis")
    tyre_degradation(year , event , "Race")

