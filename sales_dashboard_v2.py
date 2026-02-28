"""
Sales Team Dashboard
Reads live data from Google Sheets — auto-refreshes every 60 seconds.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, date
import gspread
from google.oauth2.service_account import Credentials

# ─── Page Config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Sales Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── CSS ─────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=Space+Mono:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
    .stApp { background: #0a0d18; color: #e2e8f0; }
    [data-testid="stSidebar"] { background: #0f1117; border-right: 1px solid #1e2540; }

    .dash-header {
        background: linear-gradient(135deg, #0f1e3d 0%, #0a0d18 100%);
        border: 1px solid #1e2540; border-radius: 16px;
        padding: 24px 32px; margin-bottom: 24px;
    }
    .dash-header h1 { font-family: 'Space Mono', monospace; font-size: 1.6rem; color: #63b3ed; margin: 0; }
    .dash-header p  { color: #4a5568; font-size: 0.85rem; margin: 4px 0 0 0; }

    .kpi-card {
        background: #0f1117; border: 1px solid #1e2540; border-radius: 14px;
        padding: 20px 24px; text-align: center;
    }
    .kpi-value { font-family: 'Space Mono', monospace; font-size: 2rem; font-weight: 700; color: #63b3ed; }
    .kpi-label { font-size: 0.75rem; color: #4a5568; text-transform: uppercase; letter-spacing: 1.5px; margin-top: 4px; }
    .kpi-sub   { font-size: 0.8rem; color: #718096; margin-top: 2px; }

    .section-header {
        font-family: 'Space Mono', monospace; font-size: 0.7rem;
        text-transform: uppercase; letter-spacing: 2px;
        color: #4a5568; margin: 24px 0 12px 0; padding-bottom: 8px;
        border-bottom: 1px solid #1e2540;
    }

    .live-badge {
        display: inline-flex; align-items: center; gap: 6px;
        background: rgba(72,187,120,0.15); border: 1px solid rgba(72,187,120,0.3);
        color: #68d391; padding: 3px 10px; border-radius: 20px;
        font-size: 0.72rem; font-weight: 600; font-family: 'Space Mono', monospace;
    }

    .stSelectbox label, .stMultiSelect label { color: #a0aec0 !important; font-size: 0.85rem !important; }
    .stSelectbox > div > div { background: #0f1117 !important; border: 1px solid #1e2540 !important; color: #e2e8f0 !important; }

    div[data-testid="stMetric"] { background: #0f1117; border: 1px solid #1e2540; border-radius: 12px; padding: 16px; }
    div[data-testid="stMetricValue"] { font-family: 'Space Mono', monospace; color: #63b3ed; }

    .visit-row {
        background: #0f1117; border: 1px solid #1e2540; border-left: 3px solid #63b3ed;
        border-radius: 8px; padding: 12px 16px; margin-bottom: 8px;
        display: flex; justify-content: space-between; align-items: center;
    }
</style>
""", unsafe_allow_html=True)

# ─── Google Sheets ────────────────────────────────────────────────────────────
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

@st.cache_resource
def get_gsheet_client():
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=[
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
    )
    return gspread.authorize(creds)

@st.cache_data(ttl=60)   # ← refreshes every 60 seconds automatically
def load_data():
    client = get_gsheet_client()
    sh     = client.open_by_key(st.secrets["SHEET_ID"])
    all_dfs = []
    for day in DAYS:
        try:
            ws      = sh.worksheet(day)
            records = ws.get_all_records()
            if records:
                df = pd.DataFrame(records)
                df["Day"] = day
                all_dfs.append(df)
        except gspread.WorksheetNotFound:
            continue
        except Exception:
            continue
    if not all_dfs:
        return pd.DataFrame()
    df = pd.concat(all_dfs, ignore_index=True)
    return df

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    # Parse times
    for col in ["Check-In Time", "Check-Out Time", "Login Time", "Logout Time"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], format="%H:%M", errors="coerce").dt.time

    # Duration in minutes
    def duration_mins(row):
        try:
            cin  = row.get("Check-In Time")
            cout = row.get("Check-Out Time")
            if pd.isnull(cin) or pd.isnull(cout): return 0
            diff = (datetime.combine(date.today(), cout) - datetime.combine(date.today(), cin)).total_seconds() / 60
            return max(0, int(diff))
        except Exception:
            return 0

    df["Duration (min)"] = df.apply(duration_mins, axis=1)

    # Day order
    day_order = {d: i for i, d in enumerate(DAYS)}
    df["Day Order"] = df["Day"].map(day_order)

    # Ensure Visit # is numeric
    if "Visit #" in df.columns:
        df["Visit #"] = pd.to_numeric(df["Visit #"], errors="coerce").fillna(0).astype(int)

    return df

