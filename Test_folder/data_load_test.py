# data_loader.py
import fastf1
import streamlit as st

@st.cache_data(show_spinner=True, ttl=3600)
def load_session_basic(year, event, session_type):
    """Load session without telemetry - fast for overview data"""
    session = fastf1.get_session(year, event, session_type)
    session.load(telemetry=False, weather=False, messages=False)
    return session

@st.cache_data(show_spinner=True, ttl=3600)
def load_session_with_weather(year, event, session_type):
    """Load session with weather data only"""
    session = fastf1.get_session(year, event, session_type)
    session.load(telemetry=False, weather=True, messages=False)
    return session

@st.cache_data(show_spinner=True, ttl=3600)
def load_session_full(year, event, session_type):
    """Load session with full telemetry - only when needed"""
    session = fastf1.get_session(year, event, session_type)
    session.load(telemetry=True, weather=True, messages=False)
    return session

@st.cache_data(show_spinner=True, ttl=3600)
def get_driver_telemetry(year, event, session_type, driver_abbr, lap_number=None):
    """Load telemetry for specific driver and lap - more granular caching"""
    session = fastf1.get_session(year, event, session_type)
    session.load(telemetry=True, weather=False, messages=False)
    
    if lap_number:
        lap = session.laps.pick_drivers(driver_abbr).pick_laps(lap_number)
        if not lap.empty:
            return lap.iloc[0].get_telemetry()
    else:
        # Return fastest lap telemetry
        lap = session.laps.pick_drivers(driver_abbr).pick_fastest()
        if lap is not None and hasattr(lap, 'get_telemetry'):
            return lap.get_telemetry()
    
    return None

def load_session(year, event, session_type, mode='basic'):
    """
    Universal loader with different modes:
    - 'basic': No telemetry (fastest)
    - 'weather': With weather data
    - 'full': Full telemetry (slowest)
    """
    if mode == 'basic':
        return load_session_basic(year, event, session_type)
    elif mode == 'weather':
        return load_session_with_weather(year, event, session_type)
    else:
        return load_session_full(year, event, session_type)