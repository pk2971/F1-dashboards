import fastf1
import streamlit as st
from fastf1.ergast import Ergast
# from streamlit_autorefresh import st_autorefresh


@st.cache_data(ttl = 3600 , max_entries = 5 , show_spinner=True)

def get_race_schedule(year):
    ergast = Ergast()
    schedule = ergast.get_race_schedule(year)
    # schedule is a DataFrame with raceName column
    return schedule['raceName'].tolist()

def load_session(year, event, session_type):
    session = fastf1.get_session(year, event, session_type)
    session.load(telemetry=True, weather=True)
    return session
# not being used anywhere at the moment
def load_session_light(year , event , session_type):
    session = fastf1.get_session(year, event, session_type)
    session.load(telemetry=False, weather=False)
    return session

def load_session_weather(year , event , session_type):
    session = fastf1.get_session(year, event, session_type)
    session.load(telemetry=False, weather=True)
    return session