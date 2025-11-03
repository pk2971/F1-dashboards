# import pandas as pd  # needed additionally to fastf1
# import fastf1
# import fastf1.plotting
# from matplotlib import pyplot as plt
# import numpy as np

# session = fastf1.get_session(2025, "Silverstone", 'R')
# session.load(weather=True)
# laps = session.laps
# weather_data = session.laps.get_weather_data()
# # prepare the data for joining
# laps = session.laps
# laps = laps.reset_index(drop=True)
# weather_data = weather_data.reset_index(drop=True)

# # exclude the 'Time' column from weather data when joining
# joined = pd.concat([laps, weather_data.loc[:, ~(weather_data.columns == 'Time')]], axis=1)
# print(joined.info())

# # Create a figure
# fig, ax = plt.subplots(figsize=(10, 3))

# # Loop through laps and shade those with rain
# for i, row in joined.iterrows():
#     if row['Rainfall']:
#         ax.axvspan(row['LapNumber'] - 0.5, row['LapNumber'] + 0.5,
#                    color='skyblue', alpha=0.6)  # blue shaded region

# # Set up axes
# ax.set_xlim(joined['LapNumber'].min() - 0.5, joined['LapNumber'].max() + 0.5)
# ax.set_ylim(0, 1)
# ax.set_yticks([])  # Hide y-axis since it’s not meaningful here

# # Label and grid
# ax.set_xlabel('Lap Number')
# ax.set_xticks(joined['LapNumber'])  # Show all lap numbers
# ax.set_title('Rainfall During Race Laps', fontsize=12, weight='bold')

# # Optional: add light grid lines
# ax.grid(axis='x', linestyle=':', alpha=0.5)

# plt.tight_layout()
# plt.show()
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.patches import Patch
import fastf1
import fastf1.plotting

# Load session data
session = fastf1.get_session(2025, "Silverstone", 'R')
session.load(weather=True)
laps = session.laps

# Get drivers
drivers = session.drivers
drivers = [session.get_driver(driver)["Abbreviation"] for driver in drivers]

# Prepare weather data
weather_data = session.laps.get_weather_data()
laps_reset = laps.reset_index(drop=True)
weather_reset = weather_data.reset_index(drop=True)
joined = pd.concat([laps_reset, weather_reset.loc[:, ~(weather_reset.columns == 'Time')]], axis=1)

# Prepare stint data
stints = laps[["Driver", "Stint", "Compound", "LapNumber"]]
stints = stints.groupby(["Driver", "Stint", "Compound"])
stints = stints.count().reset_index()
stints = stints.rename(columns={"LapNumber": "StintLength"})

# Create figure
fig, ax = plt.subplots(figsize=(15, 10))

# Draw tire strategy bars for each driver
for driver in drivers:
    driver_stints = stints.loc[stints["Driver"] == driver]
    
    previous_stint_end = 0
    for idx, row in driver_stints.iterrows():
        compound_color = fastf1.plotting.get_compound_color(row["Compound"], session=session)
        plt.barh(
            y=driver,
            width=row["StintLength"],
            left=previous_stint_end,
            color=compound_color,
            edgecolor="black",
            fill=True
        )
        previous_stint_end += row["StintLength"]

# Add rain overlay
for i, row in joined.iterrows():
    if row['Rainfall']:
        ax.axvspan(row['LapNumber'] - 0.5, row['LapNumber'] + 0.5,
                   color='skyblue', alpha=0.3, zorder=0)

# Configure axes
plt.title("2025 Silverstone Grand Prix - Tire Strategies with Rain", fontsize=14, weight='bold')
plt.xlabel("Lap Number", fontsize=12)
plt.ylabel("Driver", fontsize=12)

# Set x-axis to show every lap
max_lap = int(joined['LapNumber'].max())
ax.set_xlim(0, max_lap + 1)
ax.set_xticks(range(1, max_lap + 1))  # Show every lap from 1 to max
ax.grid(axis='x', linestyle='-', alpha=0.3)

# Invert y-axis
ax.invert_yaxis()

# Remove unnecessary spines
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_visible(False)

# Create legend
# Get unique compounds used in the race
compounds_used = stints['Compound'].unique()
compound_patches = [Patch(facecolor=fastf1.plotting.get_compound_color(compound, session=session),
                          edgecolor='black', label=compound) 
                   for compound in compounds_used]

# Add rain to legend
rain_patch = Patch(facecolor='skyblue', alpha=0.3, label='Rain')

# Combine all legend elements
legend_elements = compound_patches + [rain_patch]
ax.legend(handles=legend_elements, loc='lower right', title='Tire Compounds & Conditions')

plt.tight_layout()
plt.show()