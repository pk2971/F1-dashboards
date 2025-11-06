# 🏎️ Interactive Formula 1 Race Analytics Dashboard  

**Live Demo:** [Streamlit Dashboard](https://f1-dashboards-bc3ecpp8ahwayw6bw33fpf.streamlit.app/)  

**Medium Article:**  
A detailed article is in progress where I will discuss each dashboard module in depth, including the design choices, interactivity, and insights derived from the data. *Coming soon…*

---

An interactive, data-driven **Formula 1 race analytics dashboard** built with **Streamlit**, **FastF1**, **Matplotlib**, and **Pandas**. The dashboard allows users to explore race sessions from **2020–2025** with interactive visualizations and detailed telemetry insights.  

All race session data is sourced from the **[FastF1 API](https://theoehrly.github.io/Fast-F1/)** — an open-source Python library that provides access to Formula 1 timing, telemetry, and weather data.  

---

## Features

### 1. Race Position Tracker
- Visualizes **driver position changes lap-by-lap**.  
- Overlays highlight **Safety Cars, Red Flags, and Virtual Safety Car (VSC) periods**.  
- Select specific laps and drivers for custom race views.  

### 2. Tyre Strategy Analyzer
- Displays **stint lengths and tyre compounds** per driver.  
- Integrates **rainfall overlays** for weather-sensitive strategy analysis.  
- Provides insights into **pit stops, tyre management, and strategy choices**.  

### 3. Lap Time Comparison
- Charts **lap-time progression** for selected drivers.  
- Highlights **performance consistency** and race pace dynamics.  
- Filters for **quick laps** to focus on optimal driver performance.  

---

## Technical Highlights
- **Interactive filters:** Select drivers, laps, and session types dynamically.  
- **FastF1 integration:** Fetches race telemetry, weather, and session metadata.  
- **Caching:** Optimized for faster load times with `st.cache_data`.  
- **Matplotlib customization:** Driver-specific colors and tyre compound palettes for clear, intuitive visuals.  
- **Multi-tab layout:** Modular design for Race Positions, Tyre Strategies, and Lap Times.  
- Developed in **VSCode**, hosted on **Streamlit**.  

---

## Project Structure
All source code is in the `source/` directory:

source/

├─ Dashboard.py # Main Streamlit app

├─ data_loader.py # FastF1 session loader with caching

└─ plot_functions.py # Functions for Race Positions, Tyre Strategies, and Lap Time plots


---

## How to Run Locally

1. Clone the repository:  
```bash
git clone https://github.com/pk2971/F1-dashboards.git
cd src
pip install requirements.txt
```
2. Install dependecies
` pip install requirements.txt`
3. Start the Streamlit dashboard:
`streamlit run Dashboard.py`

