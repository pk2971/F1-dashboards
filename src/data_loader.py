import fastf1
import streamlit as st
@st.cache_data(show_spinner=True)
def load_session(year, event, session_type):
    session = fastf1.get_session(year, event, session_type)
    session.load(telemetry=True, weather=True)
    return session
@st.cache_data(show_spinner=True)
def load_telemetry_session(year , event , session_type):
    session = fastf1.get_session(year, event, session_type)
    session.load()
    return session