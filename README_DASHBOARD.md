# Sales Team Dashboard

Real-time sales personnel tracking and performance dashboard built with Streamlit.

## Features

### 📊 Team Overview
- Total visits, personnel count, and productivity metrics
- Visit trends by day and personnel
- Top locations heatmap
- Interactive maps showing all visit locations
- Team activity heatmap (person × day)

### 👤 Individual Performance
- Detailed metrics per salesperson
- Daily visit patterns
- Time spent by location
- Visit timeline with check-in/check-out details
- Individual location coverage map

### 📍 Location Analysis
- Location visit statistics
- Coverage analysis
- Most/least visited locations
- Geographic distribution

### ⏰ Daily Timeline
- Day-by-day activity view
- Schedule for each team member
- Visit sequences and timing

## Installation

### 1. Install Dependencies

```bash
pip install -r requirements_dashboard.txt
```

### 2. Prepare Data

Place your `sales_personnel_tracking.xlsx` file in the same directory as `sales_dashboard.py`.

The Excel file should have sheets for each day (Monday-Saturday) with columns:
- Personnel Name
- Login Time
- Visit #
- Location
- Maps Link
- Check-In Time
- Check-Out Time
- Selfie
- Logout Time

## Running the Dashboard

### Local Development

```bash
streamlit run sales_dashboard.py
```

The dashboard will open automatically in your browser at `http://localhost:8501`

### Custom Port

```bash
streamlit run sales_dashboard.py --server.port 8080
```

### Deploy to Streamlit Cloud

1. Push code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repository
4. Deploy!

## Usage Guide

### Filters (Sidebar)
- **Select Days**: Filter data by specific days of the week
- **Select Personnel**: Filter by specific team members
- **View Mode**: Switch between different views

### View Modes

#### 1. Team Overview
Get a bird's-eye view of your entire team:
- KPIs: Total personnel, visits, averages
- Bar chart: Visits by each person
- Line chart: Daily trends
- Heatmap: Person × Day visit patterns
- Map: All locations visited

#### 2. Individual Performance
Deep dive into a specific salesperson:
- Select person from dropdown
- See their metrics: total visits, days worked, unique locations
- View daily visit patterns
- Analyze time distribution by location
- See their complete visit timeline
- Map of their visited locations

#### 3. Location Analysis
Understand location coverage:
- Total locations covered
- Most visited locations
- Statistics table
- Coverage map showing visit frequency

#### 4. Daily Timeline
Review a specific day's activity:
- Select day from dropdown
- See summary metrics for that day
- Expandable view for each person's schedule
- Visit-by-visit breakdown with timing

## Dashboard Screenshots

### Team Overview
```
┌─────────────────────────────────────────────────┐
│  Total Personnel: 10  │  Total Visits: 420      │
│  Avg Visits/Day: 7    │  Avg Duration: 45 min   │
└─────────────────────────────────────────────────┘

[Bar Chart: Visits by Personnel]
[Line Chart: Daily Trends]
[Heatmap: Activity Matrix]
[Map: All Locations]
```

### Individual View
```
┌─────────────────────────────────────────────────┐
│  👤 Rajesh Kumar                                │
│  Total Visits: 42  │  Unique Locations: 15      │
│  Avg Visits/Day: 7 │  Total Field Time: 28 hrs │
└─────────────────────────────────────────────────┘

[Daily Visits Bar Chart]
[Time by Location Pie Chart]
[Visit Timeline Table]
[Personal Location Map]
```

## Customization

### Modify Colors
Edit the CSS in `sales_dashboard.py`:

```python
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #YOUR_COLOR1 0%, #YOUR_COLOR2 100%);
    }
</style>
""", unsafe_allow_html=True)
```

### Add New Metrics

```python
# Calculate new metric
new_metric = df.groupby('some_column').agg({'another_column': 'sum'})

# Display
st.metric("New Metric", new_metric)
```

### Add Charts

```python
import plotly.express as px

fig = px.scatter(df, x='column1', y='column2', title='New Chart')
st.plotly_chart(fig, use_container_width=True)
```

## Production Deployment

### Option 1: Streamlit Cloud (Free)
- Easiest option
- Free tier available
- Auto-deploys from GitHub
- Limited resources

### Option 2: Docker
```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements_dashboard.txt .
RUN pip install -r requirements_dashboard.txt

COPY sales_dashboard.py .
COPY sales_personnel_tracking.xlsx .

EXPOSE 8501

CMD ["streamlit", "run", "sales_dashboard.py", "--server.address", "0.0.0.0"]
```

Build and run:
```bash
docker build -t sales-dashboard .
docker run -p 8501:8501 sales-dashboard
```

### Option 3: AWS/GCP/Azure
- Deploy container to ECS/Cloud Run/App Service
- Add load balancer
- Connect to production database
- Set up authentication

## Database Integration

To connect to a live database instead of Excel:

```python
import psycopg2
import pandas as pd

@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_data_from_db():
    conn = psycopg2.connect(
        host="your-db-host",
        database="salesdb",
        user="user",
        password="password"
    )
    
    query = """
    SELECT 
        p.name as "Personnel Name",
        v.check_in_time as "Check-In Time",
        v.check_out_time as "Check-Out Time",
        l.name as "Location",
        to_char(v.planned_date, 'Day') as "Day"
    FROM visits v
    JOIN personnel p ON v.personnel_id = p.id
    JOIN locations l ON v.location_id = l.id
    WHERE v.check_in_time >= CURRENT_DATE - INTERVAL '7 days'
    """
    
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# Use in dashboard
df = load_data_from_db()
```

## Real-time Updates

Add WebSocket support for live updates:

```python
import asyncio
from streamlit_autorefresh import st_autorefresh

# Auto-refresh every 30 seconds
count = st_autorefresh(interval=30000, key="datarefresh")

# Or use WebSocket
import websocket

ws = websocket.WebSocket()
ws.connect("wss://your-api.com/ws/dashboard")

while True:
    update = ws.recv()
    # Update data
    st.rerun()
```

## Troubleshooting

### Dashboard won't start
```bash
# Check Python version (need 3.8+)
python --version

# Reinstall dependencies
pip install --upgrade -r requirements_dashboard.txt
```

### Excel file not found
```bash
# Check file path in code
# Update this line in sales_dashboard.py:
df = load_data('/path/to/your/sales_personnel_tracking.xlsx')
```

### Charts not displaying
```bash
# Clear Streamlit cache
streamlit cache clear
```

## Performance Optimization

For large datasets (1000+ records):

```python
# Use data sampling for visualizations
@st.cache_data
def load_data(file_path, sample_size=None):
    df = pd.read_excel(file_path)
    if sample_size and len(df) > sample_size:
        return df.sample(n=sample_size)
    return df

# Use efficient data structures
df['Check-In Time'] = pd.to_datetime(df['Check-In Time'])
df['Duration'] = pd.to_numeric(df['Duration'])

# Limit map markers
if len(location_data) > 100:
    location_data = location_data.nlargest(100, 'Total Visits')
```

## License

This dashboard is provided as-is for demonstration purposes.

## Support

For production implementation, see `ARCHITECTURE.md` for complete system design.

## Next Steps

1. ✅ Review dashboard functionality
2. ⬜ Connect to real database
3. ⬜ Add authentication
4. ⬜ Implement real-time updates
5. ⬜ Deploy to production
6. ⬜ Build mobile app (see ARCHITECTURE.md)
