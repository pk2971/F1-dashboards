import fastf1
import streamlit as st
@st.cache_data(show_spinner=True)
def load_session(year, event, session_type):
    session = fastf1.get_session(year, event, session_type)
    session.load(telemetry=False, weather=True)
    return session
