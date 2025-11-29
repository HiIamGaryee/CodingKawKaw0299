# 🚀 Quick Start - Run Your Demo

## Option 1: Using the Script (Easiest)

```bash
./RUN_DEMO.sh
```

This will:
1. Install all dependencies
2. Start the Streamlit app
3. Open in your browser automatically

---

## Option 2: Manual Steps

### Step 1: Install Dependencies
```bash
pip3 install -r requirements.txt
```

Or if you use `pip`:
```bash
pip install -r requirements.txt
```

### Step 2: Run the App
```bash
streamlit run app.py
```

### Step 3: Open Browser
The app will automatically open at:
**http://localhost:8501**

If it doesn't open automatically, manually go to that URL.

---

## 🎯 What You'll See

1. **Main Interface**:
   - Location selector (Tun Razak, Bangsar, Cheras)
   - Weather selector (Sunny/Rain)
   - 6 intervention buttons
   - Before/After image comparison
   - Metrics dashboard
   - Planner's analysis

2. **Sidebar** (Left side):
   - Settings (toggle charts)
   - Scenario saving
   - Scenario comparison
   - App info

---

## 📋 Quick Demo Checklist

Before your demo, test these:

- [ ] App loads without errors
- [ ] Can select different locations
- [ ] Can click intervention buttons
- [ ] Metrics update correctly
- [ ] Before/After images show (or map fallback)
- [ ] Can save a scenario
- [ ] Can compare scenarios
- [ ] Can download report
- [ ] Charts toggle on/off

---

## 🐛 Troubleshooting

### "streamlit: command not found"
```bash
pip3 install streamlit
```

### "Module not found"
```bash
pip3 install -r requirements.txt
```

### Port 8501 already in use
```bash
# Kill the process using port 8501
lsof -ti:8501 | xargs kill -9

# Or use a different port
streamlit run app.py --server.port 8502
```

### Images not showing
- That's OK! The app uses placeholder images from Unsplash
- It will fallback to map view if images don't load
- For demo, you can explain: "We use AI-generated before/after images"

---

## 🎤 Demo Tips

1. **Start simple**: Show one intervention (Green Corridor)
2. **Show the problem**: Try Flyover (shows negative impact)
3. **Show the solution**: Try Public Transport (shows positive impact)
4. **Compare them**: Use the comparison feature
5. **Export report**: Show practical use

---

## ✅ Ready to Demo!

Once the app is running:
- ✅ Test all features
- ✅ Practice your pitch
- ✅ Have the DEMO_GUIDE.md ready
- ✅ Be ready to explain the AI/ML components

**Good luck! 🚀**

