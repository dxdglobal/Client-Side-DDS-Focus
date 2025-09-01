# tracker.py
from datetime import datetime
from pathlib import Path
import logging
# from django.views.decorators.csrf import csrf_exempt
import json
import os
import psutil
import threading
from collections import defaultdict
import time
import openai
import pprint
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

def sanitize(text):
    """
    Text ko safe banata hai folder/file names ke liye
    e.g., test@abc.com → test_at_abc_com
    """
    return text.replace("@", "_at_").replace(" ", "_").replace("/", "_").replace(".", "_")



import requests  # ✅ Required for API call

def send_summary_to_backend(email, task_name):
    """
    Sends the latest program_summary.json to a remote backend via POST.
    """
    date_str = datetime.now().strftime("%Y-%m-%d")
    safe_email = sanitize(email)
    safe_task = sanitize(task_name)[:50]

    summary_path = os.path.join("logs", date_str, safe_email, safe_task, f"{safe_task}_program_summary.json")

    if not os.path.exists(summary_path):
        logger.warning("🚫 Summary file not found, skipping send")
        return

    try:
        with open(summary_path, "r", encoding="utf-8") as f:
            summary_data = json.load(f)

        url = "https://dxdtime.ddsolutions.io/en/api/update-log-info"

        # ✅ CSRF güvenliğini aşmak için Referer header ekliyoruz
        headers = {
            "Content-Type": "application/json",
            "Referer": "https://dxdtime.ddsolutions.io"  # CSRF için şart
        }

        response = requests.post(url, json={
            "email": email,
            "task": task_name,
            "summary": summary_data
        }, headers=headers)

        print("📤 Sent data to API:")
        print("Status Code:", response.status_code)
        print("Response Body:", response.text)
        if response.status_code == 200:
            logger.info("📤 Summary sent to backend successfully")
        else:
            logger.warning("⚠️ Backend returned %s", response.status_code)

    except Exception as e:
        logger.error(" ")



def get_current_session():
    """
    Reads email and task from current session file. Returns None if not valid.
    """
    try:
        with open("data/current_session.json", "r", encoding="utf-8") as f:
            session = json.load(f)
            email = session.get("email")
            task = session.get("task")
            if email and task:
                return email, task
            else:
                logger.warning("⚠️ Session missing email or task")
                return None
    except Exception as e:
        logger.warning("⚠️ Session file missing or invalid: %s", e)
        return None


def save_raw_program_log(email, task_name, program_data):
    """
    Appends current minute's program data to raw log file.
    File: logs/YYYY-MM-DD/email/task/program_raw.json
    """
    date_str = datetime.now().strftime("%Y-%m-%d")
    safe_email = sanitize(email)
    safe_task = sanitize(task_name)[:50]

    base_folder = os.path.join("logs", date_str, safe_email, safe_task)
    os.makedirs(base_folder, exist_ok=True)

    filename = os.path.join(base_folder, f"{safe_task}_program_raw.json")

    try:
        # Load old data if file exists
        if os.path.exists(filename):
            with open(filename, "r", encoding="utf-8") as f:
                old_data = json.load(f)
        else:
            old_data = []

        # Append new usage data
        old_data.extend(program_data)

        # Save back
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(old_data, f, indent=2, ensure_ascii=False)

        logger.info("📦 Appended raw log data to: %s", filename)
    except Exception as e:
        logger.error(" ")

    return filename


