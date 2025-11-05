import matplotlib.pyplot as plt
import streamlit as st
import pandas as pd
from matplotlib.patches import Patch
import fastf1

def tyre_strategies(session , selected_drivers , laps , year , event ):
                # --- Laps slider ---
            min_lap = int(laps['LapNumber'].min())
            max_lap = int(laps['LapNumber'].max())
            selected_laps = st.select_slider(
                "Choose lap numbers:",
                options=list(range(min_lap, max_lap + 1)),
                value=(min_lap, max_lap)  # default: full range
            )
            
            # Filter laps for selected drivers and selected lap range
            driver_laps = laps[
                (laps['Driver'].isin(selected_drivers)) &
                (laps['LapNumber'] >= selected_laps[0]) &
                (laps['LapNumber'] <= selected_laps[1])
            ].copy()
            
            if len(driver_laps) == 0:
                st.warning("No data available for the selected filters")
            else:
                # Get weather data and join with laps
                weather_data = session.laps.get_weather_data()
                laps_reset = laps.reset_index(drop=True)
                weather_reset = weather_data.reset_index(drop=True)
                joined = pd.concat([laps_reset, weather_reset.loc[:, ~(weather_reset.columns == 'Time')]], axis=1)
                
                # Filter joined data for selected lap range
                joined_filtered = joined[
                    (joined['LapNumber'] >= selected_laps[0]) &
                    (joined['LapNumber'] <= selected_laps[1])
                ]
                
                # Build stints summary for selected drivers and laps
                stints = driver_laps.groupby(["Driver", "Stint", "Compound"]).size().reset_index(name='StintLength')
                
                # Plot
                fig1, ax1 = plt.subplots(figsize=(15, max(4, len(selected_drivers) * 0.6)))
                
                for driver in selected_drivers:
                    driver_stints = stints[stints["Driver"] == driver].sort_values("Stint")
                    previous_stint_end = selected_laps[0] - 1  # Start from the beginning of selected range
                    
                    for _, row in driver_stints.iterrows():
                        compound_color = fastf1.plotting.get_compound_color(row["Compound"], session=session)
                        ax1.barh(
                            y=driver,
                            width=row["StintLength"],
                            left=previous_stint_end,
                            color=compound_color,
                            edgecolor="black",
                            linewidth=1.5,
                            fill=True
                        )
                        previous_stint_end += row["StintLength"]
                
                # Add rain overlay
                for i, row in joined_filtered.iterrows():
                    if row['Rainfall']:
                        ax1.axvspan(row['LapNumber'] - 0.5, row['LapNumber'] + 0.5,
                                color='skyblue', alpha=0.3, zorder=0)
                
                # Configure axes
                ax1.set_title(f"{year} {event} Grand Prix - Tyre Strategies", fontsize=14, fontweight='bold')
                ax1.set_xlabel("Lap Number", fontsize=12)
                ax1.set_ylabel("Driver", fontsize=12)
                ax1.set_xlim(selected_laps[0] - 1, selected_laps[1] + 1)
                
                # Set x-axis ticks based on range
                lap_range = selected_laps[1] - selected_laps[0] + 1
                if lap_range <= 20:
                    ax1.set_xticks(range(selected_laps[0], selected_laps[1] + 1))
                else:
                    # Show fewer ticks for larger ranges
                    step = max(1, lap_range // 20)
                    ax1.set_xticks(range(selected_laps[0], selected_laps[1] + 1, step))
                
                ax1.grid(axis='x', linestyle='-', alpha=0.3)
                ax1.invert_yaxis()
                ax1.spines['top'].set_visible(False)
                ax1.spines['right'].set_visible(False)
                ax1.spines['left'].set_visible(False)
                
                # Legend
                compounds_used = stints['Compound'].unique()
                compound_patches = [Patch(facecolor=fastf1.plotting.get_compound_color(compound, session=session),
                                        edgecolor='black', label=compound) 
                                for compound in compounds_used]
                
                # Adding rain to legend if there was any rainfall
                if joined_filtered['Rainfall'].any():
                    rain_patch = Patch(facecolor='skyblue', alpha=0.3, label='Rain')
                    legend_elements = compound_patches + [rain_patch]
                else:
                    legend_elements = compound_patches
                
                ax1.legend(handles=legend_elements, loc='lower right', title='Tire Compounds & Conditions')
                
                plt.tight_layout()
                st.pyplot(fig1)
