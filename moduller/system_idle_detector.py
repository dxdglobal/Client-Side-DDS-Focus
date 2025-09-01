import ctypes
import time
import threading
import requests

IDLE_THRESHOLD = 180  # seconds

def get_idle_duration():
    class LASTINPUTINFO(ctypes.Structure):
        _fields_ = [('cbSize', ctypes.c_uint), ('dwTime', ctypes.c_uint)]
    lii = LASTINPUTINFO()
    lii.cbSize = ctypes.sizeof(LASTINPUTINFO)
    ctypes.windll.user32.GetLastInputInfo(ctypes.byref(lii))
    millis = ctypes.windll.kernel32.GetTickCount() - lii.dwTime
    return millis / 1000.0  # return in seconds

def start_idle_monitor(flask_server_url, email, staff_id, task_id):
    def monitor():
        while True:
            idle = get_idle_duration()
            if idle >= IDLE_THRESHOLD:
                print(f"💤 System idle for {int(idle)} seconds. Triggering auto-pause...")

                try:
                    # 1. Auto-submit session
                    response = requests.post(f"{flask_server_url}/end_task_session", json={
                        "email": email,
                        "staff_id": staff_id,
                        "task_id": task_id,
                        "end_time": int(time.time()),
                        "note": f"Auto-paused due to {int(idle)} seconds system idle"
                    })
                    print("✅ Idle session auto-submitted:", response.status_code)

                    # 2. Notify frontend by setting idle flag
                    requests.post(f"{flask_server_url}/set_idle_flag", json={"idle": True})
                    print("📡 Idle flag sent to Flask backend")

                except Exception as e:
                    print("❌ Failed to notify Flask server:", e)
                break  # exit after one trigger
            time.sleep(5)

    threading.Thread(target=monitor, daemon=True).start()
