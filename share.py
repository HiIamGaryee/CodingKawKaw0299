import time
from pyngrok import ngrok

# --- CONFIGURATION ---
NGROK_TOKEN = "366Fc34z5ZDgyIs8kPAem6ZVIuu_2ELFeyPTNorYNrPsYTErY" 

if NGROK_TOKEN == "PASTE_YOUR_TOKEN_HERE":
    print("❌ Error: You forgot to paste your Ngrok Auth Token inside share.py!")
else:
    # Set the token
    ngrok.set_auth_token(NGROK_TOKEN)

    # Open a tunnel to port 8501 (Where Streamlit runs)
    public_url = ngrok.connect(8501).public_url

    print("======================================================")
    print(f"🚀 SEND THIS LINK TO YOUR FRIEND: {public_url}")
    print("======================================================")

    # Keep the script running so the link stays alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping tunnel...")