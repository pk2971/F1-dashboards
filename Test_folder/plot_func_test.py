# plot_functions.py
import fastf1
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

def lap_time(session, selected_drivers):
    """
    Plot lap time progression for selected drivers.
    No telemetry needed - uses basic lap data only.
    """
    fastf1.plotting.setup_mpl(color_scheme='fastf1')
    fig, ax = plt.subplots(figsize=(12, 6))

    for driver in selected_drivers:
        driver_laps = session.laps.pick_drivers(driver).pick_quicklaps().reset_index()

        if not driver_laps.empty:
            style = fastf1.plotting.get_driver_style(
                identifier=driver,
                style=['color', 'linestyle'],
                session=session
            )
            ax.plot(driver_laps['LapNumber'], driver_laps['LapTime'], **style, label=driver)

    ax.set_xlabel("Lap Number", fontsize=12)
    ax.set_ylabel("Lap Time", fontsize=12)
    ax.set_title("Lap Time Progression", fontsize=14)
    ax.legend(loc='best')
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    st.pyplot(fig)


def racepositions_plt(session, selected_drivers):
    """
    Plot race positions and track status for selected drivers with lap selection.
    No telemetry needed - uses basic lap data only.
    """
    fastf1.plotting.setup_mpl(color_scheme='fastf1')

    # --- Lap selection slider ---
    min_lap = int(session.laps['LapNumber'].min())
    max_lap = int(session.laps['LapNumber'].max())
    selected_laps = st.select_slider(
        "Choose lap numbers:",
        options=list(range(min_lap, max_lap + 1)),
        value=(min_lap, max_lap), key="race_position"
    )

    # Filter laps for selected range
    laps_filtered = session.laps[
        (session.laps['LapNumber'] >= selected_laps[0]) &
        (session.laps['LapNumber'] <= selected_laps[1])
    ].copy()

    fig, ax = plt.subplots(figsize=(20, 11))

    # Track status flags
    flag_legend_added = {'red': False, 'yellow': False, 'orange': False}

    for lap_num in laps_filtered['LapNumber'].unique():
        lap_data = laps_filtered[laps_filtered['LapNumber'] == lap_num].iloc[0]

        if 'TrackStatus' in lap_data and pd.notna(lap_data['TrackStatus']):
            track_status = str(lap_data['TrackStatus'])

            if '5' in track_status:
                label = 'Red Flag' if not flag_legend_added['red'] else None
                ax.axvspan(lap_num - 0.5, lap_num + 0.5, color='red', alpha=0.2, label=label)
                flag_legend_added['red'] = True
            elif '4' in track_status:
                label = 'Safety Car' if not flag_legend_added['yellow'] else None
                ax.axvspan(lap_num - 0.5, lap_num + 0.5, color='yellow', alpha=0.3, label=label)
                flag_legend_added['yellow'] = True
            elif '6' in track_status:
                label = 'VSC' if not flag_legend_added['orange'] else None
                ax.axvspan(lap_num - 0.5, lap_num + 0.5, color='orange', alpha=0.2, label=label)
                flag_legend_added['orange'] = True

    # Plot driver positions
    for drv in selected_drivers:
        drv_laps = laps_filtered.pick_drivers(drv)
        if len(drv_laps) == 0:
            continue
        abb = drv_laps['Driver'].iloc[0]
        style = fastf1.plotting.get_driver_style(identifier=abb, style=['color', 'linestyle'], session=session)
        ax.plot(drv_laps['LapNumber'], drv_laps['Position'], label=abb, **style)

    # y-axis (positions)
    num_drivers = len(session.drivers)
    ax.set_ylim([num_drivers + 0.5, 0.5])
    ax.set_yticks(range(1, num_drivers + 1))

    # x-axis (laps)
    ax.set_xlim(selected_laps[0] - 0.5, selected_laps[1] + 0.5)
    ax.set_xticks(range(selected_laps[0], selected_laps[1] + 1))

    ax.set_xlabel('Lap', fontsize=12)
    ax.set_ylabel('Position', fontsize=12)
    ax.set_title('Race Position Changes', fontsize=14)
    ax.grid(True, alpha=0.3)

    ax.legend(bbox_to_anchor=(1.0, 1.02), loc='upper left', framealpha=0.9)

    plt.tight_layout()
    st.pyplot(fig)


