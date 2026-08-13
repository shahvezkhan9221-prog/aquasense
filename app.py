import streamlit as st
import time
import pandas as pd
import numpy as np
from datetime import datetime

# Import local utilities
from utils.data_loader import (
    load_location_data,
    load_water_quality_base,
    get_village_metadata,
    generate_deterministic_history
)
from utils.model_utils import (
    predict_risk,
    get_parameter_status,
    PH_MIN, PH_MAX,
    TURBIDITY_LIMIT,
    TDS_LIMIT,
    DO_MINIMUM
)
from utils.charts import create_parameter_chart

# Page configuration
st.set_page_config(
    page_title="AquaSense - Village Water Intelligence",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Premium Styling
CUSTOM_CSS = """
<style>
    /* Import modern typography */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Inter', sans-serif;
        background-color: #0b0f19;
        background-image: 
            radial-gradient(at 10% 20%, rgba(6, 182, 212, 0.08) 0px, transparent 50%),
            radial-gradient(at 90% 80%, rgba(99, 102, 241, 0.04) 0px, transparent 50%);
        color: #f8fafc;
    }

    [data-testid="stHeader"] {
        background-color: rgba(11, 15, 25, 0.8);
        backdrop-filter: blur(10px);
    }

    /* Style sidebar */
    [data-testid="stSidebar"] {
        background-color: #0f172a;
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }

    /* Hide standard header & footer */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* Premium metric card */
    .metric-card {
        background: rgba(30, 41, 59, 0.45);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 20px;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.15);
        backdrop-filter: blur(8px);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        margin-bottom: 12px;
    }
    .metric-card:hover {
        transform: translateY(-3px);
        border-color: rgba(6, 182, 212, 0.4);
        box-shadow: 0 10px 30px rgba(6, 182, 212, 0.1);
    }

    /* Custom Header layout */
    .header-container {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.7), rgba(15, 23, 42, 0.8));
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 24px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 16px;
    }
    .header-badge-container {
        display: flex;
        gap: 8px;
        align-items: center;
        flex-wrap: wrap;
    }
    .badge-online {
        background: rgba(16, 185, 129, 0.12);
        color: #10b981;
        border: 1px solid rgba(16, 185, 129, 0.25);
        padding: 5px 12px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.05em;
        display: inline-flex;
        align-items: center;
        gap: 6px;
    }
    .badge-demo {
        background: rgba(6, 182, 212, 0.12);
        color: #06b6d4;
        border: 1px solid rgba(6, 182, 212, 0.25);
        padding: 5px 12px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.05em;
        display: inline-flex;
        align-items: center;
    }

    /* Pulse Animations for Risk Ring */
    @keyframes pulse-emerald {
        0% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.4); }
        70% { box-shadow: 0 0 0 15px rgba(16, 185, 129, 0); }
        100% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
    }
    @keyframes pulse-amber {
        0% { box-shadow: 0 0 0 0 rgba(245, 158, 11, 0.4); }
        70% { box-shadow: 0 0 0 15px rgba(245, 158, 11, 0); }
        100% { box-shadow: 0 0 0 0 rgba(245, 158, 11, 0); }
    }
    @keyframes pulse-crimson {
        0% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.4); }
        70% { box-shadow: 0 0 0 15px rgba(239, 68, 68, 0); }
        100% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); }
    }

    .pulse-emerald { animation: pulse-emerald 2.5s infinite; }
    .pulse-amber { animation: pulse-amber 2.5s infinite; }
    .pulse-crimson { animation: pulse-crimson 2.5s infinite; }

    /* Custom styles for selectboxes and sliders to blend with dark mode */
    div[data-baseweb="select"] > div {
        background-color: #1e293b !important;
        border-color: rgba(255, 255, 255, 0.1) !important;
        color: #f8fafc !important;
    }
    
    /* Hover highlight details card */
    .info-card {
        background: rgba(30, 41, 59, 0.2);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 16px;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# Helper function to compute trend percentages and build inline SVG sparkline
def compute_trend_and_sparkline(history_df, column, unit):
    if len(history_df) < 2:
        return 0.0, "→", "#94a3b8", ""
        
    vals = history_df[column].values
    last_val = vals[-1]
    prev_val = vals[-2]
    
    # Calculate percentage change
    if prev_val != 0:
        change = ((last_val - prev_val) / prev_val) * 100
    else:
        change = 0.0
        
    if change > 0.05:
        icon = "↑"
        color = "#10b981" # Emerald
    elif change < -0.05:
        icon = "↓"
        color = "#ef4444" # Crimson
    else:
        icon = "•"
        color = "#94a3b8" # Muted Grey
        
    # Generate SVG Sparkline
    min_v, max_v = min(vals), max(vals)
    rng = (max_v - min_v) if max_v != min_v else 1.0
    width = 120
    height = 32
    
    points = []
    for i, val in enumerate(vals[-15:]):  # Display last 15 values for sparkline
        x = (i / (min(len(vals), 15) - 1)) * width
        y = height - ((val - min_v) / rng) * (height - 4) - 2
        points.append(f"{x},{y}")
        
    points_str = " ".join(points)
    
    spark_color = "#06b6d4"
    if column == "ph": spark_color = "#38bdf8"
    elif column == "turbidity": spark_color = "#f43f5e"
    elif column == "tds": spark_color = "#10b981"
    elif column == "dissolved_oxygen": spark_color = "#fbbf24"
    
    sparkline_svg = f"""
    <svg width="{width}" height="{height}" style="overflow: visible; display: block; margin: 0 auto;">
        <polyline fill="none" stroke="{spark_color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" points="{points_str}" />
    </svg>
    """
    
    return round(change, 2), icon, color, sparkline_svg

# Load locations and prepare selects
locations_df = load_location_data()
all_villages = sorted(locations_df["village"].unique())

# Initialize session state variables
if "selected_village" not in st.session_state:
    st.session_state.selected_village = all_villages[0]
if "historical_data" not in st.session_state:
    st.session_state.historical_data = generate_deterministic_history(st.session_state.selected_village)
if "streaming_active" not in st.session_state:
    st.session_state.streaming_active = False

# ==========================================
# SIDEBAR NAVIGATION & LOGO
# ==========================================
with st.sidebar:
    st.markdown("<div style='font-size: 28px; font-weight: 900; color: #06b6d4; margin-bottom: 2px;'>💧 AquaSense</div>", unsafe_allow_html=True)
    st.markdown("<div style='font-size: 11px; font-weight: 500; color: #64748b; letter-spacing: 0.1em; text-transform: uppercase; margin-bottom: 30px;'>Village Water Intelligence</div>", unsafe_allow_html=True)
    
    nav_selection = st.radio(
        "Navigation",
        ["Overview Dashboard", "Water Quality Analytics", "Risk Simulator", "About Project"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    # Selection Mode Toggle
    st.markdown("<div style='font-size: 13px; font-weight: 700; color: #94a3b8; margin-bottom: 10px;'>LOCATION SEARCH MODE</div>", unsafe_allow_html=True)
    search_mode = st.radio(
        "Search Mode",
        ["Quick Search", "Browse by Hierarchy"],
        label_visibility="collapsed"
    )
    
    if search_mode == "Quick Search":
        # Searchable Single Dropdown
        selected_v = st.selectbox(
            "Search Village",
            all_villages,
            index=all_villages.index(st.session_state.selected_village) if st.session_state.selected_village in all_villages else 0
        )
        if selected_v != st.session_state.selected_village:
            st.session_state.selected_village = selected_v
            st.session_state.historical_data = generate_deterministic_history(selected_v)
            st.session_state.streaming_active = False
            st.rerun()
    else:
        # Cascading selectors
        states = sorted(locations_df["state"].unique())
        
        # Resolve initial indices
        curr_dist, curr_state = get_village_metadata(st.session_state.selected_village)
        state_idx = states.index(curr_state) if curr_state in states else 0
        
        selected_state = st.selectbox("Select State", states, index=state_idx)
        
        districts = sorted(locations_df[locations_df["state"] == selected_state]["district"].unique())
        dist_idx = districts.index(curr_dist) if curr_dist in districts else 0
        selected_district = st.selectbox("Select District", districts, index=dist_idx)
        
        villages = sorted(locations_df[(locations_df["state"] == selected_state) & (locations_df["district"] == selected_district)]["village"].unique())
        vill_idx = villages.index(st.session_state.selected_village) if st.session_state.selected_village in villages else 0
        selected_v = st.selectbox("Select Village", villages, index=vill_idx)
        
        if selected_v != st.session_state.selected_village:
            st.session_state.selected_village = selected_v
            st.session_state.historical_data = generate_deterministic_history(selected_v)
            st.session_state.streaming_active = False
            st.rerun()

    st.markdown("---")
    
    # Configurations display
    st.markdown("<div style='font-size: 13px; font-weight: 700; color: #94a3b8; margin-bottom: 8px;'>TELEMETRY SAFE LIMITS</div>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style='font-size: 12px; color: #94a3b8; line-height: 1.6;'>
        • pH Range: <b>{PH_MIN} - {PH_MAX}</b><br>
        • Turbidity: <b>&lt; {TURBIDITY_LIMIT} NTU</b><br>
        • TDS Limit: <b>&lt; {TDS_LIMIT} mg/L</b><br>
        • Min Oxygen: <b>&gt; {DO_MINIMUM} mg/L</b>
    </div>
    """, unsafe_allow_html=True)

