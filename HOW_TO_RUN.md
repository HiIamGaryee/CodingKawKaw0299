# 🚀 How to Run UrbanPulse

## ✅ CORRECT WAY (Use this!)

**Don't use:** `streamlit run app.py` ❌  
**Use instead:** `python3 -m streamlit run app.py` ✅

### Step-by-step:

1. Open Terminal
2. Go to project folder:
   ```bash
   cd /Applications/XAMPP/Project/UrbanPulse
   ```

3. Run the app:
   ```bash
   python3 -m streamlit run app.py
   ```

4. The app will open automatically at: **http://localhost:8501**

---

## 🔧 Why This Works

- `streamlit` command is not in your PATH
- `python3 -m streamlit` uses Python's module system (always works)
- This is the recommended way to run Streamlit

---

## 📝 Quick Copy-Paste Commands

```bash
cd /Applications/XAMPP/Project/UrbanPulse && python3 -m streamlit run app.py
```

---

## 🎯 Alternative: Add to PATH (Optional)

If you want to use `streamlit` command directly:

```bash
# Add to your ~/.zshrc file
echo 'export PATH="$HOME/Library/Python/3.9/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

But using `python3 -m streamlit` is easier and always works!

---

## ✅ Test It Works

After running `python3 -m streamlit run app.py`, you should see:

```
You can now view your Streamlit app in your browser.

Local URL: http://localhost:8501
Network URL: http://192.168.x.x:8501
```

Then open http://localhost:8501 in your browser!

