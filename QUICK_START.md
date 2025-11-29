# Quick Start Guide - UrbanPulse

## ✅ What's Changed

1. **Removed AI Dependencies** - No more ollama needed!
2. **Hardcoded Images** - Uses placeholder images from Unsplash (works immediately)
3. **Hardcoded AI Messages** - Professional planner responses without AI
4. **Enhanced UI** - Better styling, before/after comparison view
5. **Works from Scratch** - No external AI services needed

## 🚀 How to Run

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Run the App
```bash
streamlit run app.py
```

The app will open in your browser automatically!

## 📸 Adding Your Own Images

1. Place images in the `assets/` folder
2. Name them: `{location_id}_{intervention_type}.jpg`
   - Example: `Tun_Razak_Green.jpg`
   - Example: `Bangsar_Bike.jpg`

3. The app will automatically use your images if they exist, otherwise it uses placeholder images

## 🎨 Current Features

✅ **Before/After Image Comparison** - Side-by-side view
✅ **Interactive Map** - Shows location with color coding
✅ **Real-time Metrics** - Stress, Traffic, ROI calculations
✅ **Hardcoded AI Analysis** - Professional planner feedback
✅ **Multiple Interventions** - 6 different infrastructure types
✅ **3 Locations** - Tun Razak, Bangsar, Cheras

## 🔧 Customization

### Change Images
Edit the `image_urls` dictionary in `app.py` (around line 240) to use your own image URLs or local files.

### Change AI Messages
Edit the `HardcodedCopilot` class in `app.py` to customize the planner's feedback messages.

### Change Colors/Styling
Edit the CSS in the `<style>` section at the top of `app.py`.

## 📱 Sharing with Team

Use the `share.py` script to create a public link:
```bash
python share.py
```

This creates an ngrok tunnel so your team can access it from anywhere.

## 🐛 Troubleshooting

**Problem:** Images not showing
- **Solution:** Check internet connection (uses Unsplash placeholders) or add your own images to `assets/` folder

**Problem:** Models not loading
- **Solution:** Make sure `model_stress.pkl`, `model_roi.pkl`, and `encoder.pkl` are in the project folder

**Problem:** App won't start
- **Solution:** Run `pip install -r requirements.txt` again

## ✨ Next Steps

1. Add your own before/after images to `assets/` folder
2. Customize the hardcoded messages to match your pitch
3. Test all interventions and locations
4. Prepare your demo!

Good luck with your hackathon! 🚀