# ─── Load & clean ─────────────────────────────────────────────────────────────
raw_df = load_data()

if raw_df.empty:
    st.markdown("""
    <div class="dash-header">
        <h1>📊 Sales Dashboard</h1>
        <p>No data found. Reps must complete their day in the Field Logger app first.</p>
    </div>""", unsafe_allow_html=True)
    if st.button("🔄 Refresh"):
        st.cache_data.clear()
        st.rerun()
    st.stop()

df = clean_data(raw_df.copy())

# ─── Sidebar filters ──────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🔍 Filters")

    available_days  = [d for d in DAYS if d in df["Day"].unique()]
    selected_days   = st.multiselect("Days", available_days, default=available_days)

    all_personnel   = sorted(df["Personnel Name"].dropna().unique().tolist())
    selected_people = st.multiselect("Personnel", all_personnel, default=all_personnel)

    st.markdown("---")
    st.markdown("## 📋 View Mode")
    view = st.selectbox("Select View", [
        "Team Overview",
        "Individual Performance",
        "Location Analysis",
        "Daily Timeline"
    ])

    st.markdown("---")
    st.markdown('<span class="live-badge">● LIVE · refreshes every 60s</span>', unsafe_allow_html=True)
    if st.button("🔄 Force Refresh"):
        st.cache_data.clear()
        st.rerun()
    st.markdown(f"<p style='color:#4a5568;font-size:0.75rem;margin-top:8px'>Last load: {datetime.now().strftime('%H:%M:%S')}</p>", unsafe_allow_html=True)

# Apply filters
filtered = df[
    df["Day"].isin(selected_days) &
    df["Personnel Name"].isin(selected_people)
].copy()

if filtered.empty:
    st.warning("No data matches the current filters.")
    st.stop()

# ─── Header ───────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="dash-header">
    <h1>📊 Sales Team Dashboard</h1>
    <p>{len(selected_people)} personnel &nbsp;·&nbsp; {", ".join(selected_days)} &nbsp;·&nbsp; <span class="live-badge">● LIVE</span></p>
