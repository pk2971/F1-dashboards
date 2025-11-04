import fastf1
import matplotlib.pyplot as plt
import pandas as pd

# Load session
race = fastf1.get_session(2024, "Australia", 'R')
race.load()

# Collect track status data for each lap
track_status_data = []
for lap_num in sorted(race.laps['LapNumber'].unique()):
    lap_data = race.laps[race.laps['LapNumber'] == lap_num].iloc[0]
    if 'TrackStatus' in lap_data and pd.notna(lap_data['TrackStatus']):
        track_status_data.append({
            'LapNumber': lap_num,
            'TrackStatus': str(lap_data['TrackStatus'])
        })

if track_status_data:
    df_status = pd.DataFrame(track_status_data)
    print("Track Status Data:")
    print(df_status)
    
    # Create figure
    fig, ax = plt.subplots(figsize=(12, 4))
    
    # Define status types and colors
    status_colors = {
        '1': ('green', 'Green Flag'),
        '2': ('yellow', 'Yellow Flag'),
        '4': ('orange', 'Safety Car'),
        '5': ('red', 'Red Flag'),
        '6': ('purple', 'VSC'),
        '7': ('lightblue', 'VSC Ending')
    }
    
    # Plot each status type separately for legend
    for status_code, (color, label) in status_colors.items():
        status_laps = df_status[df_status['TrackStatus'] == status_code]
        if not status_laps.empty:
            ax.scatter(status_laps['LapNumber'], 
                      [1] * len(status_laps),  # All at y=1 for visibility
                      c=color, 
                      s=100, 
                      marker='o',
                      label=label,
                      alpha=0.8,
                      edgecolors='black',
                      linewidths=1.5)
    
    # Formatting
    ax.set_xlabel('Lap Number', fontsize=12)
    ax.set_ylabel('Track Status', fontsize=12)
    ax.set_yticks([1])
    ax.set_yticklabels(['Status'])
    ax.set_ylim([0.5, 1.5])
    
    # Set x-axis to show all laps
    max_lap = race.laps['LapNumber'].max()
    ax.set_xlim([0, max_lap + 1])
    ax.set_xticks(range(0, int(max_lap) + 1, 5))  # Every 5 laps
    
    ax.legend(loc='upper right', framealpha=0.9)
    ax.grid(True, alpha=0.3, axis='x')
    ax.set_title('Track Status by Lap', fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    plt.show()
    
    # Show summary
    print("\nTrack Status Summary:")
    status_summary = df_status['TrackStatus'].value_counts()
    for status, count in status_summary.items():
        status_name = status_colors.get(status, (None, 'Unknown'))[1]
        print(f"{status_name} (Code {status}): {count} laps")
else:
    print("No track status data available for this session")