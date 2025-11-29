import streamlit as st
import pydeck as pdk
import pandas as pd
import pickle
import time
import os

# --- 1. SETUP PAGE ---
st.set_page_config(layout="wide", page_title="UrbanPulse: Planner Pro")

st.markdown("""
<style>
    /* Main Background */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Button Styling */
    div.stButton > button {
        width: 100%;
        height: 80px;
        border-radius: 12px;
        border: 2px solid #4CAF50;
        background: linear-gradient(135deg, #1E1E1E 0%, #2E2E2E 100%);
        color: white;
        transition: all 0.3s;
        font-size: 16px;
        font-weight: 600;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    div.stButton > button:hover {
        border-color: #66BB6A;
        background: linear-gradient(135deg, #2E2E2E 0%, #3E3E3E 100%);
        transform: translateY(-3px);
        box-shadow: 0 6px 12px rgba(76, 175, 80, 0.3);
    }
    div.stButton > button:focus {
        border-color: #4CAF50;
        box-shadow: 0 0 15px #4CAF50;
    }
    
    /* Metric Cards */
    .metric-card {
        background: rgba(255, 255, 255, 0.95);
        padding: 20px;
        border-radius: 15px;
        border: 2px solid #4CAF50;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    /* Header Styling */
    h1 {
        color: white;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    /* Info Boxes */
    .stInfo {
        background-color: rgba(76, 175, 80, 0.1);
        border-left: 4px solid #4CAF50;
    }
    
    /* Success/Error Messages */
    .stSuccess {
        background-color: rgba(76, 175, 80, 0.2);
    }
    .stError {
        background-color: rgba(244, 67, 54, 0.2);
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
        
        # Parse Inputs - Match data generation: 0=Rain, 1=Cloudy, 2=Sunny
        if "Rain" in weather_txt:
            w_code = 0
        elif "Cloudy" in weather_txt:
            w_code = 1
        else:  # Sunny
            w_code = 2
        
        # --- NEW LOGIC FOR INTERVENTIONS ---
        i_code = 0
        traffic_mod = 0
        
        traffic = loc_data["base_traffic"]
        if w_code == 0: traffic *= 0.85  # Rain reduces traffic (people cancel trips)
        elif w_code == 2: traffic += 500 # Sunny adds traffic

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

# --- 4. HARDCODED AI COPILOT MESSAGES ---
class HardcodedCopilot:
    def ask_copilot(self, location, intervention, stress_score, roi, weather):
        # Hardcoded professional planner responses
        messages = {
            "None": "Site cleared. Ready for planning intervention.",
            "Trees": f"Green corridor will reduce stress by ~{max(0, 85-int(stress_score))} points. Estimated health savings: RM {roi}M annually through improved air quality.",
            "Bike": f"Bike lane reduces traffic by 15%. Stress level at {stress_score}/100. Promotes active transportation, aligns with SDG 11 targets.",
            "Emergency": f"Emergency route improves response time. Current stress: {stress_score}/100. Critical for public safety infrastructure.",
            "Flyover": f"⚠️ Warning: Flyover increases traffic by 15% long-term (induced demand). Stress rises to {stress_score}/100. Consider public transport alternative.",
            "PublicTransport": f"✅ Excellent choice! Public transport reduces traffic by 30%. Stress drops to {stress_score}/100. ROI: RM {roi}M/year in healthcare savings."
        }
        return messages.get(intervention, "Analysis complete. Review metrics for details.")

math_engine = UrbanPulseAI()
ai_brain = HardcodedCopilot()

# --- 5. SESSION STATE ---
if 'active_tool' not in st.session_state:
    st.session_state.active_tool = "None"
if 'saved_scenarios' not in st.session_state:
    st.session_state.saved_scenarios = []
if 'show_charts' not in st.session_state:
    st.session_state.show_charts = True

# --- 6. UI HEADER ---
c_logo, c_title = st.columns([1, 6])
with c_logo: st.image("https://img.icons8.com/color/96/city-hall.png", width=70)
with c_title: 
    st.title("UrbanPulse: Planner Pro")
    st.caption("Advanced Scenario Modeling: Highways vs. Public Transit")

selected_loc_name = st.selectbox("📍 Active District", list(LOCATIONS.keys()))
loc_data = LOCATIONS[selected_loc_name]
weather = st.radio("Weather Condition", ["☀️ Sunny", "☁️ Cloudy", "🌧️ Heavy Rain"], horizontal=True)

st.markdown("---")

# --- 8. UPDATED TOOL PALETTE (2 Rows) ---
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

# --- 9. LOGIC EXECUTION ---
current_action = st.session_state.active_tool

if current_action == "None":
    s, r, t = 85.0, 0.0, loc_data["base_traffic"]
    ai_msg = "Site cleared. Ready for planning."
else:
    with st.spinner(f"Building {current_action}..."):
        s, r, t = math_engine.predict(loc_data, weather, current_action)
        ai_msg = ai_brain.ask_copilot(selected_loc_name, current_action, s, r, weather)

# --- 9.5. SIDEBAR (After calculations) ---
with st.sidebar:
    st.image("https://img.icons8.com/color/96/city-hall.png", width=80)
    st.title("UrbanPulse")
    st.markdown("---")
    
    st.subheader("⚙️ Settings")
    show_charts = st.checkbox("📊 Show Charts", value=st.session_state.show_charts)
    st.session_state.show_charts = show_charts
    
    st.markdown("---")
    st.subheader("💾 Scenarios")
    
    # Save current scenario
    scenario_name = st.text_input("Save Scenario As:", placeholder="e.g., Green Corridor Plan")
    if st.button("💾 Save Current Scenario"):
        if scenario_name:
            scenario = {
                "name": scenario_name,
                "location": selected_loc_name,
                "intervention": current_action,
                "weather": weather,
                "stress": s,
                "roi": r,
                "traffic": t,
                "timestamp": time.strftime("%Y-%m-%d %H:%M")
            }
            st.session_state.saved_scenarios.append(scenario)
            st.success(f"✅ Saved: {scenario_name}")
            st.rerun()
        else:
            st.warning("Please enter a scenario name")
    
    # List saved scenarios
    if st.session_state.saved_scenarios:
        st.markdown("**Saved Scenarios:**")
        for idx, scenario in enumerate(st.session_state.saved_scenarios):
            with st.expander(f"📋 {scenario['name']}"):
                st.write(f"**Location:** {scenario['location']}")
                st.write(f"**Intervention:** {scenario['intervention']}")
                st.write(f"**Stress:** {scenario['stress']}/100")
                st.write(f"**ROI:** RM {scenario['roi']:.2f}M")
                st.write(f"**Traffic:** {scenario['traffic']:,}/hr")
                st.write(f"*Saved: {scenario['timestamp']}*")
                if st.button(f"🗑️ Delete", key=f"del_{idx}"):
                    st.session_state.saved_scenarios.pop(idx)
                    st.rerun()
    
    st.markdown("---")
    st.markdown("### 📊 Compare Scenarios")
    if len(st.session_state.saved_scenarios) >= 2:
        scenario_names = [s['name'] for s in st.session_state.saved_scenarios]
        compare1 = st.selectbox("Scenario 1", scenario_names, key="comp1")
        compare2 = st.selectbox("Scenario 2", scenario_names, key="comp2")
        if st.button("📊 Compare"):
            # Find scenarios
            s1 = next((x for x in st.session_state.saved_scenarios if x['name'] == compare1), None)
            s2 = next((x for x in st.session_state.saved_scenarios if x['name'] == compare2), None)
            if s1 and s2:
                st.markdown("**Comparison:**")
                st.write(f"**Stress:** {s1['name']}: {s1['stress']}/100 vs {s2['name']}: {s2['stress']}/100")
                st.write(f"**ROI:** {s1['name']}: RM {s1['roi']:.2f}M vs {s2['name']}: RM {s2['roi']:.2f}M")
                st.write(f"**Traffic:** {s1['name']}: {s1['traffic']:,}/hr vs {s2['name']}: {s2['traffic']:,}/hr")
    else:
        st.info("Save at least 2 scenarios to compare")
    
    st.markdown("---")
    
    # Share functionality
    st.markdown("### 🌐 Share App")
    if st.button("🔗 Get Shareable Link", use_container_width=True):
        st.info("💡 Run 'python3 share.py' in terminal to get ngrok link")
        st.code("python3 share.py", language="bash")
    
    st.markdown("---")
    st.caption("**UrbanPulse v1.0**\n\nSDG 11 Hackathon Project\n\nSimulate first, build second.")

# --- 10. DASHBOARD ---
st.markdown("### 📊 Impact Metrics")
k1, k2, k3 = st.columns(3)

# Stress Level with color coding
stress_delta = f"{s - 85:.1f}" if s != 85 else "0"
stress_color = "inverse" if s > 70 else "normal"
with k1:
    if s > 70:
        st.error(f"⚠️ **Stress Level**\n\n# {s}/100\n\n*High Risk*")
    elif s > 50:
        st.warning(f"⚠️ **Stress Level**\n\n# {s}/100\n\n*Moderate*")
    else:
        st.success(f"✅ **Stress Level**\n\n# {s}/100\n\n*Low Risk*")
    st.progress(s / 100)

# Traffic Volume
with k2:
    traffic_change = ((t - loc_data["base_traffic"]) / loc_data["base_traffic"]) * 100
    traffic_delta = f"{traffic_change:+.1f}%"
    st.metric("🚗 Traffic Volume", f"{t:,} /hr", delta=traffic_delta, delta_color="inverse" if traffic_change > 0 else "normal")

# Health ROI
with k3:
    roi_color = "normal" if r > 0 else "inverse"
    st.metric("💰 Health ROI", f"RM {r:.2f} M", delta="Annual Savings", delta_color=roi_color)
    if r > 0:
        st.success(f"✅ Saves healthcare costs")
    else:
        st.error(f"⚠️ Negative impact")

# --- 11. CHARTS (if enabled) ---
if st.session_state.show_charts:
    st.markdown("---")
    st.markdown("### 📈 Detailed Analytics")
    
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        # Stress comparison chart
        baseline_stress = 85.0
        stress_data = pd.DataFrame({
            'Scenario': ['Baseline', 'Current'],
            'Stress Level': [baseline_stress, s]
        })
        st.bar_chart(stress_data.set_index('Scenario'), height=200)
        st.caption("Stress Level Comparison")
    
    with chart_col2:
        # Traffic comparison chart
        traffic_data = pd.DataFrame({
            'Scenario': ['Baseline', 'Current'],
            'Traffic (veh/hr)': [loc_data["base_traffic"], t]
        })
        st.bar_chart(traffic_data.set_index('Scenario'), height=200)
        st.caption("Traffic Volume Comparison")
    
    # ROI visualization
    if r != 0:
        roi_data = pd.DataFrame({
            'Metric': ['Health ROI'],
            'Value (RM Millions)': [abs(r)]
        })
        st.bar_chart(roi_data.set_index('Metric'), height=150)
        st.caption(f"Health ROI: RM {r:.2f}M annually")
    
    # Historical comparison if scenarios exist
    if len(st.session_state.saved_scenarios) > 0:
        st.markdown("---")
        st.markdown("#### 📊 Historical Scenarios Comparison")
        
        # Create comparison chart
        hist_data = []
        for scenario in st.session_state.saved_scenarios:
            hist_data.append({
                'Scenario': scenario['name'],
                'Stress': scenario['stress'],
                'ROI': scenario['roi'],
                'Traffic': scenario['traffic']
            })
        
        if hist_data:
            hist_df = pd.DataFrame(hist_data)
            
            col_hist1, col_hist2 = st.columns(2)
            with col_hist1:
                st.bar_chart(hist_df.set_index('Scenario')[['Stress']], height=200)
                st.caption("Stress Levels Across Scenarios")
            
            with col_hist2:
                st.bar_chart(hist_df.set_index('Scenario')[['ROI']], height=200)
                st.caption("ROI Comparison Across Scenarios")

c_vis, c_ai = st.columns([1.5, 1])

with c_vis:
    st.info(f"🏗️ **Current Build:** {current_action}")
    
    # Hardcoded Image URLs (Using placeholder images from Unsplash)
    # You can replace these with your actual images later
    loc_id = loc_data["id"]
    act_id = IMAGE_MAPPING.get(current_action, "Baseline")
    
    # Hardcoded image mapping with placeholder URLs
    image_urls = {
        "Tun_Razak_Baseline": "https://images.unsplash.com/photo-1559827260-dc66d52bef19?w=800",
        "Tun_Razak_Green": "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=800",
        "Tun_Razak_Bike": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800",
        "Bangsar_Baseline": "https://images.unsplash.com/photo-1514565131-fce0801e5785?w=800",
        "Bangsar_Green": "https://images.unsplash.com/photo-1449824913935-9a10a0e1a47b?w=800",
        "Cheras_Baseline": "https://images.unsplash.com/photo-1514565131-fce0801e5785?w=800",
        "Cheras_PublicTransport": "https://images.unsplash.com/photo-1544620347-c4fd4a3d5957?w=800",
    }
    
    # Try local file first, then hardcoded URL, then map
    img_path = f"assets/{loc_id}_{act_id}.jpg"
    img_key = f"{loc_id}_{act_id}"
    
    # Before/After Comparison View
    st.subheader("📸 Visual Impact")
    col_before, col_after = st.columns(2)
    
    with col_before:
        st.markdown("**Before (Baseline)**")
        baseline_key = f"{loc_id}_Baseline"
        baseline_path = f"assets/{baseline_key}.jpg"
        
        if os.path.exists(baseline_path):
            st.image(baseline_path, use_container_width=True)
        elif baseline_key in image_urls:
            st.image(image_urls[baseline_key], use_container_width=True)
        else:
            # Fallback: Enhanced Map view
            lat, lon = loc_data["coords"]
            # Create marker data
            marker_data = pd.DataFrame({
                'lat': [lat],
                'lon': [lon],
                'name': [selected_loc_name],
                'stress': [s]
            })
            st.pydeck_chart(pdk.Deck(
                initial_view_state=pdk.ViewState(
                    latitude=lat, 
                    longitude=lon, 
                    zoom=14, 
                    pitch=50,
                    bearing=0
                ),
                layers=[
                    pdk.Layer(
                        "ScatterplotLayer",
                        data=marker_data,
                        get_position='[lon, lat]',
                        get_color='[255, 100, 100, 200]',
                        get_radius=500,
                        pickable=True
                    ),
                    pdk.Layer(
                        "TextLayer",
                        data=marker_data,
                        get_position='[lon, lat]',
                        get_text='name',
                        get_size=16,
                        get_color=[255, 255, 255, 255],
                        get_angle=0,
                        get_text_anchor="middle",
                        get_alignment_baseline="center"
                    )
                ],
                map_style=pdk.map_styles.CARTO_DARK,
                tooltip={"text": "{name}\nStress Level: {stress}/100"}
            ))
    
    with col_after:
        st.markdown(f"**After ({current_action if current_action != 'None' else 'Baseline'})**")
        if current_action == "None":
            st.info("Select an intervention to see the transformation")
        else:
            if os.path.exists(img_path):
                st.image(img_path, use_container_width=True)
            elif img_key in image_urls:
                st.image(image_urls[img_key], use_container_width=True)
            else:
                # Fallback: Enhanced Map view with intervention color
                lat, lon = loc_data["coords"]
                color = [100, 255, 100, 200] if s < 70 else [255, 100, 100, 200]
                marker_data = pd.DataFrame({
                    'lat': [lat],
                    'lon': [lon],
                    'name': [f"{selected_loc_name} - {current_action}"],
                    'stress': [s]
                })
                st.pydeck_chart(pdk.Deck(
                    initial_view_state=pdk.ViewState(
                        latitude=lat, 
                        longitude=lon, 
                        zoom=14, 
                        pitch=50,
                        bearing=0
                    ),
                    layers=[
                        pdk.Layer(
                            "ScatterplotLayer",
                            data=marker_data,
                            get_position='[lon, lat]',
                            get_color=color,
                            get_radius=500,
                            pickable=True
                        )
                    ],
                    map_style=pdk.map_styles.CARTO_DARK,
                    tooltip={"text": "{name}\nStress: {stress}/100"}
                ))

with c_ai:
    st.subheader("🤖 Planner's Analysis")
    
    # Display AI message in a styled box
    st.info(ai_msg)
    
    # Specific Context Warnings
    st.markdown("---")
    if current_action == "Flyover":
        st.error("⚠️ **Critical Warning:** Flyovers induce demand. Expect traffic to rise by 15% in 2 years.")
        st.warning("💡 **Recommendation:** Consider public transport instead for better long-term outcomes.")
    elif current_action == "PublicTransport":
        st.success("✅ **Benefit:** Public Transport aligns with 'KL Structure Plan 2040' targets.")
        st.info("📈 **Impact:** Reduces carbon emissions and promotes sustainable mobility.")
    elif current_action == "Trees":
        st.success("🌳 **Environmental Impact:** Improves air quality and reduces urban heat island effect.")
    elif current_action == "Bike":
        st.success("🚴 **Health Impact:** Promotes active transportation, reducing healthcare costs.")
    elif current_action == "Emergency":
        st.info("🏥 **Safety Impact:** Improves emergency response times, critical for public safety.")
    
    # Quick Stats
    st.markdown("---")
    st.markdown("### 📈 Quick Stats")
    st.markdown(f"- **Location:** {selected_loc_name}")
    st.markdown(f"- **Population Density:** {loc_data['density']:,} /km²")
    st.markdown(f"- **Weather:** {weather}")
    st.markdown(f"- **Intervention:** {current_action if current_action != 'None' else 'None Selected'}")
    
    # Export Report
    st.markdown("---")
    st.markdown("### 📄 Export Options")
    
    col_exp1, col_exp2 = st.columns(2)
    
    with col_exp1:
        # TXT Report
        report_data = f"""
# UrbanPulse Scenario Report

**Location:** {selected_loc_name}
**Intervention:** {current_action if current_action != 'None' else 'None'}
**Weather:** {weather}
**Date:** {time.strftime("%Y-%m-%d %H:%M")}

## Metrics
- **Stress Level:** {s}/100
- **Traffic Volume:** {t:,} vehicles/hour
- **Health ROI:** RM {r:.2f}M annually

## Analysis
{ai_msg}

## Recommendations
"""
        st.download_button(
            label="📥 TXT Report",
            data=report_data,
            file_name=f"urbanpulse_report_{time.strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain",
            use_container_width=True
        )
    
    with col_exp2:
        # CSV Export (all saved scenarios)
        if st.session_state.saved_scenarios:
            df_export = pd.DataFrame(st.session_state.saved_scenarios)
            csv_data = df_export.to_csv(index=False)
            st.download_button(
                label="📊 CSV Export",
                data=csv_data,
                file_name=f"urbanpulse_scenarios_{time.strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        else:
            st.info("Save scenarios to export CSV")
    
    # Model Status
    st.markdown("---")
    st.markdown("### 🤖 Model Status")
    if math_engine.loaded:
        st.success("✅ ML Models Loaded Successfully")
        st.caption("Using trained Random Forest models for predictions")
    else:
        st.warning("⚠️ Using Fallback Calculations")
        st.caption("ML models not found. Using hardcoded logic.")