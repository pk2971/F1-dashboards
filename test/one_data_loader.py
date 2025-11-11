import fastf1
import streamlit as st

@st.cache_data(ttl = 3600 , max_entries = 5 , show_spinner=True)
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