# Resolve selected location metadata
district, state = get_village_metadata(st.session_state.selected_village)
history_df = st.session_state.historical_data
current_reading = history_df.iloc[-1]

# ==========================================
# HEADER & HERO SECTION
# ==========================================
st.markdown(f"""
<div class="header-container">
    <div>
        <h1 style="margin: 0; font-size: 32px; font-weight: 900; background: linear-gradient(to right, #0ea5e9, #22d3ee); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">AquaSense</h1>
        <p style="margin: 4px 0 0 0; font-size: 15px; color: #94a3b8;">Real-time water quality monitoring and ML-powered risk assessment across Northeast India.</p>
    </div>
    <div class="header-badge-container">
        <div class="badge-online">
            <span style="display:inline-block; width: 8px; height: 8px; background: #10b981; border-radius: 50%;"></span>
            SYSTEM ONLINE
        </div>
        <div class="badge-demo">
            DEMO / SIMULATION MODE
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Location info breadcrumb
st.markdown(f"""
<div style="margin-bottom: 24px; padding-left: 4px;">
    <span style="font-size: 12px; font-weight: 700; color: #06b6d4; text-transform: uppercase; letter-spacing: 0.1em;">Selected Location</span>
    <h2 style="margin: 4px 0 0 0; font-size: 26px; font-weight: 800; color: #f8fafc;">{st.session_state.selected_village}</h2>
    <div style="font-size: 14px; color: #64748b; margin-top: 2px;">District: <b>{district}</b> • State: <b>{state}</b></div>
</div>
""", unsafe_allow_html=True)

# ==========================================
# MAIN INTERFACES BASED ON SELECTION
# ==========================================
if nav_selection == "Overview Dashboard":
    
    # --------------------------------------------------
    # ROW 1: RISK ASSESSMENT & LIVE SIMULATION INTERACTION
    # --------------------------------------------------
    col_risk, col_control = st.columns([2, 1])
    
    with col_risk:
        # Calculate Risk prediction
        risk_level, risk_score, risk_desc, is_real = predict_risk(
            current_reading['ph'],
            current_reading['turbidity'],
            current_reading['tds'],
            current_reading['dissolved_oxygen']
        )
        
        # Color resolution
        if risk_level == "LOW":
            color_name = "emerald"
            border_color = "#10b981"
            text_color = "#10b981"
            shadow_color = "rgba(16, 185, 129, 0.4)"
        elif risk_level == "MEDIUM":
            color_name = "amber"
            border_color = "#f59e0b"
            text_color = "#f59e0b"
            shadow_color = "rgba(245, 158, 11, 0.4)"
        else:
            color_name = "crimson"
            border_color = "#ef4444"
            text_color = "#ef4444"
            shadow_color = "rgba(239, 68, 68, 0.4)"
            
        st.markdown(f"""
        <div class="risk-container" style="display: flex; align-items: center; justify-content: center; flex-direction: column; padding: 28px; background: rgba(30, 41, 59, 0.35); border: 1px solid rgba(255,255,255,0.06); border-radius: 16px; text-align: center;">
            <div class="risk-indicator pulse-{color_name}" style="width: 100px; height: 100px; border-radius: 50%; display: flex; align-items: center; justify-content: center; border: 4px solid {border_color}; margin-bottom: 16px;">
                <span style="font-size: 22px; font-weight: 800; color: #f8fafc;">{risk_score}%</span>
            </div>
            <div style="font-size: 11px; text-transform: uppercase; letter-spacing: 0.15em; color: #94a3b8; font-weight: 700;">ML Risk Index</div>
            <div style="font-size: 30px; font-weight: 900; color: {text_color}; margin-top: 4px; letter-spacing: 0.05em; text-shadow: 0 0 20px {shadow_color};">{risk_level} RISK</div>
            <p style="margin: 12px 0 0 0; font-size: 14px; color: #cbd5e1; max-width: 460px; line-height: 1.5;">{risk_desc}</p>
            <div style="margin-top: 14px; font-size: 11px; color: #64748b; font-style: italic; border-top: 1px solid rgba(255,255,255,0.05); padding-top: 8px; width: 100%;">
                ⚡ <b>DEMO MODEL</b> — NOT FOR CLINICAL DIAGNOSIS
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_control:
        st.markdown(f"""
        <div class="info-card" style="height: 100%; display: flex; flex-direction: column; justify-content: space-between;">
            <div>
                <h4 style="margin: 0; font-size: 16px; font-weight: 700; color: #f8fafc;">Sensor Simulation Engine</h4>
                <p style="font-size: 13px; color: #94a3b8; margin: 6px 0 16px 0; line-height: 1.4;">
                    Enable live telemetry simulation to stream water readings dynamically using a smooth random-walk model.
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        # Time-range control
        time_range = st.selectbox(
            "Graph Telemetry Time Range",
            ["LIVE", "1H", "6H", "12H", "24H", "7D"],
            index=0
        )
        
        if time_range == "LIVE":
            stream_btn = st.checkbox("Stream Simulated Telemetry", value=st.session_state.streaming_active)
            if stream_btn != st.session_state.streaming_active:
                st.session_state.streaming_active = stream_btn
                st.rerun()
                
            if st.session_state.streaming_active:
                st.markdown("<p style='font-size: 12px; color: #10b981; margin: 4px 0 0 0;'>🟢 Telemetry stream active. Updating UI...</p>", unsafe_allow_html=True)
            else:
                st.markdown("<p style='font-size: 12px; color: #e2e8f0; margin: 4px 0 0 0;'>⚪ Stream paused.</p>", unsafe_allow_html=True)
        else:
            st.session_state.streaming_active = False
            st.markdown(f"<p style='font-size: 12px; color: #94a3b8; margin: 4px 0 0 0;'>Displaying static history of {time_range}.</p>", unsafe_allow_html=True)
            
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    # --------------------------------------------------
    # ROW 2: WATER QUALITY METRIC CARDS (4 COLUMNS)
    # --------------------------------------------------
    st.markdown("<h3 style='font-size: 18px; font-weight: 700; color: #94a3b8; margin-bottom: 12px;'>Current Water Quality Parameters</h3>", unsafe_allow_html=True)
    
    cols = st.columns(4)
    
    # 1. pH
    ph_val = current_reading['ph']
    ph_status, ph_color_name = get_parameter_status("ph", ph_val)
    ph_change, ph_icon, ph_t_color, ph_spark = compute_trend_and_sparkline(history_df, "ph", "")
    
    # 2. Turbidity
    turb_val = current_reading['turbidity']
    turb_status, turb_color_name = get_parameter_status("turbidity", turb_val)
    turb_change, turb_icon, turb_t_color, turb_spark = compute_trend_and_sparkline(history_df, "turbidity", "NTU")
    
    # 3. TDS
    tds_val = current_reading['tds']
    tds_status, tds_color_name = get_parameter_status("tds", tds_val)
    tds_change, tds_icon, tds_t_color, tds_spark = compute_trend_and_sparkline(history_df, "tds", "mg/L")
    
    # 4. Dissolved Oxygen
    do_val = current_reading['dissolved_oxygen']
    do_status, do_color_name = get_parameter_status("dissolved_oxygen", do_val)
    do_change, do_icon, do_t_color, do_spark = compute_trend_and_sparkline(history_df, "dissolved_oxygen", "mg/L")
    
    # Card 1 HTML
    status_bg = "rgba(16, 185, 129, 0.12)" if ph_color_name == "Emerald" else "rgba(245, 158, 11, 0.12)" if ph_color_name == "Amber" else "rgba(239, 68, 68, 0.12)"
    status_text = "#10b981" if ph_color_name == "Emerald" else "#f59e0b" if ph_color_name == "Amber" else "#ef4444"
    cols[0].markdown(f"""
    <div class="metric-card">
        <div style="display: flex; justify-content: space-between; align-items: flex-start;">
            <div>
                <div style="font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; color: #94a3b8;">Water pH Level</div>
                <div style="font-size: 28px; font-weight: 800; color: #f8fafc; margin-top: 6px;">{ph_val}</div>
            </div>
            <div style="text-align: right;">
                <span style="background: {status_bg}; color: {status_text}; border: 1px solid rgba(255,255,255,0.05); padding: 3px 8px; border-radius: 20px; font-size: 10px; font-weight: 700; letter-spacing: 0.05em;">{ph_status}</span>
                <div style="font-size: 11px; font-weight: 700; color: {ph_t_color}; margin-top: 8px;">{ph_icon} {abs(ph_change)}%</div>
            </div>
        </div>
        <div style="margin-top: 18px;">
            {ph_spark}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Card 2 HTML
    status_bg = "rgba(16, 185, 129, 0.12)" if turb_color_name == "Emerald" else "rgba(245, 158, 11, 0.12)" if turb_color_name == "Amber" else "rgba(239, 68, 68, 0.12)"
    status_text = "#10b981" if turb_color_name == "Emerald" else "#f59e0b" if turb_color_name == "Amber" else "#ef4444"
    cols[1].markdown(f"""
    <div class="metric-card">
        <div style="display: flex; justify-content: space-between; align-items: flex-start;">
            <div>
                <div style="font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; color: #94a3b8;">Turbidity</div>
                <div style="font-size: 28px; font-weight: 800; color: #f8fafc; margin-top: 6px;">{turb_val} <span style="font-size: 12px; color: #64748b; font-weight: 500;">NTU</span></div>
            </div>
            <div style="text-align: right;">
                <span style="background: {status_bg}; color: {status_text}; border: 1px solid rgba(255,255,255,0.05); padding: 3px 8px; border-radius: 20px; font-size: 10px; font-weight: 700; letter-spacing: 0.05em;">{turb_status}</span>
                <div style="font-size: 11px; font-weight: 700; color: {turb_t_color}; margin-top: 8px;">{turb_icon} {abs(turb_change)}%</div>
            </div>
        </div>
        <div style="margin-top: 18px;">
            {turb_spark}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Card 3 HTML
    status_bg = "rgba(16, 185, 129, 0.12)" if tds_color_name == "Emerald" else "rgba(245, 158, 11, 0.12)" if tds_color_name == "Amber" else "rgba(239, 68, 68, 0.12)"
    status_text = "#10b981" if tds_color_name == "Emerald" else "#f59e0b" if tds_color_name == "Amber" else "#ef4444"
    cols[2].markdown(f"""
    <div class="metric-card">
        <div style="display: flex; justify-content: space-between; align-items: flex-start;">
            <div>
                <div style="font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; color: #94a3b8;">Dissolved Solids</div>
                <div style="font-size: 28px; font-weight: 800; color: #f8fafc; margin-top: 6px;">{int(tds_val)} <span style="font-size: 12px; color: #64748b; font-weight: 500;">mg/L</span></div>
            </div>
            <div style="text-align: right;">
                <span style="background: {status_bg}; color: {status_text}; border: 1px solid rgba(255,255,255,0.05); padding: 3px 8px; border-radius: 20px; font-size: 10px; font-weight: 700; letter-spacing: 0.05em;">{tds_status}</span>
                <div style="font-size: 11px; font-weight: 700; color: {tds_t_color}; margin-top: 8px;">{tds_icon} {abs(tds_change)}%</div>
            </div>
        </div>
        <div style="margin-top: 18px;">
            {tds_spark}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Card 4 HTML
    status_bg = "rgba(16, 185, 129, 0.12)" if do_color_name == "Emerald" else "rgba(245, 158, 11, 0.12)" if do_color_name == "Amber" else "rgba(239, 68, 68, 0.12)"
    status_text = "#10b981" if do_color_name == "Emerald" else "#f59e0b" if do_color_name == "Amber" else "#ef4444"
    cols[3].markdown(f"""
    <div class="metric-card">
        <div style="display: flex; justify-content: space-between; align-items: flex-start;">
            <div>
                <div style="font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; color: #94a3b8;">Dissolved Oxygen</div>
                <div style="font-size: 28px; font-weight: 800; color: #f8fafc; margin-top: 6px;">{do_val} <span style="font-size: 12px; color: #64748b; font-weight: 500;">mg/L</span></div>
            </div>
            <div style="text-align: right;">
                <span style="background: {status_bg}; color: {status_text}; border: 1px solid rgba(255,255,255,0.05); padding: 3px 8px; border-radius: 20px; font-size: 10px; font-weight: 700; letter-spacing: 0.05em;">{do_status}</span>
                <div style="font-size: 11px; font-weight: 700; color: {do_t_color}; margin-top: 8px;">{do_icon} {abs(do_change)}%</div>
            </div>
        </div>
        <div style="margin-top: 18px;">
            {do_spark}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # --------------------------------------------------
    # ROW 3: WATER PARAMETERS DUAL CHARTS GRID
    # --------------------------------------------------
    st.markdown("<h3 style='font-size: 18px; font-weight: 700; color: #94a3b8; margin-bottom: 12px;'>Telemetry Historical Visualizations</h3>", unsafe_allow_html=True)
    
    # Select subset of data based on selection range
    if time_range == "LIVE" or time_range == "24H":
        filtered_df = history_df.tail(24)
    elif time_range == "1H":
        filtered_df = history_df.tail(4)
    elif time_range == "6H":
        filtered_df = history_df.tail(6)
    elif time_range == "12H":
        filtered_df = history_df.tail(12)
    else:  # 7D
        filtered_df = history_df
        
    g_col1, g_col2 = st.columns(2)
    
    with g_col1:
        st.markdown("<div style='font-size: 13px; font-weight: 700; color: #cbd5e1; margin-bottom: 8px;'>Water pH Level Trend</div>", unsafe_allow_html=True)
        st.plotly_chart(
            create_parameter_chart(filtered_df, "ph", "pH Level", "", PH_MIN, PH_MAX, line_color="#38bdf8", fill_color="rgba(56, 189, 248, 0.06)"),
            use_container_width=True
        )
        
        st.markdown("<div style='font-size: 13px; font-weight: 700; color: #cbd5e1; margin-bottom: 8px;'>Total Dissolved Solids (TDS) Trend</div>", unsafe_allow_html=True)
        st.plotly_chart(
            create_parameter_chart(filtered_df, "tds", "TDS", "mg/L", 0.0, TDS_LIMIT, line_color="#10b981", fill_color="rgba(16, 185, 129, 0.06)"),
            use_container_width=True
        )
        
    with g_col2:
        st.markdown("<div style='font-size: 13px; font-weight: 700; color: #cbd5e1; margin-bottom: 8px;'>Turbidity Level Trend</div>", unsafe_allow_html=True)
        st.plotly_chart(
            create_parameter_chart(filtered_df, "turbidity", "Turbidity", "NTU", 0.0, TURBIDITY_LIMIT, line_color="#f43f5e", fill_color="rgba(244, 63, 94, 0.06)"),
            use_container_width=True
        )
        
        st.markdown("<div style='font-size: 13px; font-weight: 700; color: #cbd5e1; margin-bottom: 8px;'>Dissolved Oxygen Trend</div>", unsafe_allow_html=True)
        st.plotly_chart(
            create_parameter_chart(filtered_df, "dissolved_oxygen", "DO", "mg/L", DO_MINIMUM, 14.0, line_color="#fbbf24", fill_color="rgba(251, 191, 36, 0.06)"),
            use_container_width=True
        )

    # --------------------------------------------------
    # LIVE TELEMETRY SIMULATION LOOP RUNNING AT END
    # --------------------------------------------------
    if st.session_state.streaming_active and time_range == "LIVE":
        # Increment telemetries with small smooth changes
        time.sleep(1.0)
        
        latest_ph = np.clip(current_reading['ph'] + np.random.normal(0, 0.03), 4.5, 9.5)
        latest_turb = np.clip(current_reading['turbidity'] + np.random.normal(0, 0.15), 0.2, 22.0)
        latest_tds = np.clip(current_reading['tds'] + np.random.normal(0, 4.0), 30.0, 750.0)
        latest_do = np.clip(current_reading['dissolved_oxygen'] + np.random.normal(0, 0.1), 1.5, 12.0)
        
        new_row = {
            "timestamp": datetime.now(),
            "ph": round(latest_ph, 2),
            "turbidity": round(latest_turb, 2),
            "tds": round(latest_tds, 1),
            "dissolved_oxygen": round(latest_do, 2)
        }
        
        # Append to historical data and trim length to keep it clean
        updated_history = pd.concat([history_df, pd.DataFrame([new_row])], ignore_index=True)
        if len(updated_history) > 60:
            updated_history = updated_history.iloc[1:]
            
        st.session_state.historical_data = updated_history
        st.rerun()

elif nav_selection == "Water Quality Analytics":
    st.markdown("<h3 style='font-size: 20px; font-weight: 700; color: #cbd5e1; margin-bottom: 16px;'>Water Quality Metric Distribution</h3>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("<div style='font-size: 14px; font-weight: 600; color: #94a3b8; margin-bottom: 12px;'>Parameter Ranges and Deviations</div>", unsafe_allow_html=True)
        
        # Create statistics table
        summary_stats = history_df[["ph", "turbidity", "tds", "dissolved_oxygen"]].describe().T
        summary_stats.columns = ["Data Count", "Mean Value", "Std Dev", "Minimum", "25%", "Median", "75%", "Maximum"]
        st.dataframe(summary_stats.style.format("{:.2f}"), use_container_width=True)
        
    with col2:
        st.markdown("<div style='font-size: 14px; font-weight: 600; color: #94a3b8; margin-bottom: 12px;'>Correlation Matrix of Water Attributes</div>", unsafe_allow_html=True)
        # Numerical Correlation
        corr = history_df[["ph", "turbidity", "tds", "dissolved_oxygen"]].corr()
        import plotly.express as px
        fig_corr = px.imshow(
            corr,
            text_auto=True,
            aspect="auto",
            color_continuous_scale="RdBu_r",
            labels=dict(color="Correlation")
        )
        fig_corr.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#94a3b8"),
            height=240,
            margin=dict(l=20, r=20, t=10, b=10)
        )
        st.plotly_chart(fig_corr, use_container_width=True)

    st.markdown("<br>---", unsafe_allow_html=True)
    st.markdown("<h3 style='font-size: 18px; font-weight: 700; color: #cbd5e1; margin-bottom: 16px;'>Historical Data Table</h3>", unsafe_allow_html=True)
    
    # Render interactive data explorer
    st.dataframe(
        history_df.sort_values(by="timestamp", ascending=False).style.format({
            "ph": "{:.2f}",
            "turbidity": "{:.2f} NTU",
            "tds": "{:.1f} mg/L",
            "dissolved_oxygen": "{:.2f} mg/L"
        }),
        use_container_width=True,
        height=350
    )

elif nav_selection == "Risk Simulator":
    st.markdown("<h3 style='font-size: 20px; font-weight: 700; color: #cbd5e1; margin-bottom: 6px;'>Interactive Risk Simulator</h3>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 14px; color: #94a3b8; margin-bottom: 24px;'>Manually adjust water metrics to simulate how variations affect predicted disease risk indexes.</p>", unsafe_allow_html=True)
    
    sim_col1, sim_col2 = st.columns([1, 1])
    
    with sim_col1:
        st.markdown("<div style='font-size: 14px; font-weight: 700; color: #f8fafc; margin-bottom: 16px;'>Adjust Parameters</div>", unsafe_allow_html=True)
        
        sim_ph = st.slider("Water pH Level", 4.0, 10.0, float(current_reading['ph']), 0.1)
        sim_turb = st.slider("Turbidity (NTU)", 0.1, 25.0, float(current_reading['turbidity']), 0.1)
        sim_tds = st.slider("Total Dissolved Solids (mg/L)", 10.0, 800.0, float(current_reading['tds']), 10.0)
        sim_do = st.slider("Dissolved Oxygen (mg/L)", 1.0, 14.0, float(current_reading['dissolved_oxygen']), 0.1)
        
    with sim_col2:
        st.markdown("<div style='font-size: 14px; font-weight: 700; color: #f8fafc; margin-bottom: 16px;'>Simulation Risk Result</div>", unsafe_allow_html=True)
        
        # Compute prediction
        sim_risk, sim_score, sim_desc, _ = predict_risk(sim_ph, sim_turb, sim_tds, sim_do)
        
        if sim_risk == "LOW":
            sim_color = "#10b981"
            sim_shadow = "rgba(16, 185, 129, 0.4)"
            sim_color_name = "emerald"
        elif sim_risk == "MEDIUM":
            sim_color = "#f59e0b"
            sim_shadow = "rgba(245, 158, 11, 0.4)"
            sim_color_name = "amber"
        else:
            sim_color = "#ef4444"
            sim_shadow = "rgba(239, 68, 68, 0.4)"
            sim_color_name = "crimson"
            
        st.markdown(f"""
        <div class="risk-container" style="display: flex; align-items: center; justify-content: center; flex-direction: column; padding: 32px; background: rgba(30, 41, 59, 0.35); border: 1px solid rgba(255,255,255,0.06); border-radius: 16px; text-align: center; height: 100%;">
            <div class="risk-indicator pulse-{sim_color_name}" style="width: 110px; height: 110px; border-radius: 50%; display: flex; align-items: center; justify-content: center; border: 4px solid {sim_color}; margin-bottom: 20px;">
                <span style="font-size: 24px; font-weight: 800; color: #f8fafc;">{sim_score}%</span>
            </div>
            <div style="font-size: 11px; text-transform: uppercase; letter-spacing: 0.15em; color: #94a3b8; font-weight: 700;">Simulated Index</div>
            <div style="font-size: 32px; font-weight: 900; color: {sim_color}; margin-top: 4px; letter-spacing: 0.05em; text-shadow: 0 0 20px {sim_shadow};">{sim_risk} RISK</div>
            <p style="margin: 14px 0 0 0; font-size: 14px; color: #cbd5e1; max-width: 420px; line-height: 1.5;">{sim_desc}</p>
        </div>
        """, unsafe_allow_html=True)

elif nav_selection == "About Project":
    st.markdown("<h3 style='font-size: 20px; font-weight: 700; color: #cbd5e1; margin-bottom: 12px;'>About AquaSense</h3>", unsafe_allow_html=True)
    st.markdown("""
    **AquaSense** is a smart water intelligence dashboard designed to monitor and predict water quality metrics 
    and associated water-borne disease risk factors across village locations in the 8 states of Northeast India.
    
    ### Core Objectives
    - **Democratized Accessibility**: Provides local municipal bodies and health inspectors with easy access to village-level diagnostic criteria.
    - **Early Warnings**: Evaluates pH, Turbidity, TDS, and DO to predict contamination vectors using machine learning.
    - **Continuous Telemetry**: Standardized structures designed for instant IoT telemetry pipelines and offline database integration.
    
    ### Safe Water Quality Parameters
    The system follows project-defined thresholds aligned with World Health Organization (WHO) and Indian Standard guidelines:
    - **pH Level**: 6.5 – 8.5 (Ensures water is neither too acidic nor alkaline)
    - **Turbidity**: < 5.0 NTU (Measures cloudiness, indicative of suspended particles/pathogens)
    - **Total Dissolved Solids (TDS)**: < 500 mg/L (Total concentration of inorganic substances)
    - **Dissolved Oxygen (DO)**: > 5.0 mg/L (Essential parameter indicating fresh, flowing water)
    
    ### Model & Data Integration Specs
    This deployment runs on **Demo Model Mode**. The interface is designed with a separate modular structure so that:
    1. A trained pipeline (`models/model.pkl`) can be dropped in.
    2. Real-time IoT databases (e.g. PostgreSQL, InfluxDB) can replace the CSV data loaders (`utils/data_loader.py`).
    """, unsafe_allow_html=True)
