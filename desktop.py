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
import signal
import atexit

# Create necessary folders on startup
def create_required_folders():
    folders_to_create = ["logs", "output", "data"]
    for folder in folders_to_create:
        if not os.path.exists(folder):
            os.makedirs(folder, exist_ok=True)
            print(f"[OK] Created folder: {folder}")

# Call folder creation
create_required_folders()

def kill_existing_connector():
    for proc in psutil.process_iter(['name']):
        try:
            if 'connector.exe' in proc.info['name']:
                logging.info(f"[CLEAN] Killing old connector: PID {proc.pid}")
                proc.kill()
        except Exception as e:
            logging.warning(f"[WARN] Could not kill connector: {e}")

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
    logging.error("[ERROR] Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
sys.excepthook = handle_exception

def start_flask():
    global connector_process
    
    # ✅ Improved path detection for both development and packaged environments
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        base_path = os.path.dirname(sys.executable)
        logging.info(f"[LAUNCH] Running as packaged app from: {base_path}")
        
        # For PyInstaller, the connector.exe should be in the same directory as DDSFocusPro.exe
        app_path = os.path.join(base_path, "connector.exe")
        logging.info(f"[LAUNCH] Looking for connector at: {app_path}")
        
        # Alternative: Check in the temporary extraction folder (_MEIPASS)
        if not os.path.exists(app_path):
            temp_path = getattr(sys, '_MEIPASS', base_path)
            app_path = os.path.join(temp_path, "connector.exe")
            logging.info(f"[LAUNCH] Trying temp path: {app_path}")
            
    else:
        # Running in development mode
        base_path = os.path.abspath(".")
        logging.info(f"[LAUNCH] Running in development from: {base_path}")
        
        # Check if connector.exe exists in dist folder (built separately)
        app_path = os.path.join(base_path, "dist", "connector.exe")
        if not os.path.exists(app_path):
            app_path = os.path.join(base_path, "connector.exe")

    logging.info(f"[LAUNCH] Final connector path: {app_path}")
    
    if not os.path.exists(app_path):
        logging.error(f"[ERROR] connector.exe not found at: {app_path}")
        
        # List files in the directory to debug
        try:
            dir_to_check = os.path.dirname(app_path)
            files = os.listdir(dir_to_check)
            logging.info(f"[DEBUG] Files in {dir_to_check}: {files}")
        except Exception as e:
            logging.error(f"[DEBUG] Could not list directory: {e}")
        
        # Try to build connector if we're in development
        if not getattr(sys, 'frozen', False):
            logging.info("[LAUNCH] Attempting to build connector...")
            try:
                build_cmd = f'pyinstaller --clean --noconfirm --onefile --noconsole --name connector app.py'
                result = subprocess.run(build_cmd, shell=True, capture_output=True, text=True)
                if result.returncode == 0:
                    app_path = os.path.join(base_path, "dist", "connector.exe")
                    logging.info(f"[LAUNCH] Connector built successfully: {app_path}")
                else:
                    logging.error(f"[LAUNCH] Failed to build connector: {result.stderr}")
                    return
            except Exception as e:
                logging.error(f"[LAUNCH] Error building connector: {e}")
                return
        else:
            logging.error("[ERROR] Cannot find connector.exe in packaged application")
            logging.error("[ERROR] This means the build process did not properly embed the connector")
            return

    # ✅ Start the connector process
    flask_log_path = os.path.join(log_folder, "flask.log")
    logging.info(f"[LAUNCH] Starting connector with logs at: {flask_log_path}")
    
    try:
        flask_log = open(flask_log_path, "w", encoding='utf-8')
        startupinfo = subprocess.STARTUPINFO() if os.name == 'nt' else None
        if startupinfo:
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        connector_process = subprocess.Popen(
            [app_path],
            stdout=flask_log,
            stderr=flask_log,
            shell=False,  # Changed from True to False for better process control
            creationflags=subprocess.CREATE_NO_WINDOW | subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0,
            startupinfo=startupinfo
        )
        logging.info("[OK] Connector started")
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
                logging.info("[OK] Flask ready")
                return
        except:
            pass  # no log here
        time.sleep(0.25)
    logging.warning("[TIMEOUT] Timeout: Flask not ready in time")


def background_launcher():
    global flask_ready
    start_flask()
    wait_until_flask_ready(float("inf"))  # [OK] FIXED

    
    if flask_ready:
        logging.info("🌐 Opening main app window")
        webview.windows[0].load_url("http://127.0.0.1:5000")
    else:
        logging.warning("[ERROR] Flask did not respond in time. Keeping loader visible.")





def cleanup_and_exit():
    global connector_process
    logging.info("[CLEANUP] UI closed by user. Cleaning up...")

    # ✅ First priority: Try to trigger auto-save through JavaScript beforeunload
    try:
        logging.info("[CLEANUP] Attempting to trigger auto-save via browser...")
        
        # Give the webview some time to execute beforeunload event
        if webview.windows:
            logging.info("[CLEANUP] Sending beforeunload signal to webview...")
            # Small delay to allow JavaScript beforeunload to execute
            time.sleep(2)
        
    except Exception as e:
        logging.warning(f"[CLEANUP] Could not trigger beforeunload: {e}")

    # ✅ Backup: Direct auto-save call to backend if webview method fails
    try:
        logging.info("[CLEANUP] Performing backup auto-save to backend...")
        
        # Try to get timer status
        response = requests.get("http://127.0.0.1:5000/api/timer-status", timeout=3)
        if response.status_code == 200:
            timer_data = response.json()
            logging.info(f"[CLEANUP] Timer status received: {timer_data}")
        else:
            logging.info("[CLEANUP] Could not get timer status, attempting direct cleanup...")
            
        # Always try to trigger cleanup_active_timers which should handle auto-save
        response = requests.post("http://127.0.0.1:5000/cleanup_active_timers", timeout=5)
        if response.status_code == 200:
            logging.info("[CLEANUP] ✅ Active timers cleaned up (auto-save included)")
        else:
            logging.warning(f"[CLEANUP] ⚠️ Timer cleanup returned status: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        logging.warning(f"[CLEANUP] ⚠️ Could not perform backup auto-save: {e}")
    except Exception as e:
        logging.warning(f"[CLEANUP] ⚠️ Auto-save error: {e}")

    # ✅ Give a final moment for any pending operations
    time.sleep(1)

    # ✅ Send shutdown signal to Flask app
    try:
        logging.info("[CLEANUP] Sending shutdown signal to Flask app...")
        response = requests.post("http://127.0.0.1:5000/shutdown", timeout=3)
        logging.info("[CLEANUP] ✅ Shutdown signal sent to Flask app")
    except requests.exceptions.RequestException as e:
        logging.warning(f"[CLEANUP] ⚠️ Could not send shutdown signal: {e}")
    except Exception as e:
        logging.warning(f"[CLEANUP] ⚠️ Shutdown signal failed: {e}")

    try:
        if connector_process and connector_process.poll() is None:
            logging.info("🛑 Terminating connector...")
            connector_process.terminate()
            connector_process.wait(timeout=5)
            logging.info("[OK] Connector terminated.")
    except Exception as e:
        logging.warning(f"⚠️ Failed to terminate connector cleanly: {e}")

    # Fallback: kill any remaining
    kill_existing_connector()

    logging.info("👋 Exiting application.")
    os._exit(0)

# ------------------ Main Launcher ------------------
if __name__ == '__main__':
    # ✅ Register cleanup handlers for various exit scenarios
    atexit.register(cleanup_and_exit)
    signal.signal(signal.SIGINT, lambda sig, frame: cleanup_and_exit())
    signal.signal(signal.SIGTERM, lambda sig, frame: cleanup_and_exit())
    
    kill_existing_connector()
    threading.Thread(target=background_launcher, daemon=True).start()

    # Show UI immediately (no wait)
    try:
        loader_path = pathlib.Path(__file__).parent / "templates" / "loader.html"

        if not loader_path.exists():
            logging.error(f"[ERROR] loader.html NOT FOUND at {loader_path}")
            raise FileNotFoundError("loader.html missing.")

        logging.info(f"[OK] loader.html found at {loader_path}")

        with open(loader_path, "r", encoding="utf-8") as f:
            loader_html = f.read()

        webview.create_window(
            title="DDS FocusPro",
            html=loader_html,
            width=1024,
            height=750,
        )


        # ✅ Properly attach cleanup handlers for EXE
        def on_window_created():
            try:
                if webview.windows:
                    # Register the close event handler
                    webview.windows[0].events.closed += cleanup_and_exit
                    logging.info("[OK] Window close handler registered")
            except Exception as e:
                logging.error(f"[ERROR] Failed to register close handler: {e}")

        # ✅ Add Windows-specific signal handlers for EXE
        if os.name == 'nt':
            try:
                import win32api
                import win32con
                
                def win_handler(signal_type):
                    logging.info(f"[SIGNAL] Windows signal received: {signal_type}")
                    cleanup_and_exit()
                    return True
                
                win32api.SetConsoleCtrlHandler(win_handler, True)
                logging.info("[OK] Windows signal handler registered")
            except ImportError:
                logging.warning("[WARN] win32api not available, using standard handlers")

        webview.start(gui='edgechromium', debug=False, func=on_window_created)
        
        # ✅ Ensure cleanup runs when webview.start() returns (window closed)
        logging.info("[WEBVIEW] Window closed, running cleanup...")
        cleanup_and_exit()

    except Exception as e:
        logging.error(f"[ERROR] WebView failed: {e}")
        cleanup_and_exit()  # Ensure cleanup even if webview fails