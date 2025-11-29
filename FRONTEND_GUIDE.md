# Frontend Development Guide for UrbanPulse

## Quick Answer: What Language for Frontend?

**✅ ANSWER: Continue with Streamlit (Python)**

You're already using Streamlit, which is perfect for your hackathon prototype. No need to switch languages!

### Why Streamlit?

- ✅ Already set up and working
- ✅ Python-based (you know it)
- ✅ Fast to develop
- ✅ Built-in components (maps, charts, forms)
- ✅ Perfect for data science/AI apps
- ✅ Easy to deploy

### Alternative Options (NOT recommended for hackathon):

- ❌ React/Next.js - Too time-consuming, need to rebuild everything
- ❌ Vue.js - Unnecessary complexity
- ❌ Pure HTML/CSS/JS - Would need to create backend API

---

## Priority Tasks (Do These First!)

### 1. Create Assets Folder

```bash
mkdir assets
mkdir assets/before
mkdir assets/after
```

### 2. Get Images

You need before/after images. Options:

- **Option A (Fastest)**: Use AI image generators
  - ChatGPT DALL-E: "A busy street in Kuala Lumpur with traffic and pollution"
  - Then: "Same street with green trees and bike lanes"
- **Option B**: Use stock photos from Unsplash/Pexels
  - Search: "Kuala Lumpur street", "urban planning", "green city"
- **Option C**: Use existing photos and edit them (Photoshop/GIMP)

**Minimum needed**: 6 images (3 locations × 2 states: before + one intervention)

### 3. Update app.py Image Display

The code already looks for images at `assets/{location_id}_{intervention}.jpg`

Just make sure your images match this naming:

- `Tun_Razak_Baseline.jpg`
- `Tun_Razak_Green.jpg`
- `Bangsar_Baseline.jpg`
- etc.

---

## Quick UI Improvements You Can Make

### 1. Better Color Scheme

Add to your CSS in app.py:

```python
st.markdown("""
<style>
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .metric-card {
        background: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)
```

### 2. Side-by-Side Image Comparison

Replace the single image display with:

```python
col1, col2 = st.columns(2)
with col1:
    st.subheader("Before")
    st.image("assets/Tun_Razak_Baseline.jpg")
with col2:
    st.subheader("After")
    st.image("assets/Tun_Razak_Green.jpg")
```

### 3. Better Metrics Display

Add icons and colors:

```python
if s > 70:
    st.error(f"⚠️ Stress Level: {s}/100 (High)")
elif s > 50:
    st.warning(f"⚠️ Stress Level: {s}/100 (Medium)")
else:
    st.success(f"✅ Stress Level: {s}/100 (Low)")
```

---

## Testing Your Frontend

1. **Run locally**:

   ```bash
   streamlit run app.py
   ```

2. **Share with team**:

   ```bash
   python share.py
   ```

   (This creates an ngrok tunnel)

3. **Check on mobile**: Open the ngrok link on your phone

---

## Common Streamlit Frontend Patterns

### Custom Buttons

```python
if st.button("🌳 Add Trees", use_container_width=True):
    # Your code here
```

### Progress Bars

```python
st.progress(stress_score / 100)
```

### Expanders (Collapsible Sections)

```python
with st.expander("📊 Detailed Metrics"):
    st.write("More info here")
```

### Columns Layout

```python
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.image("your_image.jpg")
```

---

## Time Management

**Essential (2-3 hours)**:

- ✅ Create assets folder
- ✅ Get 6-10 images
- ✅ Fix image display
- ✅ Basic UI polish

**Important (2-3 hours)**:

- ✅ Better metrics display
- ✅ Image comparison view
- ✅ Improved AI copilot UI

**Bonus (if time)**:

- ✅ Scenario saving
- ✅ Mobile responsive
- ✅ Advanced animations

---

## Need Help?

- Streamlit Docs: https://docs.streamlit.io
- Streamlit Components: https://streamlit.io/components
- Streamlit Gallery: https://streamlit.io/gallery

---

## Remember for Pitching

1. **Show the before/after images** - This is your "wow" factor
2. **Demonstrate the AI copilot** - Shows AI integration
3. **Show ROI calculations** - Proves value
4. **Explain the "Drop & See" concept** - Your unique selling point

Good luck! 🚀
