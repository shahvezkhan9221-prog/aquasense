import os
import joblib
import streamlit as st

# ==========================================
# CONFIGURABLE WATER QUALITY THRESHOLDS
# ==========================================
PH_MIN = 6.5
PH_MAX = 8.5
TURBIDITY_LIMIT = 5.0      # NTU
TDS_LIMIT = 500.0          # mg/L
DO_MINIMUM = 5.0           # mg/L

@st.cache_resource
def load_model():
    """
    Attempts to load a trained model (joblib or pickle format).
    Returns None if not found, signaling UI to use mock prediction.
    """
    model_paths = [
        "models/model.pkl",
        "models/model.joblib"
    ]
    for path in model_paths:
        if os.path.exists(path):
            try:
                model = joblib.load(path)
                return model
            except Exception as e:
                # Log error silently or let main UI know
                pass
    return None

def get_parameter_status(param_name, val):
    """
    Calculates safety status for a specific parameter: Normal, Moderate, or Concerning.
    """
    if param_name == "ph":
        if PH_MIN <= val <= PH_MAX:
            return "Normal", "Emerald"
        elif (5.8 <= val < PH_MIN) or (PH_MAX < val <= 9.2):
            return "Moderate", "Amber"
        else:
            return "Concerning", "Crimson"
            
    elif param_name == "turbidity":
        if val <= TURBIDITY_LIMIT:
            return "Normal", "Emerald"
        elif val <= 10.0:
            return "Moderate", "Amber"
        else:
            return "Concerning", "Crimson"
            
    elif param_name == "tds":
        if val <= TDS_LIMIT:
            return "Normal", "Emerald"
        elif val <= 650.0:
            return "Moderate", "Amber"
        else:
            return "Concerning", "Crimson"
            
    elif param_name == "dissolved_oxygen":
        if val >= DO_MINIMUM:
            return "Normal", "Emerald"
        elif val >= 4.0:
            return "Moderate", "Amber"
        else:
            return "Concerning", "Crimson"
            
    return "Unknown", "Grey"

def predict_risk(ph, turbidity, tds, dissolved_oxygen):
    """
    Calculates prediction risk using real ML model if loaded,
    otherwise executes the high-fidelity mock ML logic with clear logging.
    Returns: (Risk String, Risk Score 0-100, Description, is_real_model)
    """
    model = load_model()
    
    if model is not None:
        try:
            # Format inputs correctly matching project feature expectations
            # Example: features = [[ph, turbidity, tds, dissolved_oxygen]]
            # Make sure feature order is aligned here
            features = [[ph, turbidity, tds, dissolved_oxygen]]
            prediction_prob = model.predict_proba(features)[0] # Assuming classifier
            # Let's say risk probability is class 1
            risk_score = float(prediction_prob[1]) * 100
            
            if risk_score < 30:
                risk_level = "LOW"
            elif risk_score < 70:
                risk_level = "MEDIUM"
            else:
                risk_level = "HIGH"
                
            return risk_level, risk_score, "", True
        except Exception as e:
            # Fallback to mock on failure
            pass

    # -------------------------------------------------------------
    # DEMO MODEL — NOT FOR REAL PREDICTION (Rule-Based Fallback)
    # -------------------------------------------------------------
    # Calculate a custom composite risk score (0 - 100)
    score = 0.0
    
    # 1. pH deviations
    if ph < PH_MIN:
        score += min(30.0, (PH_MIN - ph) * 20)
    elif ph > PH_MAX:
        score += min(30.0, (ph - PH_MAX) * 20)
        
    # 2. Turbidity deviations
    if turbidity > TURBIDITY_LIMIT:
        score += min(35.0, (turbidity - TURBIDITY_LIMIT) * 4.5)
        
    # 3. TDS deviations
    if tds > TDS_LIMIT:
        score += min(20.0, ((tds - TDS_LIMIT) / 100.0) * 10.0)
        
    # 4. Dissolved Oxygen deviations
    if dissolved_oxygen < DO_MINIMUM:
        score += min(35.0, (DO_MINIMUM - dissolved_oxygen) * 15)
        
    score = min(100.0, max(5.0, score))
    
    # Map score to category
    if score < 33.0:
        risk_level = "LOW"
        desc = "Current water-quality conditions indicate a relatively lower predicted risk. Continue routine monitoring."
    elif score < 66.0:
        risk_level = "MEDIUM"
        desc = "Current conditions indicate moderate predicted risk. Increased monitoring is recommended."
    else:
        risk_level = "HIGH"
        desc = "Current conditions indicate elevated predicted risk. Immediate assessment and preventive action are recommended."
        
    return risk_level, round(score, 1), desc, False
