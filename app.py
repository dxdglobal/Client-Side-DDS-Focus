# -*- coding: utf-8 -*-
import os
import sys
import io

try:
    if sys.stdout:
        sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding='utf-8')
    if sys.stderr:
        sys.stderr = io.TextIOWrapper(sys.stderr.detach(), encoding='utf-8')
except Exception as e:
    print(f"[Warning] Could not set UTF-8 encoding for stdout/stderr: {e}")


from flask_mail import Mail, Message
from moduller.tracker import save_raw_program_log, logs_file, collect_program_usage, get_program_history_and_save, upload_program_data_to_s3
from moduller.tracker import auto_log_every_minute, start_logging, stop_logging, upload_logs_on_app_close

from flask import Flask, render_template, request, jsonify
import requests 
import os, sys
import logging  # ✅ MOVE THIS HERE
from dotenv import load_dotenv
from moduller.veritabani_yoneticisi import VeritabaniYoneticisi
from moduller.ai_query_handler import execute_sql_from_prompt
from moduller.ai_filtered_project import get_ai_filtered_projects
from moduller.system_idle_detector import start_idle_monitor

import json
from datetime import datetime
from flask_mail import Message
from PIL import Image
import mss
import threading
import time
# from moduller.s3_uploader import logs
# from moduller.tracker import logs_file
# from moduller.tracker import collect_program_usage, logs_file
from moduller.ai_summarizer import summarize_program_usage
import io

import cv2
import numpy as np
import pyautogui
import time
import threading
import mss
import mss.tools
import boto3
import openai
# from moduller.tracker import TaskLogger
# from moduller.tracker import start_browser_tracking
# from moduller.tracker import stop_browser_tracking
# from moduller.tracker import collect_all_history
import logging
from moduller.config_manager import config_manager

is_user_idle = False  # Global idle flag


#  Ensures .env works even after converting to .exe
if getattr(sys, 'frozen', False):
    # Running as .exe from PyInstaller
     base_path = os.path.dirname(sys.executable)
else:
    # Running in normal Python
    base_path = os.path.abspath(".")

dotenv_path = os.path.join(base_path, '.env')
print(f" .env path: {dotenv_path}")
load_dotenv(dotenv_path)
logging.info("✅ .env loaded from: %s", dotenv_path)
logging.info("🔐 AWS_ACCESS_KEY_ID: %s", os.getenv("AWS_ACCESS_KEY_ID"))

DATA_FOLDER = 'data'
if not os.path.exists(DATA_FOLDER):
    os.makedirs(DATA_FOLDER)

LOG_FILE = "session_logs.json"

recording_active = False
recording_thread = None
current_recording_folder = None

# --- Configuration ---
load_dotenv()
PERFEX_API_URL = "https://crm.deluxebilisim.com/api/timesheets"
# AUTH_TOKEN = os.getenv("AUTH_TOKEN")
# DB_HOST = os.getenv("DB_HOST")
# DB_USER = os.getenv("DB_USER")
# DB_PASSWORD = os.getenv("DB_PASSWORD")
# DB_NAME = os.getenv("DB_NAME")
# DB_PORT = int(os.getenv("DB_PORT", 3306))
# Hardcoded database config
AUTH_TOKEN = os.getenv("AUTH_TOKEN")

# Database configuration from environment variables
DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
DB_PORT = int(os.getenv("DB_PORT", 3306))



import logging
import os
import sys

log_folder = "logs"
if not os.path.exists(log_folder):
    os.makedirs(log_folder)




