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

# Fix working directory for double-click launches
def fix_working_directory():
    """Ensure we're in the correct working directory"""
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        if sys.platform == 'darwin':  # macOS
            # Get the app bundle's Resources directory or the parent directory
            app_path = os.path.dirname(sys.executable)
            if 'Contents/MacOS' in app_path:
                # We're inside an app bundle, go to the project root
                project_root = os.path.join(app_path, '..', '..', '..', '..')
                project_root = os.path.abspath(project_root)
                if os.path.exists(os.path.join(project_root, 'app.py')):
                    os.chdir(project_root)
                    print(f"[INIT] Set working directory to project root: {project_root}")
                else:
                    # Try the MacOS directory itself
                    os.chdir(app_path)
                    print(f"[INIT] Set working directory to app path: {app_path}")
            else:
                os.chdir(app_path)
                print(f"[INIT] Set working directory to: {app_path}")
        else:
            # Windows/Linux
            app_dir = os.path.dirname(sys.executable)
            os.chdir(app_dir)
            print(f"[INIT] Set working directory to: {app_dir}")
    else:
        # Running as script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(script_dir)
        print(f"[INIT] Set working directory to script location: {script_dir}")

# Fix working directory first
fix_working_directory()

# Create necessary folders on startup
def create_required_folders():
    folders_to_create = ["logs", "output", "data"]
    for folder in folders_to_create:
        if not os.path.exists(folder):
            os.makedirs(folder, exist_ok=True)
            print(f"[OK] Created folder: {folder}")

# Call folder creation
create_required_folders()

def open_exec_terminal():
    """Opens the exec terminal automatically"""
    try:
        # Get the directory where the desktop app is located
        base_path = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.abspath(".")
        
        logging.info(f"[EXEC] Starting exec terminal from: {base_path}")
        
        # Multiple strategies to open terminal/exec
        try:
            # Strategy 1: Try to find and open Terminal with our directory
            applescript = f'''
            tell application "Terminal"
                activate
                do script "cd '{base_path}'"
            end tell
            '''
            subprocess.run(['osascript', '-e', applescript], check=True)
            logging.info("[OK] Terminal opened with directory context")
            
        except Exception as e1:
            logging.warning(f"[WARN] AppleScript failed: {e1}")
            
            try:
                # Strategy 2: Open Terminal app directly
                subprocess.Popen(['open', '/Applications/Utilities/Terminal.app'])
                logging.info("[OK] Terminal app opened")
                
            except Exception as e2:
                logging.warning(f"[WARN] Direct Terminal open failed: {e2}")
                
                # Strategy 3: Try iTerm if available
                try:
                    subprocess.Popen(['open', '/Applications/iTerm.app'])
                    logging.info("[OK] iTerm opened")
                except Exception as e3:
                    logging.warning(f"[WARN] iTerm not available: {e3}")
        
        time.sleep(3)  # Give terminal time to start and be ready
        
    except Exception as e:
        logging.warning(f"[WARN] Could not open exec terminal: {e}")
        logging.info("[INFO] Continuing without exec terminal...")

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
    base_path = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.abspath(".")
    current_dir = os.getcwd()
    
    logging.info(f"[FLASK] Starting integrated Flask server...")
    logging.info(f"[DEBUG] Base path: {base_path}")
    logging.info(f"[DEBUG] Current working directory: {current_dir}")
    
    try:
        # Import and run Flask app directly in this process
        import importlib.util
        import threading
        
        # Try to import the main app
        try:
            # Method 1: Look for app.py in multiple locations
            possible_app_paths = [
                os.path.join(current_dir, "app.py"),  # Current working directory
                os.path.join(base_path, "app.py"),    # Executable directory
                os.path.join(os.path.dirname(base_path), "app.py"),  # Parent of executable
            ]
            
            app_path = None
            for path in possible_app_paths:
                logging.info(f"[DEBUG] Checking for app.py at: {path}")
                if os.path.exists(path):
                    app_path = path
                    logging.info(f"[FOUND] app.py found at: {app_path}")
                    break
            
            if app_path:
                # Load app.py as a module
                spec = importlib.util.spec_from_file_location("app", app_path)
                app_module = importlib.util.module_from_spec(spec)
                
                # Run Flask in a separate thread
                def run_flask_app():
                    try:
                        logging.info("[FLASK] Starting Flask application...")
                        spec.loader.exec_module(app_module)
                    except Exception as e:
                        logging.error(f"[ERROR] Flask app failed: {e}")
                
                flask_thread = threading.Thread(target=run_flask_app, daemon=True)
                flask_thread.start()
                logging.info("[OK] Flask app started in background thread")
                
            else:
                # Method 2: Try to run as subprocess if app.py not found
                logging.warning("[WARN] app.py not found in any location, trying subprocess method...")
                
                # Try to find executable versions
                possible_executables = [
                    os.path.join(base_path, "DDSFocusPro-App"),
                    os.path.join(base_path, "app"),
                    os.path.join(os.path.dirname(base_path), "dist", "DDSFocusPro-App"),
                ]
                
                app_executable = None
                for exe_path in possible_executables:
                    if os.path.exists(exe_path):
                        app_executable = exe_path
                        break
                
                if app_executable:
                    logging.info(f"[FLASK] Starting Flask executable: {app_executable}")
                    connector_process = subprocess.Popen(
                        [app_executable],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        cwd=base_path
                    )
                    logging.info(f"[OK] Flask executable started with PID: {connector_process.pid}")
                else:
                    logging.error("[ERROR] No Flask app found!")
                    return
                
        except Exception as e:
            logging.error(f"[ERROR] Failed to start Flask: {e}")
            
    except Exception as e:
        logging.error(f"[ERROR] Failed to start connector: {e}")

