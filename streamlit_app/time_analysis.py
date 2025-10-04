"""
Time-based analysis module for NYC Yellow Taxi data.
Provides temporal insights for optimal trip timing and demand patterns.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


def add_time_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add time-derived columns for analysis."""
    df = df.copy()
    df['pickup_weekday'] = df['tpep_pickup_datetime'].dt.weekday  # 0=Mon, 6=Sun
    df['is_weekend'] = df['pickup_weekday'].isin([5, 6])
    
    # Earnings efficiency metric (handle division by zero)
    df['earnings_per_min'] = df['fare_amount'] / df['trip_duration_min']
    df['earnings_per_min'] = df['earnings_per_min'].replace([float('inf'), -float('inf')], pd.NA)
    
    return df


def time_kpi_cards(df: pd.DataFrame) -> None:
    """Display top-level time-based KPIs."""
    # Best hour by average fare
    hourly_fare = df.groupby('pickup_hour')['fare_amount'].mean()
    best_hour = int(hourly_fare.idxmax())
    best_hour_fare = float(hourly_fare.max())
    
    # Busiest hour
    hourly_trips = df.groupby('pickup_hour').size()
    busiest_hour = int(hourly_trips.idxmax())
    busiest_count = int(hourly_trips.max())
    
    # Best day
    daily_trips = df.groupby('pickup_dow').size()
    # Reorder to have proper week order
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    daily_trips = daily_trips.reindex([d for d in day_order if d in daily_trips.index])
    best_day = daily_trips.idxmax()
    
    # Weekend vs weekday
    weekend_trips = int(df[df['is_weekend']].shape[0])
    weekend_pct = (weekend_trips / len(df)) * 100 if len(df) > 0 else 0
    
    # Best efficiency
    efficiency = df.groupby('pickup_hour')['earnings_per_min'].mean()
    most_efficient_hour = int(efficiency.idxmax())
    
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Best Earning Hour", f"{best_hour}:00", f"${best_hour_fare:.2f} avg")
    c2.metric("Peak Demand Hour", f"{busiest_hour}:00", f"{busiest_count:,} trips")
    c3.metric("Busiest Day", best_day)
    c4.metric("Weekend Share", f"{weekend_pct:.1f}%", f"{weekend_trips:,} trips")
    c5.metric("Most Efficient Hour", f"{most_efficient_hour}:00", "$/min highest")