log_file = os.path.join(log_folder, "app.log")
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(log_file, mode='w', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

def handle_exception(exc_type, exc_value, exc_traceback):
    logging.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

sys.excepthook = handle_exception







app = Flask(
    __name__,
    template_folder=os.path.join(sys._MEIPASS, "templates") if getattr(sys, 'frozen', False) else "templates",
    static_folder=os.path.join(sys._MEIPASS, "static") if getattr(sys, 'frozen', False) else "static"
)



# 🔽 YAHAN SE SMTP CONFIG SHURU
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True') == 'True'
app.config['MAIL_USE_SSL'] = os.getenv('MAIL_USE_SSL', 'False') == 'True'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_USERNAME')

mail = Mail(app)
# 🔼 YAHAN TAK SMTP CONFIG END



# @app.route('/start_tracking', methods=['POST'])
# def start_tracking():
#     data = request.get_json()
#     email = data.get('email')
#     start_browser_tracking(email)
#     return jsonify({"status": "started"})

# @app.route('/stop_tracking', methods=['POST'])
# def stop_tracking():
#     stop_browser_tracking()
#     return jsonify({"status": "stopped"})

# @app.route("/force_log")
# def force_log():
#     print("🔥 force_log triggered")
#     result = collect_all_history("testuser@example.com")
#     print("✅ force_log finished")
#     return jsonify(result)


# --- Database Connection Check ---
@app.route('/check-db-connection', methods=['GET'])
def check_db_connection():
    """Check if the database connection is successful and return the result."""
    # db_host = os.getenv("DB_HOST")
    # db_user = os.getenv("DB_USER")
    # db_password = os.getenv("DB_PASSWORD")
    # db_name = os.getenv("DB_NAME")
    # port = int(os.getenv("DB_PORT"))
    # AUTH_TOKEN="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyIjoiZGVsdXhldGltZSIsIm5hbWUiOiJkZWx1eGV0aW1lIiwiQVBJX1RJTUUiOjE3NDUzNDQyNjJ9.kJGo5DksaPwkHwufDvLMGaMmjk5q2F7GhjzwdHtfT_o"
    db_host = "92.113.22.65"
    db_user = "u906714182_sqlrrefdvdv"
    db_password = "3@6*t:lU"
    db_name = "u906714182_sqlrrefdvdv"
    port = 3306

    # Initialize the VeritabaniYoneticisi object and try to connect
    veritabani = VeritabaniYoneticisi(db_host, db_user, db_password, db_name, port)
    veritabani.baglanti_olustur()

    # Check if the database connection is active
    if veritabani.baglanti_testi():
        return jsonify({"status": "success", "message": " "})
    else:
        return jsonify({"status": "error", "message": "Database connection failed. app"})


CACHE_FOLDER = "user_cache"

# Function to save user data (projects and tasks) into cache
def save_user_cache(email, username, projects_with_tasks):
    filename = os.path.join(CACHE_FOLDER, f"{email.replace('@', '_at_')}.json")
    print(f"Saving user cache to: {filename}")  # Debugging line
    with open(filename, "w", encoding="utf-8") as f:
        json.dump({
            "email": email,
            "username": username,
            "projects": projects_with_tasks
        }, f, ensure_ascii=False, indent=2)
    print(f" Cached projects and tasks for {email}")

@app.route('/loader.html')
def loader():
    return render_template('loader.html')


# Route to save user data (projects + tasks)
@app.route('/cache_user_projects', methods=['POST'])
def cache_user_projects():
    data = request.json
    email = data.get('email')
    username = data.get('username')
    projects = data.get('projects')  # This should include both projects and tasks

    # Debugging log
    print(f"Received data: {data}")

    if not email or not projects:
        return jsonify({"status": "error", "message": "Missing email or projects"}), 400

    save_user_cache(email, username, projects)
    return jsonify({"status": "success", "message": "User cache saved."})



# Route to load user projects from cache
@app.route('/load_user_projects/<email>', methods=['GET'])
def load_user_projects(email):
    filename = os.path.join(CACHE_FOLDER, f"{email.replace('@', '_at_')}.json")
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            user_data = json.load(f)
        return jsonify({"status": "success", "data": user_data})
    else:
        return jsonify({"status": "error", "message": "No cached data for user"}), 404


# --- Fetch Data from tblstaff ---
@app.route('/get-staff-data', methods=['GET'])
def get_staff_data():
    """Fetch and show all data from the tblstaff table"""
    # db_host = os.getenv("DB_HOST")
    # db_user = os.getenv("DB_USER")
    # db_password = os.getenv("DB_PASSWORD")
    # db_name = os.getenv("DB_NAME")
    # port = int(os.getenv("DB_PORT"))
    db_host = "92.113.22.65"
    db_user = "u906714182_sqlrrefdvdv"
    db_password = "3@6*t:lU"
    db_name = "u906714182_sqlrrefdvdv"
    port = 3306

    # Initialize the VeritabaniYoneticisi object and try to connect
    veritabani = VeritabaniYoneticisi(db_host, db_user, db_password, db_name, port)
    veritabani.baglanti_olustur()

    # Query to get all data from the tblstaff table
    query = "SELECT * FROM tblstaff"
    staff_data = veritabani.sorgu_calistir(query)


    if staff_data:
        # Print all staff data in the terminal
        print("Staff Data from tblstaff table:")
        for staff in staff_data:
            print(f"Staff ID: {staff.get('staffid')}")
            print("-" * 30)

        # Returning the staff data in JSON response
        return jsonify({"status": "success", "staff_data": staff_data})
    else:
        return jsonify({"status": "error", "message": "No staff data found."})



from flask import session  # Make sure you import session at the top

@app.route('/get_projects', methods=['GET'])
def get_all_projects():
    print(" Fetching all projects (no staffid filtering)")

    # db_host = os.getenv("DB_HOST")
    # db_user = os.getenv("DB_USER")
    # db_password = os.getenv("DB_PASSWORD")
    # db_name = os.getenv("DB_NAME")
    # port = int(os.getenv("DB_PORT"))
    db_host = "92.113.22.65"
    db_user = "u906714182_sqlrrefdvdv"
    db_password = "3@6*t:lU"
    db_name = "u906714182_sqlrrefdvdv"
    port = 3306

    veritabani = VeritabaniYoneticisi(db_host, db_user, db_password, db_name, port)
    veritabani.baglanti_olustur()

    query = "SELECT * FROM tblprojects"
    projects = veritabani.sorgu_calistir(query)

    if projects:
        total = len(projects)
        print(f" Total Projects Fetched: {total}")
        for project in projects:
            print(f" ID: {project.get('id')}, Name: {project.get('name')}")
        return jsonify({"status": "success", "count": total, "projects": projects})
    else:
        print(" No projects found.")
        return jsonify({"status": "error", "message": "No projects found."})


from flask import request

from flask import request  # make sure you imported request

@app.route('/get_ai_filtered_projects', methods=['POST'])
def get_ai_filtered_projects_route():
    try:
        data = request.get_json()
        print("Received POST data:", data)  #  ADD THIS

        email = data.get('email')
        username = data.get('username')

        print(f"Email: {email}, Username: {username}")  #  ADD THIS

        if not email and not username:
            print(" Missing email and username")
            return jsonify({"status": "error", "message": "No email or username provided."}), 400

        return get_ai_filtered_projects(email, username)
    

    except Exception as e:
        print(f" Screenshot capture failed: {e}")
        print(" Internal server error:", str(e))
        return jsonify({"status": "error", "message": "Internal server error", "details": str(e)}), 500





@app.route('/upload_ai_summary', methods=['POST'])
def upload_ai_summary():
    data = request.get_json()
    email = data.get("email")
    task_name = data.get("task_name")

    if not email or not task_name:
        return jsonify({"success": False, "message": "Missing email or task name"}), 400

    usage_logs = collect_program_usage()
    ai_summary = summarize_program_usage(usage_logs)

    usage_logs.append({
        "program": "AI_Summary",
        "start": datetime.now().isoformat(),
        "end": datetime.now().isoformat(),
        "summary": ai_summary
    })

    url = upload_program_data_to_s3(email, task_name, usage_logs)
    if url:
        return jsonify({"success": True, "message": "AI log uploaded", "url": url})
    else:
        return jsonify({"success": False, "message": "Upload failed"}), 500



@app.route('/upload_log_file', methods=['POST'])
def upload_log_file():
    data = request.json
    local_path = data.get("local_path")  # Path to local log file
    email = data.get("email")
    task_name = data.get("task_name")

    if not local_path or not email or not task_name:
        return jsonify({"status": "error", "message": "Missing required parameters"}), 400

    url = logs_file(local_path, email, task_name)
    if url:
        return jsonify({"status": "success", "uploaded_url": url})
    else:
        return jsonify({"status": "error", "message": "Upload failed"}), 500















def start_screen_recording(folder_path, email, task_name):
    def record():
        global recording_active

        print(f" Starting screenshot capture - uploading directly to S3")
        with mss.mss() as sct:
            monitor = sct.monitors[1]  # full screen

            while recording_active:
                try:
                    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                    sct_img = sct.grab(monitor)

                    # Convert mss image to PIL image and save to bytes buffer
                    img = Image.frombytes('RGB', sct_img.size, sct_img.rgb)
                    
                    # Save to bytes buffer instead of local file
                    import io
                    img_buffer = io.BytesIO()
                    img.save(img_buffer, format="WEBP")
                    img_bytes = img_buffer.getvalue()

                    print(f" Screenshot captured: {timestamp}.webp")

                    # Upload directly to S3 without saving locally
                    from moduller.s3_uploader import upload_screenshot_direct
                    result_url = upload_screenshot_direct(img_bytes, email, task_name, "webp")
                    
                    if result_url:
                        logging.info(f"📸 Screenshot uploaded to S3: {result_url}")
                    else:
                        logging.error(f"❌ Failed to upload screenshot to S3")

                    time.sleep(30)  # every 30 seconds
                except Exception as e:
                    logging.error(f"❌ Screenshot error: {e}")
                    break















    global recording_thread
    recording_thread = threading.Thread(target=record, daemon=True)
    recording_thread.start()


























# --- Routes ---
@app.route('/')
def index():
    """Render the login page when the root route is accessed"""
    return render_template('login.html')

# --- Client Page ---
@app.route('/client')
def client():
    """Render the client page after successful login"""
    return render_template('client.html')  # This will render client.html from the templates folder

# --- Configuration API Endpoints ---
@app.route('/api/config', methods=['GET'])
def get_configuration():
    """
    Get application configuration for frontend
    Returns safe configuration without sensitive credentials
    """
    try:
        # Get safe configuration for frontend
        safe_config = config_manager.get_config_for_frontend()
        
        return jsonify({
            'success': True,
            'config': safe_config,
            'source': 'api' if config_manager.config_cache else 'default'
        })
    except Exception as e:
        logging.error(f"Error getting configuration: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/config/refresh', methods=['POST'])
def refresh_configuration():
    """
    Force refresh configuration from API
    """
    try:
        # Force refresh configuration
        fresh_config = config_manager.get_config(force_refresh=True)
        safe_config = config_manager.get_config_for_frontend()
        
        return jsonify({
            'success': True,
            'message': 'Configuration refreshed successfully',
            'config': safe_config
        })
    except Exception as e:
        logging.error(f"Error refreshing configuration: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/config/screenshot-interval', methods=['GET'])
def get_screenshot_interval():
    """
    Get current screenshot capture interval
    """
    try:
        interval = config_manager.get_screenshot_interval()
        return jsonify({
            'success': True,
            'interval_seconds': interval
        })
    except Exception as e:
        logging.error(f"Error getting screenshot interval: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500





@app.route('/get_tasks/<int:project_id>', methods=['GET'])
def get_tasks(project_id):
    db_host = "92.113.22.65"
    db_user = "u906714182_sqlrrefdvdv"
    db_password = "3@6*t:lU"
    db_name = "u906714182_sqlrrefdvdv"
    port = 3306

    veritabani = VeritabaniYoneticisi(db_host, db_user, db_password, db_name, port)
    veritabani.baglanti_olustur()

    query = f"""
        SELECT id, name, status
        FROM tbltasks
        WHERE rel_type = 'project'
          AND rel_id = {project_id}
          AND status != 5
    """
    tasks = veritabani.sorgu_calistir(query)

    if tasks:
        print(f"✅ Found {len(tasks)} tasks for project {project_id} (excluding status=5):")
        for task in tasks:
            print(f"🧾 Task ID: {task['id']} | Name: {task['name']} | Status: {task['status']}")
        return jsonify({"status": "success", "tasks": tasks})
    else:
        return jsonify({"status": "error", "message": "No tasks found for this project."})



@app.route('/ai-query', methods=['POST'])
def ai_query():
    user_input = request.json.get('query')
    if not user_input:
        return jsonify({"status": "error", "message": "No query provided"}), 400

    response = execute_sql_from_prompt(user_input)

    if "error" in response:
        return jsonify({"status": "error", "message": response["error"], "query": response.get("query")}), 500

    return jsonify({"status": "success", "query": response["query"], "data": response["result"]})



@app.route('/save_session_log', methods=['POST'])
def save_session_log():
    data = request.get_json()
    print(" Saving session log:", data)
    log_entry = {
        "email": data.get("email"),
        "taskId": data.get("taskId"),
        "startTime": data.get("startTime"),
        "endTime": data.get("endTime"),
        "totalSeconds": data.get("totalSeconds")
    }

    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            logs = json.load(f)
    else:
        logs = []

    logs.append(log_entry)

    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)

    return jsonify({"status": "success", "message": "Log saved"})




@app.route('/get_today_total/<email>', methods=['GET'])
def get_today_total(email):
    today = datetime.now().date().isoformat()
    total = 0

    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            logs = json.load(f)
            for log in logs:
                if log["email"] == email and log["startTime"].startswith(today):
                    total += log["totalSeconds"]

    return jsonify({"status": "success", "totalSeconds": total})

def create_recording_folder(base_dir, user_email, project_name, task_name):
    safe_email = user_email.replace('@', '_at_')
    safe_project = project_name[:50].replace(' ', '_')  # truncate project name
    safe_task = task_name[:50].replace(' ', '_')        # truncate task name
    # safe_project = project_name.replace(' ', '_')
    # safe_task = task_name.replace(' ', '_')

    project_root = os.path.abspath(os.path.dirname(__file__))  # This gives full path to current .py file
    folder_path = os.path.join(project_root, base_dir, safe_email, safe_project, safe_task)

    os.makedirs(folder_path, exist_ok=True)
    return folder_path






















@app.route('/start_screen_recording', methods=['POST'])
def start_screen_recording_api():
    global recording_active, current_recording_folder

    data = request.get_json()
    user_email = data.get("email")
    project_name = data.get("project")
    task_name = data.get("task")

    if not user_email or not project_name or not task_name:
        return jsonify({"status": "error", "message": "Missing data"}), 400

    folder_path = create_recording_folder("Screen-Recordings", user_email, project_name, task_name)
    current_recording_folder = folder_path
    recording_active = True

    #  Pass email and task name to recording function
    start_screen_recording(folder_path, user_email, task_name)

    return jsonify({"status": "success", "message": "Screen recording started."})


def start_screen_recording(folder_path, email, task_name):
    def record():
        global recording_active

        # Get screenshot interval from configuration
        screenshot_interval = config_manager.get_screenshot_interval()
        print(f"🔧 Starting screenshot capture - uploading directly to S3 (interval: {screenshot_interval}s)")
        
        with mss.mss() as sct:
            monitor = sct.monitors[1]  # full screen

            while recording_active:
                try:
                    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                    sct_img = sct.grab(monitor)

                    # Convert mss image to PIL image and save to bytes buffer
                    img = Image.frombytes('RGB', sct_img.size, sct_img.rgb)
                    
                    # Save to bytes buffer instead of local file
                    import io
                    img_buffer = io.BytesIO()
                    img.save(img_buffer, format="WEBP")
                    img_bytes = img_buffer.getvalue()

                    print(f"📸 Screenshot captured: {timestamp}.webp")

                    # Upload directly to S3 without saving locally
                    from moduller.s3_uploader import upload_screenshot_direct
                    result_url = upload_screenshot_direct(img_bytes, email, task_name, "webp")
                    
                    if result_url:
                        print(f"☁️ Screenshot uploaded to S3: {result_url}")
                    else:
                        print(f"❌ Failed to upload screenshot to S3")

                    time.sleep(screenshot_interval)  # Use configurable interval
                except Exception as e:
                    print(f"❌ Screenshot error: {e}")
                    break

    global recording_thread
    recording_thread = threading.Thread(target=record, daemon=True)
    recording_thread.start()


























@app.route('/stop_screen_recording', methods=['POST'])
def stop_screen_recording_api():
    global recording_active, recording_thread

    recording_active = False

    if recording_thread:
        recording_thread.join()
        recording_thread = None

    return jsonify({"status": "success", "message": "Screen recording stopped."})


from flask import jsonify
import os
import json
from datetime import datetime

@app.route('/get_task_time_summary/<email>', methods=['GET'])
def get_task_time_summary(email):
    task_times = {}

    if os.path.exists("session_logs.json") and os.stat("session_logs.json").st_size != 0:
        with open("session_logs.json", "r", encoding="utf-8") as f:
            logs = json.load(f)

        for log in logs:
            if log["email"] == email:
                start = int(log["startTime"])
                end = int(log["endTime"])
                duration = end - start
                task_id = log["taskId"]
                task_times[task_id] = task_times.get(task_id, 0) + duration

    # Format duration as HH:MM:SS
    formatted_summary = {
        task_id: f"{seconds // 3600:02}:{(seconds % 3600) // 60:02}:{seconds % 60:02}"
        for task_id, seconds in task_times.items()
    }

    return jsonify({"status": "success", "summary": formatted_summary})









@app.route("/get_program_history", methods=["GET"])
def get_program_history():
    from moduller.tracker import collect_program_usage
    try:
        logs = collect_program_usage()
        return jsonify({"program_history": logs})
    except Exception as e:
        return jsonify({"error": str(e)})





@app.route('/save_task_detail_json', methods=['POST'])

def save_task_detail_json():
    data = request.json
    email = data.get('email')
    entry = data.get('data')  #  Get inner payload

    if not email or not entry:
        return jsonify({"error": "Missing email or task data"}), 400

    # File name per user
    filename = os.path.join(DATA_FOLDER, f"{email.replace('@', '_at_').replace('.', '_')}.json")

    # Load existing or initialize
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            user_data = json.load(f)
    else:
        user_data = []

    # Append and save
    user_data.append(entry)
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(user_data, f, indent=4, ensure_ascii=False)

    print(f" Saved to {filename}:\n", json.dumps(entry, indent=4, ensure_ascii=False))

    return jsonify({"status": "success", "message": "Formatted task saved"})

















@app.route('/insert_user_timesheet', methods=['POST'])

def insert_user_timesheet():
    import json
    from flask import request, jsonify
    from datetime import datetime
    import pymysql

    try:
        req = request.get_json()
        
        # Debug: Log the type and content of the request
        logging.info(f"Request type: {type(req)}, Content: {req}")
        
        # Handle if request is a list (take the first item if it's a dict)
        if isinstance(req, list):
            if len(req) > 0 and isinstance(req[0], dict):
                req = req[0]
            else:
                return jsonify({'error': 'Invalid request format'}), 400
        elif not isinstance(req, dict):
            return jsonify({'error': 'Request must be JSON object'}), 400
            
        email = req.get('email')
        if not email:
            return jsonify({'error': 'Missing email'}), 400
    except Exception as e:
        logging.error(f"Error processing request: {e}")
        return jsonify({'error': 'Invalid JSON data'}), 400



    BASE_DIR = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.abspath(".")
    DATA_FOLDER = os.path.join(BASE_DIR, "data")

    # Ensure folder exists
    os.makedirs(DATA_FOLDER, exist_ok=True)

    # Now define your filename properly
    # Match data filename
    filename = os.path.join(DATA_FOLDER, email.replace("@", "_at_").replace(".", "_") + ".json")
    if not os.path.exists(filename):
        return jsonify({'error': 'No task data found'}), 404

    try:
        with open(filename, "r", encoding="utf-8") as f:
            entries = json.load(f)

        if not entries:
            return jsonify({'status': 'empty', 'message': 'No entries to insert.'}), 200

        connection = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            port=DB_PORT,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )

        inserted = 0
        with connection.cursor() as cursor:
            for entry in entries:
                task_id = entry["task_id"]
                staff_id = entry["staff_id"]
                start_time = entry["start_time"]
                end_time = entry["end_time"]
                note = entry["note"]
                hourly_rate = entry.get("hourly_rate")
                #  Console log:
                print(f" Inserting into DB  task_id: {task_id}, staff_id: {staff_id}, start_time: {start_time}, end_time: {end_time}, note: {note}, hourly_rate: {hourly_rate}")


                print(" INSERTING TO DATABASE:")
                print(f"   Task ID     : {task_id}")
                print(f"   Staff ID    : {staff_id}")
                print(f"   Start Time  : {start_time}")
                print(f"   End Time    : {end_time}")
                print(f"   Note        : {note}")
                print(f"   Hourly Rate : {hourly_rate}")

                #  Safe duplicate check using BINARY
                check_query = """
                    SELECT id FROM tbltaskstimers
                    WHERE task_id = %s AND staff_id = %s AND start_time = %s AND end_time = %s
                    AND BINARY note = BINARY %s
                    LIMIT 1
                """
                cursor.execute(check_query, (task_id, staff_id, start_time, end_time, note))
                if cursor.fetchone():
                    continue  # skip if already inserted

                insert_query = """
                    INSERT INTO tbltaskstimers (task_id, staff_id, start_time, end_time, note, hourly_rate)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                cursor.execute(insert_query, (task_id, staff_id, start_time, end_time, note, hourly_rate))
                print(f" Inserted: Task {task_id} / Staff {staff_id}")
                inserted += 1

            connection.commit()

        return jsonify({'status': 'success', 'inserted': inserted})

    except Exception as e:
        print(" Error during insert:", str(e))
        return jsonify({'error': str(e)}), 500
















@app.route('/submit_all_data_files', methods=['POST'])
def submit_all_data_files():
    from glob import glob
    import os
    import json
    from moduller.veritabani_yoneticisi import VeritabaniYoneticisi

    os.makedirs("logs", exist_ok=True)

    def convert_filename_to_email(filename):
        return filename.replace("_at_", "@").replace(".json", "")

    db = VeritabaniYoneticisi(DB_HOST, DB_USER, DB_PASSWORD, DB_NAME, DB_PORT)
    db.baglanti_olustur()

    folder_path = "data"
    inserted_total = 0
    results = {}

    for filepath in glob(os.path.join(folder_path, "*.json")):
        filename = os.path.basename(filepath)
        email = convert_filename_to_email(filename)
        user_inserted = 0
        submitted_entries = []

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                entries = json.load(f)
        except Exception as e:
            print(f" Error reading {filename}: {e}")
            continue

        # Ensure entries is a list
        if not isinstance(entries, list):
            print(f" Warning: {filename} does not contain a list of entries. Skipping.")
            continue

        for entry in entries:
            # Ensure entry is a dictionary
            if not isinstance(entry, dict):
                print(f" Warning: Invalid entry format in {filename}. Skipping entry: {entry}")
                continue
                
            # Check if required fields exist
            required_fields = ["task_id", "staff_id", "start_time", "end_time", "note"]
            if not all(field in entry for field in required_fields):
                print(f" Warning: Missing required fields in entry from {filename}. Skipping.")
                continue
                
            task_id = entry["task_id"]
            staff_id = entry["staff_id"]
            start_time = entry["start_time"]
            end_time = entry["end_time"]
            note = entry["note"]
            hourly_rate = entry.get("hourly_rate")


            print(" INSERTING TO DATABASE:")
            print(f"   Task ID     : {task_id}")
            print(f"   Staff ID    : {staff_id}")
            print(f"   Start Time  : {start_time}")
            print(f"   End Time    : {end_time}")
            print(f"   Note        : {note}")
            print(f"   Hourly Rate : {hourly_rate}")

            # Check if already exists
            check_query = """
                SELECT id FROM tbltaskstimers
                WHERE task_id = %s AND staff_id = %s AND start_time = %s AND end_time = %s AND note = %s
                LIMIT 1
            """
            exists = db.sorgu_calistir(check_query, (task_id, staff_id, start_time, end_time, note))

            if exists:
                continue

            # Insert
            insert_query = """
                INSERT INTO tbltaskstimers (task_id, staff_id, start_time, end_time, note, hourly_rate)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            db.sorgu_calistir(insert_query, (task_id, staff_id, start_time, end_time, note, hourly_rate))
            user_inserted += 1
            submitted_entries.append(entry)

        #  Save submitted entries into history log (keep original file intact)
        if submitted_entries:
            BASE_DIR = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.abspath(".")
            LOGS_FOLDER = os.path.join(BASE_DIR, "logs")
            os.makedirs(LOGS_FOLDER, exist_ok=True)

            filename_only = os.path.basename(filename)  # Strip full path, just keep the file name
            log_path = os.path.join(LOGS_FOLDER, filename_only.replace(".json", "_history.json"))

            if os.path.exists(log_path):
                with open(log_path, "r", encoding="utf-8") as f:
                    history = json.load(f)
            else:
                history = []

            history.extend(submitted_entries)
            with open(log_path, "w", encoding="utf-8") as f:
                json.dump(history, f, indent=2, ensure_ascii=False)

        results[email] = user_inserted
        inserted_total += user_inserted

    return jsonify({
        "status": "success",
        "inserted_total": inserted_total,
        "inserted_by_user": results,
        "message": f" {inserted_total} entries inserted."
    })
















@app.route('/get_crm_task_id', methods=['POST'])
def get_crm_task_id():
    task_name = request.json.get('task_name')
    # print(f" Searching CRM for task name: {task_name}")  

    headers = {
        'authtoken': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyIjoiZGVsdXhldGltZSIsIm5hbWUiOiJkZWx1eGV0aW1lIiwiQVBJX1RJTUUiOjE3NDUzNDQyNjJ9.kJGo5DksaPwkHwufDvLMGaMmjk5q2F7GhjzwdHtfT_o'
    }

    url = f"https://crm.deluxebilisim.com/api/tasks/search/{task_name}"

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        try:
            data = response.json()
            # print(f" CRM responded with: {data}")
            return jsonify(data)
        except json.JSONDecodeError:
            return jsonify({"error": "Invalid CRM JSON"}), 502
    except Exception as e:
        # print(f" CRM request failed: {e}")
        return jsonify({"error": "CRM error", "details": str(e)}), 500











@app.route('/upload_screenshots', methods=['POST'])
def upload_all_screenshots_to_s3():
    from glob import glob
    from pathlib import Path

    # print(" Triggered: /upload_screenshots route")

    all_uploaded = []
    failed = []

    for root, _, files in os.walk("Screen-Recordings"):
        for file in files:
            if file.endswith(".png"):
                full_path = os.path.join(root, file)
                try:
                    path = Path(full_path)
                    email = path.parents[2].name.replace("_at_", "@")
                    task_name = path.parents[0].name

                    # print(f" Uploading: {full_path}")
                    # print(f" Email: {email}")
                    # print(f" Task Name: {task_name}")

                    result_url = upload_screenshot(full_path)  # now only needs local_path

                    if result_url:
                        all_uploaded.append(result_url)
                    else:
                        failed.append(full_path)
                except Exception as e:
                    # print(f" Upload error for {full_path}: {e}")
                    failed.append(full_path)

    return jsonify({
        "status": "success",
        "uploaded": len(all_uploaded),
        "failed": len(failed),
        "urls": all_uploaded
    })









#  New endpoint to store session START
@app.route('/start_task_session', methods=['POST'])
def start_task_session():
    import pymysql
    data = request.get_json()
    email = data.get('email')
    staff_id = data.get('staff_id')
    task_id = data.get('task_id')
    start_time = data.get('start_time')  # should be ISO 8601 string

    # ✅ Get actual task name from database
    task_name = "Unknown Task"
    try:
        connection = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            port=DB_PORT,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        
        with connection.cursor() as cursor:
            # Fetch task name from database
            task_query = "SELECT name FROM tbltasks WHERE id = %s"
            cursor.execute(task_query, (task_id,))
            result = cursor.fetchone()
            if result:
                task_name = result['name']
                print(f"✅ Found task name: {task_name} for task_id: {task_id}")
            else:
                print(f"⚠️ Task not found for task_id: {task_id}")
                task_name = f"Task_{task_id}"  # Fallback to task_id format
        
        connection.close()
    except Exception as e:
        print(f"❌ Error fetching task name: {e}")
        task_name = f"Task_{task_id}"  # Fallback to task_id format

    # ✅ DEBUG: Create session file so background logger starts
    session_data = {
        "email": email,
        "task": task_name  # Use actual task name instead of Task_ID
    }

    os.makedirs("data", exist_ok=True)  # Ensure folder exists

    with open("data/current_session.json", "w", encoding="utf-8") as f:
        json.dump(session_data, f, indent=2)

    print("✅ current_session.json created:", session_data)
    # ✅ Save session tracking folder & dummy log
    from moduller.tracker import save_raw_program_log
    save_raw_program_log(email=email, task_name=task_name, program_data=[{
        "program": "SessionStart",
        "start": datetime.now().isoformat(),
        "note": "Auto-generated on task start"
    }])



    if not all([email, staff_id, task_id, start_time]):
        return jsonify({"status": "error", "message": "Missing required data"}), 400

    try:
        connection = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            port=DB_PORT,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )

        with connection.cursor() as cursor:
            insert_query = """
                INSERT INTO tbltaskstimers (task_id, staff_id, start_time)
                VALUES (%s, %s, %s)
            """
            cursor.execute(insert_query, (task_id, staff_id, start_time))
            connection.commit()
        
        # ✅ Start system-level idle monitor
        start_idle_monitor(
            flask_server_url="http://127.0.0.1:5000",
            email=email,
            staff_id=staff_id,
            task_id=task_id
        )
        
        # ✅ Start automatic logging when timer starts
        start_logging()
        print("✅ Automatic logging started with timer")

        return jsonify({"status": "success", "message": "Start session inserted into DB"})

    except Exception as e:
        # print(" DB insert error (start):", str(e)) 
        return jsonify({"status": "error", "message": str(e)}), 500





@app.route('/set_idle_flag', methods=['POST'])
def set_idle_flag():
    global is_user_idle
    data = request.get_json()
    is_user_idle = data.get('idle', False)
    return jsonify({"status": "idle flag updated", "idle": is_user_idle})

@app.route('/check_idle_state')
def check_idle_state():
    global is_user_idle
    was_idle = is_user_idle
    is_user_idle = False  # Reset after checking
    return jsonify({"idle": was_idle})







@app.route('/end_task_session', methods=['POST'])
def end_task_session():
    import pymysql
    data = request.get_json()
    email = data.get("email")
    staff_id = data.get("staff_id")
    task_id = data.get("task_id")
    end_time = int(data.get("end_time"))
    note = data.get("note", "").lower()

    # ✅ If idle note detected, minus 180 seconds
    if "idle" in note or "boşta" in note:
        print("⏳ Idle session detected, subtracting 180 seconds from end_time")
        end_time -= 180
    note = data.get("note")

    if not all([email, staff_id, task_id, end_time, note]):
        return jsonify({"error": "Missing required fields"}), 400

    print("✅ END SESSION RECEIVED:")
    print(f"📧 Email: {email}")
    print(f"🆔 Task ID: {task_id}")
    print(f"🧑 Staff ID: {staff_id}")
    print(f"🕐 End Time: {end_time}")
    print(f"📝 Note: {note}")

    try:
        connection = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            port=DB_PORT,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )

        with connection.cursor() as cursor:
            # 👇 UPDATE karein jahan end_time NULL hai
            update_query = """
                UPDATE tbltaskstimers
                SET end_time = %s, note = %s
                WHERE task_id = %s AND staff_id = %s AND end_time IS NULL
                ORDER BY start_time DESC
                LIMIT 1
            """
            cursor.execute(update_query, (end_time, note, task_id, staff_id))
            connection.commit()

        # ✅ Stop automatic logging when timer ends
        stop_logging()
        print("✅ Automatic logging stopped with timer")
        
        # ✅ Clean up session file when timer stops
        try:
            import os
            session_file = "data/current_session.json"
            if os.path.exists(session_file):
                os.remove(session_file)
                print("✅ Session file cleaned up")
        except Exception as session_error:
            print(f"⚠️ Could not clean up session file: {session_error}")

        return jsonify({"status": "success", "message": "End task updated!"})
    except Exception as e:
        print("❌ DB error (end):", str(e))
        return jsonify({"status": "error", "message": str(e)}), 500