def update_summary_log(email, task_name, _program_data=None):
    """
    Summarizes all raw log entries by:
    - Program name (with aliases)
    - Grouped by category (e.g., Browsers, Communication)
    - ✅ FIXED: Only counts unique minutes per program
    """
    date_str = datetime.now().strftime("%Y-%m-%d")
    safe_email = sanitize(email)
    safe_task = sanitize(task_name)[:50]

    base_folder = os.path.join("logs", date_str, safe_email, safe_task)
    raw_file = os.path.join(base_folder, f"{safe_task}_program_raw.json")
    summary_file = os.path.join(base_folder, f"{safe_task}_program_summary.json")

    program_aliases = {
        "Code.exe": "VSCode",
        "chrome.exe": "Chrome",
        "msedge.exe": "Edge",
        "explorer.exe": "File Explorer",
        "Teams.exe": "Teams",
        "WhatsApp.exe": "WhatsApp",
        "Zoom.exe": "Zoom",
        "POWERPNT.EXE": "PowerPoint",
        "WINWORD.EXE": "Word",
        "EXCEL.EXE": "Excel"
    }

    program_categories = {
        "VSCode": "Development",
        "Chrome": "Browsers",
        "Edge": "Browsers",
        "File Explorer": "Productivity",
        "Teams": "Communication",
        "WhatsApp": "Communication",
        "Zoom": "Communication",
        "PowerPoint": "Productivity",
        "Word": "Productivity",
        "Excel": "Productivity"
    }

    system_processes = {
        "svchost.exe", "conhost.exe", "csrss.exe", "dllhost.exe", "winlogon.exe",
        "wininit.exe", "lsass.exe", "services.exe", "smss.exe", "spoolsv.exe",
        "fontdrvhost.exe", "taskhostw.exe", "RuntimeBroker.exe", "MemCompression",
        "SearchIndexer.exe", "SearchProtocolHost.exe", "SearchFilterHost.exe",
        "ApplicationFrameHost.exe", "dwm.exe", "ctfmon.exe", "sihost.exe",
        "ShellExperienceHost.exe", "StartMenuExperienceHost.exe", "LockApp.exe",
        "SystemSettings.exe", "NVIDIA Web Helper.exe", "MsMpEng.exe", "SecurityHealthService.exe",
        "SecurityHealthSystray.exe", "MpDefenderCoreService.exe", "vmcompute.exe", "vmms.exe",
        "vmnetdhcp.exe", "vmnat.exe", "vmware-authd.exe", "vmware-usbarbitrator64.exe", "vmware-tray.exe",
        "CompPkgSrv.exe", "NisSrv.exe", "WmiPrvSE.exe", "UserOOBEBroker.exe", "PhoneExperienceHost.exe"
    }

    try:
        with open(raw_file, "r", encoding="utf-8") as f:
            raw_data = json.load(f)
    except Exception as e:
        logger.error(" ")
        return

    # ✅ Build program → set of unique minute timestamps
    program_time_map = defaultdict(set)

    for entry in raw_data:
        raw_name = entry.get("program", "Unknown")
        timestamp = entry.get("timestamp")

        if raw_name in system_processes:
            continue

        if not timestamp:
            continue

        # Normalize to "YYYY-MM-DDTHH:MM" (minute-level)
        minute_key = timestamp[:16]
        program_name = program_aliases.get(raw_name, raw_name)
        program_time_map[program_name].add(minute_key)

    # ✅ Create summary based on unique minutes
    sorted_programs = dict(sorted(program_time_map.items(), key=lambda x: len(x[1]), reverse=True))
    program_summary = {prog: f"{len(minutes):.1f} mins" for prog, minutes in sorted_programs.items()}

    # ✅ Build category summary
    category_counts = defaultdict(int)
    for prog, minutes in sorted_programs.items():
        category = program_categories.get(prog, "Unknown")
        category_counts[category] += len(minutes)

    sorted_categories = dict(sorted(category_counts.items(), key=lambda x: x[1], reverse=True))
    category_summary = {k: f"{v:.1f} mins" for k, v in sorted_categories.items()}

    final_summary = {
        "categories": category_summary,
        "programs": program_summary
    }

    try:
        with open(summary_file, "w", encoding="utf-8") as f:
            json.dump(final_summary, f, indent=2, ensure_ascii=False)
        logger.info("📊 Summary with categories saved: %s", summary_file)
    except Exception as e:
        logger.error(" ")


def save_text_log():
    """
    Session info ko ek plain text (.txt) file mein save karta hai.
    """
    email, task_name = get_current_session()

    today = datetime.now().strftime("%Y-%m-%d")
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    safe_email = sanitize(email)
    safe_task = sanitize(task_name)

    folder_path = Path("logs") / today / safe_email / safe_task
    folder_path.mkdir(parents=True, exist_ok=True)

    content = f"📝 Log for {email} working on {task_name} at {timestamp}"
    file_path = folder_path / f"{safe_task}_note.txt"

    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        logger.info("✅ Text file saved at: %s", file_path)
    except Exception as e:
        logger.error(" ")


def get_program_history_and_save(email: str, task_name: str) -> str:
    """
    Programs ka usage collect kar ke raw log save karta hai.
    File path return karta hai.
    """
    usage_data = collect_active_programs()
    file_path = save_raw_program_log(email, task_name, usage_data)
    return file_path


def collect_active_programs():
    """System ke current active programs ka simple snapshot."""
    active_programs = []
    for proc in psutil.process_iter(['pid', 'name', 'exe']):
        try:
            info = proc.info
            if info['name'] and info['exe']:
                active_programs.append({
                    "program": info['name'],
                    "path": info['exe'],
                    "timestamp": datetime.now().isoformat()
                })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return active_programs





def auto_log_every_minute():
    def log_loop():
        while True:
            session = get_current_session()
            if session:
                email, task_name = session
                usage = collect_active_programs()

                # 🛠 Save actual usage to raw file
                save_raw_program_log(email=email, task_name=task_name, program_data=usage)

                # ✅ Now update summary file based on updated raw log
                update_summary_log(email=email, task_name=task_name)

                # ✅ Send to backend
                send_summary_to_backend(email=email, task_name=task_name)

            else:
                logger.warning("⛔ Skipping log — session not valid.")

            time.sleep(60)

    t = threading.Thread(target=log_loop, daemon=True)
    t.start()
    logger.info("🕒 Started auto summary + upload thread")



if __name__ == "__main__":
    save_text_log()
    auto_log_every_minute()  # ✅ Start logging every minute!
