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



from flask import Flask, render_template, request, jsonify
import requests 
import os, sys
import logging  # ✅ MOVE THIS HERE
from dotenv import load_dotenv
from moduller.veritabani_yoneticisi import VeritabaniYoneticisi
from moduller.ai_query_handler import execute_sql_from_prompt
from moduller.ai_filtered_project import get_ai_filtered_projects
import json
from datetime import datetime
from moduller.s3_uploader import upload_screenshot
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
from moduller.tracker import TaskLogger
# from moduller.tracker import start_browser_tracking
# from moduller.tracker import stop_browser_tracking
# from moduller.tracker import collect_all_history
import logging





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
# load_dotenv()
PERFEX_API_URL = "https://crm.deluxebilisim.com/api/timesheets"
# AUTH_TOKEN = os.getenv("AUTH_TOKEN")
# DB_HOST = os.getenv("DB_HOST")
# DB_USER = os.getenv("DB_USER")
# DB_PASSWORD = os.getenv("DB_PASSWORD")
# DB_NAME = os.getenv("DB_NAME")
# DB_PORT = int(os.getenv("DB_PORT", 3306))
# Hardcoded database config
AUTH_TOKEN="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyIjoiZGVsdXhldGltZSIsIm5hbWUiOiJkZWx1eGV0aW1lIiwiQVBJX1RJTUUiOjE3NDUzNDQyNjJ9.kJGo5DksaPwkHwufDvLMGaMmjk5q2F7GhjzwdHtfT_o"

DB_HOST = "92.113.22.65"  # ✅ WORKING
DB_USER = "u906714182_sqlrrefdvdv"
DB_PASSWORD = "3@6*t:lU"
DB_NAME = "u906714182_sqlrrefdvdv"
DB_PORT = 3306



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


















def start_screen_recording(folder_path, email, task_name):


    def record():
        global recording_active

        print(f" Starting screenshot capture to: {folder_path}")
        with mss.mss() as sct:
            monitor = sct.monitors[1]  # full screen

            while recording_active:
                try:
                    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                    filename = os.path.join(folder_path, f"{timestamp}.webp")
                    sct_img = sct.grab(monitor)

                    # Convert mss image to PIL image and save as webp
                    img = Image.frombytes('RGB', sct_img.size, sct_img.rgb)
                    img.save(filename, "WEBP")

                    logging.info(f"📸 Screenshot saved: {filename}")
                    upload_screenshot(filename, email, task_name)
                    time.sleep(5)

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





@app.route('/get_tasks/<project_id>', methods=['GET'])
def get_tasks(project_id):
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

    query = f"SELECT * FROM tbltasks WHERE rel_type = 'project' AND rel_id = {project_id}"
    tasks = veritabani.sorgu_calistir(query)

    if tasks:
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

        print(f" Starting screenshot capture to: {folder_path}")
        with mss.mss() as sct:
            monitor = sct.monitors[1]  # full screen

            while recording_active:
                try:
                    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                    filename = os.path.join(folder_path, f"{timestamp}.webp")
                    sct_img = sct.grab(monitor)
                    mss.tools.to_png(sct_img.rgb, sct_img.size, output=filename)
                    print(f" Screenshot saved: {filename}")

                    #  Auto-upload right after saving
                    from moduller.s3_uploader import upload_screenshot
                    upload_screenshot(filename, email, task_name)

                    time.sleep(5)  # every 5 seconds
                except Exception as e:
                    print(f" Screenshot error: {e}")
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

    req = request.get_json()
    email = req.get('email')
    if not email:
        return jsonify({'error': 'Missing email'}), 400



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

        for entry in entries:
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



    # print(" Received session start data:") 
    # print(f" - Email  Start zzzz    : {email}") 
    # print(f" - Staff ID Start zzzz : {staff_id}") 
    # print(f" - Task ID  Start zzzz  : {task_id}") 
    # print(f" - Start Time Start zzzz: {start_time}") 

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

        return jsonify({"status": "success", "message": "Start session inserted into DB"})

    except Exception as e:
        # print(" DB insert error (start):", str(e)) 
        return jsonify({"status": "error", "message": str(e)}), 500












@app.route('/end_task_session', methods=['POST'])
def end_task_session():
    import pymysql
    data = request.get_json()
    email = data.get("email")
    staff_id = data.get("staff_id")
    task_id = data.get("task_id")
    end_time = data.get("end_time")
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

        return jsonify({"status": "success", "message": "End task updated!"})
    except Exception as e:
        print("❌ DB error (end):", str(e))
        return jsonify({"status": "error", "message": str(e)}), 500








@app.route('/api/log-task', methods=['POST'])
def log_task():
    data = request.json
    
    logger = TaskLogger(
        email=data['email'],
        bucket=data['bucket'],
        region=data.get('region')
    )
    
    result = logger.upload_task_log(
        task_name=data['task_name'],
        start_time=datetime.fromisoformat(data['start_time']),
        end_time=datetime.fromisoformat(data['end_time']),
        program_history=[
            {
                'program': item['program'],
                'start': datetime.fromisoformat(item['start']),
                'end': datetime.fromisoformat(item['end'])
            }
            for item in data['program_history']
        ]
    )
    
    return jsonify(result)








# Function to run Flask in a separate thread
def run_flask():
    app.run(debug=False, use_reloader=False, port=5000)

# Start Flask in a separate thread
# flask_thread = threading.Thread(target=run_flask, daemon=True)
# flask_thread.start()


















import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

print("[INFO] Starting Flask in background...")





if __name__ == "__main__":
    app.run(debug=False, port=5000)


