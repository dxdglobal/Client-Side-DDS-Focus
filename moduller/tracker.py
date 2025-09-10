from datetime import datetime
from pathlib import Path
import logging
import boto3
import os
import glob
import json
import psutil
import threading
from collections import defaultdict
import time
import requests

try:
    from .active_window_tracker import get_tracker as get_window_tracker, start_active_window_tracking, get_current_activity_summary
except ImportError:
    # Fallback if active_window_tracker is not available
    get_window_tracker = None
    start_active_window_tracking = None
    get_current_activity_summary = None

logger = logging.getLogger(__name__)

def sanitize(text):
    """
    Text ko safe banata hai folder/file names ke liye
    e.g., test@abc.com → test_at_abc_com
    """
    return text.replace("@", "_at_").replace(" ", "_").replace("/", "_").replace(".", "_")

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
        logger.error("❌ Error sending summary to backend: %s", e)

def save_raw_program_log(email, task_name, program_data):
    """
    Appends current minute's program data to raw log file.
    File: logs/YYYY-MM-DD/email/task_name/task_name_program_raw.json
    """
    date_str = datetime.now().strftime("%Y-%m-%d")
    safe_email = sanitize(email)
    # Keep the original task name but sanitize it for folder/file names
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
        logger.error("❌ Error saving raw program log: %s", e)

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
        logger.error("❌ Error reading raw file: %s", e)
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
        logger.error("❌ Error saving summary file: %s", e)

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
        logger.error("❌ Error saving text log: %s", e)

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

def collect_program_usage():
    """Alias for collect_active_programs for backward compatibility"""
    return collect_active_programs()

def auto_log_every_minute():
    global _logging_active, _logging_thread
    
    def log_loop():
        while _logging_active:
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

    if not _logging_active:
        _logging_active = True
        _logging_thread = threading.Thread(target=log_loop, daemon=True)
        _logging_thread.start()
        logger.info("🕒 Started auto summary + upload thread")

def logs_file(local_path, email, task_name):
    logger.info("📤 [upload_screenshot] started")

    # Check boto3
    logger.info("✅ boto3 module already imported at top")

    # Load AWS credentials from environment variables
    access_key = os.getenv("AWS_ACCESS_KEY_ID")
    secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    bucket = os.getenv("S3_BUCKET_NAME", "ddsfocustime")
    region = os.getenv("AWS_REGION", "us-east-1")


    logger.info("🔐 AWS_ACCESS_KEY_ID: %s", access_key)
    logger.info("🪣 S3_BUCKET_NAME: %s", bucket)
    logger.info("🌍 AWS_REGION: %s", region)

    # Check if credentials are missing
    if not all([access_key, secret_key, bucket, region]):
        logger.error("❌ One or more AWS environment variables are missing.")
        return None

    # Check if local file exists
    if not Path(local_path).exists():
        logger.error("❌ File not found: %s", local_path)
        return None

    filename = Path(local_path).name
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    date_folder = datetime.now().strftime("%Y-%m-%d")
    safe_email = email.replace("@", "_at_")
    safe_task = task_name.replace(" ", "_").replace("/", "_")
    s3_key = f"logs/{date_folder}/{safe_email}/{safe_task}/{timestamp}_{filename}"

    logger.info("📁 Local file: %s", local_path)
    logger.info("👤 Email: %s", email)
    logger.info("📝 Task: %s", task_name)
    logger.info("☁️ S3 key: %s", s3_key)

    try:
        session = boto3.Session(
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region
        )
        s3 = session.client('s3')
        s3.upload_file(str(local_path), bucket, s3_key)

        url = f"https://{bucket}.s3.{region}.amazonaws.com/{s3_key}"
        logger.info("✅ Upload successful: %s", url)
        return url
    except Exception as e:
        logger.error("❌ Upload failed: %s", e)
        return None

def upload_tracker_logs(logs_base_path=None):
    """
    Scan the logs directory and upload all tracker log files to S3
    """
    if logs_base_path is None:
        # Default to the logs directory relative to this file
        current_dir = Path(__file__).parent.parent
        logs_base_path = current_dir / "logs"
    
    logs_base_path = Path(logs_base_path)
    
    if not logs_base_path.exists():
        logger.error("❌ Logs directory not found: %s", logs_base_path)
        return []
    
    logger.info("🔍 Scanning tracker logs in: %s", logs_base_path)
    
    uploaded_files = []
    
    # Find all JSON files in the logs directory structure
    json_pattern = str(logs_base_path / "**" / "*.json")
    json_files = glob.glob(json_pattern, recursive=True)
    
    for json_file in json_files:
        json_path = Path(json_file)
        
        # Skip the "--_İş_Emri_Seçin_--" folder
        if "--_İş_Emri_Seçin_--" in str(json_path):
            logger.info("⏭️ Skipping excluded folder: %s", json_path)
            continue
        
        # Parse the path structure to extract email and task info
        # Expected structure: logs/YYYY-MM-DD/email_at_domain_com/TaskName/filename.json
        try:
            parts = json_path.parts
            
            # Find the email part (contains "_at_")
            email_part = None
            task_part = None
            
            for i, part in enumerate(parts):
                if "_at_" in part and "@" not in part:
                    email_part = part
                    # Get the task part after email (any folder name)
                    if i + 1 < len(parts):
                        task_part = parts[i + 1]
                    break
            
            if not email_part or not task_part:
                logger.warning("⚠️ Could not parse email/task from path: %s", json_file)
                continue
            
            # Convert email format back to normal
            email = email_part.replace("_at_", "@").replace("_com", ".com").replace("_org", ".org")
            # Use actual task name instead of task ID
            task_name = task_part.replace("_", " ")  # Convert underscores back to spaces for readability
            
            logger.info("📄 Found log file: %s", json_path.name)
            logger.info("   👤 Email: %s", email)
            logger.info("   📝 Task: %s", task_name)
            
            # Upload the file
            url = logs_file(str(json_path), email, task_name)
            if url:
                uploaded_files.append({
                    'local_path': str(json_path),
                    'email': email,
                    'task': task_name,
                    'url': url
                })
                logger.info("✅ Uploaded: %s", json_path.name)
            else:
                logger.error("❌ Failed to upload: %s", json_path.name)
                
        except Exception as e:
            logger.error("❌ Error processing %s: %s", json_file, e)
            continue
    
    logger.info("📊 Upload summary: %d files processed, %d uploaded successfully", 
                len(json_files), len(uploaded_files))
    
    return uploaded_files

