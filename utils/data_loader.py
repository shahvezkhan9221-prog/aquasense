import pandas as pd
import numpy as np
import streamlit as st
import hashlib
from datetime import datetime, timedelta

@st.cache_data
def load_location_data():
    """
    Loads mapping of state, district, village from CSV.
    """
    try:
        df = pd.read_csv("data/locations.csv")
        return df
    except Exception as e:
        st.error(f"Error loading locations.csv: {e}")
        # Fallback minimal dataset in case file is missing
        return pd.DataFrame({
            "state": ["Meghalaya", "Assam"],
            "district": ["East Khasi Hills", "Kamrup Metropolitan"],
            "village": ["Mawlynnong Village", "Guwahati Town"]
        })

@st.cache_data
def load_water_quality_base():
    """
    Loads baseline water quality data points from CSV.
    """
    try:
        df = pd.read_csv("data/water_quality.csv")
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        return df
    except Exception:
        return pd.DataFrame(columns=["village", "timestamp", "ph", "turbidity", "tds", "dissolved_oxygen"])

def get_village_metadata(village_name):
    """
    Returns (district, state) for a village.
    """
    df = load_location_data()
    row = df[df['village'] == village_name]
    if not row.empty:
        return row.iloc[0]['district'], row.iloc[0]['state']
    return "Unknown District", "Unknown State"

def generate_deterministic_history(village_name, hours=24):
    """
    Generates realistic, smooth, and deterministic time-series water quality readings
    for a village using a seed generated from the village name.
    """
    # Create a stable seed from the village name
    hash_object = hashlib.md5(village_name.encode('utf-8'))
    seed = int(hash_object.hexdigest(), 16) % 10**8
    np.random.seed(seed)
    
    # Establish base attributes based on the seed
    # Normal ranges:
    # pH: 6.5 - 8.5
    # Turbidity: 0 - 15 NTU
    # TDS: 50 - 600 mg/L
    # DO: 3 - 10 mg/L
    
    base_ph = 6.5 + np.random.rand() * 2.0  # 6.5 to 8.5
    base_turb = 0.5 + (np.random.rand() ** 2) * 12.0  # skew lower but can be higher
    base_tds = 80.0 + np.random.rand() * 400.0  # 80 to 480
    base_do = 4.5 + np.random.rand() * 4.5  # 4.5 to 9.0
    
    # Allow some villages to have abnormal levels for rich risk display
    if seed % 7 == 0:  # High risk village
        base_ph = 5.2 if seed % 2 == 0 else 9.1
        base_turb = 12.5
        base_tds = 580.0
        base_do = 3.2
    elif seed % 5 == 0:  # Moderate risk village
        base_ph = 6.2
        base_turb = 6.0
        base_tds = 390.0
        base_do = 5.1

    # Generate time series
    now = datetime.now()
    records = []
    
    current_ph = base_ph
    current_turb = base_turb
    current_tds = base_tds
    current_do = base_do
    
    for i in range(hours):
        # Time steps going backward
        timestamp = now - timedelta(hours=hours - 1 - i)
        
        # Smooth random walk (interpolation simulation)
        current_ph = np.clip(current_ph + np.random.normal(0, 0.05), 4.0, 10.0)
        current_turb = np.clip(current_turb + np.random.normal(0, 0.2), 0.1, 25.0)
        current_tds = np.clip(current_tds + np.random.normal(0, 5.0), 10.0, 800.0)
        current_do = np.clip(current_do + np.random.normal(0, 0.15), 1.0, 14.0)
        
        records.append({
            "timestamp": timestamp,
            "ph": round(current_ph, 2),
            "turbidity": round(current_turb, 2),
            "tds": round(current_tds, 1),
            "dissolved_oxygen": round(current_do, 2)
        })
        
    return pd.DataFrame(records)
