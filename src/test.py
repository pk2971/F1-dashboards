import fastf1
import matplotlib.pyplot as plt
import pandas as pd

print("Loading session data...")
session = fastf1.get_session(2025, "Brazil", 'R')
session.load(telemetry=True, weather=True, messages=True, laps=True)
lap_number = session.laps['LapNumber']
print(lap_number)
