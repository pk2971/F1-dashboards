import fastf1.plotting
import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.units as munits
munits.registry.clear()  # clear timple converter
from one_plot_functions import racepositions_plt , tyre_strategies , lap_time

st.set_page_config(page_title="F1 Dashboard", layout="wide")

st.title("🏎️💨 F1 Race Dashboard ")

# --- Sidebar controls ---
year = st.sidebar.selectbox("Select Year", list(range(2023, 2026))[::-1], index=1)
races= [
    "Bahrain", "Saudi Arabia", "Australia", "Azerbaijan", "Miami",
    "Emilia Romagna", "Monaco", "Spain", "Canada", "Austria",
    "Britain", "Hungary", "Belgium", "Netherlands", "Italy",
    "Singapore", "Japan", "Qatar", "Texas", "Mexico",
    "Brazil", "Las Vegas", "Abu Dhabi"
]
event = st.sidebar.selectbox("Select Grand Prix", options=races, index=races.index("Australia"))
session_type = st.sidebar.selectbox("Session Type", ["Race", "Qualifying"], index=0)
tab1 , tab2 , tab3 = st.tabs(["Race Positions", "Tyre Strategies",  "Lap Time"])

with tab1:
    st.subheader("Race Positions")
    racepositions_plt(year , event , session_type )
with tab2:
    st.subheader("Tyre Strategies")
    tyre_strategies(year , event , session_type)
with tab3:
    st.subheader("Lap Times")
    lap_time(year , event , session_type)