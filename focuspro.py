# focuspro_combined.py
import os, sys, time, threading, subprocess, requests, logging
from flask import Flask, render_template
import tkinter as tk

# === Logging ===
log_folder = "logs"
os.makedirs(log_folder, exist_ok=True)
log_file = os.path.join(log_folder, "combined.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(log_file, encoding="utf-8"),
        logging.StreamHandler()
    ]
)
sys.excepthook = lambda etype, value, tb: logging.error("❌ Uncaught exception", exc_info=(etype, value, tb))

# === Flask ===
app = Flask(__name__, template_folder="templates", static_folder="static")

@app.route("/")
def home():
    return render_template("login.html")

@app.route("/health")
def health():
    return "OK", 200

def run_flask():
    logging.info("🚀 Starting Flask backend...")
    app.run(debug=False, port=5000, use_reloader=False)

# === Web UI Launcher ===
def run_webview():
    import webbrowser
    try:
        import webview
        webview.create_window("DDS FocusPro", "http://127.0.0.1:5000", width=1024, height=720)
        webview.start()
    except Exception as e:
        logging.warning(f"🌐 WebView failed: {e}, opening in browser.")
        webbrowser.open("http://127.0.0.1:5000")

# === Splash Screen ===
splash = tk.Tk()
splash.title("DDS FocusPro")
splash.geometry("400x200")
splash.configure(bg="#1a2c4c")
tk.Label(splash, text="🚀 DDS FocusPro is starting...", font=("Segoe UI", 14), bg="#1a2c4c", fg="white").pack(expand=True)

def wait_and_start_ui():
    for _ in range(30):
        try:
            r = requests.get("http://127.0.0.1:5000/health")
            if r.status_code == 200:
                splash.destroy()
                run_webview()
                return
        except:
            time.sleep(0.5)
    splash.destroy()
    logging.error("❌ Flask server didn't start. Exiting.")

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    threading.Thread(target=wait_and_start_ui, daemon=True).start()
    splash.mainloop()
