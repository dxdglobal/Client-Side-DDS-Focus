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
            if 'DDSFocusPro' in proc.info['name']:
                logging.info(f"[CLEANUP] Killing old connector: PID {proc.pid}")
                proc.kill()
        except Exception as e:
            logging.warning(f"[WARNING] Could not kill connector: {e}")

# ------------------ Globals ------------------
connector_process = None
flask_ready = False

# ------------------ Logging ------------------
# Get the directory where the executable is located
if getattr(sys, 'frozen', False):
    # Running as PyInstaller executable
    base_dir = os.path.dirname(sys.executable)
else:
    # Running as Python script
    base_dir = os.path.dirname(os.path.abspath(__file__))

log_folder = os.path.join(base_dir, "logs")
os.makedirs(log_folder, exist_ok=True)
log_file = os.path.join(log_folder, "desktop.log")

# Simple logging setup without stdout/stderr redirection
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(log_file, mode='w', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

def handle_exception(exc_type, exc_value, exc_traceback):
    logging.error("[ERROR] Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
sys.excepthook = handle_exception

# ------------------ Flask Starter ------------------
def start_flask():
    global connector_process
    # Get the correct base path for both executable and script modes
    if getattr(sys, 'frozen', False):
        # Running as PyInstaller executable - use directory of executable
        base_path = os.path.dirname(sys.executable)
    else:
        # Running as Python script - use dist directory if available
        script_dir = os.path.dirname(os.path.abspath(__file__))
        dist_dir = os.path.join(script_dir, "dist")
        if os.path.exists(os.path.join(dist_dir, "DDSFocusPro Connector.exe")):
            base_path = dist_dir
        else:
            base_path = script_dir
    
    app_path = os.path.join(base_path, "DDSFocusPro Connector.exe")

    logging.info(f"[LAUNCH] Base path: {base_path}")
    logging.info(f"[LAUNCH] Starting: {app_path}")
    if not os.path.exists(app_path):
        logging.error(f"[ERROR] File not found: {app_path}")
        logging.error(f"[DEBUG] Available files in {base_path}: {os.listdir(base_path) if os.path.exists(base_path) else 'Directory not found'}")
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
        logging.info("[SUCCESS] Connector started")
    except Exception as e:
        logging.error(f"[ERROR] Failed to start connector: {e}")

# ------------------ Background Flask Monitor ------------------
def wait_until_flask_ready(max_wait=float("inf")):
    global flask_ready
    start_time = time.time()
    while time.time() - start_time < max_wait:
        try:
            r = requests.get("http://127.0.0.1:5000")
            if r.status_code == 200:
                flask_ready = True
                logging.info("[SUCCESS] Flask ready")
                return
        except:
            pass  # no log here
        time.sleep(0.25)
    logging.warning("[TIMEOUT] Flask not ready in time")

def background_launcher():
    global flask_ready
    logging.info("[BACKGROUND] Starting Flask connector")
    start_flask()
    logging.info("[BACKGROUND] Waiting for Flask to be ready")
    wait_until_flask_ready(float("inf"))  # FIXED
    
    if flask_ready:
        logging.info("[UI] Opening main app window")
        if webview.windows:
            webview.windows[0].load_url("http://127.0.0.1:5000")
        else:
            logging.error("[ERROR] No webview windows available to load URL")
    else:
        logging.warning("[WARNING] Flask did not respond in time. Keeping loader visible.")

def cleanup_and_exit():
    global connector_process
    logging.info("[CLEANUP] UI closed by user. Cleaning up...")

    try:
        if connector_process and connector_process.poll() is None:
            logging.info("[CLEANUP] Terminating DDSFocusPro Connector...")
            connector_process.terminate()
            connector_process.wait(timeout=5)
            logging.info("[SUCCESS] DDSFocusPro Connector terminated.")
    except Exception as e:
        logging.warning(f"[WARNING] Failed to terminate connector cleanly: {e}")    # Fallback: kill any remaining
    kill_existing_connector()

    logging.info("[EXIT] Exiting application.")
    os._exit(0)

# ------------------ Main Launcher ------------------
if __name__ == '__main__':
    try:
        logging.info("[MAIN] Starting DDSFocusPro desktop application")
        kill_existing_connector()
        
        logging.info("[MAIN] Starting background launcher thread")
        background_thread = threading.Thread(target=background_launcher, daemon=True)
        background_thread.start()
        logging.info("[MAIN] Background thread started successfully")
    except Exception as e:
        logging.error(f"[ERROR] Failed during initialization: {e}")
        logging.error("[ERROR] Exception details:", exc_info=True)
        raise

    # Show UI immediately (no wait)
    try:
        logging.info("[MAIN] Preparing to show UI")
        
        # Get the correct base path for PyInstaller executable
        if getattr(sys, 'frozen', False):
            # If running as executable, use sys._MEIPASS for temporary files
            base_path = sys._MEIPASS
            logging.info(f"[MAIN] Running as executable, base_path: {base_path}")
        else:
            # If running as script, use script directory
            base_path = pathlib.Path(__file__).parent
            logging.info(f"[MAIN] Running as script, base_path: {base_path}")
        
        loader_path = pathlib.Path(base_path) / "templates" / "loader.html"

        if not loader_path.exists():
            logging.error(f"[ERROR] loader.html NOT FOUND at {loader_path}")
            logging.error(f"[DEBUG] Base path: {base_path}")
            logging.error(f"[DEBUG] Available files: {list(pathlib.Path(base_path).rglob('*'))}")
            raise FileNotFoundError("loader.html missing.")

        logging.info(f"[SUCCESS] loader.html found at {loader_path}")

        logging.info("[UI] Reading loader.html content")
        with open(loader_path, "r", encoding="utf-8") as f:
            loader_html = f.read()

        logging.info("[UI] Creating webview window")
        webview.create_window(
            title="DDS FocusPro",
            html=loader_html,
            width=1024,
            height=750,
        )

        # Attach cleanup after window opens
        def after_window_created():
            logging.info("[UI] Window created callback executed")
            if webview.windows:
                logging.info("[UI] Attaching cleanup handler to window close event")
                webview.windows[0].events.closed += cleanup_and_exit
            else:
                logging.error("[ERROR] No webview windows found")

        logging.info("[UI] Starting webview with EdgeChromium")
        try:
            webview.start(gui='edgechromium', debug=False, func=after_window_created)
            logging.info("[UI] Webview.start() completed")
        except Exception as webview_error:
            logging.error(f"[ERROR] WebView.start() failed: {webview_error}")
            logging.error("[ERROR] WebView exception details:", exc_info=True)
            raise

    except Exception as e:
        logging.error(f"[ERROR] UI creation failed: {e}")
        logging.error("[ERROR] Exception details:", exc_info=True)
        # Try to keep the application running for debugging
        input("Press Enter to exit...")