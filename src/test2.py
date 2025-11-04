import fastf1
import matplotlib.pyplot as plt

# Load the session with messages and laps
session = fastf1.get_session(2024, "Brazil", 'R')
session.load(telemetry=True, weather=True, messages=True, laps=True)

# Pick lap 10 specifically and find the fastest driver in that lap
lap_number = 10
lap_10_laps = session.laps[session.laps['LapNumber'] == lap_number]

# Get the fastest lap from lap 10
fastest_lap_10 = lap_10_laps.pick_fastest()

# Get the telemetry data for the fastest lap
telemetry = fastest_lap_10.get_telemetry() 

# Create a figure with 3 subplots
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 10))
fig.suptitle(f'Lap {lap_number} - Fastest: {fastest_lap_10["Driver"]} - {fastest_lap_10["LapTime"]}', 
             fontsize=16, fontweight='bold')

# Plot 1: Speed vs Distance
ax1.plot(telemetry['Distance'], telemetry['Speed'], color='purple', linewidth=2)
ax1.set_ylabel('Speed (km/h)', fontsize=12)
ax1.set_xlabel('Distance (m)', fontsize=12)
ax1.set_title('Speed vs Distance', fontsize=14)
ax1.grid(True, alpha=0.3)

# Plot 2: Throttle vs Distance
ax2.plot(telemetry['Distance'], telemetry['Throttle'], color='green', linewidth=2)
ax2.set_ylabel('Throttle (%)', fontsize=12)
ax2.set_xlabel('Distance (m)', fontsize=12)
ax2.set_title('Throttle vs Distance', fontsize=14)
ax2.grid(True, alpha=0.3)
ax2.set_ylim(0, 105)

# Plot 3: Brake vs Distance
ax3.plot(telemetry['Distance'], telemetry['Brake'], color='red', linewidth=2)
ax3.set_ylabel('Brake Pressure', fontsize=12)
ax3.set_xlabel('Distance (m)', fontsize=12)
ax3.set_title('Brake vs Distance', fontsize=14)
ax3.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

# Print info about the fastest lap
print(f"Lap Number: {lap_number}")
print(f"Fastest Driver: {fastest_lap_10['Driver']}")
print(f"Team: {fastest_lap_10['Team']}")
print(f"Lap Time: {fastest_lap_10['LapTime']}")
print(f"Max Speed: {telemetry['Speed'].max():.2f} km/h")