# ------------------ Background Flask Monitor ------------------
def wait_until_flask_ready(max_wait=float("inf")):
    global flask_ready
    start_time = time.time()
    
    # Check multiple ports since app now finds free ports
    ports_to_check = [5000, 5001, 5002, 5003, 5004, 5005]
    
    while time.time() - start_time < max_wait:
        for port in ports_to_check:
            try:
                r = requests.get(f"http://127.0.0.1:{port}", timeout=2)
                if r.status_code == 200:
                    flask_ready = True
                    logging.info(f"[OK] Flask ready on port {port}")
                    return f"http://127.0.0.1:{port}"
            except:
                pass  # no log here
        time.sleep(1)
        
        # Show progress every 5 seconds
        elapsed = time.time() - start_time
        if int(elapsed) % 5 == 0:
            logging.info(f"[WAIT] Still waiting for Flask... ({int(elapsed)}s)")
    
    logging.warning("[TIMEOUT] Timeout: Flask not ready in time")
    return None


def background_launcher():
    global flask_ready
    start_flask()
    flask_url = wait_until_flask_ready(60)  # Wait max 60 seconds

    
    if flask_ready and flask_url:
        logging.info(f"🌐 Opening main app window at {flask_url}")
        webview.windows[0].load_url(flask_url)
    else:
        logging.warning("[ERROR] Flask did not respond in time. Keeping loader visible.")





def cleanup_and_exit():
    global connector_process
    logging.info("[CLEANUP] UI closed by user. Cleaning up...")

    # Step 1: Try to gracefully shut down Flask app via API
    try:
        logging.info("🛑 Sending shutdown signal to Flask app...")
        
        # Try multiple ports since the Flask app finds free ports
        ports_to_try = [5000, 5001, 5002, 5003, 5004, 5005]
        shutdown_success = False
        
        for port in ports_to_try:
            try:
                import requests
                response = requests.post(f"http://127.0.0.1:{port}/shutdown", timeout=5)
                if response.status_code == 200:
                    logging.info(f"✅ Flask app shutdown successfully on port {port}")
                    shutdown_success = True
                    break
            except requests.exceptions.RequestException:
                continue  # Try next port
        
        if shutdown_success:
            logging.info("⏳ Waiting for Flask app to shutdown...")
            time.sleep(3)  # Give Flask time to cleanup
        else:
            logging.warning("⚠️ Could not reach Flask app via API")
            
    except Exception as e:
        logging.warning(f"⚠️ Failed to shutdown Flask gracefully: {e}")

    # Step 2: Try to terminate connector process
    try:
        if connector_process and connector_process.poll() is None:
            logging.info("🛑 Terminating connector process...")
            connector_process.terminate()
            connector_process.wait(timeout=5)
            logging.info("✅ Connector terminated.")
    except Exception as e:
        logging.warning(f"⚠️ Failed to terminate connector cleanly: {e}")

    # Step 3: Fallback - kill any remaining processes
    try:
        logging.info("🧹 Cleaning up any remaining processes...")
        kill_existing_connector()
        
        # Also kill any Python processes that might be running the Flask app
        for proc in psutil.process_iter(['name', 'cmdline']):
            try:
                if 'python' in proc.info['name'].lower() and proc.info['cmdline']:
                    cmdline = ' '.join(proc.info['cmdline'])
                    if 'app.py' in cmdline or 'DDSFocusPro' in cmdline:
                        logging.info(f"� Killing Flask process: PID {proc.pid}")
                        proc.kill()
            except Exception as e:
                continue
                
    except Exception as e:
        logging.warning(f"⚠️ Error during process cleanup: {e}")

    logging.info("👋 Application cleanup complete. Exiting.")
    os._exit(0)

# ------------------ Main Launcher ------------------
if __name__ == '__main__':
    # Step 1: Open exec terminal first
    logging.info("🚀 Starting DDS Focus Pro with exec terminal...")
    open_exec_terminal()
    
    # Step 2: Clean up existing processes
    kill_existing_connector()
    
    # Step 3: Start background launcher
    threading.Thread(target=background_launcher, daemon=True).start()

    # Step 4: Show UI immediately (no wait)
    try:
        # Try multiple locations for loader.html
        current_dir = os.getcwd()
        possible_loader_paths = [
            os.path.join(current_dir, "templates", "loader.html"),
            os.path.join(os.path.dirname(__file__), "templates", "loader.html"),
            os.path.join(os.path.dirname(sys.executable), "templates", "loader.html") if getattr(sys, 'frozen', False) else None,
        ]
        
        loader_path = None
        for path in possible_loader_paths:
            if path and os.path.exists(path):
                loader_path = path
                break
        
        if not loader_path:
            logging.error(f"[ERROR] loader.html NOT FOUND in any of these locations:")
            for path in possible_loader_paths:
                if path:
                    logging.error(f"  - {path}")
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


        # [OK] Attach cleanup after window opens
        def after_window_created():
            if webview.windows:
                webview.windows[0].events.closed += cleanup_and_exit

        webview.start(gui='edgechromium', debug=False, func=after_window_created)

    except Exception as e:
        logging.error(f"[ERROR] WebView failed: {e}")