def tyre_strategies(session, selected_drivers, laps, year, event):
    """
    Plot tyre strategies (stints) for selected drivers and laps.
    Requires weather data - loaded separately with mode='weather'.
    """
    fastf1.plotting.setup_mpl(color_scheme='fastf1')

    # Laps slider
    min_lap = int(laps['LapNumber'].min())
    max_lap = int(laps['LapNumber'].max())
    selected_laps = st.select_slider(
        "Choose lap numbers:",
        options=list(range(min_lap, max_lap + 1)),
        value=(min_lap, max_lap), key="tyre_strat"
    )

    driver_laps = laps[
        (laps['Driver'].isin(selected_drivers)) &
        (laps['LapNumber'] >= selected_laps[0]) &
        (laps['LapNumber'] <= selected_laps[1])
    ].copy()

    if len(driver_laps) == 0:
        st.warning("No data available for the selected filters")
        return

    # Join laps with weather - only load if needed
    try:
        weather_data = session.laps.get_weather_data()
        laps_reset = laps.reset_index(drop=True)
        weather_reset = weather_data.reset_index(drop=True)
        joined = pd.concat([laps_reset, weather_reset.loc[:, ~(weather_reset.columns == 'Time')]], axis=1)
        joined_filtered = joined[
            (joined['LapNumber'] >= selected_laps[0]) &
            (joined['LapNumber'] <= selected_laps[1])
        ]
        show_rain = True
    except Exception as e:
        st.warning(f"Weather data not available: {e}")
        joined_filtered = pd.DataFrame()
        show_rain = False

    # Build stints summary
    stints = driver_laps.groupby(["Driver", "Stint", "Compound"]).size().reset_index(name='StintLength')

    fig1, ax1 = plt.subplots(figsize=(15, max(4, len(selected_drivers) * 0.6)))

    for driver in selected_drivers:
        driver_stints = stints[stints["Driver"] == driver].sort_values("Stint")
        previous_stint_end = selected_laps[0] - 1

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

    # Rain overlay (only if weather data available)
    if show_rain and not joined_filtered.empty:
        for i, row in joined_filtered.iterrows():
            if row['Rainfall']:
                ax1.axvspan(row['LapNumber'] - 0.5, row['LapNumber'] + 0.5, color='skyblue', alpha=0.3, zorder=0)

    # Configure axes
    ax1.set_title(f"{year} {event} Grand Prix - Tyre Strategies", fontsize=14, fontweight='bold')
    ax1.set_xlabel("Lap Number", fontsize=12)
    ax1.set_ylabel("Driver", fontsize=12)
    ax1.set_xlim(selected_laps[0] - 1, selected_laps[1] + 1)

    lap_range = selected_laps[1] - selected_laps[0] + 1
    if lap_range <= 20:
        ax1.set_xticks(range(selected_laps[0], selected_laps[1] + 1))
    else:
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

    if show_rain and not joined_filtered.empty and joined_filtered['Rainfall'].any():
        rain_patch = Patch(facecolor='skyblue', alpha=0.3, label='Rain')
        legend_elements = compound_patches + [rain_patch]
    else:
        legend_elements = compound_patches

    ax1.legend(handles=legend_elements, loc='lower right', title='Tire Compounds & Conditions')

    plt.tight_layout()
    st.pyplot(fig1)


# ============= TELEMETRY FUNCTIONS (Require full session load) =============

