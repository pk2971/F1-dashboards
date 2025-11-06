from data_loader import load_session
import matplotlib
matplotlib.use("MacOSX")
from matplotlib import pyplot as plt



session = load_session(2024, "Brazil", "R")
fastest_driver_1 = session.laps.pick_drivers("VER").pick_fastest()
fastest_driver_2 = session.laps.pick_drivers("GAS").pick_fastest()

# Get telemetry from fastest laps
telemetry_driver_1 = fastest_driver_1.get_car_data().add_distance()
telemetry_driver_2 = fastest_driver_2.get_car_data().add_distance()

fig, ax = plt.subplots(3)
fig.suptitle("Fastest Race Lap Telemetry Comparison")

ax[0].plot(telemetry_driver_1['Distance'], telemetry_driver_1['Speed'], label='BOT')
ax[0].plot(telemetry_driver_2['Distance'], telemetry_driver_2['Speed'], label='HAM')
ax[0].set(ylabel='Speed')
ax[0].legend(loc="lower right")
ax[1].plot(telemetry_driver_1['Distance'], telemetry_driver_1['Throttle'], label='BOT')
ax[1].plot(telemetry_driver_2['Distance'], telemetry_driver_2['Throttle'], label='HAM')
ax[1].set(ylabel='Throttle')
ax[2].plot(telemetry_driver_1['Distance'], telemetry_driver_1['Brake'], label='BOT')
ax[2].plot(telemetry_driver_2['Distance'], telemetry_driver_2['Brake'], label='HAM')
ax[2].set(ylabel='Brakes')
# Hide x labels and tick labels for top plots and y ticks for right plots.
for a in ax.flat:
    a.label_outer()
    
plt.show()