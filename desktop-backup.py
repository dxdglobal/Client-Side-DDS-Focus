import os
import threading
import webview
import time
import subprocess
import requests
import sys
import psutil
import signal

flask_process = None




def start_flask():
    global flask_process

    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.abspath(".")

    import platform
    ext = ".exe" if platform.system() == "Windows" else ""
    app_path = os.path.join(base_path, "app" + ext)

    if not os.path.exists(app_path):
        print(f"[ERROR] app.exe not found at {app_path}")
        sys.exit(1)

    log_file = os.path.join(base_path, "flask.log")

    # ❗️DON'T use `with` — keep file open while process runs
    f = open(log_file, "w")

    flask_process = subprocess.Popen(
        [app_path],
        stdout=f,
        stderr=f,
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
    )

    print("[INFO] app.exe launched successfully.")







def wait_for_flask():
    for _ in range(30):
        try:
            response = requests.get("http://127.0.0.1:5000/health")
            if response.status_code == 200:
                return True
        except:
            time.sleep(1)
    return False

def on_closed():
    print("[INFO] Webview closed. Killing app.exe if running...")

    # ✅ First try clean kill using subprocess reference
    try:
        if flask_process:
            print(f"[INFO] Terminating app.exe (PID: {flask_process.pid}) via subprocess...")
            if os.name == 'nt':
                flask_process.send_signal(signal.CTRL_BREAK_EVENT)
            flask_process.terminate()
            flask_process.wait(timeout=5)
    except Exception as e:
        print(f"[WARN] Subprocess kill failed: {e}")

    # ✅ Fallback: Force kill any leftovers via psutil
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            if proc.info['name'].lower() == 'app.exe':
                print(f"[INFO] Forcibly killing PID {proc.info['pid']} (app.exe)")
                proc.kill()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    print("[INFO] All app.exe processes terminated.")
    os._exit(0)

if __name__ == '__main__':
    print("[INFO] Starting Flask backend...")
    flask_thread = threading.Thread(target=start_flask, daemon=True)
    flask_thread.start()

    print("[INFO] Waiting for Flask to be ready...")
    if wait_for_flask():
        print("[INFO] Flask is ready. Launching desktop app.")
        webview.create_window("DDS-FocusPro", "http://127.0.0.1:5000", width=900, height=750)
        # webview.start(on_closed)
        try:
            webview.start()  # Don't pass on_closed to avoid breaking the UI
        except KeyboardInterrupt:
            pass
        finally:
            on_closed()  # Call clean-up manually after window closes
    else:
        print("[ERROR] Flask failed to start.")