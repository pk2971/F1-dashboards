import streamlit as st
import fastf1
import pandas as pd
import altair as alt
import streamlit as st
from fastf1 import plotting
from data_loader import load_session_light , load_session_weather ,  load_session

def race_overview(year, event, session_type):

    plotting.setup_mpl(color_scheme='fastf1')

    # --- Light session load ---
    session = load_session_light(year, event, session_type)
    laps = session.laps

    # --- Get race results from laps (final lap of each driver) ---
    final_laps = laps.groupby('Driver').last().reset_index()
    results = final_laps.sort_values('Position')  # Ensure P1, P2, P3 order

    # P1, P2, P3
    p1 = results.iloc[0]
    p2 = results.iloc[1]
    p3 = results.iloc[2]

    # Full names of drivers
    p1_abbr = p1['Driver']
    p2_abbr = p2['Driver']
    p3_abbr = p3['Driver']
    
    p1_full_name = session.get_driver(p1_abbr)['FullName']
    p2_full_name = session.get_driver(p2_abbr)['FullName']
    p3_full_name = session.get_driver(p3_abbr)['FullName']

    # Time - Format as HH:MM:SS.mmm
    def format_time(time_delta):
        if pd.isna(time_delta):
            return "N/A"
        total_seconds = time_delta.total_seconds()
        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        seconds = total_seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:06.3f}"
    
    def format_delta(time_delta):
        if pd.isna(time_delta):
            return "N/A"
        total_seconds = time_delta.total_seconds()
        return f"+{total_seconds:.3f}s"

    p1_time = p1['Time']
    p2_delta = p2['Time'] - p1_time
    p3_delta = p3['Time'] - p1_time

    p1_time_str = format_time(p1_time)
    p2_delta_str = format_delta(p2_delta)
    p3_delta_str = format_delta(p3_delta)

    # Team colors
    p1_color = fastf1.plotting.get_team_color(p1['Team'], session=session)
    p2_color = fastf1.plotting.get_team_color(p2['Team'], session=session)
    p3_color = fastf1.plotting.get_team_color(p3['Team'], session=session)

    # Race caption
    st.markdown(f"### {session.event['EventName']} - {session.event['EventDate'].strftime('%Y-%m-%d')}")
    
    # --- Three columns for podium boxes ---
    col1, col2, col3 = st.columns(3)

    # P2 - left
    with col1:
        st.markdown(
            f"""
            <div style='background-color:{p2_color};padding:40px;border-radius:15px;text-align:center;height:250px;display:flex;flex-direction:column;justify-content:center;border:3px solid white;'>
                <div style='font-size:32px;font-weight:bold;color:white;margin-bottom:10px;'>P2</div>
                <div style='font-size:24px;font-weight:bold;color:white;margin-bottom:8px;'>{p2_full_name}</div>
                <div style='font-size:16px;color:white;opacity:0.9;margin-bottom:8px;'>{p2['Team']}</div>
                <div style='font-size:20px;font-weight:bold;color:white;'>{p2_delta_str}</div>
            </div>
            """, 
            unsafe_allow_html=True
        )

    # P1 - center
    with col2:
        st.markdown(
            f"""
            <div style='background-color:{p1_color};padding:40px;border-radius:15px;text-align:center;height:250px;display:flex;flex-direction:column;justify-content:center;border:3px solid white;'>
                <div style='font-size:32px;font-weight:bold;color:white;margin-bottom:10px;'>P1</div>
                <div style='font-size:24px;font-weight:bold;color:white;margin-bottom:8px;'>{p1_full_name}</div>
                <div style='font-size:16px;color:white;opacity:0.9;margin-bottom:8px;'>{p1['Team']}</div>
                <div style='font-size:20px;font-weight:bold;color:white;'>{p1_time_str}</div>
            </div>
            """, 
            unsafe_allow_html=True
        )

    # P3 - right
    with col3:
        st.markdown(
            f"""
            <div style='background-color:{p3_color};padding:40px;border-radius:15px;text-align:center;height:250px;display:flex;flex-direction:column;justify-content:center;border:3px solid white;'>
                <div style='font-size:32px;font-weight:bold;color:white;margin-bottom:10px;'>P3</div>
                <div style='font-size:24px;font-weight:bold;color:white;margin-bottom:8px;'>{p3_full_name}</div>
                <div style='font-size:16px;color:white;opacity:0.9;margin-bottom:8px;'>{p3['Team']}</div>
                <div style='font-size:20px;font-weight:bold;color:white;'>{p3_delta_str}</div>
            </div>
            """, 
            unsafe_allow_html=True
        )
    
    # --- Pole Position and Fastest Lap ---
    st.markdown("---")
    
    # Pole position (P1 in qualifying)
    try:
        quali_session = load_session_light(year, event, 'Q')
        quali_results = quali_session.results.sort_values('Position')
        pole_driver = quali_results.iloc[0]
        pole_driver_full_name = quali_session.get_driver(pole_driver['Abbreviation'])['FullName']
        pole_time = format_time(pole_driver['Q3']) if pd.notna(pole_driver.get('Q3')) else format_time(pole_driver.get('Q2', pole_driver.get('Q1')))
        pole_color = fastf1.plotting.get_team_color(pole_driver['TeamName'], session=quali_session)
    except:
        pole_driver_full_name = "N/A"
        pole_time = "N/A"
        pole_color = "#888888"
    
    # Fastest lap
    fastest_lap = laps.loc[laps['LapTime'].idxmin()]
    fastest_driver_abbr = fastest_lap['Driver']
    fastest_driver_full_name = session.get_driver(fastest_driver_abbr)['FullName']
    fastest_time = format_time(fastest_lap['LapTime'])
    fastest_lap_num = int(fastest_lap['LapNumber'])
    fastest_color = fastf1.plotting.get_team_color(fastest_lap['Team'], session=session)
    
    # Two columns for pole and fastest lap
    stat_col1, stat_col2 = st.columns(2)
    
    with stat_col1:
        st.markdown(
            f"""
            <div style='background:linear-gradient(135deg, rgba(0,0,0,0.7), rgba(0,0,0,0.5));padding:25px;border-radius:12px;border-left:5px solid {pole_color};min-height:140px;'>
                <div style='font-size:14px;color:#aaa;text-transform:uppercase;letter-spacing:2px;margin-bottom:8px;'>🏁 Pole Position</div>
                <div style='font-size:28px;font-weight:bold;color:white;margin-bottom:5px;'>{pole_driver_full_name}</div>
                <div style='font-size:18px;color:{pole_color};font-weight:bold;'>{pole_time}</div>
                <div style='font-size:14px;color:#999;margin-top:5px;visibility:hidden;'>Spacer</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    with stat_col2:
        st.markdown(
            f"""
            <div style='background:linear-gradient(135deg, rgba(0,0,0,0.7), rgba(0,0,0,0.5));padding:25px;border-radius:12px;border-left:5px solid {fastest_color};min-height:140px;'>
                <div style='font-size:14px;color:#aaa;text-transform:uppercase;letter-spacing:2px;margin-bottom:8px;'>⚡ Fastest Lap</div>
                <div style='font-size:28px;font-weight:bold;color:white;margin-bottom:5px;'>{fastest_driver_full_name}</div>
                <div style='font-size:18px;color:{fastest_color};font-weight:bold;'>{fastest_time}</div>
                <div style='font-size:14px;color:#999;margin-top:5px;'>Lap {fastest_lap_num}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    # --- Full Race Results Grid (P1-P20) ---
    st.markdown("---")
    st.markdown("### Race Results")
    
    results_data = []
    
    # All finishers (with valid positions)
    finishers = results[results['Position'].notna()].sort_values('Position').reset_index(drop=True)
    winner_time = finishers.iloc[0]['Time'] if len(finishers) > 0 else None
    
    for idx, row in finishers.iterrows():
        position = int(row['Position'])
        driver_abbr = row['Driver']
        driver_full_name = session.get_driver(driver_abbr)['FullName']
        team = row['Team']
        
        if position == 1:
            time_str = format_time(row['Time'])
        else:
            # Check if time is valid
            if pd.notna(row['Time']) and pd.notna(winner_time):
                delta = row['Time'] - winner_time
                time_str = format_delta(delta)
            else:
                time_str = "DNF"
        
        results_data.append({
            'Position': position,
            'Driver': driver_full_name,
            'Team': team,
            'Time': time_str
        })
    
    # Add DNF drivers (those with NaN positions)
    dnf_drivers = results[results['Position'].isna()]
    for idx, row in dnf_drivers.iterrows():
        driver_abbr = row['Driver']
        driver_full_name = session.get_driver(driver_abbr)['FullName']
        team = row['Team']
        
        results_data.append({
            'Position': 'DNF',
            'Driver': driver_full_name,
            'Team': team,
            'Time': 'DNF'
        })
    
    results_df = pd.DataFrame(results_data)
    
    # Display as table
    st.dataframe(
        results_df,
        hide_index=True,
        use_container_width=True,
        height=600
    )

def racepositions_plt(year, event, session_type):
    fastf1.plotting.setup_mpl(color_scheme='fastf1')
    session = load_session_light(year, event, session_type)
    drivers = session.drivers
    laps = session.laps
    drivers = [session.get_driver(drv)["Abbreviation"] for drv in drivers]

    # --- DRIVER SELECTION ---
    with st.expander("Select Drivers:", expanded=False):
        cols = st.columns(4)
        selected_drivers = []
        for idx, driver in enumerate(drivers):
            with cols[idx % 4]:
                is_selected = st.checkbox(
                    driver,
                    value=True,
                    key=f"race_position_{driver}"
                )
                if is_selected:
                    selected_drivers.append(driver)

    if not selected_drivers:
        st.warning("Please select at least one driver")
        return

    # --- LAP SELECTION ---
    min_lap = int(laps['LapNumber'].min())
    max_lap = int(laps['LapNumber'].max())
    selected_laps = st.select_slider(
        "Choose lap range:",
        options=list(range(min_lap, max_lap + 1)),
        value=(min_lap, max_lap),
        key="racepositions_laps"
    )

    laps_filtered = laps[
        (laps['LapNumber'] >= selected_laps[0]) &
        (laps['LapNumber'] <= selected_laps[1])
    ].copy()

    laps_filtered_selected = laps_filtered[laps_filtered['Driver'].isin(selected_drivers)].copy()
    if laps_filtered_selected.empty:
        st.warning("No data for selected drivers and lap range")
        return

    # --- DRIVER COLORS & DASHES ---
    driver_colors = {}
    driver_teams = {}
    for drv in selected_drivers:
        drv_laps = laps_filtered_selected[laps_filtered_selected['Driver'] == drv]
        if len(drv_laps) == 0:
            continue
        abb = drv_laps['Driver'].iloc[0]
        team = drv_laps['Team'].iloc[0]
        style = fastf1.plotting.get_driver_style(identifier=abb, style=['color'], session=session)
        driver_colors[drv] = style['color']
        driver_teams[drv] = team

    # Dash: first driver per team solid, second dashed
    team_driver_count = {}
    driver_dashes = {}
    for drv, team in driver_teams.items():
        team_driver_count[team] = team_driver_count.get(team, 0) + 1
        driver_dashes[drv] = [0] if team_driver_count[team] == 1 else [5,5]

    # --- DYNAMIC Y-AXIS ---
    min_pos = laps_filtered_selected['Position'].min()
    max_pos = laps_filtered_selected['Position'].max()

    # --- MAIN CHART WITH INDIVIDUAL TOOLTIP ---
    chart = alt.Chart(laps_filtered_selected).mark_line(strokeWidth=3).encode(
        x=alt.X('LapNumber:O',
                title='Lap Number',
                axis=alt.Axis(values=list(laps_filtered_selected['LapNumber'].unique()),
                              tickMinStep=1,
                              labelAngle=0,
                              grid=False)),
        y=alt.Y('Position:Q',
                title='Position',
                scale=alt.Scale(domain=[max_pos, min_pos]),
                axis=alt.Axis(grid=False)),
        color=alt.Color('Driver:N', scale=alt.Scale(domain=list(driver_colors.keys()),
                                                    range=list(driver_colors.values())),legend=alt.Legend()),
        strokeDash=alt.StrokeDash('Driver:N', scale=alt.Scale(domain=list(driver_dashes.keys()),
                                                              range=list(driver_dashes.values()))),
        tooltip=[
            alt.Tooltip('LapNumber:Q', title='Lap'),
            alt.Tooltip('Position:Q', title='Position'),
            alt.Tooltip('Driver:N', title='Driver'),
            alt.Tooltip('Team:N', title='Team')
        ]
    )
    points = alt.Chart(laps_filtered_selected).mark_point(
    size=25,        
    filled=True,
    opacity=0.3,   
    strokeWidth=0
            ).encode(
                x='LapNumber:O',
                y='Position:Q',
                color=alt.Color('Driver:N', scale=alt.Scale(domain=list(driver_colors.keys()),
                                                            range=list(driver_colors.values())),
                                legend=None),
                strokeDash=alt.StrokeDash('Driver:N', scale=alt.Scale(domain=list(driver_dashes.keys()),
                                                                        range=list(driver_dashes.values())),legend=None),
                tooltip=[
                    alt.Tooltip('LapNumber:Q', title='Lap'),
                    alt.Tooltip('Position:Q', title='Position'),
                    alt.Tooltip('Driver:N', title='Driver'),
                    alt.Tooltip('Team:N', title='Team')
                ]
            )
    # --- TRACK STATUS COLORS ---
    status_colors = {
        "4": "#FFFF00AA",   # Safety Car → yellow 
        "5": "#FF0000AA",   # Red flag
        "6": "#FFA500AA"    # VSC -> orange
    }

    status_labels = {
        "4": "Safety Car",
        "5": "Red Flag",
        "6": "VSC"
    }

    # Filter ts_df to match selected lap range
    ts_df = laps[['LapNumber', 'TrackStatus']].copy()
    ts_df = ts_df[
        (ts_df['LapNumber'] >= selected_laps[0]) &
        (ts_df['LapNumber'] <= selected_laps[1])
    ].copy()
    ts_df['TrackStatus'] = ts_df['TrackStatus'].fillna('1').astype(str)
    ts_df['LapNumber_plus1'] = ts_df['LapNumber'] + 1

    # Filter out normal track status
    ts_df = ts_df[ts_df['TrackStatus'] != '1'].copy()

    # Add label column for legend
    ts_df['TrackStatusLabel'] = ts_df['TrackStatus'].map(status_labels)

    # Get only the statuses that exist in your filtered data
    existing_statuses = ts_df['TrackStatus'].unique()
    domain = [status_labels[s] for s in existing_statuses if s in status_labels]
    range_colors = [status_colors[s] for s in existing_statuses if s in status_colors]

    # --- BACKGROUND RECTANGLES ---
    background = (
        alt.Chart(ts_df)
        .mark_rect(opacity=0.03, tooltip=None)  # Higher opacity for visibility
        .encode(
            x=alt.X('LapNumber:O'),
            x2='LapNumber_plus1:O',
            y=alt.value(0),
            y2=alt.value('height'),
            color=alt.Color('TrackStatusLabel:N',
                        scale=alt.Scale(domain=domain, range=range_colors),
                        legend=alt.Legend(title="Track Status", orient="top",symbolOpacity=1))
        )
    )

    final_chart = (background + chart + points).properties(
        width = 1200,
        height = 500
    ).resolve_scale(
        color='independent',
        strokeDash='independent'
    ).resolve_legend(
        color='independent'
    ).resolve_axis(
        x='shared',
        y='shared'
    )
    st.altair_chart(final_chart, use_container_width=True)

def tyre_strategies(year, event, session_type):
    fastf1.plotting.setup_mpl(color_scheme='fastf1')
    session = load_session_weather(year, event, session_type)
    
    # --- Drivers and laps ---
    drivers = session.drivers
    laps = session.laps
    
    # Sort drivers by their final race position
    driver_info = []
    for drv in drivers:
        abbr = session.get_driver(drv)["Abbreviation"]
        driver_laps = laps[laps['Driver'] == abbr]
        if not driver_laps.empty:
            final_position = driver_laps.iloc[-1]['Position']
            driver_info.append((abbr, final_position))
    
    # Sort by position (handle NaN values by putting them at the end)
    driver_info.sort(key=lambda x: (pd.isna(x[1]), x[1] if pd.notna(x[1]) else float('inf')))
    drivers = [d[0] for d in driver_info]

    # --- DRIVER SELECTION ---
    with st.expander("Select Drivers:", expanded=False):
        cols = st.columns(4)
        selected_drivers = []
        for idx, driver in enumerate(drivers):
            with cols[idx % 4]:
                is_selected = st.checkbox(
                    driver,
                    value=True,
                    key=f"race_position1_{driver}"
                )
                if is_selected:
                    selected_drivers.append(driver)

    if not selected_drivers:
        st.warning("Please select at least one driver")
        return

    # --- Lap selection slider ---
    min_lap = int(laps['LapNumber'].min())
    max_lap = int(laps['LapNumber'].max())
    selected_laps = st.select_slider(
        "Choose lap numbers:",
        options=list(range(min_lap, max_lap + 1)),
        value=(min_lap, max_lap),
        key="tyre_strat_laps"
    )

    # --- Filter laps for selected drivers and lap range ---
    driver_laps = laps[
        (laps['Driver'].isin(selected_drivers)) &
        (laps['LapNumber'] >= selected_laps[0]) &
        (laps['LapNumber'] <= selected_laps[1])
    ].copy()

    if driver_laps.empty:
        st.warning("No data available for the selected filters")
        return

    # --- Build stints summary ---
    stints = driver_laps.groupby(["Driver", "Stint", "Compound"]).size().reset_index(name='StintLength')

    # --- Compute x_start and x_end safely ---
    stints_sorted = pd.DataFrame()
    drivers_with_data = []  # Track drivers that actually have stint data
    for driver in selected_drivers:
        driver_stints = stints[stints['Driver'] == driver].sort_values("Stint").copy()
        if driver_stints.empty:
            continue
        drivers_with_data.append(driver)
        cumsum = driver_stints['StintLength'].cumsum()
        x_start = [selected_laps[0]] + list(selected_laps[0] + cumsum[:-1])
        driver_stints['x_start'] = x_start
        driver_stints['x_end'] = driver_stints['x_start'] + driver_stints['StintLength']
        stints_sorted = pd.concat([stints_sorted, driver_stints])
    stints = stints_sorted
    
    # Convert Driver column to categorical to preserve order
    stints['Driver'] = pd.Categorical(stints['Driver'], categories=drivers_with_data, ordered=True)

    if stints.empty:
        st.warning("No stint data to plot")
        return

    # Define shared y-axis encoding
    y_encoding = alt.Y('Driver:N',
                       sort=drivers_with_data,
                       title='Driver',
                       axis=alt.Axis(labelAngle=0))

    # --- Tyre strategy chart ---
    tyre_chart = alt.Chart(stints).mark_bar().encode(
        x=alt.X('x_start:Q',
                axis=alt.Axis(tickMinStep=1, title='Lap Number'),
                scale=alt.Scale(domain=[selected_laps[0], selected_laps[1] + 1])),
        x2='x_end:Q',
        y=y_encoding,
        color=alt.Color('Compound:N',
                        scale=alt.Scale(
                            domain=stints['Compound'].unique(),
                            range=[fastf1.plotting.get_compound_color(comp, session=session)
                                   for comp in stints['Compound'].unique()]
                        ),
                        legend=alt.Legend(title='Tyre Compound')),
        opacity=alt.value(0.8),
        tooltip=[
            alt.Tooltip('Driver:N', title='Driver'),
            alt.Tooltip('x_start:Q', title='Stint Start Lap'),
            alt.Tooltip('x_end:Q', title='Stint End Lap'),
            alt.Tooltip('Compound:N', title='Compound')
        ]
    ).properties(
        width=1000,
        height=max(300, len(drivers_with_data) * 40),
        title=f"{year} {event} Grand Prix - Tyre Strategies"
    )

    # --- Rainfall overlay ---
    weather_data = session.laps.get_weather_data().reset_index(drop=True)

    # Rename Time column to avoid duplicates
    if 'Time' in weather_data.columns:
        weather_data = weather_data.rename(columns={'Time': 'WeatherTime'})

    joined_filtered = pd.concat([laps.reset_index(drop=True), weather_data], axis=1)

    if "Rainfall" in joined_filtered.columns and joined_filtered['Rainfall'].any():
        # Get rainfall laps
        rain = joined_filtered[
            (joined_filtered['Rainfall'] > 0) & 
            (joined_filtered['LapNumber'] >= selected_laps[0]) & 
            (joined_filtered['LapNumber'] <= selected_laps[1])
        ][['LapNumber']].drop_duplicates().copy()
        
        if not rain.empty:
            rain['LapEnd'] = rain['LapNumber'] + 1
            
            # Create list of all drivers for the y-axis span
            # Add padding drivers to extend rain bars above and below
            extended_drivers = ['_top_padding'] + drivers_with_data + ['_bottom_padding']
            rain['Driver'] = [extended_drivers] * len(rain)
            rain_expanded = rain.explode('Driver')

            rain_chart = alt.Chart(rain_expanded).mark_rect(opacity=0.25).encode(
                x=alt.X('LapNumber:Q', 
                        title='Lap Number',
                        scale=alt.Scale(domain=[selected_laps[0], selected_laps[1] + 1])),
                x2='LapEnd:Q',
                y=alt.Y('Driver:N', 
                        sort=extended_drivers,
                        title='Driver',
                        axis=alt.Axis(labelAngle=0)),
                tooltip=[alt.Tooltip('LapNumber:Q', title='Rainfall Lap')],
                color=alt.value('lightblue')
            )

            # --- Layer charts ---
            final_chart = alt.layer(
                rain_chart,
                tyre_chart
            ).resolve_scale(
                color='independent',
                x='shared'  # Force shared x-axis scale
            )
        else:
            final_chart = tyre_chart
    else:
        final_chart = tyre_chart

    final_chart = final_chart.configure_axis(
        grid=True
    ).configure_title(
        fontSize=16,
        anchor='start'
    )

    st.altair_chart(final_chart, use_container_width=True)

def lap_time(year, event, session_type):
    session = load_session_light(year, event, session_type)
    drivers = [session.get_driver(drv)["Abbreviation"] for drv in session.drivers]

    # --- Driver selection ---
    with st.expander("Select Drivers: ", expanded=False):
        cols = st.columns(4)
        selected_drivers = []
        for idx, driver in enumerate(drivers):
            with cols[idx % 4]:
                default_value = idx < 3
                is_selected = st.checkbox(
                    driver,
                    value=default_value,
                    key=f"driver_laptime_{driver}"
                )
                if is_selected:
                    selected_drivers.append(driver)

    if not selected_drivers:
        st.warning("Please select at least one driver")
        return
    st.caption(f"Comparing {len(selected_drivers)} driver(s): {', '.join(selected_drivers)}")

    # --- Prepare full lap range ---
    max_lap_number = int(session.laps['LapNumber'].max())
    all_laps = pd.DataFrame({'LapNumber': range(1, max_lap_number + 1)})

    # --- Prepare driver data ---
    driver_dfs = []
    for driver in selected_drivers:
        driver_laps = session.laps.pick_drivers(driver).reset_index()
        if driver_laps.empty:
            continue

        driver_laps = driver_laps[driver_laps['LapNumber'] > 0]  # remove negative laps

        # Lap times
        driver_laps['LapTimeSeconds'] = driver_laps['LapTime'].dt.total_seconds()
        driver_laps['LapTimeFormatted'] = driver_laps['LapTimeSeconds'].apply(
            lambda x: f"{int(x//60)}:{x%60:06.3f}" if pd.notna(x) else "N/A"
        )

        # Driver color
        style = fastf1.plotting.get_driver_style(driver, style=['color'], session=session)
        driver_laps['Driver'] = driver
        driver_laps['Color'] = style['color']

        # Merge with all laps to show all laps even if missing for this driver
        df_full = all_laps.merge(
            driver_laps[['LapNumber', 'LapTimeSeconds', 'LapTimeFormatted', 'Driver', 'Color']],
            on='LapNumber',
            how='left'
        )
        df_full['Driver'] = driver 
        driver_dfs.append(df_full)

    df = pd.concat(driver_dfs, ignore_index=True)

    if df.empty:
        st.warning("No valid lap data found")
        return

    chart = alt.Chart(df).mark_line(strokeWidth=2.5, point=True).encode(
        x=alt.X(
            'LapNumber:Q',
            title='Lap Number',
            scale=alt.Scale(domain=[1, max_lap_number]),
            axis=alt.Axis(tickMinStep=1)
        ),
        y=alt.Y(
            'LapTimeSeconds:Q',
            title='Lap Time',
            scale=alt.Scale(zero=False),
            axis=alt.Axis(
                labelExpr="floor(datum.value / 60) + ':' + (datum.value % 60 < 10 ? '0' : '') + format(datum.value % 60, '.3f')"
            )
        ),
        color=alt.Color(
            'Driver:N',
            scale=alt.Scale(
                domain=df['Driver'].dropna().unique().tolist(),
                range=df.groupby('Driver')['Color'].first().tolist()
            ),
            legend=alt.Legend(title='Driver', orient='right')
        ),
        tooltip=[
            alt.Tooltip('Driver:N', title='Driver'),
            alt.Tooltip('LapNumber:Q', title='Lap'),
            alt.Tooltip('LapTimeFormatted:N', title='Lap Time')
        ]
    ).properties(
        height=450,
        title={
            "text": "Lap Time Progression",
            "fontSize": 16,
            "font": "Arial",
            "fontWeight": "bold"
        }
    ).configure_axis(
        labelFontSize=11,
        titleFontSize=13,
        gridOpacity=0.3
    ).configure_legend(
        labelFontSize=11,
        titleFontSize=12
    ).interactive()

    st.altair_chart(chart, use_container_width=True, theme="streamlit")
def telemetry_driver_comparison(year, event, session_type):
    session = load_session(year, event, session_type)

    drivers = [session.get_driver(drv)["Abbreviation"] for drv in session.drivers]
    laps = session.laps

    # --- DRIVER SELECTION ---
    col1, col2 = st.columns(2)
    with col1:
        driver_1 = st.selectbox("Driver 1:", drivers, index=0, key="driver_1")
    with col2:
        driver_2 = st.selectbox("Driver 2:", drivers, index=1, key="driver_2")

    selected_drivers = [driver_1, driver_2]

    # --- Default to fastest lap of driver 1 ---
    fastest_lap = laps.pick_drivers(driver_1).pick_fastest()
    lap_numbers = [int(lap) for lap in laps['LapNumber'].unique()]
    fastest_index = lap_numbers.index(int(fastest_lap['LapNumber']))
    selected_lap = int(st.selectbox("Select lap: (default to fastest lap of Driver 1)", lap_numbers, index=fastest_index))
    st.markdown(f"### Comparing {driver_1} vs {driver_2} in lap {selected_lap}")

    # --- Driver 1 & Driver 2 overview ---
    lap_1 = laps.pick_drivers(driver_1)
    lap_1 = lap_1[lap_1['LapNumber'].astype(int) == selected_lap].reset_index(drop=True)
    lap_2 = laps.pick_drivers(driver_2)
    lap_2 = lap_2[lap_2['LapNumber'].astype(int) == selected_lap].reset_index(drop=True)

    if lap_1.empty or lap_2.empty:
        st.warning(f"Telemetry not available for lap {selected_lap} for one or both drivers")
        return

    stint_1 = int(lap_1['Stint'].iloc[0])
    tyre_1 = lap_1['Compound'].iloc[0]

    stint_2 = int(lap_2['Stint'].iloc[0])
    tyre_2 = lap_2['Compound'].iloc[0]

    st.markdown(f"#### {driver_1} Overview")
    st.markdown(f"**🥇 Tyre Compound:** {tyre_1}  |  **🏁 Stint:** {stint_1}")
    st.markdown(f"#### {driver_2} Overview")
    st.markdown(f"**🥈 Tyre Compound:** {tyre_2}  |  **🏁 Stint:** {stint_2}")
    st.divider()

    # --- Prepare telemetry data ---
    dfs = []
    for idx, driver in enumerate(selected_drivers):
        driver_lap = laps.pick_drivers(driver)
        driver_lap = driver_lap[driver_lap['LapNumber'].astype(int) == selected_lap]
        tel = driver_lap.get_telemetry()
        tel = tel[tel["Distance"] >= 0].copy()
        tel["Driver"] = driver
        tel["Color"] = fastf1.plotting.get_driver_style(driver, style=['color'], session=session)['color']
        # Assign line style: first driver solid, second driver dashed
        tel["LineStyle"] = "solid" if idx == 0 else "dashed"
        # Assign opacity: first driver slightly transparent (0.7), second driver full opacity (1.0)
        tel["Opacity"] = 0.7 if idx == 0 else 1.0
        dfs.append(tel)

    df = pd.concat(dfs, ignore_index=True)

    # --- Function to create chart with zoom/pan and line tooltips ---
    def create_chart(y_col, title, fmt=".1f"):
        return alt.Chart(df).mark_line(strokeWidth=2.5).encode(
            x=alt.X("Distance:Q", title="Distance (m)"),
            y=alt.Y(f"{y_col}:Q", title=title),
            color=alt.Color(
                "Driver:N",
                scale=alt.Scale(
                    domain=df['Driver'].unique().tolist(),
                    range=df.groupby('Driver')['Color'].first().tolist()
                ),
                legend=alt.Legend(title='Driver')
            ),
            strokeDash=alt.StrokeDash(
                "LineStyle:N",
                scale=alt.Scale(
                    domain=["solid", "dashed"],
                    range=[[1, 0], [5, 5]]  # [1,0] = solid, [5,5] = dashed
                ),
                legend=None 
            ),
            opacity=alt.Opacity(
                "Opacity:Q",
                scale=None, 
                legend=None
            ),
            tooltip=[alt.Tooltip("Driver:N"), alt.Tooltip("Distance:Q", format=".2f"), alt.Tooltip(f"{y_col}:Q", format=fmt)]
        ).interactive()  

    # --- Create charts ---
    speed_chart = create_chart("Speed", "Speed (km/h)")
    brake_chart = create_chart("Brake", "Brake")
    throttle_chart = create_chart("Throttle", "Throttle (%)")

    # --- Combine charts vertically with shared color scale ---
    final_chart = alt.vconcat(
        speed_chart,
        brake_chart,
        throttle_chart
    ).resolve_scale(color="shared")

    st.altair_chart(final_chart, use_container_width=True, theme="streamlit")
def tyre_degradation(year, event, session_type):
    
    session = load_session(year, event, session_type)
    drivers = [session.get_driver(drv)["Abbreviation"] for drv in session.drivers]
    laps = session.laps

    # --- DRIVER SELECTION ---
    selected_driver = st.selectbox("Select driver: ", drivers, index=0)
    driver_laps = laps.pick_drivers(selected_driver)
    stint_numbers = driver_laps['Stint'].unique().astype(int)
    selected_stint = st.selectbox(f"Select Stint for driver {selected_driver}", stint_numbers, index=0)
    stint_lap = driver_laps[driver_laps['Stint'] == selected_stint]

    # --- Stint info ---
    min_lap_num = int(stint_lap['LapNumber'].min())
    max_lap_num = int(stint_lap['LapNumber'].max())
    compound = stint_lap['Compound'].iloc[0]
    st.markdown(f"**🛞 Tyre Compound:** {compound}  |  **Stint Start Lap:** {min_lap_num}  |  **Stint End Lap:** {max_lap_num}")

    # --- Get telemetry for first and last lap of stint ---
    min_lap = stint_lap[stint_lap['LapNumber'] == min_lap_num].iloc[0]
    max_lap = stint_lap[stint_lap['LapNumber'] == max_lap_num].iloc[0]
    tel_min = min_lap.get_telemetry()
    tel_max = max_lap.get_telemetry()
    tel_min["Lap"] = f"Lap {min_lap_num}"
    tel_max["Lap"] = f"Lap {max_lap_num}"

    df = pd.concat([tel_min, tel_max], ignore_index=True)
    df = df[df["Distance"] >= 0].copy()  # remove negative distances

    # --- Base chart ---
    base = alt.Chart(df).encode(x=alt.X("Distance:Q", title="Distance (m)"))

    # --- Function to create individual chart ---
    def create_chart(y_col, title, fmt=".1f"):
        return base.mark_line(opacity=0.7, strokeWidth=2.5).encode(
            y=alt.Y(f"{y_col}:Q", title=title),
            color=alt.Color(
                "Lap:N",
                scale=alt.Scale(range=["red", "blue"]),
                legend=alt.Legend(title='Lap')
            ),
            tooltip=[
                alt.Tooltip("Lap:N"),
                alt.Tooltip("Distance:Q", format=".2f"),
                alt.Tooltip(f"{y_col}:Q", format=fmt)
            ]
        ).interactive().properties(height=200, title=title)

    speed_chart = create_chart("Speed", f"Speed Comparison: Stint {selected_stint}")
    brake_chart = create_chart("Brake", f"Brake Comparison: Stint {selected_stint}")
    throttle_chart = create_chart("Throttle", f"Throttle Comparison: Stint {selected_stint}")

    # --- Combine charts vertically ---
    final_chart = alt.vconcat(
        speed_chart,
        brake_chart,
        throttle_chart
    ).resolve_scale(color="shared")

    st.altair_chart(final_chart, use_container_width=True)