def upload_specific_tracker_log(log_file_path):
    """
    Upload a specific tracker log file to S3
    
    Args:
        log_file_path (str): Path to the specific log file to upload
        
    Returns:
        str: S3 URL if successful, None if failed
    """
    log_path = Path(log_file_path)
    
    if not log_path.exists():
        logger.error("❌ Log file not found: %s", log_file_path)
        return None
    
    # Skip the "--_İş_Emri_Seçin_--" folder
    if "--_İş_Emri_Seçin_--" in str(log_path):
        logger.info("⏭️ Skipping excluded folder: %s", log_path)
        return None
    
    # Parse the path to extract email and task info
    try:
        parts = log_path.parts
        
        # Find the email part (contains "_at_")
        email_part = None
        task_part = None
        
        for i, part in enumerate(parts):
            if "_at_" in part and "@" not in part:
                email_part = part
                # Get the task part after email (any folder name)
                if i + 1 < len(parts):
                    task_part = parts[i + 1]
                break
        
        if not email_part or not task_part:
            logger.error("❌ Could not parse email/task from path: %s", log_file_path)
            return None
        
        # Convert email format back to normal
        email = email_part.replace("_at_", "@").replace("_com", ".com").replace("_org", ".org")
        # Use actual task name instead of task ID
        task_name = task_part.replace("_", " ")  # Convert underscores back to spaces for readability
        
        logger.info("📤 Uploading specific tracker log:")
        logger.info("   📄 File: %s", log_path.name)
        logger.info("   👤 Email: %s", email)
        logger.info("   📝 Task: %s", task_name)
        
        # Upload the file
        url = logs_file(str(log_path), email, task_name)
        return url
        
    except Exception as e:
        logger.error("❌ Error processing %s: %s", log_file_path, e)
        return None

def upload_program_data_to_s3(email, task_name, program_data):
    """
    Creates a temporary file from program data and uploads to S3
    This is for compatibility with app.py calls that pass data directly
    """
    try:
        # Create temporary file with the program data
        import tempfile
        import json
        
        # Create temp file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as temp_file:
            json.dump(program_data, temp_file, indent=2, ensure_ascii=False)
            temp_file_path = temp_file.name
        
        # Upload the temp file
        url = logs_file(temp_file_path, email, task_name)
        
        # Clean up temp file
        os.unlink(temp_file_path)
        
        return url
        
    except Exception as e:
        logger.error("❌ Error creating/uploading program data: %s", e)
        return None

# Global variables for logging control
_logging_active = False
_logging_thread = None

def start_logging():
    """
    Start the logging system - compatibility function for app.py
    """
    global _logging_active, _logging_thread
    if not _logging_active:
        _logging_active = True
        auto_log_every_minute()
        logger.info("🚀 Logging system started")
    else:
        logger.info("ℹ️ Logging system already running")

def stop_logging():
    """
    Stop the logging system - compatibility function for app.py
    """
    global _logging_active
    _logging_active = False
    logger.info("🛑 Logging system stopped")

def upload_logs_on_app_close():
    """
    Upload all pending logs when app closes - compatibility function for app.py
    """
    try:
        logger.info("📤 Uploading logs on app close...")
        uploaded_files = upload_tracker_logs()
        logger.info(f"✅ Upload complete: {len(uploaded_files)} files uploaded")
        return uploaded_files
    except Exception as e:
        logger.error(f"❌ Error uploading logs on close: {e}")
        return []

if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) > 1:
        # Upload specific file
        specific_file = sys.argv[1]
        logger.info("🎯 Uploading specific file: %s", specific_file)
        url = upload_specific_tracker_log(specific_file)
        if url:
            print(f"✅ Successfully uploaded: {url}")
        else:
            print("❌ Upload failed")
    else:
        # Upload all tracker logs
        logger.info("📁 Uploading all tracker logs...")
        uploaded_files = upload_tracker_logs()
        print(f"📊 Upload complete: {len(uploaded_files)} files uploaded")
        for file_info in uploaded_files:
            print(f"   ✅ {file_info['local_path']} -> {file_info['url']}")