def speed_comparison(session, selected_drivers):
    """
    Compare speed telemetry for selected drivers' fastest laps.
    REQUIRES: session loaded with mode='full' (telemetry=True)
    """
    fastf1.plotting.setup_mpl(color_scheme='fastf1')
    
    # Show progress for telemetry loading
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    fig, ax = plt.subplots(figsize=(15, 8))
    
    total_drivers = len(selected_drivers)
    for idx, driver in enumerate(selected_drivers):
        status_text.text(f"Loading telemetry for {driver}...")
        progress_bar.progress((idx + 1) / total_drivers)
        
        # Get fastest lap
        fastest_lap = session.laps.pick_drivers(driver).pick_fastest()
        
        if fastest_lap is None or (isinstance(fastest_lap, pd.DataFrame) and fastest_lap.empty):
            st.warning(f"No fastest lap data for {driver}")
            continue
        
        # Get telemetry - this is the heavy operation
        try:
            telemetry = fastest_lap.get_telemetry()
            
            if telemetry is None or telemetry.empty:
                st.warning(f"No telemetry available for {driver}")
                continue
            
            # Get driver style
            style = fastf1.plotting.get_driver_style(
                identifier=driver,
                style=['color', 'linestyle'],
                session=session
            )
            
            # Format lap time for label
            lap_time_str = str(fastest_lap['LapTime']).split(' ')[-1] if pd.notna(fastest_lap['LapTime']) else 'N/A'
            
            # Plot speed
            ax.plot(
                telemetry['Distance'], 
                telemetry['Speed'],
                label=f"{driver} ({lap_time_str})",
                **style,
                linewidth=2
            )
            
        except Exception as e:
            st.warning(f"Could not load telemetry for {driver}: {e}")
            continue
    
    # Clear progress indicators
    progress_bar.empty()
    status_text.empty()
    
    ax.set_xlabel('Distance (m)', fontsize=12)
    ax.set_ylabel('Speed (km/h)', fontsize=12)
    ax.set_title('Speed Comparison - Fastest Laps', fontsize=14, fontweight='bold')
    ax.legend(loc='best', fontsize=10)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    st.pyplot(fig)
    
    # Add mini stats below plot
    st.subheader("Speed Statistics")
    cols = st.columns(len(selected_drivers))
    
    for idx, driver in enumerate(selected_drivers):
        with cols[idx]:
            try:
                fastest_lap = session.laps.pick_drivers(driver).pick_fastest()
                if fastest_lap is not None and not (isinstance(fastest_lap, pd.DataFrame) and fastest_lap.empty):
                    telemetry = fastest_lap.get_telemetry()
                    if telemetry is not None and not telemetry.empty:
                        st.metric(
                            driver,
                            f"{telemetry['Speed'].max():.1f} km/h",
                            f"Avg: {telemetry['Speed'].mean():.1f}"
                        )
            except:
                pass


def gear_analysis(session, driver):
    """
    Analyze gear usage throughout fastest lap.
    REQUIRES: session loaded with mode='full' (telemetry=True)
    """
    fastf1.plotting.setup_mpl(color_scheme='fastf1')
    
    with st.spinner(f"Loading telemetry for {driver}..."):
        fastest_lap = session.laps.pick_drivers(driver).pick_fastest()
        
        if fastest_lap is None or (isinstance(fastest_lap, pd.DataFrame) and fastest_lap.empty):
            st.error(f"No fastest lap data available for {driver}")
            return
        
        try:
            telemetry = fastest_lap.get_telemetry()
            
            if telemetry is None or telemetry.empty:
                st.error("No telemetry data available")
                return
            
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 10), sharex=True)
            
            # Speed and gear
            ax1_twin = ax1.twinx()
            ax1.plot(telemetry['Distance'], telemetry['Speed'], color='blue', linewidth=2, label='Speed')
            ax1_twin.plot(telemetry['Distance'], telemetry['nGear'], color='orange', linewidth=1.5, label='Gear', alpha=0.7)
            
            ax1.set_ylabel('Speed (km/h)', fontsize=12, color='blue')
            ax1_twin.set_ylabel('Gear', fontsize=12, color='orange')
            ax1.set_title(f'{driver} - Gear Usage Analysis (Fastest Lap)', fontsize=14, fontweight='bold')
            ax1.grid(True, alpha=0.3)
            
            # Add legends
            lines1, labels1 = ax1.get_legend_handles_labels()
            lines2, labels2 = ax1_twin.get_legend_handles_labels()
            ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
            
            # Throttle and brake
            ax2.plot(telemetry['Distance'], telemetry['Throttle'], color='green', linewidth=2, label='Throttle')
            ax2.plot(telemetry['Distance'], telemetry['Brake'] * 100, color='red', linewidth=2, label='Brake', alpha=0.7)
            
            ax2.set_xlabel('Distance (m)', fontsize=12)
            ax2.set_ylabel('Input (%)', fontsize=12)
            ax2.set_title('Throttle and Brake Application', fontsize=14)
            ax2.legend(loc='upper right')
            ax2.grid(True, alpha=0.3)
            ax2.set_ylim([0, 105])
            
            plt.tight_layout()
            st.pyplot(fig)
            
            # Stats
            st.subheader("Telemetry Statistics")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Max Speed", f"{telemetry['Speed'].max():.1f} km/h")
            with col2:
                st.metric("Avg Speed", f"{telemetry['Speed'].mean():.1f} km/h")
            with col3:
                st.metric("Top Gear", int(telemetry['nGear'].max()))
            with col4:
                # Calculate time on throttle
                throttle_time = (telemetry['Throttle'] > 95).sum() / len(telemetry) * 100
                st.metric("Full Throttle", f"{throttle_time:.1f}%")
            
        except Exception as e:
            st.error(f"Error loading telemetry: {e}")
            import traceback
            with st.expander("Show error details"):
                st.code(traceback.format_exc())