def section_hourly_patterns(df: pd.DataFrame) -> None:
    """Hourly demand and revenue patterns with detailed explanations."""
    st.markdown("""
    ### 📈 Hourly Demand & Revenue Patterns
    
    **Understanding the curves below:**
    - **Blue line (Trips)**: Shows raw demand volume throughout the day. Peak hours indicate when most passengers need rides.
    - **Red line (Revenue)**: Total earnings per hour. High revenue hours are prime time for drivers.
    - **Key insight**: Look for hours where both lines peak - these are optimal working hours with high demand AND high earnings.
    """)
    
    hourly = df.groupby('pickup_hour', as_index=False).agg(
        Trips=('VendorID', 'count'),
        Revenue=('total_amount', 'sum'),
        Avg_Fare=('fare_amount', 'mean')
    )
    
    # Create dual-axis chart
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=hourly['pickup_hour'],
        y=hourly['Trips'],
        name='Trips',
        mode='lines+markers',
        line=dict(color='#1f77b4', width=3),
        yaxis='y1'
    ))
    
    fig.add_trace(go.Scatter(
        x=hourly['pickup_hour'],
        y=hourly['Revenue'],
        name='Revenue',
        mode='lines+markers',
        line=dict(color='#d62728', width=3),
        yaxis='y2'
    ))
    
    fig.update_layout(
        title='Trips and Revenue by Hour of Day',
        xaxis=dict(title='Hour of Day', tickmode='linear', tick0=0, dtick=2),
        yaxis=dict(title='Number of Trips', side='left', showgrid=False),
        yaxis2=dict(title='Revenue ($)', side='right', overlaying='y', showgrid=False, tickprefix='$'),
        hovermode='x unified',
        height=450
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Add average fare line chart
    fig2 = px.line(
        hourly,
        x='pickup_hour',
        y='Avg_Fare',
        markers=True,
        title='Average Fare by Hour',
        labels={'pickup_hour': 'Hour of Day', 'Avg_Fare': 'Average Fare ($)'}
    )
    fig2.update_layout(
        xaxis=dict(tickmode='linear', tick0=0, dtick=2),
        yaxis_tickprefix='$',
        height=350
    )
    fig2.update_traces(line_color='#2ca02c', line_width=3)
    
    st.plotly_chart(fig2, use_container_width=True)
    
    st.info("💡 **Driver Tip**: Hours with higher average fares often indicate longer trips or surge pricing. Combine this with trip volume to find your sweet spot.")


def section_heatmap(df: pd.DataFrame) -> None:
    """Hour × Day heatmap showing demand patterns."""
    st.markdown("""
    ### 🔥 Demand Heatmap: Hour × Day of Week
    
    **How to read this heatmap:**
    - **Darker red = Higher demand** (more trips in that hour+day combination)
    - **Lighter yellow = Lower demand**
    - **Rows**: Hours of the day (0 = midnight, 12 = noon, 23 = 11 PM)
    - **Columns**: Days of the week
    
    **What to look for:**
    - Dark red blocks = Prime earning opportunities
    - Patterns across rows show daily rhythms (e.g., rush hours)
    - Patterns down columns show weekly rhythms (e.g., weekend vs weekday)
    """)
    
    # Create pivot table for heatmap
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    df_filtered = df[df['pickup_dow'].isin(day_order)].copy()
    
    heatmap_data = df_filtered.groupby(['pickup_hour', 'pickup_dow']).size().reset_index(name='Trips')
    heatmap_pivot = heatmap_data.pivot(index='pickup_hour', columns='pickup_dow', values='Trips')
    heatmap_pivot = heatmap_pivot.reindex(columns=day_order)
    
    fig = px.imshow(
        heatmap_pivot,
        labels=dict(x="Day of Week", y="Hour of Day", color="Trips"),
        x=heatmap_pivot.columns,
        y=heatmap_pivot.index,
        color_continuous_scale='YlOrRd',
        aspect='auto',
        title='Trip Volume Heatmap: When is NYC Busiest?'
    )
    
    fig.update_layout(
        xaxis_title="Day of Week",
        yaxis_title="Hour of Day",
        height=600,
        yaxis=dict(tickmode='linear', tick0=0, dtick=1)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Add fare heatmap
    st.markdown("#### 💰 Average Fare Heatmap")
    fare_data = df_filtered.groupby(['pickup_hour', 'pickup_dow'])['fare_amount'].mean().reset_index()
    fare_pivot = fare_data.pivot(index='pickup_hour', columns='pickup_dow', values='fare_amount')
    fare_pivot = fare_pivot.reindex(columns=day_order)
    
    fig2 = px.imshow(
        fare_pivot,
        labels=dict(x="Day of Week", y="Hour of Day", color="Avg Fare ($)"),
        x=fare_pivot.columns,
        y=fare_pivot.index,
        color_continuous_scale='Viridis',
        aspect='auto',
        title='Average Fare Heatmap: When Do Trips Pay More?'
    )
    
    fig2.update_layout(
        xaxis_title="Day of Week",
        yaxis_title="Hour of Day",
        height=600,
        yaxis=dict(tickmode='linear', tick0=0, dtick=1)
    )
    
    st.plotly_chart(fig2, use_container_width=True)
    
    st.success("🎯 **Strategy**: Target dark red (high volume) + green/yellow (high fare) zones for maximum earnings!")


def section_weekday_weekend(df: pd.DataFrame) -> None:
    """Compare weekday vs weekend patterns."""
    st.markdown("""
    ### 📅 Weekday vs Weekend Analysis
    
    **Why this matters:**
    - **Weekdays**: Business travel, commuter rush hours, predictable patterns
    - **Weekends**: Leisure travel, late-night entertainment, different peak hours
    
    Understanding these differences helps drivers optimize their schedules and target the right passengers at the right times.
    """)
    
    # Split data
    weekday_df = df[~df['is_weekend']]
    weekend_df = df[df['is_weekend']]
    
    # Hourly comparison
    weekday_hourly = weekday_df.groupby('pickup_hour').size().reset_index(name='Trips')
    weekday_hourly['Type'] = 'Weekday'
    
    weekend_hourly = weekend_df.groupby('pickup_hour').size().reset_index(name='Trips')
    weekend_hourly['Type'] = 'Weekend'
    
    combined = pd.concat([weekday_hourly, weekend_hourly])
    
    fig = px.line(
        combined,
        x='pickup_hour',
        y='Trips',
        color='Type',
        markers=True,
        title='Hourly Trip Volume: Weekday vs Weekend',
        labels={'pickup_hour': 'Hour of Day', 'Trips': 'Number of Trips'},
        color_discrete_map={'Weekday': '#1f77b4', 'Weekend': '#ff7f0e'}
    )
    
    fig.update_layout(
        xaxis=dict(tickmode='linear', tick0=0, dtick=2),
        height=450,
        hovermode='x unified'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Comparison metrics
    st.markdown("#### 📊 Key Metrics Comparison")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Weekday Stats**")
        wd_trips = len(weekday_df)
        wd_avg_fare = weekday_df['fare_amount'].mean()
        wd_avg_distance = weekday_df['trip_distance'].mean()
        wd_avg_duration = weekday_df['trip_duration_min'].mean()
        
        metrics_df = pd.DataFrame({
            'Metric': ['Total Trips', 'Avg Fare', 'Avg Distance', 'Avg Duration'],
            'Value': [
                f"{wd_trips:,}",
                f"${wd_avg_fare:.2f}",
                f"{wd_avg_distance:.2f} mi",
                f"{wd_avg_duration:.1f} min"
            ]
        })
        st.dataframe(metrics_df, hide_index=True, use_container_width=True)
    
    with col2:
        st.markdown("**Weekend Stats**")
        we_trips = len(weekend_df)
        we_avg_fare = weekend_df['fare_amount'].mean()
        we_avg_distance = weekend_df['trip_distance'].mean()
        we_avg_duration = weekend_df['trip_duration_min'].mean()
        
        metrics_df = pd.DataFrame({
            'Metric': ['Total Trips', 'Avg Fare', 'Avg Distance', 'Avg Duration'],
            'Value': [
                f"{we_trips:,}",
                f"${we_avg_fare:.2f}",
                f"{we_avg_distance:.2f} mi",
                f"{we_avg_duration:.1f} min"
            ]
        })
        st.dataframe(metrics_df, hide_index=True, use_container_width=True)
    
    # Insights
    fare_diff_pct = ((we_avg_fare - wd_avg_fare) / wd_avg_fare) * 100
    fare_direction = "higher" if fare_diff_pct > 0 else "lower"
    
    st.info(f"💡 **Insight**: Weekend fares are {abs(fare_diff_pct):.1f}% {fare_direction} than weekdays on average. Weekend trips tend to be more leisure-focused with different time patterns.")


def section_optimal_windows(df: pd.DataFrame) -> None:
    """Find and display optimal time windows for drivers."""
    st.markdown("""
    ### 🎯 Optimal Time Windows for Maximum Earnings
    
    **What makes a time window "optimal"?**
    - **High trip volume**: Steady stream of customers (shorter wait times)
    - **Good average fare**: Each trip is worth your time
    - **Efficiency score**: Revenue per minute of trip time
    
    The table below ranks hour+day combinations by different metrics to help you plan your shifts strategically.
    """)
    
    # Calculate metrics for each hour+day combo
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    df_filtered = df[df['pickup_dow'].isin(day_order)].copy()
    
    combo_stats = df_filtered.groupby(['pickup_dow', 'pickup_hour'], as_index=False).agg(
        Trips=('VendorID', 'count'),
        Avg_Fare=('fare_amount', 'mean'),
        Total_Revenue=('fare_amount', 'sum'),
        Avg_Duration=('trip_duration_min', 'mean'),
        Efficiency=('earnings_per_min', 'mean')
    )
    
    # Ensure numeric types and drop rows with NaN efficiency
    combo_stats['Efficiency'] = pd.to_numeric(combo_stats['Efficiency'], errors='coerce')
    combo_stats['Avg_Fare'] = pd.to_numeric(combo_stats['Avg_Fare'], errors='coerce')
    combo_stats['Trips'] = pd.to_numeric(combo_stats['Trips'], errors='coerce')
    combo_stats = combo_stats.dropna(subset=['Efficiency', 'Avg_Fare', 'Trips'])
    
    combo_stats['Time_Window'] = combo_stats['pickup_dow'] + ' ' + combo_stats['pickup_hour'].astype(str) + ':00'
    
    # Top by different metrics
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🏆 Top 10: Highest Volume (Most Trips)")
        st.caption("Best for: Consistent work, shorter wait between fares")
        
        top_volume = combo_stats.nlargest(10, 'Trips')[['Time_Window', 'Trips', 'Avg_Fare']].reset_index(drop=True)
        top_volume.index = top_volume.index + 1
        top_volume.columns = ['Time Window', 'Trips', 'Avg Fare']
        top_volume['Avg Fare'] = top_volume['Avg Fare'].apply(lambda x: f"${x:.2f}")
        st.dataframe(top_volume, use_container_width=True, height=390)
    
    with col2:
        st.markdown("#### 💰 Top 10: Highest Average Fare")
        st.caption("Best for: Maximizing per-trip earnings, longer trips")
        
        top_fare = combo_stats.nlargest(10, 'Avg_Fare')[['Time_Window', 'Avg_Fare', 'Trips']].reset_index(drop=True)
        top_fare.index = top_fare.index + 1
        top_fare.columns = ['Time Window', 'Avg Fare', 'Trips']
        top_fare['Avg Fare'] = top_fare['Avg Fare'].apply(lambda x: f"${x:.2f}")
        st.dataframe(top_fare, use_container_width=True, height=390)
    
    st.markdown("#### ⚡ Top 15: Best Efficiency (Revenue per Minute)")
    st.caption("Best for: Maximizing hourly earnings, short trips with good fares")
    
    top_efficiency = combo_stats.nlargest(15, 'Efficiency')[['Time_Window', 'Efficiency', 'Avg_Fare', 'Trips']].reset_index(drop=True)
    top_efficiency.index = top_efficiency.index + 1
    top_efficiency.columns = ['Time Window', '$/min', 'Avg Fare', 'Trips']
    top_efficiency['$/min'] = top_efficiency['$/min'].apply(lambda x: f"${x:.2f}")
    top_efficiency['Avg Fare'] = top_efficiency['Avg Fare'].apply(lambda x: f"${x:.2f}")
    
    st.dataframe(top_efficiency, use_container_width=True, height=390)
    
    st.success("""
    🚕 **Driver Recommendations**:
    - **New drivers**: Start with high-volume windows for consistent experience
    - **Experienced drivers**: Target high-efficiency windows to maximize earnings per hour
    - **Part-time drivers**: Focus on specific high-fare windows that fit your schedule
    """)


def render_time_analysis(df: pd.DataFrame) -> None:
    """Main function to render all time analysis sections."""
    st.title("⏰ Time-Based Analysis")
    st.markdown("""
    Discover the **best times to drive** and understand **temporal demand patterns** in NYC's taxi ecosystem.
    This analysis helps drivers maximize earnings and passengers understand demand dynamics.
    """)
    
    # Add time features
    df = add_time_features(df)
    
    # KPI Cards at top
    time_kpi_cards(df)
    
    st.divider()
    
    # Section 1: Hourly patterns
    section_hourly_patterns(df)
    
    st.divider()
    
    # Section 2: Heatmap
    section_heatmap(df)
    
    st.divider()
    
    # Section 3: Weekday vs Weekend
    section_weekday_weekend(df)
    
    st.divider()
    
    # Section 4: Optimal windows
    section_optimal_windows(df)

