# sam_dashboard_from_excel.py
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, time as dt_time
import plotly.graph_objects as go
import plotly.express as px
import os
from typing import Dict, Any, Optional

# -------------------------------
# 1. Set Page Config
# -------------------------------
st.set_page_config(
    page_title="SAM Recovery Intelligence", 
    layout="wide",
    page_icon="🧬",
    initial_sidebar_state="collapsed"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #2C3E50;
        font-size: 3rem;
        font-weight: bold;
        margin-bottom: 2rem;
    }
    .team-overview-header {
        color: #34495E;
        font-size: 2rem;
        margin: 1rem 0;
        border-bottom: 3px solid #3498DB;
        padding-bottom: 0.5rem;
    }
    .athlete-card {
        background: white;
        border: 2px solid #e9ecef;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        transition: all 0.2s ease;
    }
    .athlete-card:hover {
        border-color: #3498DB;
        box-shadow: 0 4px 8px rgba(52, 152, 219, 0.2);
    }
    .metric-card {
        background: white;
        border: 1px solid #dee2e6;
        border-radius: 8px;
        padding: 1rem;
        text-align: center;
        margin: 0.5rem 0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .metric-card h2 {
        margin: 0.5rem 0;
        font-weight: bold;
    }
    .metric-card h3 {
        margin: 0 0 0.5rem 0;
        color: #495057;
        font-size: 1.1rem;
    }
    .status-indicator {
        font-size: 1.2rem;
        margin: 0.5rem 0;
        font-weight: 500;
    }
    .alert-summary {
        padding: 1.5rem;
        border-radius: 8px;
        margin: 1rem 0;
        border: 1px solid #dee2e6;
    }
    .alert-summary h4 {
        margin: 0 0 0.5rem 0;
        font-weight: bold;
    }
    .alert-summary h2 {
        margin: 0.5rem 0;
        font-weight: bold;
    }
    .alert-summary p {
        margin: 0;
        color: #6c757d;
    }
    .alert-high { 
        background-color: #fff5f5; 
        border-left: 4px solid #e53e3e;
        color: #742a2a;
    }
    .alert-medium { 
        background-color: #fffbf0; 
        border-left: 4px solid #dd6b20;
        color: #744210;
    }
    .alert-low { 
        background-color: #f0fff4; 
        border-left: 4px solid #38a169;
        color: #22543d;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='main-header'>🧬 SAM Recovery Intelligence</h1>", unsafe_allow_html=True)

# -------------------------------
# 2. Load Excel Data with Error Handling
# -------------------------------
EXCEL_FILE = "SAM_Recovery_Data_Template.xlsx"

@st.cache_data
def load_data():
    """Load and cache Excel data with comprehensive error handling"""
    if not os.path.exists(EXCEL_FILE):
        st.error(f"❌ Excel file not found: `{EXCEL_FILE}`")
        st.markdown("**Please ensure the Excel file exists in the same folder as this script.**")
        st.info("💡 **Tip**: The expected file structure should contain sheets: athlete_profiles, genetic_profiles, biometric_daily, sam_metrics_config, predictive_rules")
        st.stop()

    try:
        # Load all sheets
        athletes_df = pd.read_excel(EXCEL_FILE, sheet_name="athlete_profiles")
        genetics_df = pd.read_excel(EXCEL_FILE, sheet_name="genetic_profiles")
        biometrics_df = pd.read_excel(EXCEL_FILE, sheet_name="biometric_daily")
        metrics_config = pd.read_excel(EXCEL_FILE, sheet_name="sam_metrics_config")
        rules_df = pd.read_excel(EXCEL_FILE, sheet_name="predictive_rules")
        
        # Validate required columns
        required_athlete_cols = ['athlete_id', 'name', 'sport', 'age', 'team']
        missing_cols = [col for col in required_athlete_cols if col not in athletes_df.columns]
        if missing_cols:
            st.error(f"Missing columns in athlete_profiles: {missing_cols}")
            st.stop()
        
        # Process biometric data with better error handling
        if 'date' in biometrics_df.columns:
            biometrics_df['date'] = pd.to_datetime(biometrics_df['date'], errors='coerce')
            biometrics_df = biometrics_df.dropna(subset=['date'])
        else:
            st.error("Missing 'date' column in biometric_daily sheet")
            st.stop()

        # Handle time columns safely
        def safe_time_convert(time_str):
            """Safely convert time strings to datetime.time objects"""
            try:
                if pd.isna(time_str) or time_str == '' or time_str is None:
                    return None
                if isinstance(time_str, str):
                    return pd.to_datetime(time_str, format='%H:%M:%S').time()
                elif isinstance(time_str, pd.Timestamp):
                    return time_str.time()
                elif isinstance(time_str, dt_time):
                    return time_str
                else:
                    return pd.to_datetime(str(time_str)).time()
            except Exception:
                return None

        if 'sleep_onset_time' in biometrics_df.columns:
            biometrics_df['sleep_onset_time'] = biometrics_df['sleep_onset_time'].apply(safe_time_convert)
        if 'wake_time' in biometrics_df.columns:
            biometrics_df['wake_time'] = biometrics_df['wake_time'].apply(safe_time_convert)

        # Process athlete baseline dates
        if 'baseline_start_date' in athletes_df.columns:
            athletes_df['baseline_start_date'] = pd.to_datetime(athletes_df['baseline_start_date'], errors='coerce').dt.date
        
        return athletes_df, genetics_df, biometrics_df, metrics_config, rules_df
        
    except Exception as e:
        st.error(f"❌ Error reading Excel file: {e}")
        st.markdown("**Common issues:**")
        st.markdown("- Sheet names don't match expected names")
        st.markdown("- Missing required columns")
        st.markdown("- Data format inconsistencies")
        st.stop()

# Load data
athletes_df, genetics_df, biometrics_df, metrics_config, rules_df = load_data()

# Create pivot table for easy access
try:
    biometrics_pivot = biometrics_df.set_index(['athlete_id', 'date']).sort_index()
except KeyError as e:
    st.error(f"Missing required columns in biometric data: {e}")
    st.stop()

# -------------------------------
# 3. Helper Functions with Error Handling
# -------------------------------

def get_zone_status(value: float, metric_name: str, thresholds: pd.DataFrame) -> str:
    """Get zone status with better error handling"""
    try:
        if pd.isna(value):
            return "⚪ No Data"
        
        matching_rows = thresholds[thresholds['metric_name'] == metric_name]
        if matching_rows.empty:
            return "⚪ No Config"
        
        row = matching_rows.iloc[0]
        
        # Check red zones
        red_ranges = [(row.get('red_low', float('inf')), row.get('red_high', float('-inf')))]
        if 'red_low2' in row and pd.notna(row['red_low2']):
            red_ranges.append((row['red_low2'], row['red_high2']))
        
        for r_low, r_high in red_ranges:
            if not (pd.isna(r_low) or pd.isna(r_high)) and r_low <= value <= r_high:
                return "🔴 Red"
        
        # Check yellow zones
        yellow_ranges = [(row.get('yellow_low', float('inf')), row.get('yellow_high', float('-inf')))]
        if 'yellow_low2' in row and pd.notna(row['yellow_low2']):
            yellow_ranges.append((row['yellow_low2'], row['yellow_high2']))
        
        for y_low, y_high in yellow_ranges:
            if not (pd.isna(y_low) or pd.isna(y_high)) and y_low <= value <= y_high:
                return "🟡 Yellow"
        
        # Check green zone
        green_low, green_high = row.get('green_low', float('inf')), row.get('green_high', float('-inf'))
        if not (pd.isna(green_low) or pd.isna(green_high)) and green_low <= value <= green_high:
            return "🟢 Green"
        
        return "⚪ Unknown"
        
    except Exception:
        return "⚪ Error"

def safe_get_value(df: pd.DataFrame, column: str, default: Any = 0) -> Any:
    """Safely get value from dataframe"""
    try:
        if column in df.columns:
            value = df[column].iloc[-1] if len(df) > 0 else default
            return value if not pd.isna(value) else default
        return default
    except Exception:
        return default

def generate_alert(athlete_id: str, df: pd.DataFrame, genetic_dict: Dict) -> Dict[str, str]:
    """Generate predictive alerts with better error handling"""
    try:
        if len(df) == 0:
            return {
                "type": "no_data",
                "title": "📊 No Data",
                "cause": "No recent biometric data available",
                "rec": "Please ensure data collection is active."
            }
        
        latest = df.iloc[-1]
        
        # Get values safely
        hrv_night = safe_get_value(df, 'hrv_night', 50)
        resting_hr = safe_get_value(df, 'resting_hr', 60)
        temp_trend_c = safe_get_value(df, 'temp_trend_c', 36.5)
        spo2_night = safe_get_value(df, 'spo2_night', 97)
        deep_sleep_pct = safe_get_value(df, 'deep_sleep_pct', 20)
        rem_sleep_pct = safe_get_value(df, 'rem_sleep_pct', 20)
        sleep_duration_h = safe_get_value(df, 'sleep_duration_h', 8)
        resp_rate_night = safe_get_value(df, 'resp_rate_night', 15)
        sleep_onset_time = safe_get_value(df, 'sleep_onset_time', None)
        
        # Deviation logic with safe comparison
        if len(df) >= 2:
            prev = df.iloc[-2]
            prev_hrv = safe_get_value(pd.DataFrame([prev]), 'hrv_night', 50)
            prev_rhr = safe_get_value(pd.DataFrame([prev]), 'resting_hr', 60)
            
            hrv_drop = (prev_hrv - hrv_night) / prev_hrv > 0.15 if prev_hrv > 0 else False
            rhr_rise = (resting_hr - prev_rhr) / prev_rhr > 0.05 if prev_rhr > 0 else False
        else:
            hrv_drop = hrv_night < 40  # Absolute threshold if no comparison
            rhr_rise = resting_hr > 70
        
        # Alert conditions
        temp_high = temp_trend_c >= 37.0
        spo2_low = spo2_night <= 94
        deep_low = deep_sleep_pct < 17
        rem_low = rem_sleep_pct < 16
        sleep_short = sleep_duration_h < 7.0
        resp_high = resp_rate_night >= 17
        
        # Safe time comparison
        ref_time = dt_time(23, 30)  # 11:30 PM
        sleep_late = sleep_onset_time is not None and sleep_onset_time > ref_time
        
        # Apply alert rules
        if hrv_drop and rhr_rise and temp_high and spo2_low:
            return {
                "type": "inflammation",
                "title": "⚠️ Inflammation/Illness Risk",
                "cause": f"HRV↓({hrv_night:.0f}) + RHR↑({resting_hr:.0f}) + Temp↑({temp_trend_c:.1f}) + SpO₂↓({spo2_night:.1f})",
                "rec": "Prioritize rest, hydration, anti-inflammatory nutrition. Monitor temperature closely."
            }
        elif hrv_drop and deep_low and sleep_late:
            onset_str = sleep_onset_time.strftime('%H:%M') if sleep_onset_time else 'Late'
            return {
                "type": "circadian",
                "title": "🌙 Circadian Misalignment",
                "cause": f"HRV↓ + Deep Sleep↓({deep_sleep_pct:.1f}%) + Late Sleep({onset_str})",
                "rec": "Advance bedtime by 45min, increase morning light exposure, avoid screens after 9PM."
            }
        elif hrv_drop and rem_low and not temp_high:
            return {
                "type": "nutrition",
                "title": "🥗 Possible Nutrient Gap",
                "cause": f"HRV↓ + REM↓({rem_sleep_pct:.1f}%) with stable temperature",
                "rec": "Check iron, magnesium, omega-3, B12 status. Increase nutrient-dense foods."
            }
        elif spo2_low and resp_high:
            return {
                "type": "airway",
                "title": "🌬️ Airway/Respiratory Stress",
                "cause": f"SpO₂={spo2_night:.1f}% + Resp Rate={resp_rate_night:.1f}/min",
                "rec": "Evaluate sleep environment, nasal breathing. Consider air quality assessment."
            }
        else:
            return {
                "type": "green",
                "title": "🟢 Optimal Recovery State",
                "cause": "All metrics within target ranges",
                "rec": "Maintain current training and recovery protocols."
            }
            
    except Exception as e:
        return {
            "type": "error",
            "title": "❌ Analysis Error",
            "cause": f"Error processing data: {str(e)[:50]}...",
            "rec": "Check data quality and try refreshing the dashboard."
        }

# -------------------------------
# 4. Navigation
# -------------------------------

if 'page' not in st.session_state:
    st.session_state.page = 'home'
    st.session_state.athlete_id = None

def go_to_athlete(athlete_id):
    st.session_state.page = 'athlete'
    st.session_state.athlete_id = athlete_id

def go_home():
    st.session_state.page = 'home'
    st.session_state.athlete_id = None

# -------------------------------
# 5. Enhanced Main Page: Team Overview
# -------------------------------

if st.session_state.page == 'home':
    
    # Team Statistics Overview
    st.markdown("<h3 class='team-overview-header'>📊 Team Performance Dashboard</h3>", unsafe_allow_html=True)
    
    try:
        # Get latest data for each athlete
        latest_data = biometrics_df.sort_values('date').groupby('athlete_id').last().reset_index()
        
        if latest_data.empty:
            st.warning("⚠️ No biometric data available for any athletes.")
            st.info("Please ensure biometric data is properly loaded in the Excel file.")
        else:
            # Team-level statistics
            col1, col2, col3, col4 = st.columns(4)
            
            total_athletes = len(latest_data)
            avg_hrv = latest_data['hrv_night'].mean()
            avg_sleep = latest_data['sleep_duration_h'].mean()
            
            # Count alerts by type
            alert_counts = {"inflammation": 0, "circadian": 0, "nutrition": 0, "airway": 0, "green": 0, "error": 0}
            
            for _, row in latest_data.iterrows():
                athlete_id = row['athlete_id']
                try:
                    genetic_dict = genetics_df[genetics_df.athlete_id == athlete_id].set_index('gene')['genotype'].to_dict()
                    df = biometrics_pivot.loc[athlete_id].sort_index() if athlete_id in biometrics_pivot.index.get_level_values(0) else pd.DataFrame()
                    alert = generate_alert(athlete_id, df, genetic_dict)
                    alert_counts[alert["type"]] += 1
                except Exception:
                    alert_counts["error"] += 1
            
            with col1:
                st.markdown("""
                <div class='metric-card'>
                    <h3>👥 Total Athletes</h3>
                    <h2 style='color: #3498DB;'>{}</h2>
                </div>
                """.format(total_athletes), unsafe_allow_html=True)
            
            with col2:
                st.markdown("""
                <div class='metric-card'>
                    <h3>💓 Avg HRV</h3>
                    <h2 style='color: #2ECC71;'>{:.0f} ms</h2>
                </div>
                """.format(avg_hrv), unsafe_allow_html=True)
            
            with col3:
                st.markdown("""
                <div class='metric-card'>
                    <h3>😴 Avg Sleep</h3>
                    <h2 style='color: #9B59B6;'>{:.1f}h</h2>
                </div>
                """.format(avg_sleep), unsafe_allow_html=True)
            
            with col4:
                ready_athletes = alert_counts["green"]
                readiness_pct = (ready_athletes / total_athletes) * 100
                st.markdown("""
                <div class='metric-card'>
                    <h3>✅ Team Readiness</h3>
                    <h2 style='color: #28A745;'>{:.0f}%</h2>
                </div>
                """.format(readiness_pct), unsafe_allow_html=True)
            
            # Alert Summary
            st.markdown("### 🚨 Alert Summary")
            alert_col1, alert_col2, alert_col3 = st.columns(3)
            
            with alert_col1:
                high_risk = alert_counts["inflammation"] + alert_counts["airway"]
                st.markdown(f"""
                <div class='alert-summary alert-high'>
                    <h4>🔴 High Priority</h4>
                    <h2>{high_risk} athletes</h2>
                    <p>Require immediate attention</p>
                </div>
                """, unsafe_allow_html=True)
            
            with alert_col2:
                medium_risk = alert_counts["circadian"] + alert_counts["nutrition"]
                st.markdown(f"""
                <div class='alert-summary alert-medium'>
                    <h4>🟡 Monitor Closely</h4>
                    <h2>{medium_risk} athletes</h2>
                    <p>May need intervention</p>
                </div>
                """, unsafe_allow_html=True)
            
            with alert_col3:
                st.markdown(f"""
                <div class='alert-summary alert-low'>
                    <h4>🟢 Optimal</h4>
                    <h2>{alert_counts["green"]} athletes</h2>
                    <p>Ready for training</p>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("---")
            st.markdown("### 👥 Individual Athlete Status")
            
            # Display athletes in a responsive grid
            num_cols = 3
            cols = st.columns(num_cols)
            
            for idx, (_, row) in enumerate(latest_data.iterrows()):
                athlete_id = row['athlete_id']
                
                # Get athlete info safely
                athlete_matches = athletes_df[athletes_df.athlete_id == athlete_id]
                if athlete_matches.empty:
                    continue
                    
                athlete_row = athlete_matches.iloc[0]
                
                try:
                    genetic_dict = genetics_df[genetics_df.athlete_id == athlete_id].set_index('gene')['genotype'].to_dict()
                    df = biometrics_pivot.loc[athlete_id].sort_index() if athlete_id in biometrics_pivot.index.get_level_values(0) else pd.DataFrame()
                    alert = generate_alert(athlete_id, df, genetic_dict)
                except Exception as e:
                    alert = {
                        "type": "error",
                        "title": "❌ Data Error",
                        "cause": "Unable to process data",
                        "rec": "Check data integrity"
                    }
                
                # Color coding and icons
                color_map = {
                    "inflammation": "#E74C3C", "airway": "#E74C3C",
                    "circadian": "#F39C12", "nutrition": "#F39C12", 
                    "green": "#28A745", "error": "#6C757D", "no_data": "#6C757D"
                }
                icon_map = {
                    "inflammation": "🔴", "airway": "🔴",
                    "circadian": "🟡", "nutrition": "🟡",
                    "green": "🟢", "error": "⚪", "no_data": "⚪"
                }
                
                color = color_map.get(alert["type"], "#6C757D")
                icon = icon_map.get(alert["type"], "⚪")
                
                with cols[idx % num_cols]:
                    st.markdown(f"""
                    <div class='athlete-card'>
                        <h4 style='margin-bottom: 0.5rem; color: #2C3E50;'>{athlete_row['name']}</h4>
                        <p style='color: #6c757d; margin-bottom: 1rem;'>{athlete_row['sport']} | Age {athlete_row['age']}</p>
                        <div style='display: flex; justify-content: space-between; margin-bottom: 1rem; color: #495057;'>
                            <span><strong>HRV:</strong> {row.get('hrv_night', 'N/A'):.0f} ms</span>
                            <span><strong>Sleep:</strong> {row.get('sleep_duration_h', 'N/A'):.1f}h</span>
                        </div>
                        <div class='status-indicator' style='color: {color};'>
                            {icon} {alert['title'].replace('🔴', '').replace('🟡', '').replace('🟢', '').replace('❌', '').replace('📊', '').strip()}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.button(
                        "📊 View Dashboard", 
                        key=f"btn_{athlete_id}", 
                        on_click=go_to_athlete, 
                        args=(athlete_id,),
                        use_container_width=True
                    )
    
    except Exception as e:
        st.error(f"Error loading team overview: {e}")
        st.info("Please check your data format and try refreshing the page.")

# -------------------------------
# 6. Enhanced Athlete Dashboard
# -------------------------------

else:
    aid = st.session_state.athlete_id
    
    # Validate athlete exists
    athlete_matches = athletes_df[athletes_df.athlete_id == aid]
    if athlete_matches.empty:
        st.error(f"Athlete ID '{aid}' not found in athlete profiles.")
        st.button("⬅️ Back to Team Overview", on_click=go_home)
        st.stop()
    
    athlete_row = athlete_matches.iloc[0]
    
    try:
        genetic_dict = genetics_df[genetics_df.athlete_id == aid].set_index('gene')['genotype'].to_dict()
        if aid in biometrics_pivot.index.get_level_values(0):
            df = biometrics_pivot.loc[aid].sort_index()
        else:
            df = pd.DataFrame()
    except Exception as e:
        st.error(f"Error loading athlete data: {e}")
        genetic_dict = {}
        df = pd.DataFrame()
    
    if df.empty:
        st.error("No biometric data available for this athlete.")
        st.button("⬅️ Back to Team Overview", on_click=go_home)
        st.stop()
    
    latest = df.iloc[-1]
    alert = generate_alert(aid, df, genetic_dict)

    # Header with improved layout
    col1, col2, col3 = st.columns([3, 3, 1])
    with col1:
        st.markdown(f"### 👤 {athlete_row['name']}")
        st.markdown(f"**{athlete_row['sport']}** | Age {athlete_row['age']} | Team: {athlete_row.get('team', 'N/A')}")
    
    with col2:
        st.markdown("### 🧬 Genetic Profile")
        if genetic_dict:
            snp_text = " | ".join([f"**{k}**: {v}" for k, v in list(genetic_dict.items())[:3]])
            st.markdown(snp_text)
        else:
            st.markdown("*No genetic data available*")
    
    with col3:
        st.button("⬅️ Back", on_click=go_home, use_container_width=True)

    st.markdown("---")

    # Display current alert status prominently
    if alert["type"] in ["inflammation", "airway"]:
        st.error(f"**{alert['title']}**\n\n**Cause**: {alert['cause']}\n\n**Recommendation**: {alert['rec']}")
    elif alert["type"] in ["circadian", "nutrition"]:
        st.warning(f"**{alert['title']}**\n\n**Cause**: {alert['cause']}\n\n**Recommendation**: {alert['rec']}")
    else:
        st.success(f"**{alert['title']}**\n\n{alert['rec']}")

    # Tabs for detailed information
    tab1, tab2, tab3 = st.tabs(["📊 Current Metrics", "📈 Trends & Analysis", "🧠 Predictive Insights"])

    with tab1:
        st.subheader("Today's Readiness Metrics")
        
        # Metrics with better organization
        metrics_map = {
            "HRV (Night)": ("hrv_night", "ms"),
            "Resting HR": ("resting_hr", "bpm"),
            "SpO₂ (Night)": ("spo2_night", "%"),
            "Respiratory Rate": ("resp_rate_night", "/min"),
            "Deep Sleep %": ("deep_sleep_pct", "%"),
            "REM Sleep %": ("rem_sleep_pct", "%"),
            "Sleep Duration": ("sleep_duration_h", "h"),
            "Temperature": ("temp_trend_c", "°C"),
            "Training Load": ("training_load_pct", "%")
        }

        cols = st.columns(3)
        for i, (name, (key, unit)) in enumerate(metrics_map.items()):
            val = safe_get_value(pd.DataFrame([latest]), key, 0)
            
            # Get status with proper metric name formatting
            metric_name_formatted = key.replace("_", " ").title()
            status = get_zone_status(val, metric_name_formatted, metrics_config)
            
            with cols[i % 3]:
                st.markdown(f"""
                <div class='metric-card'>
                    <h3>{name}</h3>
                    <h2 style='color: #2C3E50;'>{val:.1f} {unit}</h2>
                    <p><strong>Status:</strong> {status}</p>
                </div>
                """, unsafe_allow_html=True)

    with tab2:
        st.subheader("7-Day Performance Trends")
        
        if len(df) >= 2:
            # HRV and RHR trend
            fig1 = go.Figure()
            fig1.add_trace(go.Scatter(
                x=df.index, y=df['hrv_night'], 
                mode='lines+markers', name='HRV (ms)', 
                line=dict(color='#2ECC71', width=3),
                marker=dict(size=8)
            ))
            fig1.add_trace(go.Scatter(
                x=df.index, y=df['resting_hr'], 
                mode='lines+markers', name='RHR (bpm)', 
                line=dict(color='#E74C3C', width=3),
                marker=dict(size=8),
                yaxis='y2'
            ))
            fig1.update_layout(
                title="HRV & Resting Heart Rate Trends",
                xaxis_title="Date",
                yaxis_title="HRV (ms)",
                yaxis2=dict(title="RHR (bpm)", overlaying='y', side='right'),
                template="plotly_white",
                height=400,
                showlegend=True
            )
            st.plotly_chart(fig1, use_container_width=True)

            # Sleep architecture
            if all(col in df.columns for col in ['deep_sleep_pct', 'rem_sleep_pct', 'light_sleep_pct']):
                fig2 = go.Figure()
                fig2.add_trace(go.Bar(x=df.index, y=df['deep_sleep_pct'], name='Deep Sleep', marker_color='#3498DB'))
                fig2.add_trace(go.Bar(x=df.index, y=df['rem_sleep_pct'], name='REM Sleep', marker_color='#9B59B6'))
                fig2.add_trace(go.Bar(x=df.index, y=df['light_sleep_pct'], name='Light Sleep', marker_color='#F39C12'))
                fig2.update_layout(
                    barmode='stack',
                    title="Sleep Architecture Distribution",
                    xaxis_title="Date",
                    yaxis_title="Sleep Percentage (%)",
                    template="plotly_white",
                    height=400
                )
                st.plotly_chart(fig2, use_container_width=True)

            # Multi-dimensional correlation plot
            if all(col in df.columns for col in ['resting_hr', 'hrv_night', 'temp_trend_c', 'spo2_night', 'sleep_duration_h']):
                fig3 = px.scatter(
                    df.reset_index(), 
                    x='resting_hr', 
                    y='hrv_night', 
                    size='temp_trend_c', 
                    color='spo2_night',
                    hover_data=['date', 'sleep_duration_h'], 
                    title="HRV vs RHR Analysis (Size = Temperature, Color = SpO₂)",
                    labels={'resting_hr': 'Resting HR (bpm)', 'hrv_night': 'HRV (ms)'}
                )
                fig3.update_layout(template="plotly_white", height=400)
                st.plotly_chart(fig3, use_container_width=True)
        else:
            st.info("📊 Need at least 2 days of data to show trends. Current data points: {}".format(len(df)))

    with tab3:
        st.subheader("🧠 AI-Powered Recovery Insights")
        
        # Current alert details
        st.markdown("#### Current Status Analysis")
        if alert["type"] in ["inflammation", "airway"]:
            st.error(f"**{alert['title']}**")
            st.markdown(f"**Root Cause:** {alert['cause']}")
            st.markdown(f"**Action Plan:** {alert['rec']}")
        elif alert["type"] in ["circadian", "nutrition"]:
            st.warning(f"**{alert['title']}**")
            st.markdown(f"**Contributing Factors:** {alert['cause']}")
            st.markdown(f"**Optimization Strategy:** {alert['rec']}")
        else:
            st.success(f"**{alert['title']}**")
            st.markdown(f"**Status:** {alert['cause']}")
            st.markdown(f"**Maintenance Plan:** {alert['rec']}")
        
        st.markdown("---")
        
        # Personalized insights based on genetics
        st.markdown("#### 🧬 Genotype-Specific Recommendations")
        if genetic_dict:
            genetic_insights = []
            
            # PER3 gene insights
            if genetic_dict.get("PER3") == "long":
                genetic_insights.append({
                    "gene": "PER3 (Long variant)",
                    "trait": "Natural night owl tendency",
                    "recommendation": "Allow later bedtimes when possible, prioritize consistent wake times, use bright light therapy in morning"
                })
            elif genetic_dict.get("PER3") == "short":
                genetic_insights.append({
                    "gene": "PER3 (Short variant)", 
                    "trait": "Natural early bird tendency",
                    "recommendation": "Optimize early morning training, avoid late evening intense exercise, maintain regular early bedtime"
                })
            
            # CLOCK gene insights
            if genetic_dict.get("CLOCK") == "AA":
                genetic_insights.append({
                    "gene": "CLOCK (AA genotype)",
                    "trait": "Enhanced circadian sensitivity",
                    "recommendation": "Maintain strict sleep schedule, minimize blue light exposure 2h before bed, prioritize sleep environment optimization"
                })
            
            # ACTN3 gene insights
            if genetic_dict.get("ACTN3") == "XX":
                genetic_insights.append({
                    "gene": "ACTN3 (XX genotype)",
                    "trait": "Enhanced endurance capacity",
                    "recommendation": "Focus on aerobic base building, longer recovery periods between high-intensity sessions, emphasize mitochondrial health"
                })
            elif genetic_dict.get("ACTN3") == "RR":
                genetic_insights.append({
                    "gene": "ACTN3 (RR genotype)",
                    "trait": "Enhanced power/sprint capacity", 
                    "recommendation": "Optimize explosive training, shorter but more intense sessions, focus on neuromuscular recovery"
                })
            
            for insight in genetic_insights:
                st.markdown(f"""
                <div style='background: #f8f9fa; border-left: 4px solid #007bff; padding: 1rem; margin: 0.5rem 0; border-radius: 5px;'>
                    <h5 style='color: #007bff; margin-bottom: 0.5rem;'>{insight['gene']}</h5>
                    <p style='margin-bottom: 0.5rem;'><strong>Trait:</strong> {insight['trait']}</p>
                    <p style='margin-bottom: 0;'><strong>Strategy:</strong> {insight['recommendation']}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("🧬 Genetic data not available. Consider genetic testing for personalized insights.")
        
        st.markdown("---")
        
        # Predictive rules reference
        st.markdown("#### 📋 Evidence-Based Recovery Framework")
        if not rules_df.empty:
            st.markdown("**Decision Matrix for Recovery Interventions:**")
            
            # Format rules dataframe for better display
            display_rules = rules_df.copy()
            if 'metric_drop' in display_rules.columns:
                display_rules = display_rules.rename(columns={
                    'metric_drop': 'Biometric Pattern',
                    'genetic_condition': 'Genetic Context',
                    'cause': 'Likely Root Cause',
                    'recommendation': 'Intervention Protocol'
                })
            
            st.dataframe(
                display_rules,
                use_container_width=True,
                hide_index=True,
                height=300
            )
        else:
            st.info("📋 Predictive rules configuration not available.")
        
        # Performance prediction
        st.markdown("---")
        st.markdown("#### 🔮 Performance Readiness Forecast")
        
        if len(df) >= 3:
            # Simple trend analysis
            recent_hrv = df['hrv_night'].tail(3).mean()
            recent_rhr = df['resting_hr'].tail(3).mean()
            recent_sleep = df['sleep_duration_h'].tail(3).mean()
            
            # Calculate trend direction
            hrv_trend = "↗️" if df['hrv_night'].iloc[-1] > df['hrv_night'].iloc[-2] else "↘️"
            rhr_trend = "↗️" if df['resting_hr'].iloc[-1] > df['resting_hr'].iloc[-2] else "↘️"
            sleep_trend = "↗️" if df['sleep_duration_h'].iloc[-1] > df['sleep_duration_h'].iloc[-2] else "↘️"
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("""
                <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 1.5rem; border-radius: 10px;'>
                    <h4>🎯 Readiness Indicators</h4>
                    <p><strong>HRV Trend:</strong> {:.1f} ms {}</p>
                    <p><strong>RHR Trend:</strong> {:.1f} bpm {}</p>
                    <p><strong>Sleep Trend:</strong> {:.1f}h {}</p>
                </div>
                """.format(recent_hrv, hrv_trend, recent_rhr, rhr_trend, recent_sleep, sleep_trend), 
                unsafe_allow_html=True)
            
            with col2:
                # Simple readiness score
                hrv_score = 1 if recent_hrv > 45 else 0.5 if recent_hrv > 35 else 0
                rhr_score = 1 if recent_rhr < 65 else 0.5 if recent_rhr < 75 else 0
                sleep_score = 1 if recent_sleep > 7.5 else 0.5 if recent_sleep > 6.5 else 0
                
                overall_score = (hrv_score + rhr_score + sleep_score) / 3 * 100
                
                score_color = "#28a745" if overall_score > 75 else "#ffc107" if overall_score > 50 else "#dc3545"
                score_emoji = "🟢" if overall_score > 75 else "🟡" if overall_score > 50 else "🔴"
                
                st.markdown("""
                <div style='background: white; border: 2px solid {}; padding: 1.5rem; border-radius: 10px; text-align: center;'>
                    <h4>📊 Readiness Score</h4>
                    <h2 style='color: {}; margin: 1rem 0;'>{} {:.0f}%</h2>
                    <p style='margin: 0;'>Based on HRV, RHR & Sleep</p>
                </div>
                """.format(score_color, score_color, score_emoji, overall_score), unsafe_allow_html=True)
        else:
            st.info("🔮 Need at least 3 days of data for performance forecasting.")

# -------------------------------
# 7. Enhanced Footer
# -------------------------------
st.markdown("---")
st.markdown("""
<div style='text-align: center; padding: 2rem; background: linear-gradient(45deg, #f8f9fa 0%, #e9ecef 100%); border-radius: 10px; margin-top: 2rem;'>
    <h4 style='color: #6c757d; margin-bottom: 1rem;'>🧬 SAM Recovery Intelligence Engine v4.0</h4>
    <p style='color: #6c757d; margin: 0;'>
        Integrating Genetics × Biometrics × AI for Precision Recovery
    </p>
    <p style='color: #6c757d; margin: 0.5rem 0 0 0; font-size: 0.9rem;'>
        🔬 Evidence-based algorithms • 🧬 Personalized insights • 📊 Real-time monitoring
    </p>
</div>
""", unsafe_allow_html=True)
