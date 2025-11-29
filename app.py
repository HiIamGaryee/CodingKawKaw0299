import streamlit as st
import pydeck as pdk
import pandas as pd
import pickle
import time
import ollama
import os

# --- 1. SETUP PAGE ---
st.set_page_config(layout="wide", page_title="UrbanPulse: Planner Pro")

st.markdown("""
<style>
    div.stButton > button {
        width: 100%;
        height: 80px;
        border-radius: 12px;
        border: 2px solid #303030;
        background-color: #1E1E1E;
        color: white;
        transition: all 0.3s;
        font-size: 16px;
    }
    div.stButton > button:hover {
        border-color: #4CAF50;
        background-color: #2E2E2E;
        transform: translateY(-2px);
    }
    div.stButton > button:focus {
        border-color: #4CAF50;
        box-shadow: 0 0 10px #4CAF50;
    }
    .metric-card {
        background-color: #0E1117;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #303030;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. CONFIGURATION ---
LOCATIONS = {
    "Jalan Tun Razak (Commercial)": {"id": "Tun_Razak", "coords": [3.1579, 101.7116], "district": "Bukit Bintang", "density": 11000, "base_traffic": 8500},
    "Bangsar South (Mixed Usage)":  {"id": "Bangsar",   "coords": [3.1110, 101.6650], "district": "Bangsar",       "density": 6500,  "base_traffic": 6000},
    "Cheras Utama (Residential)":   {"id": "Cheras",    "coords": [3.0550, 101.7560], "district": "Cheras",        "density": 9500,  "base_traffic": 7000}
}

# Image Mapping
IMAGE_MAPPING = {
    "None": "Baseline",
    "Trees": "Green",
    "Bike": "Bike",
    "Emergency": "Emergency",
    "Flyover": "Flyover",
    "PublicTransport": "PublicTransport"
}

# --- 3. MATH ENGINE (Updated with Logic for Flyovers/PT) ---
class UrbanPulseAI:
    def __init__(self):
        try:
            with open("model_stress.pkl", "rb") as f: self.stress_model = pickle.load(f)
            with open("model_roi.pkl", "rb") as f: self.roi_model = pickle.load(f)
            with open("encoder.pkl", "rb") as f: self.le = pickle.load(f)
            self.loaded = True
        except:
            self.loaded = False

    def predict(self, loc_data, weather_txt, intervention_code):
        if not self.loaded: return 85.0, 0.0, 8000
        
        # Parse Inputs
        w_code = 0 if "Rain" in weather_txt else 2
        
        # --- NEW LOGIC FOR INTERVENTIONS ---
        i_code = 0
        traffic_mod = 0
        
        traffic = loc_data["base_traffic"]
        if w_code == 2: traffic += 500 # Sunny adds traffic

        if intervention_code == "Trees": 
            i_code = 1
            
        elif intervention_code == "Bike": 
            i_code = 2
            traffic *= 0.85 # 15% reduction
            
        elif intervention_code == "Emergency": 
            i_code = 3
            
        elif intervention_code == "Flyover":
            i_code = 4 # Logic: Flyover
            # INDUCED DEMAND: Building roads creates MORE traffic long term
            traffic *= 1.15 
            
        elif intervention_code == "PublicTransport":
            i_code = 5 # Logic: Bus/Tram Lane
            # MODAL SHIFT: Efficient PT reduces cars significantly
            traffic *= 0.70 

        # Prepare Data for ML (We fallback to i_code=0 for unknown types to prevent crash, 
        # but modify traffic/stress manually below for the new types)
        
        try: dist_code = self.le.transform([loc_data["district"]])[0]
        except: dist_code = 0
            
        # Predict using ML (Base calculations)
        # Note: We pass i_code 0 for new types to get a baseline, then adjust below
        ml_i_code = i_code if i_code <= 3 else 0 
        
        inputs = pd.DataFrame(
            [[traffic, w_code, ml_i_code, loc_data["density"], dist_code]], 
            columns=["traffic", "weather", "intervention", "density", "district_code"]
        )
        
        stress = self.stress_model.predict(inputs)[0]
        roi = self.roi_model.predict(inputs)[0]
        
        # --- MANUAL OVERRIDES FOR NEW TYPES (Since ML wasn't trained on them) ---
        if intervention_code == "Flyover":
            stress += 15.0 # Noise & Visual pollution
            roi -= 1.5     # High cost, negative health impact
            
        if intervention_code == "PublicTransport":
            stress -= 10.0 # Better flow
            roi += 4.5     # Massive health benefit (Active travel + less pollution)

        return round(stress, 1), round(roi, 2), int(traffic)

# --- 4. AI COPILOT ---
class SeaLionBrain:
    def ask_copilot(self, location, intervention, stress_score, roi, weather):
        system_prompt = """
        ACT AS: Senior Town Planner for DBKL.
        TONE: Professional, concise, Malaysian government style.
        TASK: Review the simulation. Keep it under 2 sentences.
        """
        user_prompt = f"Data: {location}, {weather}, {intervention}, Stress: {stress_score}, ROI: {roi}M."
        try:
            response = ollama.chat(model='llama3.2', messages=[{'role': 'system', 'content': system_prompt}, {'role': 'user', 'content': user_prompt}])
            return response['message']['content']
        except:
            return "⚠️ AI Offline."

math_engine = UrbanPulseAI()
ai_brain = SeaLionBrain()

# --- 5. SESSION STATE ---
if 'active_tool' not in st.session_state:
    st.session_state.active_tool = "None"

# --- 6. UI HEADER ---
c_logo, c_title = st.columns([1, 6])
with c_logo: st.image("https://img.icons8.com/color/96/city-hall.png", width=70)
with c_title: 
    st.title("UrbanPulse: Planner Pro")
    st.caption("Advanced Scenario Modeling: Highways vs. Public Transit")

selected_loc_name = st.selectbox("📍 Active District", list(LOCATIONS.keys()))
loc_data = LOCATIONS[selected_loc_name]
weather = st.radio("Weather Condition", ["☀️ Sunny", "🌧️ Heavy Rain"], horizontal=True)

st.markdown("---")

# --- 7. UPDATED TOOL PALETTE (2 Rows) ---
st.subheader("🛠️ Infrastructure Dock")

# Row 1: The "Soft" Interventions
c1, c2, c3 = st.columns(3)
with c1:
    if st.button("🚫 Clear Site"): st.session_state.active_tool = "None"
with c2:
    if st.button("🌳 Green Corridor"): st.session_state.active_tool = "Trees"
with c3:
    if st.button("🚴 Bike Lane"): st.session_state.active_tool = "Bike"

# Row 2: The "Hard" Interventions
c4, c5, c6 = st.columns(3)
with c4:
    if st.button("🏥 Emergency Route"): st.session_state.active_tool = "Emergency"
with c5:
    if st.button("🛣️ Highway Flyover"): st.session_state.active_tool = "Flyover"
with c6:
    if st.button("🚌 Public Transport"): st.session_state.active_tool = "PublicTransport"

# --- 8. LOGIC EXECUTION ---
current_action = st.session_state.active_tool

if current_action == "None":
    s, r, t = 85.0, 0.0, loc_data["base_traffic"]
    ai_msg = "Site cleared. Ready for planning."
else:
    with st.spinner(f"Building {current_action}..."):
        s, r, t = math_engine.predict(loc_data, weather, current_action)
        ai_msg = ai_brain.ask_copilot(selected_loc_name, current_action, s, r, weather) if math_engine.loaded else "Models missing."

# --- 9. DASHBOARD ---
k1, k2, k3 = st.columns(3)
k1.metric("Predicted Stress", f"{s}/100", delta="ML Score", delta_color="inverse")
k2.metric("Traffic Vol", f"{t} /hr", delta="Simulated Input")
k3.metric("Health ROI", f"RM {r} M", delta="Annual Savings")

c_vis, c_ai = st.columns([1.5, 1])

with c_vis:
    st.info(f"🏗️ **Current Build:** {current_action}")
    
    # Image Logic (Update your 'assets' folder with new images!)
    loc_id = loc_data["id"]
    act_id = IMAGE_MAPPING.get(current_action, "Baseline")
    img_path = f"assets/{loc_id}_{act_id}.jpg"
    
    if os.path.exists(img_path):
        st.image(img_path, caption="Live Render", use_column_width=True)
    else:
        # Fallback Map
        lat, lon = loc_data["coords"]
        color = [255, 0, 0, 180] if s > 70 else [0, 255, 100, 180]
        st.pydeck_chart(pdk.Deck(
            initial_view_state=pdk.ViewState(latitude=lat, longitude=lon, zoom=15, pitch=50),
            layers=[pdk.Layer("ScatterplotLayer", data=pd.DataFrame({'lat':[lat],'lon':[lon]}), get_position='[lon,lat]', get_color=color, get_radius=400)],
            map_style=pdk.map_styles.CARTO_DARK
        ))

with c_ai:
    st.subheader("🤖 AI Audit")
    st.success(ai_msg)
    
    # Specific Context Warnings
    if current_action == "Flyover":
        st.error("⚠️ **Critical Warning:** Flyovers induce demand. Expect traffic to rise by 15% in 2 years.")
    if current_action == "PublicTransport":
        st.success("✅ **Benefit:** Public Transport aligns with 'KL Structure Plan 2040' targets.")