def fastest_lap_comparison(session, selected_drivers):
    """
    Multi-panel comparison of fastest laps.
    REQUIRES: session loaded with mode='full' (telemetry=True)
    """
    fastf1.plotting.setup_mpl(color_scheme='fastf1')
    
    # Show loading progress
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    fig, axes = plt.subplots(3, 1, figsize=(15, 12), sharex=True)
    
    total_drivers = len(selected_drivers)
    successfully_loaded = []
    
    for idx, driver in enumerate(selected_drivers):
        status_text.text(f"Loading telemetry for {driver}...")
        progress_bar.progress((idx + 1) / total_drivers)
        
        fastest_lap = session.laps.pick_drivers(driver).pick_fastest()
        
        if fastest_lap is None or (isinstance(fastest_lap, pd.DataFrame) and fastest_lap.empty):
            continue
        
        try:
            telemetry = fastest_lap.get_telemetry()
            
            if telemetry is None or telemetry.empty:
                continue
            
            style = fastf1.plotting.get_driver_style(
                identifier=driver,
                style=['color', 'linestyle'],
                session=session
            )
            
            # Speed
            axes[0].plot(telemetry['Distance'], telemetry['Speed'], 
                        label=driver, **style, linewidth=2)
            
            # Throttle
            axes[1].plot(telemetry['Distance'], telemetry['Throttle'], 
                        label=driver, **style, linewidth=2)
            
            # Brake (convert to percentage if needed)
            brake_data = telemetry['Brake'] * 100 if telemetry['Brake'].max() <= 1 else telemetry['Brake']
            axes[2].plot(telemetry['Distance'], brake_data, 
                        label=driver, **style, linewidth=2)
            
            successfully_loaded.append(driver)
            
        except Exception as e:
            st.warning(f"Could not load telemetry for {driver}: {e}")
            continue
    
    # Clear progress indicators
    progress_bar.empty()
    status_text.empty()
    
    if not successfully_loaded:
        st.error("Could not load telemetry for any selected drivers")
        return
    
    axes[0].set_ylabel('Speed (km/h)', fontsize=11)
    axes[0].set_title('Fastest Lap Comparison', fontsize=14, fontweight='bold')
    axes[0].legend(loc='upper right', fontsize=9)
    axes[0].grid(True, alpha=0.3)
    
    axes[1].set_ylabel('Throttle (%)', fontsize=11)
    axes[1].grid(True, alpha=0.3)
    axes[1].set_ylim([0, 105])
    
    axes[2].set_ylabel('Brake (%)', fontsize=11)
    axes[2].set_xlabel('Distance (m)', fontsize=11)
    axes[2].grid(True, alpha=0.3)
    axes[2].set_ylim([0, 105])
    
    plt.tight_layout()
    st.pyplot(fig)
    
    st.success(f"Successfully loaded telemetry for: {', '.join(successfully_loaded)}")