@app.route('/api/log-task', methods=['POST'])
def log_task():
    data = request.json
    email = data.get('email')
    task_name = data.get('task_name')
    program_history = data.get('program_history', [])

    if not email or not task_name or not program_history:
        return jsonify({"status": "error", "message": "Missing required fields"}), 400

    try:
        url = upload_program_data_to_s3(email, task_name, program_history)
        if url:
            return jsonify({"status": "success", "uploaded_url": url})
        else:
            return jsonify({"status": "error", "message": "Upload failed"}), 500
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/upload_log_to_s3", methods=["POST"])
def upload_log_to_s3():
    data = request.get_json()
    email = data.get("email")
    task_name = data.get("task_name")

    if not email or not task_name:
        return jsonify({"success": False, "message": "Missing email or task name"})

    try:
        from moduller.tracker import get_program_history_and_save, logs_file

        # ✅ Step 1: Save local log
        file_path = get_program_history_and_save(email, task_name)

        # ✅ Step 2: Read raw log
        with open(file_path, "r", encoding="utf-8") as f:
            raw_json = f.read()

        # ✅ Step 3: Generate AI summary
        from moduller.ai_summarizer import summarize_program_usage
        ai_summary = summarize_program_usage(raw_json)

        # ✅ Step 4: Save summary locally
        summary_file_path = file_path.replace("_program_raw.json", "_summary.txt")
        with open(summary_file_path, "w", encoding="utf-8") as f:
            f.write(ai_summary)

        # ✅ Step 5: Also upload JSON log to S3
        program_history = json.loads(raw_json)
        upload_program_data_to_s3(email, task_name, program_history)

        return jsonify({
            "success": True,
            "message": "Log collected, summarized, and uploaded.",
            "summary": ai_summary,
            "url": summary_file_path  # Local path for now
        })

    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