</div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# VIEW 1 — TEAM OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════
if view == "Team Overview":

    # KPIs
    total_visits    = len(filtered)
    total_personnel = filtered["Personnel Name"].nunique()
    total_locations = filtered["Location"].nunique()
    avg_duration    = filtered["Duration (min)"].mean()
    avg_visits_pp   = total_visits / total_personnel if total_personnel else 0

    c1, c2, c3, c4, c5 = st.columns(5)
    for col, val, label, sub in [
        (c1, total_personnel,          "Personnel",        f"active this week"),
        (c2, total_visits,             "Total Visits",     f"{avg_visits_pp:.1f} avg / person"),
        (c3, total_locations,          "Locations",        "unique covered"),
        (c4, f"{avg_duration:.0f}m",   "Avg Duration",     "per visit"),
        (c5, f"{total_visits / len(selected_days) if selected_days else 0:.1f}", "Visits / Day", "average"),
    ]:
        col.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-value">{val}</div>
            <div class="kpi-label">{label}</div>
            <div class="kpi-sub">{sub}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown('<div class="section-header">Visits by Personnel</div>', unsafe_allow_html=True)
    visits_by_person = (filtered.groupby("Personnel Name")
                        .agg(Visits=("Visit #","count"), Avg_Duration=("Duration (min)","mean"))
                        .reset_index().sort_values("Visits", ascending=False))
    fig = px.bar(visits_by_person, x="Personnel Name", y="Visits",
                 color="Avg_Duration", color_continuous_scale="Blues",
                 labels={"Avg_Duration":"Avg Duration (min)", "Personnel Name":""},
                 template="plotly_dark")
    fig.update_layout(paper_bgcolor="#0f1117", plot_bgcolor="#0f1117",
                      font_color="#a0aec0", coloraxis_colorbar_title="Avg min")
    st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="section-header">Daily Trend</div>', unsafe_allow_html=True)
        daily = (filtered.groupby("Day").size().reset_index(name="Visits"))
        daily["Day Order"] = daily["Day"].map({d:i for i,d in enumerate(DAYS)})
        daily = daily.sort_values("Day Order")
        fig2 = px.line(daily, x="Day", y="Visits", markers=True, template="plotly_dark",
                       color_discrete_sequence=["#63b3ed"])
        fig2.update_layout(paper_bgcolor="#0f1117", plot_bgcolor="#0f1117", font_color="#a0aec0")
        fig2.update_traces(line_width=2, marker_size=8)
        st.plotly_chart(fig2, use_container_width=True)

    with col2:
        st.markdown('<div class="section-header">Time in Field (hrs)</div>', unsafe_allow_html=True)
        field_time = (filtered.groupby("Personnel Name")["Duration (min)"]
                      .sum().reset_index()
                      .assign(Hours=lambda x: x["Duration (min)"] / 60)
                      .sort_values("Hours", ascending=True))
        fig3 = px.bar(field_time, x="Hours", y="Personnel Name", orientation="h",
                      template="plotly_dark", color_discrete_sequence=["#4299e1"])
        fig3.update_layout(paper_bgcolor="#0f1117", plot_bgcolor="#0f1117",
                           font_color="#a0aec0", yaxis_title="")
        st.plotly_chart(fig3, use_container_width=True)

    st.markdown('<div class="section-header">Activity Heatmap (Person × Day)</div>', unsafe_allow_html=True)
    pivot = (filtered.groupby(["Personnel Name","Day"]).size()
             .unstack(fill_value=0).reindex(columns=[d for d in DAYS if d in filtered["Day"].unique()]))
    fig4 = px.imshow(pivot, color_continuous_scale="Blues", aspect="auto",
                     labels=dict(color="Visits"), template="plotly_dark")
    fig4.update_layout(paper_bgcolor="#0f1117", plot_bgcolor="#0f1117", font_color="#a0aec0")
    st.plotly_chart(fig4, use_container_width=True)

    st.markdown('<div class="section-header">Top Locations</div>', unsafe_allow_html=True)
    top_locs = (filtered.groupby("Location").size().reset_index(name="Visits")
                .sort_values("Visits", ascending=False).head(15))
    fig5 = px.bar(top_locs, x="Visits", y="Location", orientation="h",
                  template="plotly_dark", color_discrete_sequence=["#63b3ed"])
    fig5.update_layout(paper_bgcolor="#0f1117", plot_bgcolor="#0f1117",
                       font_color="#a0aec0", yaxis_title="", height=450)
    st.plotly_chart(fig5, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# VIEW 2 — INDIVIDUAL PERFORMANCE
# ══════════════════════════════════════════════════════════════════════════════
elif view == "Individual Performance":

    person = st.selectbox("Select Salesperson", sorted(filtered["Personnel Name"].unique()))
    pdf    = filtered[filtered["Personnel Name"] == person].copy()

    total_v   = len(pdf)
    days_w    = pdf["Day"].nunique()
    unique_l  = pdf["Location"].nunique()
    total_hrs = pdf["Duration (min)"].sum() / 60

    c1, c2, c3, c4 = st.columns(4)
    for col, val, label in [
        (c1, total_v,           "Total Visits"),
        (c2, days_w,            "Days Worked"),
        (c3, unique_l,          "Unique Locations"),
        (c4, f"{total_hrs:.1f}h", "Field Hours"),
    ]:
        col.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-value">{val}</div>
            <div class="kpi-label">{label}</div>
        </div>""", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="section-header">Visits per Day</div>', unsafe_allow_html=True)
        daily_p = pdf.groupby("Day").size().reset_index(name="Visits")
        daily_p["Day Order"] = daily_p["Day"].map({d:i for i,d in enumerate(DAYS)})
        daily_p = daily_p.sort_values("Day Order")
        fig = px.bar(daily_p, x="Day", y="Visits", template="plotly_dark",
                     color_discrete_sequence=["#63b3ed"])
        fig.update_layout(paper_bgcolor="#0f1117", plot_bgcolor="#0f1117", font_color="#a0aec0")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown('<div class="section-header">Time by Location</div>', unsafe_allow_html=True)
        time_loc = (pdf.groupby("Location")["Duration (min)"].sum()
                    .reset_index().sort_values("Duration (min)", ascending=False).head(10))
        fig2 = px.pie(time_loc, names="Location", values="Duration (min)",
                      template="plotly_dark", color_discrete_sequence=px.colors.sequential.Blues_r)
        fig2.update_layout(paper_bgcolor="#0f1117", font_color="#a0aec0")
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown('<div class="section-header">Visit Timeline</div>', unsafe_allow_html=True)

    display_cols = ["Day", "Visit #", "Location", "Check-In Time", "Check-Out Time", "Duration (min)", "Maps Link"]
    show_cols    = [c for c in display_cols if c in pdf.columns]
    timeline_df  = pdf[show_cols].copy()
    timeline_df["Day Order"] = timeline_df["Day"].map({d:i for i,d in enumerate(DAYS)})
    timeline_df  = timeline_df.sort_values(["Day Order", "Visit #"]).drop(columns=["Day Order"])
    timeline_df["Check-In Time"]  = timeline_df["Check-In Time"].astype(str)
    timeline_df["Check-Out Time"] = timeline_df["Check-Out Time"].astype(str)
    timeline_df["Duration (min)"] = timeline_df["Duration (min)"].apply(lambda x: f"{x} min")

    st.dataframe(timeline_df, use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════════════════════════════════════
# VIEW 3 — LOCATION ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════
elif view == "Location Analysis":

    loc_stats = (filtered.groupby("Location")
                 .agg(
                     Visits=("Visit #","count"),
                     Personnel=("Personnel Name","nunique"),
                     Avg_Duration=("Duration (min)","mean"),
                     Total_Duration=("Duration (min)","sum"),
                 )
                 .reset_index()
                 .sort_values("Visits", ascending=False))

    c1, c2, c3 = st.columns(3)
    c1.markdown(f'<div class="kpi-card"><div class="kpi-value">{len(loc_stats)}</div><div class="kpi-label">Locations Covered</div></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="kpi-card"><div class="kpi-value">{loc_stats["Visits"].max()}</div><div class="kpi-label">Max Visits (single location)</div></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="kpi-card"><div class="kpi-value">{loc_stats["Avg_Duration"].mean():.0f}m</div><div class="kpi-label">Overall Avg Duration</div></div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="section-header">Most Visited Locations</div>', unsafe_allow_html=True)
        fig = px.bar(loc_stats.head(12), x="Visits", y="Location", orientation="h",
                     template="plotly_dark", color_discrete_sequence=["#63b3ed"])
        fig.update_layout(paper_bgcolor="#0f1117", plot_bgcolor="#0f1117",
                          font_color="#a0aec0", yaxis_title="", height=420)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown('<div class="section-header">Avg Visit Duration by Location</div>', unsafe_allow_html=True)
        top_dur = loc_stats.nlargest(12, "Avg_Duration")
        fig2 = px.bar(top_dur, x="Avg_Duration", y="Location", orientation="h",
                      template="plotly_dark", color_discrete_sequence=["#4299e1"],
                      labels={"Avg_Duration": "Avg Duration (min)"})
        fig2.update_layout(paper_bgcolor="#0f1117", plot_bgcolor="#0f1117",
                           font_color="#a0aec0", yaxis_title="", height=420)
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown('<div class="section-header">Location Statistics</div>', unsafe_allow_html=True)
    loc_stats["Avg_Duration"] = loc_stats["Avg_Duration"].round(1).astype(str) + " min"
    loc_stats["Total_Duration"] = (loc_stats["Total_Duration"] / 60).round(1).astype(str) + " hrs"
    st.dataframe(loc_stats.rename(columns={
        "Avg_Duration": "Avg Duration", "Total_Duration": "Total Time",
        "Personnel": "# Personnel"
    }), use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════════════════════════════════════
# VIEW 4 — DAILY TIMELINE
# ══════════════════════════════════════════════════════════════════════════════
elif view == "Daily Timeline":

    available_days_f = [d for d in DAYS if d in filtered["Day"].unique()]
    selected_day     = st.selectbox("Select Day", available_days_f)
    day_df           = filtered[filtered["Day"] == selected_day].copy()

    c1, c2, c3 = st.columns(3)
    c1.markdown(f'<div class="kpi-card"><div class="kpi-value">{day_df["Personnel Name"].nunique()}</div><div class="kpi-label">Active Personnel</div></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="kpi-card"><div class="kpi-value">{len(day_df)}</div><div class="kpi-label">Total Visits</div></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="kpi-card"><div class="kpi-value">{day_df["Location"].nunique()}</div><div class="kpi-label">Locations Covered</div></div>', unsafe_allow_html=True)

    st.markdown(f'<div class="section-header">Schedule — {selected_day}</div>', unsafe_allow_html=True)

    for person in sorted(day_df["Personnel Name"].unique()):
        person_day = day_df[day_df["Personnel Name"] == person].sort_values("Visit #")
        total_v    = len(person_day)
        total_mins = person_day["Duration (min)"].sum()
        hrs_str    = f"{total_mins // 60}h {total_mins % 60}m" if total_mins else "—"

        with st.expander(f"👤 {person}  ·  {total_v} visits  ·  {hrs_str} in field"):
            for _, row in person_day.iterrows():
                cin  = str(row.get("Check-In Time",  "")).replace("None","—")
                cout = str(row.get("Check-Out Time", "")).replace("None","—")
                dur  = f"{row['Duration (min)']} min" if row["Duration (min)"] else "—"
                maps = f"[📍 Map]({row['Maps Link']})" if row.get("Maps Link") else ""
                st.markdown(f"""
                **Visit {int(row['Visit #'])}** &nbsp; `{cin} → {cout}` &nbsp; *({dur})* &nbsp; {maps}
                > {row['Location']}
                """)