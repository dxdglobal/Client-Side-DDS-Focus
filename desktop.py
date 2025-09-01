import os
import sys
import time
import threading
import subprocess
import requests
import logging
import tkinter as tk
import webview
import psutil
import webbrowser
import pathlib

# ------------------ Kill Old Connector ------------------
def kill_existing_connector():
    for proc in psutil.process_iter(['name']):
        try:
            if 'DDSFocusPro Connector.exe' in proc.info['name']:
                logging.info(f"🧹 Killing old connector: PID {proc.pid}")
                proc.kill()
        except Exception as e:
            logging.warning(f"⚠️ Could not kill connector: {e}")

# ------------------ Globals ------------------
connector_process = None
flask_ready = False

# ------------------ Logging ------------------
log_folder = "logs"
os.makedirs(log_folder, exist_ok=True)
log_file = os.path.join(log_folder, "desktop.log")
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(log_file, mode='w', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

def handle_exception(exc_type, exc_value, exc_traceback):
    logging.error("❌ Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
sys.excepthook = handle_exception

# ------------------ Flask Starter ------------------
def start_flask():
    global connector_process
    base_path = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.abspath(".")
    app_path = os.path.join(base_path, "DDSFocusPro Connector.exe")

    logging.info(f"🔍 Launching: {app_path}")
    if not os.path.exists(app_path):
        logging.error(f"❌ File not found: {app_path}")
        return

    flask_log = open(os.path.join(log_folder, "flask.log"), "w")
    startupinfo = subprocess.STARTUPINFO() if os.name == 'nt' else None
    if startupinfo:
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

    try:
        connector_process = subprocess.Popen(
            [app_path],
            stdout=flask_log,
            stderr=flask_log,
            shell=True,
            creationflags=subprocess.CREATE_NO_WINDOW | subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0,
            startupinfo=startupinfo
        )
        logging.info("✅ Connector started")
    except Exception as e:
        logging.error(f"❌ Failed to start connector: {e}")

# ------------------ Background Flask Monitor ------------------
def wait_until_flask_ready(max_wait=float("inf")):
    global flask_ready
    start_time = time.time()
    while time.time() - start_time < max_wait:
        try:
            r = requests.get("http://127.0.0.1:5000")
            if r.status_code == 200:
                flask_ready = True
                logging.info("✅ Flask ready")
                return
        except:
            pass  # no log here
        time.sleep(0.25)
    logging.warning("⏱️ Timeout: Flask not ready in time")


def background_launcher():
    global flask_ready
    start_flask()
    wait_until_flask_ready(float("inf"))  # ✅ FIXED

    
    if flask_ready:
        logging.info("🌐 Opening main app window")
        webview.windows[0].load_url("http://127.0.0.1:5000")
    else:
        logging.warning("❌ Flask did not respond in time. Keeping loader visible.")





def cleanup_and_exit():
    global connector_process
    logging.info("❌ UI closed by user. Cleaning up...")

    try:
        if connector_process and connector_process.poll() is None:
            logging.info("🛑 Terminating DDSFocusPro Connector...")
            connector_process.terminate()
            connector_process.wait(timeout=5)
            logging.info("✅ DDSFocusPro Connector terminated.")
    except Exception as e:
        logging.warning(f"⚠️ Failed to terminate connector cleanly: {e}")

    # Fallback: kill any remaining
    kill_existing_connector()

    logging.info("👋 Exiting application.")
    os._exit(0)

# ------------------ Main Launcher ------------------
if __name__ == '__main__':
    kill_existing_connector()
    threading.Thread(target=background_launcher, daemon=True).start()

    # Show UI immediately (no wait)
    try:
        loader_path = pathlib.Path(__file__).parent / "templates" / "loader.html"

        if not loader_path.exists():
            logging.error(f"❌ loader.html NOT FOUND at {loader_path}")
            raise FileNotFoundError("loader.html missing.")

        logging.info(f"✅ loader.html found at {loader_path}")

        with open(loader_path, "r", encoding="utf-8") as f:
            loader_html = f.read()

        webview.create_window(
            title="DDS FocusPro",
            html=loader_html,
            width=1024,
            height=750,
        )


        # ✅ Attach cleanup after window opens
        def after_window_created():
            if webview.windows:
                webview.windows[0].events.closed += cleanup_and_exit

        webview.start(gui='edgechromium', debug=False, func=after_window_created)

    except Exception as e:
        logging.error(f"❌ WebView failed: {e}")