@app.route('/get_idle_limit', methods=['GET'])
def get_idle_limit():
    try:
        # Default value
        default_seconds = 300

        # Optional config file path
        config_path = os.path.join("config", "admin.json")
        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
            idle_limit = int(config.get("idle_limit_seconds", default_seconds))
        else:
            idle_limit = default_seconds

        return jsonify({"idle_limit_seconds": idle_limit})
    except Exception as e:
        print(f"❌ Failed to get idle time config: {e}")
        return jsonify({"idle_limit_seconds": 300})



@app.route("/en/api/update-log-info", methods=["POST"])
def update_log_info():
    try:
        data = request.get_json()
        print("📥 Received summary data:", data)

        # ✅ Baad mein file ya database mein save bhi kar sakte ho
        return jsonify({"status": "received"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400




# Function to run Flask in a separate thread
def run_flask():
    app.run(debug=True, use_reloader=False, port=5000)

# Start Flask in a separate thread
# flask_thread = threading.Thread(target=run_flask, daemon=True)
# flask_thread.start()







@app.route('/send-test-email')
def send_test_email():
    try:
        msg = Message(
            subject='🧪 Test Email from DDS-FocusPro',
            recipients=['haseebcodejourney@gmail.com'],  # 🔁 Change this to your email for test
            body='Hello! This is a test email from your DDS-FocusPro app.'
        )
        mail.send(msg)
        return jsonify({'status': 'success', 'message': 'Email sent!'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})


@app.route('/submit-feedback', methods=['POST'])
def submit_feedback():
    try:
        data = request.get_json()
        user_email = data.get('email')
        user_name = data.get('username')
        feedback_message = data.get('message')

        if not all([user_email, user_name, feedback_message]):
            return jsonify({'status': 'error', 'message': 'Missing required fields'})

        msg = Message(
            subject=f"📝 Feedback from {user_name}",
            recipients=["feedback@dxdglobal.com"],  # Or your actual support email
            body=f"📧 From: {user_email}\n👤 Name: {user_name}\n\n🗨️ Feedback:\n{feedback_message}"
        )
        mail.send(msg)

        return jsonify({'status': 'success', 'message': 'Feedback sent successfully!'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})








import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

print("[INFO] Starting Flask in background...")

import signal
import atexit

def signal_handler(sig, frame):
    """
    Handle termination signals (like Ctrl+C) gracefully
    """
    print(f"\n🛑 Received signal {sig}. Uploading logs and shutting down gracefully...")
    
    # Stop logging first
    try:
        from moduller.tracker import stop_logging
        stop_logging()
    except Exception as e:
        print(f"❌ Error stopping logging: {e}")
    
    # Upload any remaining logs
    try:
        from moduller.tracker import upload_logs_on_app_close
        upload_logs_on_app_close()
    except Exception as e:
        print(f"❌ Error uploading logs on shutdown: {e}")
    
    print("✅ Graceful shutdown complete.")
    exit(0)

# Register signal handlers for graceful shutdown
signal.signal(signal.SIGINT, signal_handler)   # Ctrl+C
signal.signal(signal.SIGTERM, signal_handler)  # Termination signal

# Register exit handler
atexit.register(lambda: upload_logs_on_app_close())

if __name__ == "__main__":
    # Arka planda loglama başlat
    threading.Thread(target=auto_log_every_minute, daemon=True).start()
    
    try:
        app.run(debug=True, port=5000)
    except KeyboardInterrupt:
        print("\n🛑 Application stopped by user")
        upload_logs_on_app_close()
    except Exception as e:
        print(f"❌ Application error: {e}")
        upload_logs_on_app_close()
        raise

@app.route('/upload_all_tracker_logs', methods=['POST'])
def upload_all_tracker_logs_endpoint():
    """
    Manual endpoint to upload all tracker logs to S3
    """
    try:
        from moduller.tracker import upload_tracker_logs
        
        uploaded_files = upload_tracker_logs()
        
        if uploaded_files:
            return jsonify({
                "status": "success",
                "message": f"Successfully uploaded {len(uploaded_files)} tracker log files to S3",
                "uploaded_files": uploaded_files
            })
        else:
            return jsonify({
                "status": "info",
                "message": "No tracker log files found to upload"
            })
            
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Error uploading tracker logs: {str(e)}"
        }), 500


