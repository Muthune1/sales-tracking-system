import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

# Page config
st.set_page_config(
    page_title="Sales Team Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .kpi-value {
        font-size: 2.5rem;
        font-weight: bold;
    }
    .kpi-label {
        font-size: 1rem;
        opacity: 0.9;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data(file_path):
    """Load data from Excel file"""
    all_data = []
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    
    for day in days:
        try:
            df = pd.read_excel(file_path, sheet_name=day)
            df['Day'] = day
            all_data.append(df)
        except:
            pass
    
    if all_data:
        combined_df = pd.concat(all_data, ignore_index=True)
        return combined_df
    return pd.DataFrame()

def parse_time(time_str):
    """Convert time string to minutes from midnight"""
    if pd.isna(time_str):
        return None
    try:
        h, m = map(int, str(time_str).split(':'))
        return h * 60 + m
    except:
        return None

def calculate_duration(check_in, check_out):
    """Calculate duration in minutes"""
    ci = parse_time(check_in)
    co = parse_time(check_out)
    if ci is not None and co is not None:
        return co - ci
    return 0

def get_location_coordinates(location_name):
    """Get approximate coordinates for Bengaluru locations"""
    coordinates = {
        "MG Road": (12.9716, 77.5946),
        "Koramangala": (12.9352, 77.6245),
        "Indiranagar": (12.9784, 77.6408),
        "Whitefield": (12.9698, 77.7499),
        "Electronic City": (12.8456, 77.6603),
        "Jayanagar": (12.9250, 77.5838),
        "Malleswaram": (13.0033, 77.5667),
        "BTM Layout": (12.9165, 77.6101),
        "HSR Layout": (12.9082, 77.6476),
        "Marathahalli": (12.9591, 77.6974),
        "Banashankari": (12.9250, 77.5483),
        "Rajajinagar": (12.9916, 77.5544),
        "JP Nagar": (12.9079, 77.5857),
        "Yelahanka": (13.1007, 77.5963),
        "Hebbal": (13.0358, 77.5970)
    }
    return coordinates.get(location_name, (12.9716, 77.5946))

def main():
    st.markdown('<div class="main-header">📊 Sales Team Performance Dashboard</div>', unsafe_allow_html=True)
    
    # Load data
    df = load_data('/home/claude/sales_personnel_tracking.xlsx')
    
    if df.empty:
        st.error("No data found. Please check the Excel file.")
        return
    
    # Sidebar filters
    st.sidebar.header("🔍 Filters")
    
    # Day filter
    days_available = df['Day'].unique().tolist()
    selected_days = st.sidebar.multiselect(
        "Select Days",
        options=days_available,
        default=days_available
    )
    
    # Personnel filter
    personnel_list = df['Personnel Name'].dropna().unique().tolist()
    selected_personnel = st.sidebar.multiselect(
        "Select Personnel",
        options=personnel_list,
        default=personnel_list
    )
    
    # Filter data
    filtered_df = df[
        (df['Day'].isin(selected_days)) & 
        (df['Personnel Name'].isin(selected_personnel))
    ]
    
    # View selector
    view_mode = st.sidebar.radio(
        "📋 View Mode",
        ["Team Overview", "Individual Performance", "Location Analysis", "Daily Timeline"]
    )
    
    if view_mode == "Team Overview":
        show_team_overview(filtered_df)
    elif view_mode == "Individual Performance":
        show_individual_performance(filtered_df, personnel_list)
    elif view_mode == "Location Analysis":
        show_location_analysis(filtered_df)
    else:
        show_daily_timeline(filtered_df)

def show_team_overview(df):
    """Display team-wide metrics and charts"""
    st.header("👥 Team Overview")
    
    # Calculate metrics
    total_personnel = df['Personnel Name'].nunique()
    total_visits = len(df)
    total_days = df['Day'].nunique()
    
    # Calculate work hours
    df['Duration'] = df.apply(lambda x: calculate_duration(x['Check-In Time'], x['Check-Out Time']), axis=1)
    avg_visit_duration = df['Duration'].mean()
    
    # Top row KPIs
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Personnel", total_personnel, delta=None)
    with col2:
        st.metric("Total Visits", total_visits, delta=None)
    with col3:
        st.metric("Avg Visits/Day/Person", f"{total_visits/(total_personnel*total_days):.1f}", delta=None)
    with col4:
        st.metric("Avg Visit Duration", f"{avg_visit_duration:.0f} min", delta=None)
    
    st.markdown("---")
    
    # Charts row 1
    col1, col2 = st.columns(2)
    
    with col1:
        # Visits by personnel
        visits_by_person = df.groupby('Personnel Name').size().reset_index(name='Total Visits')
        visits_by_person = visits_by_person.sort_values('Total Visits', ascending=False)
        
        fig1 = px.bar(
            visits_by_person,
            x='Personnel Name',
            y='Total Visits',
            title='Total Visits by Personnel',
            color='Total Visits',
            color_continuous_scale='Blues'
        )
        fig1.update_layout(xaxis_tickangle=-45, height=400)
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        # Visits by day
        visits_by_day = df.groupby('Day').size().reset_index(name='Total Visits')
        day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
        visits_by_day['Day'] = pd.Categorical(visits_by_day['Day'], categories=day_order, ordered=True)
        visits_by_day = visits_by_day.sort_values('Day')
        
        fig2 = px.line(
            visits_by_day,
            x='Day',
            y='Total Visits',
            title='Daily Visit Trends',
            markers=True
        )
        fig2.update_traces(line_color='#667eea', line_width=3, marker_size=10)
        fig2.update_layout(height=400)
        st.plotly_chart(fig2, use_container_width=True)
    
    # Charts row 2
    col1, col2 = st.columns(2)
    
    with col1:
        # Top locations
        top_locations = df.groupby('Location').size().reset_index(name='Visits')
        top_locations = top_locations.sort_values('Visits', ascending=False).head(10)
        
        fig3 = px.bar(
            top_locations,
            x='Visits',
            y='Location',
            orientation='h',
            title='Top 10 Visited Locations',
            color='Visits',
            color_continuous_scale='Viridis'
        )
        fig3.update_layout(height=400)
        st.plotly_chart(fig3, use_container_width=True)
    
    with col2:
        # Heatmap of visits by person and day
        pivot_data = df.groupby(['Personnel Name', 'Day']).size().reset_index(name='Visits')
        pivot_table = pivot_data.pivot(index='Personnel Name', columns='Day', values='Visits').fillna(0)
        
        day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
        pivot_table = pivot_table.reindex(columns=[d for d in day_order if d in pivot_table.columns])
        
        fig4 = px.imshow(
            pivot_table,
            labels=dict(x="Day", y="Personnel", color="Visits"),
            title='Visit Heatmap (Person × Day)',
            color_continuous_scale='YlOrRd',
            aspect='auto'
        )
        fig4.update_layout(height=400)
        st.plotly_chart(fig4, use_container_width=True)
    
    # Location map
    st.subheader("🗺️ All Visit Locations")
    location_counts = df.groupby('Location').size().reset_index(name='Visit Count')
    location_counts['lat'] = location_counts['Location'].apply(lambda x: get_location_coordinates(x)[0])
    location_counts['lon'] = location_counts['Location'].apply(lambda x: get_location_coordinates(x)[1])
    
    fig_map = px.scatter_mapbox(
        location_counts,
        lat='lat',
        lon='lon',
        size='Visit Count',
        color='Visit Count',
        hover_name='Location',
        hover_data={'Visit Count': True, 'lat': False, 'lon': False},
        color_continuous_scale='Reds',
        size_max=30,
        zoom=10,
        title='Visit Locations in Bengaluru'
    )
    fig_map.update_layout(
        mapbox_style='open-street-map',
        height=500
    )
    st.plotly_chart(fig_map, use_container_width=True)

def show_individual_performance(df, personnel_list):
    """Display individual performance metrics"""
    st.header("👤 Individual Performance")
    
    selected_person = st.selectbox("Select Personnel", personnel_list)
    
    person_df = df[df['Personnel Name'] == selected_person]
    
    if person_df.empty:
        st.warning(f"No data available for {selected_person}")
        return
    
    # Metrics
    total_visits = len(person_df)
    days_worked = person_df['Day'].nunique()
    unique_locations = person_df['Location'].nunique()
    
    person_df['Duration'] = person_df.apply(lambda x: calculate_duration(x['Check-In Time'], x['Check-Out Time']), axis=1)
    avg_duration = person_df['Duration'].mean()
    total_field_time = person_df['Duration'].sum()
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Total Visits", total_visits)
    with col2:
        st.metric("Days Worked", days_worked)
    with col3:
        st.metric("Avg Visits/Day", f"{total_visits/days_worked:.1f}")
    with col4:
        st.metric("Unique Locations", unique_locations)
    with col5:
        st.metric("Total Field Time", f"{total_field_time/60:.1f} hrs")
    
    st.markdown("---")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Daily visits
        daily_visits = person_df.groupby('Day').size().reset_index(name='Visits')
        day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
        daily_visits['Day'] = pd.Categorical(daily_visits['Day'], categories=day_order, ordered=True)
        daily_visits = daily_visits.sort_values('Day')
        
        fig1 = px.bar(
            daily_visits,
            x='Day',
            y='Visits',
            title=f'{selected_person} - Daily Visits',
            color='Visits',
            color_continuous_scale='Blues'
        )
        fig1.update_layout(height=400)
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        # Time spent by location
        location_time = person_df.groupby('Location')['Duration'].sum().reset_index()
        location_time = location_time.sort_values('Duration', ascending=False).head(10)
        location_time['Duration (hrs)'] = location_time['Duration'] / 60
        
        fig2 = px.pie(
            location_time,
            values='Duration (hrs)',
            names='Location',
            title=f'{selected_person} - Time by Location (Top 10)'
        )
        fig2.update_layout(height=400)
        st.plotly_chart(fig2, use_container_width=True)
    
    # Visit timeline
    st.subheader("📅 Visit Timeline")
    
    timeline_df = person_df[['Day', 'Location', 'Check-In Time', 'Check-Out Time', 'Duration']].copy()
    timeline_df['Duration (min)'] = timeline_df['Duration']
    timeline_df = timeline_df.drop('Duration', axis=1)
    
    st.dataframe(
        timeline_df,
        use_container_width=True,
        hide_index=True
    )
    
    # Individual location map
    st.subheader(f"🗺️ {selected_person}'s Visit Locations")
    
    person_locations = person_df.groupby('Location').size().reset_index(name='Visits')
    person_locations['lat'] = person_locations['Location'].apply(lambda x: get_location_coordinates(x)[0])
    person_locations['lon'] = person_locations['Location'].apply(lambda x: get_location_coordinates(x)[1])
    
    fig_map = px.scatter_mapbox(
        person_locations,
        lat='lat',
        lon='lon',
        size='Visits',
        color='Visits',
        hover_name='Location',
        hover_data={'Visits': True, 'lat': False, 'lon': False},
        color_continuous_scale='Greens',
        size_max=25,
        zoom=10
    )
    fig_map.update_layout(
        mapbox_style='open-street-map',
        height=500
    )
    st.plotly_chart(fig_map, use_container_width=True)

def show_location_analysis(df):
    """Display location-based analytics"""
    st.header("📍 Location Analysis")
    
    # Location metrics
    location_stats = df.groupby('Location').agg({
        'Personnel Name': 'count',
        'Check-In Time': 'count'
    }).rename(columns={'Personnel Name': 'Total Visits', 'Check-In Time': 'Visit Count'})
    
    location_stats['Unique Personnel'] = df.groupby('Location')['Personnel Name'].nunique()
    location_stats = location_stats.sort_values('Total Visits', ascending=False)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Locations", len(location_stats))
    with col2:
        st.metric("Most Visited", location_stats.index[0])
    with col3:
        st.metric("Visits to Top Location", int(location_stats.iloc[0]['Total Visits']))
    
    st.markdown("---")
    
    # Location table
    st.subheader("📊 Location Statistics")
    
    display_stats = location_stats.reset_index()
    display_stats = display_stats[['Location', 'Total Visits', 'Unique Personnel']]
    
    st.dataframe(
        display_stats,
        use_container_width=True,
        hide_index=True
    )
    
    # Map with all locations
    st.subheader("🗺️ Location Coverage Map")
    
    location_data = df.groupby('Location').size().reset_index(name='Total Visits')
    location_data['lat'] = location_data['Location'].apply(lambda x: get_location_coordinates(x)[0])
    location_data['lon'] = location_data['Location'].apply(lambda x: get_location_coordinates(x)[1])
    
    fig = px.scatter_mapbox(
        location_data,
        lat='lat',
        lon='lon',
        size='Total Visits',
        color='Total Visits',
        hover_name='Location',
        hover_data={'Total Visits': True, 'lat': False, 'lon': False},
        color_continuous_scale='Plasma',
        size_max=35,
        zoom=10,
        title='All Locations by Visit Frequency'
    )
    fig.update_layout(
        mapbox_style='open-street-map',
        height=600
    )
    st.plotly_chart(fig, use_container_width=True)

def show_daily_timeline(df):
    """Display daily timeline view"""
    st.header("⏰ Daily Timeline View")
    
    selected_day = st.selectbox("Select Day", df['Day'].unique().tolist())
    
    day_df = df[df['Day'] == selected_day].copy()
    
    if day_df.empty:
        st.warning(f"No data for {selected_day}")
        return
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Visits", len(day_df))
    with col2:
        st.metric("Active Personnel", day_df['Personnel Name'].nunique())
    with col3:
        st.metric("Locations Covered", day_df['Location'].nunique())
    with col4:
        avg_visits = len(day_df) / day_df['Personnel Name'].nunique()
        st.metric("Avg Visits/Person", f"{avg_visits:.1f}")
    
    st.markdown("---")
    
    # Timeline by person
    st.subheader(f"📅 {selected_day} - Team Activity")
    
    # Group by person and show their schedule
    for person in sorted(day_df['Personnel Name'].unique()):
        person_data = day_df[day_df['Personnel Name'] == person].sort_values('Check-In Time')
        
        with st.expander(f"👤 {person} ({len(person_data)} visits)"):
            cols = st.columns([1, 2, 1, 1, 2])
            
            cols[0].write("**Visit #**")
            cols[1].write("**Location**")
            cols[2].write("**Check-In**")
            cols[3].write("**Check-Out**")
            cols[4].write("**Duration**")
            
            for idx, row in person_data.iterrows():
                cols = st.columns([1, 2, 1, 1, 2])
                duration = calculate_duration(row['Check-In Time'], row['Check-Out Time'])
                
                cols[0].write(f"{int(row['Visit #'])}")
                cols[1].write(row['Location'])
                cols[2].write(row['Check-In Time'])
                cols[3].write(row['Check-Out Time'])
                cols[4].write(f"{duration} min")

if __name__ == "__main__":
    main()
