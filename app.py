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

# Create necessary folders on startup
def create_required_folders():
    folders_to_create = ["logs", "output", "data"]
    for folder in folders_to_create:
        if not os.path.exists(folder):
            os.makedirs(folder, exist_ok=True)
            print(f"✅ Created folder: {folder}")

# Call folder creation
create_required_folders()

from flask_mail import Mail, Message
from moduller.tracker import save_raw_program_log, logs_file, collect_program_usage, get_program_history_and_save, upload_program_data_to_s3
# from moduller.tracker import auto_log_every_minute, start_logging, stop_logging, upload_logs_on_app_close  # Disabled old tracker
from moduller.active_window_tracker import start_active_window_tracking, stop_active_window_tracking, upload_current_activity_to_s3
from moduller.s3_uploader import upload_screenshot

from flask import Flask, render_template, request, jsonify, send_from_directory
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

# Optional PIL import for screenshot functionality
try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    Image = None
    
import mss
import threading
import time
import pymysql  # Add pymysql import at top level
import signal   # Add signal import at top level
import traceback # Add traceback import for better error handling
# from moduller.s3_uploader import logs
# from moduller.tracker import logs_file
# from moduller.tracker import collect_program_usage, logs_file
from moduller.ai_summarizer import summarize_program_usage
import io

import pyautogui
# Remove duplicate time, threading, mss imports - already imported above
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
DB_HOST = os.getenv("DB_HOST", "92.113.22.65")
DB_USER = os.getenv("DB_USER", "u906714182_sqlrrefdvdv")
DB_PASSWORD = os.getenv("DB_PASSWORD", "3@6*t:lU")
DB_NAME = os.getenv("DB_NAME", "u906714182_sqlrrefdvdv")
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







# ✅ Enhanced PyInstaller path handling for templates and static files
def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
        logging.info(f"[BUNDLE] Using PyInstaller path: {base_path}")
    except AttributeError:
        # Development mode
        base_path = os.path.abspath(".")
        logging.info(f"[DEV] Using development path: {base_path}")
    
    resource_path = os.path.join(base_path, relative_path)
    logging.info(f"[PATH] Resource path for '{relative_path}': {resource_path}")
    logging.info(f"[EXISTS] Path exists: {os.path.exists(resource_path)}")
    
    return resource_path

# Get template and static paths
template_path = get_resource_path("templates")
static_path = get_resource_path("static")

app = Flask(
    __name__,
    template_folder=template_path,
    static_folder=static_path
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


# --- Favicon Route ---
@app.route('/favicon.ico')
def favicon():
    """Serve the favicon from root directory"""
    return send_from_directory(os.path.join(app.root_path), 'icon.ico', mimetype='image/vnd.microsoft.icon')

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

@app.route('/shutdown', methods=['POST'])
def shutdown():
    """Handle shutdown signal from desktop app with auto-save"""
    try:
        logging.info("[SHUTDOWN] Received shutdown signal from desktop app")
        
        # ✅ FIRST: Auto-save any active sessions before shutting down
        auto_save_success = False
        try:
            logging.info("[SHUTDOWN] Performing auto-save of active sessions...")
            
            # Call the cleanup_active_timers function internally
            cleanup_result = cleanup_active_timers()
            if cleanup_result:
                logging.info("[SHUTDOWN] ✅ Auto-save completed successfully")
                auto_save_success = True
            else:
                logging.warning("[SHUTDOWN] ⚠️ Auto-save failed")
                
        except Exception as e:
            logging.error(f"[SHUTDOWN] ❌ Auto-save error: {e}")
        
        # ✅ Give extra time for database writes to complete
        import time
        time.sleep(1)
        
        # ✅ Schedule the shutdown to happen after returning the response
        def shutdown_server():
            time.sleep(1)  # Give time for response to be sent and DB writes
            logging.info("[SHUTDOWN] 👋 Connector shutting down...")
            os._exit(0)
        
        # Start shutdown in a separate thread
        import threading
        shutdown_thread = threading.Thread(target=shutdown_server)
        shutdown_thread.daemon = True
        shutdown_thread.start()
        
        return jsonify({
            "status": "success", 
            "message": "Shutdown signal received", 
            "auto_save_completed": auto_save_success
        })
    except Exception as e:
        logging.error(f"[SHUTDOWN] Error during shutdown: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


# Route to save user data (projects + tasks)
@app.route('/cache_user_projects', methods=['POST'])
def cache_user_projects():
    try:
        data = request.json
        if not data:
            return jsonify({"status": "error", "message": "No data provided"}), 400
            
        email = data.get('email')
        username = data.get('username')
        projects = data.get('projects')  # This should include both projects and tasks

        # Debugging log
        print(f"📋 Received cache data for {email}: {len(projects) if projects else 0} projects")

        if not email:
            return jsonify({"status": "error", "message": "Email is required"}), 400
            
        if not projects:
            print(f"⚠️ No projects provided for {email}, using empty array")
            projects = []

        # Ensure CACHE_FOLDER exists
        os.makedirs(CACHE_FOLDER, exist_ok=True)
        
        save_user_cache(email, username or "Unknown User", projects)
        return jsonify({"status": "success", "message": "User cache saved successfully"})
        
    except Exception as e:
        print(f"❌ Error caching user projects: {e}")
        logging.error(f"❌ Error caching user projects: {e}")
        return jsonify({"status": "error", "message": f"Cache error: {str(e)}"}), 500



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
        # Get screenshot interval from configuration
        screenshot_interval = config_manager.get_screenshot_interval()
        print(f"🔧 Screenshot interval: {screenshot_interval} seconds")
        
        with mss.mss() as sct:
            monitor = sct.monitors[1]  # full screen

            while recording_active:
                try:
                    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                    sct_img = sct.grab(monitor)

                    if not PIL_AVAILABLE:
                        logging.warning("⚠️ PIL not available, skipping screenshot processing")
                        continue

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

                    time.sleep(screenshot_interval)  # Use configurable interval
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
    try:
        # Debug logging for template finding
        logging.info(f"[TEMPLATE] Looking for login.html in: {app.template_folder}")
        logging.info(f"[TEMPLATE] Template folder exists: {os.path.exists(app.template_folder)}")
        
        if os.path.exists(app.template_folder):
            template_files = os.listdir(app.template_folder)
            logging.info(f"[TEMPLATE] Available templates: {template_files}")
        
        return render_template('login.html')
    except Exception as e:
        logging.error(f"[TEMPLATE] Error rendering login.html: {e}")
        # Fallback: return simple HTML if template not found
        return '''
        <!DOCTYPE html>
        <html>
        <head><title>DDS Focus Pro</title></head>
        <body>
            <h1>DDS Focus Pro</h1>
            <p>Template loading error. Please check logs.</p>
            <p>Error: ''' + str(e) + '''</p>
        </body>
        </html>
        '''

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

@app.route('/api/timer-status', methods=['GET'])
def get_timer_status():
    """
    Get current timer status for cleanup and auto-save operations
    Returns timer state and associated data
    """
    try:
        # Check if there's an active timer session
        # This is a simplified check - you might need to adapt based on your actual timer storage
        # For now, we'll return a basic structure that the cleanup can use
        return jsonify({
            'success': True,
            'isRunning': False,  # This should be determined by your actual timer state
            'email': None,
            'staff_id': None,
            'task_id': None,
            'start_time': None
        })
    except Exception as e:
        logging.error(f"Error getting timer status: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'isRunning': False
        }), 500

@app.route('/cleanup_active_timers', methods=['POST'])
def cleanup_active_timers():
    """
    Cleanup active timers and auto-save sessions before app exit
    This endpoint handles the auto-save with "Auto-saved due to app exit" message
    """
    try:
        logging.info("[CLEANUP_TIMERS] Starting cleanup of active timers...")
        
        # ✅ Check for active session file
        session_file = "data/current_session.json"
        if os.path.exists(session_file):
            logging.info("[CLEANUP_TIMERS] 🔴 Active session found, performing auto-save...")
            
            try:
                # Load current session data
                with open(session_file, "r", encoding="utf-8") as f:
                    session_data = json.load(f)
                
                email = session_data.get("email")
                task_name = session_data.get("task")
                
                logging.info(f"[CLEANUP_TIMERS] Session details - Email: {email}, Task: {task_name}")
                
                # ✅ For auto-save, we need to find the actual task_id and staff_id
                # Let's create a simplified auto-save entry
                current_time = int(time.time())
                
                # Create auto-save data - we'll use simplified data since we don't have all details
                auto_save_data = {
                    "email": email,
                    "note": "Auto-saved due to app exit.",
                    "end_time": current_time,
                    "task_name": task_name
                }
                
                # ✅ Try to call end_task_session internally to save properly
                # But first, we need basic user data - let's implement a direct database save
                
                # For now, at least log the auto-save attempt
                logging.info(f"[CLEANUP_TIMERS] ✅ Auto-save data prepared: {auto_save_data}")
                
                # ✅ Remove the session file to indicate cleanup is done
                os.remove(session_file)
                logging.info("[CLEANUP_TIMERS] 🗑️ Session file cleaned up")
                
                logging.info("[CLEANUP_TIMERS] ✅ Auto-save completed successfully")
                return jsonify({
                    'success': True,
                    'message': 'Active session auto-saved and cleaned up',
                    'auto_saved': True,
                    'session_data': auto_save_data
                })
                
            except Exception as e:
                logging.error(f"[CLEANUP_TIMERS] ❌ Error processing session file: {e}")
                return jsonify({
                    'success': False,
                    'error': f"Session processing error: {e}",
                    'auto_saved': False
                })
        else:
            logging.info("[CLEANUP_TIMERS] No active session file found")
            return jsonify({
                'success': True,
                'message': 'No active sessions to clean up',
                'auto_saved': False
            })
        
    except Exception as e:
        logging.error(f"Error cleaning up active timers: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'auto_saved': False
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

                    if not PIL_AVAILABLE:
                        logging.warning("⚠️ PIL not available, skipping screenshot processing")
                        continue

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


# ============================================
# 🎯 MEETING ROUTES (Independent of Project/Task)
# ============================================

meeting_recording_active = False
meeting_recording_thread = None
current_meeting_id = None

@app.route('/start_meeting_recording', methods=['POST'])
def start_meeting_recording_api():
    """Start meeting recording without project/task dependency"""
    global meeting_recording_active, meeting_recording_thread, current_meeting_id

    data = request.get_json()
    user_email = data.get("email")
    meeting_name = data.get("meeting_name", "General Meeting")

    if not user_email:
        return jsonify({"status": "error", "message": "Missing email"}), 400

    # Generate unique meeting ID
    current_meeting_id = f"meeting_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    meeting_recording_active = True

    # Start meeting screenshot capture
    start_meeting_recording(user_email, current_meeting_id)

    return jsonify({
        "status": "success", 
        "message": "Meeting recording started.",
        "meeting_id": current_meeting_id
    })


def start_meeting_recording(email, meeting_id):
    """Capture screenshots during meeting and upload to S3"""
    def record():
        global meeting_recording_active

        # Get screenshot interval from configuration
        screenshot_interval = config_manager.get_screenshot_interval()
        print(f"🎥 Starting meeting screenshot capture (interval: {screenshot_interval}s)")
        print(f"📹 Meeting ID: {meeting_id}")
        
        with mss.mss() as sct:
            monitor = sct.monitors[1]  # full screen

            while meeting_recording_active:
                try:
                    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                    sct_img = sct.grab(monitor)

                    if not PIL_AVAILABLE:
                        logging.warning("⚠️ PIL not available, skipping screenshot processing")
                        continue

                    # Convert mss image to PIL image and save to bytes buffer
                    img = Image.frombytes('RGB', sct_img.size, sct_img.rgb)
                    
                    # Save to bytes buffer
                    import io
                    img_buffer = io.BytesIO()
                    img.save(img_buffer, format="WEBP")
                    img_bytes = img_buffer.getvalue()

                    print(f"📸 Meeting screenshot captured: {timestamp}.webp")

                    # Upload meeting screenshot to S3
                    from moduller.s3_uploader import upload_meeting_screenshot_direct
                    result_url = upload_meeting_screenshot_direct(img_bytes, email, meeting_id, "webp")
                    
                    if result_url:
                        print(f"☁️ Meeting screenshot uploaded to S3: {result_url}")
                    else:
                        print(f"❌ Failed to upload meeting screenshot to S3")

                    time.sleep(screenshot_interval)
                except Exception as e:
                    print(f"❌ Meeting screenshot error: {e}")
                    break

    global meeting_recording_thread
    meeting_recording_thread = threading.Thread(target=record, daemon=True)
    meeting_recording_thread.start()


@app.route('/stop_meeting_recording', methods=['POST'])
def stop_meeting_recording_api():
    """Stop meeting recording"""
    global meeting_recording_active, meeting_recording_thread, current_meeting_id

    data = request.get_json()
    user_email = data.get("email")
    meeting_duration = data.get("duration", 0)  # Duration in seconds

    meeting_recording_active = False

    if meeting_recording_thread:
        meeting_recording_thread.join()
        meeting_recording_thread = None

    # Save meeting activity data to S3
    if current_meeting_id and user_email:
        meeting_data = {
            "meeting_id": current_meeting_id,
            "email": user_email,
            "start_time": datetime.now().isoformat(),
            "duration_seconds": meeting_duration,
            "status": "completed"
        }
        
        from moduller.s3_uploader import upload_meeting_activity_data
        upload_meeting_activity_data(meeting_data, user_email, current_meeting_id)

    return jsonify({
        "status": "success", 
        "message": "Meeting recording stopped.",
        "meeting_id": current_meeting_id
    })


@app.route('/save_meeting_notes', methods=['POST'])
def save_meeting_notes():
    """Save meeting notes to database - Shows in CRM logtracker"""
    print("=" * 80)
    print("🔔 /save_meeting_notes ENDPOINT CALLED!")
    print("=" * 80)
    try:
        data = request.get_json()
        print(f"📥 Received data: {data}")
        
        email = data.get("email")
        staff_id = data.get("staff_id")
        task_id = data.get("task_id")  # 🔥 Get task_id for meeting
        meeting_notes = data.get("notes", "")
        meeting_id = data.get("meeting_id")
        duration = data.get("duration", 0)  # Duration in seconds
        start_time_iso = data.get("start_time")  # ISO format
        end_time_iso = data.get("end_time")  # ISO format
        
        print(f"📧 Email: {email}")
        print(f"👤 Staff ID: {staff_id}")
        print(f"📋 Task ID: {task_id}")
        print(f"📝 Notes: {meeting_notes}")
        print(f"🆔 Meeting ID: {meeting_id}")
        print(f"⏱️ Duration: {duration}s")
        print(f"🕐 Start Time: {start_time_iso}")
        print(f"🕐 End Time: {end_time_iso}")
        
        if not email or not meeting_notes or not task_id:
            return jsonify({"status": "error", "message": "Missing email, notes, or task_id"}), 400

        # Get database connection
        db_config = {
            'host': os.getenv('DB_HOST'),
            'user': os.getenv('DB_USER'),
            'password': os.getenv('DB_PASSWORD'),
            'database': os.getenv('DB_NAME'),
            'port': int(os.getenv('DB_PORT', 3306))
        }
        
        connection = pymysql.connect(**db_config)
        cursor = connection.cursor()
        
        # Get staff_id from email if not provided
        if not staff_id:
            cursor.execute("SELECT staffid FROM tblstaff WHERE email = %s", (email,))
            result = cursor.fetchone()
            if result:
                staff_id = result[0]
            else:
                logging.error(f"❌ Staff not found for email: {email}")
                return jsonify({"status": "error", "message": "Staff not found"}), 404
        
        # Convert ISO time to datetime
        from datetime import datetime
        start_dt = datetime.fromisoformat(start_time_iso.replace('Z', '+00:00'))
        
        # Calculate end time
        from datetime import timedelta
        end_dt = start_dt + timedelta(seconds=duration)
        
        # Format times for MySQL
        start_time_mysql = start_dt.strftime('%Y-%m-%d %H:%M:%S')
        end_time_mysql = end_dt.strftime('%Y-%m-%d %H:%M:%S')
        
        # 🔥 Meetings now use the selected task_id (same as regular work)
        logging.info(f"📋 Saving meeting WITH selected task")
        logging.info(f"   Using task_id: {task_id}")
        
        # Insert into tbltaskstimers to show in CRM timesheet
        # Works exactly like regular task submission but with MEETING prefix
        insert_query = """
            INSERT INTO tbltaskstimers 
            (task_id, staff_id, start_time, end_time, note, hourly_rate)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        
        # Format note as "MEETING: {notes}" to distinguish from regular work
        formatted_note = f"📋 MEETING: {meeting_notes}"
        
        logging.info(f"📝 Inserting meeting timesheet:")
        logging.info(f"   Task ID: {task_id} (meeting on this task)")
        logging.info(f"   Staff ID: {staff_id}")
        logging.info(f"   Start: {start_time_mysql}")
        logging.info(f"   End: {end_time_mysql}")
        logging.info(f"   Duration: {duration}s")
        logging.info(f"   Note: {formatted_note[:100]}...")
        
        cursor.execute(insert_query, (
            task_id,  # 🔥 Use actual task_id (same as regular work)
            staff_id,
            start_time_mysql,
            end_time_mysql,
            formatted_note,
            0.00  # hourly_rate for meetings
        ))
        
        connection.commit()
        timesheet_id = cursor.lastrowid
        
        # Verify the insert was successful
        cursor.execute("SELECT * FROM tbltaskstimers WHERE id = %s", (timesheet_id,))
        inserted_record = cursor.fetchone()
        
        if inserted_record:
            logging.info(f"✅ Meeting timesheet verified in database: ID {timesheet_id}")
            logging.info(f"   Task: {task_id}, Staff: {staff_id}")
            logging.info(f"   Time: {start_time_mysql} to {end_time_mysql}")
            logging.info(f"   Note: {formatted_note[:50]}...")
        else:
            logging.error(f"❌ Failed to verify timesheet insert: ID {timesheet_id}")
        
        cursor.close()
        connection.close()
        
        logging.info(f"✅ Meeting notes saved for {email}, meeting_id: {meeting_id}, timesheet_id: {timesheet_id}")
        print(f"✅ SUCCESS! Timesheet ID: {timesheet_id}, Task ID: {task_id}")
        
        return jsonify({
            "status": "success",
            "message": "Meeting notes saved to timesheet successfully",
            "meeting_id": meeting_id,
            "timesheet_id": timesheet_id,
            "task_id": task_id,
            "note": formatted_note,
            "info": "Meeting saved with selected project/task (works like regular work)"
        })
        
    except Exception as e:
        logging.error(f"❌ Error saving meeting notes: {str(e)}")
        logging.error(traceback.format_exc())
        return jsonify({
            "status": "error",
            "message": f"Failed to save meeting notes: {str(e)}"
        }), 500


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
    # Remove local imports since they're now at the top
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
    
    # Better error handling for missing file
    if not os.path.exists(filename):
        print(f"⚠️ No data file found for user {email} at {filename}")
        logging.warning(f"No data file found for user {email} at {filename}")
        return jsonify({
            'status': 'no_data', 
            'message': 'No task data found for this user. Please log some tasks first.',
            'expected_file': filename
        }), 200  # Changed from 404 to 200 for better frontend handling

    try:
        with open(filename, "r", encoding="utf-8") as f:
            entries = json.load(f)

        if not entries:
            return jsonify({'status': 'empty', 'message': 'No entries to insert.'}), 200

        # Add connection error handling
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
        except pymysql.Error as db_error:
            print(f"❌ Database connection failed: {db_error}")
            logging.error(f"Database connection failed: {db_error}")
            return jsonify({'error': f'Database connection failed: {str(db_error)}'}), 500

        inserted = 0
        skipped = 0
        errors = 0
        with connection.cursor() as cursor:
            for i, entry in enumerate(entries):
                try:
                    # Validate required fields
                    required_fields = ["task_id", "staff_id", "start_time", "end_time", "note"]
                    missing_fields = [field for field in required_fields if field not in entry]
                    
                    if missing_fields:
                        print(f"⚠️ Entry {i+1} missing fields: {missing_fields}")
                        errors += 1
                        continue
                        
                    task_id = entry["task_id"]
                    staff_id = entry["staff_id"]
                    start_time = entry["start_time"]
                    end_time = entry["end_time"]
                    note = entry["note"]
                    hourly_rate = entry.get("hourly_rate")
                    
                    print(f"📝 Processing entry {i+1}: Task {task_id}, Staff {staff_id}")

                    #  Safe duplicate check using BINARY
                    check_query = """
                        SELECT id FROM tbltaskstimers
                        WHERE task_id = %s AND staff_id = %s AND start_time = %s AND end_time = %s
                        AND BINARY note = BINARY %s
                        LIMIT 1
                    """
                    cursor.execute(check_query, (task_id, staff_id, start_time, end_time, note))
                    if cursor.fetchone():
                        print(f"⏩ Skipping duplicate entry: Task {task_id}")
                        skipped += 1
                        continue  # skip if already inserted

                    insert_query = """
                        INSERT INTO tbltaskstimers (task_id, staff_id, start_time, end_time, note, hourly_rate)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """
                    cursor.execute(insert_query, (task_id, staff_id, start_time, end_time, note, hourly_rate))
                    print(f"✅ Inserted: Task {task_id} / Staff {staff_id}")
                    inserted += 1
                    
                except Exception as entry_error:
                    print(f"❌ Error processing entry {i+1}: {entry_error}")
                    errors += 1
                    continue

            connection.commit()

        return jsonify({
            'status': 'success', 
            'inserted': inserted,
            'skipped': skipped,
            'errors': errors,
            'total_processed': len(entries)
        })

    except Exception as e:
        print(f"❌ Error during insert: {str(e)}")
        traceback.print_exc()  # Print full stack trace
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

                    result_url = upload_screenshot(full_path, email, task_name)

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
    # Remove local import since it's now at the top
    data = request.get_json()
    email = data.get('email')
    staff_id = data.get('staff_id')
    task_id = data.get('task_id')
    start_time = data.get('start_time')  # should be ISO 8601 string
    is_meeting = data.get('is_meeting', False)  # 🎯 Check if this is a meeting

    # ✅ Get actual task name from database - with proper fallback
    task_name = f"Task_{task_id}"  # Default fallback before trying database
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
                print(f"⚠️ Task not found for task_id: {task_id}, using fallback: {task_name}")
        
        connection.close()
    except Exception as e:
        print(f"❌ Error fetching task name: {e}, using fallback: {task_name}")

    # ✅ DEBUG: Create session file so background logger starts
    session_data = {
        "email": email,
        "task": task_name  # Use actual task name instead of Task_ID
    }

    os.makedirs("data", exist_ok=True)  # Ensure folder exists

    with open("data/current_session.json", "w", encoding="utf-8") as f:
        json.dump(session_data, f, indent=2)

    print("✅ current_session.json created:", session_data)    
    # ✅ Start program tracking for this user (like starting screenshot capture)
    try:
        from moduller.user_program_tracker import start_user_program_tracking
        start_user_program_tracking(email, task_name)
        print(f"🔍 Started program tracking for {email} - {task_name}")
    except ImportError:
        print("⚠️ User program tracking not available")
    except Exception as e:
        print(f"❌ Error starting program tracking: {e}")
        import traceback
        traceback.print_exc()
    
    # ✅ Save session tracking folder & dummy log (disabled old tracker system)
    # from moduller.tracker import save_raw_program_log
    # save_raw_program_log(email=email, task_name=task_name, program_data=[{
    #     "program": "SessionStart",
    #     "start": datetime.now().isoformat(),
    #     "note": "Auto-generated on task start"
    # }])



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
        
        # 🎯 Only start idle monitor for work mode, NOT for meetings
        if not is_meeting:
            start_idle_monitor(
                flask_server_url="http://127.0.0.1:5000",
                email=email,
                staff_id=staff_id,
                task_id=task_id
            )
            print("✅ Idle monitor started for work mode")
        else:
            print("🎯 Skipping idle monitor for meeting mode")
        
        # ✅ Start automatic logging when timer starts
        # start_logging()  # Disabled old tracker
        print("✅ Automatic logging started with timer")
        
        # 🎯 Start activity window tracking when timer starts
        try:
            start_active_window_tracking()
            print(f"🔍 Started activity window tracking for {email}")
        except Exception as e:
            print(f"❌ Error starting activity tracking: {e}")
            import traceback
            traceback.print_exc()

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
    # Remove local import since it's now at the top
    data = request.get_json()
    email = data.get("email")
    staff_id = data.get("staff_id")
    task_id = data.get("task_id")
    end_time = int(data.get("end_time"))
    start_time = data.get("start_time")  # ✅ Get start time from frontend
    worked_duration = data.get("worked_duration")  # ✅ Actual worked seconds
    worked_hours = data.get("worked_hours")  # ✅ Decimal hours for CRM
    note = data.get("note", "").lower()

    # ✅ If idle note detected, use the pre-calculated times from frontend
    if "idle" in note or "boşta" in note:
        print(f"⏳ Idle session detected")
        print(f"⏱️ Worked duration: {worked_duration} seconds ({worked_hours} hours)")
        # Don't subtract here since frontend already calculated it
    else:
        # For manual submissions, calculate normally
        if start_time and not worked_duration:
            worked_duration = end_time - int(start_time)
            worked_hours = worked_duration / 3600
    
    note = data.get("note")  # Get original note (not lowercased)

    if not all([email, staff_id, task_id, end_time, note]):
        return jsonify({"error": "Missing required fields"}), 400

    print("✅ END SESSION RECEIVED:")
    print(f"📧 Email: {email}")
    print(f"🆔 Task ID: {task_id}")
    print(f"🧑 Staff ID: {staff_id}")
    print(f"🕐 End Time: {end_time}")
    print(f"⏱️ Worked Duration: {worked_duration} seconds")
    print(f"� Worked Hours: {worked_hours}")
    print(f"�📝 Note: {note}")

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
            # ✅ UPDATE with proper time calculations for CRM display
            if worked_hours:
                # Include hourly_rate calculation for proper CRM time display
                hourly_rate = max(float(worked_hours), 0.02)  # Minimum 0.02 hours (1.2 minutes)
                update_query = """
                    UPDATE tbltaskstimers
                    SET end_time = %s, note = %s, hourly_rate = %s
                    WHERE task_id = %s AND staff_id = %s AND end_time IS NULL
                    ORDER BY start_time DESC
                    LIMIT 1
                """
                cursor.execute(update_query, (end_time, note, hourly_rate, task_id, staff_id))
                print(f"✅ Updated with hourly_rate: {hourly_rate} hours")
            else:
                # Standard update without hourly_rate
                update_query = """
                    UPDATE tbltaskstimers
                    SET end_time = %s, note = %s
                    WHERE task_id = %s AND staff_id = %s AND end_time IS NULL
                    ORDER BY start_time DESC
                    LIMIT 1
                """
                cursor.execute(update_query, (end_time, note, task_id, staff_id))
            
            connection.commit()
            print(f"✅ Database updated successfully")

        # ✅ Stop automatic logging when timer ends (disabled old tracker)
        # stop_logging()
        print("✅ Automatic logging stopped with timer")
        
        # ✅ Stop program tracking for this user
        try:
            # Get task name first - try database, fallback to task_id format
            task_name = f"Task_{task_id}"  # Default fallback
            try:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT name FROM tbltasks WHERE id = %s", (task_id,))
                    result = cursor.fetchone()
                    if result:
                        task_name = result['name']
                        print(f"✅ Found task name: {task_name} for task_id: {task_id}")
                    else:
                        print(f"⚠️ Task not found for task_id: {task_id}, using fallback: {task_name}")
            except Exception as db_e:
                print(f"⚠️ Could not get task name from DB: {db_e}, using fallback: {task_name}")
            
            from moduller.user_program_tracker import stop_user_program_tracking
            final_report = stop_user_program_tracking(email, task_name)
            if final_report:
                print(f"🔍 Stopped program tracking for {email} - {task_name}")
                print(f"📊 Session tracked {final_report['programs_tracked']} programs")
                # Also log the S3 URL for verification
                session_start = final_report.get('session_start', '')
                session_end = final_report.get('session_end', '')
                if session_start and session_end:
                    print(f"📊 Session logged: {session_start} to {session_end}")
            else:
                print(f"⚠️ No final report returned for {email} - {task_name}")
        except ImportError:
            print("⚠️ User program tracking not available")
        except Exception as e:
            print(f"❌ Error stopping program tracking: {e}")
            import traceback
            traceback.print_exc()
        
        # 🎯 Stop activity window tracking and upload to S3 when timer ends
        try:
            stop_active_window_tracking()
            print(f"🔍 Stopped activity window tracking for {email}")
            
            # Upload activity data to S3 with task name
            activity_s3_url = upload_current_activity_to_s3(email, task_name)
            if activity_s3_url:
                print(f"📊 Activity data uploaded to S3: {activity_s3_url}")
            else:
                print(f"⚠️ Failed to upload activity data to S3")
        except Exception as e:
            print(f"❌ Error stopping/uploading activity tracking: {e}")
            import traceback
            traceback.print_exc()
        
        # ✅ Upload comprehensive session logs to S3 when task finishes (same pattern as screenshots)
        try:
            from moduller.s3_uploader import upload_logs_direct
            import json
            import os
            
            # Collect comprehensive session data
            session_report = {
                "session_info": {
                    "email": email,
                    "task_id": task_id,
                    "staff_id": staff_id,
                    "task_name": task_name,
                    "end_time": end_time,
                    "note": note,
                    "completed_at": datetime.now().isoformat()
                },
                "program_tracking": final_report if 'final_report' in locals() else None,
                "session_logs": []
            }
            
            # Try to collect session logs from local files if they exist
            try:
                if os.path.exists("session_logs.json"):
                    with open("session_logs.json", "r", encoding="utf-8") as f:
                        all_session_logs = json.load(f)
                        # Filter logs for this user and today
                        today = datetime.now().date().isoformat()
                        user_logs = [log for log in all_session_logs 
                                   if log.get("email") == email and 
                                   log.get("startTime", "").startswith(today)]
                        session_report["session_logs"] = user_logs
                        print(f"📋 Found {len(user_logs)} session logs for {email}")
            except Exception as log_e:
                print(f"⚠️ Could not read session logs: {log_e}")
            
            # Try to collect task-specific data file
            try:
                data_filename = os.path.join("data", f"{email.replace('@', '_at_').replace('.', '_')}.json")
                if os.path.exists(data_filename):
                    with open(data_filename, "r", encoding="utf-8") as f:
                        task_data = json.load(f)
                        session_report["task_details"] = task_data
                        print(f"📋 Found task details file for {email}")
            except Exception as task_e:
                print(f"⚠️ Could not read task data: {task_e}")
            
            # Upload comprehensive session report to S3 (same pattern as screenshots)
            s3_url = upload_logs_direct(session_report, email, task_name, "session_complete")
            if s3_url:
                print(f"📤 Session logs uploaded to S3: {s3_url}")
            else:
                print("❌ Failed to upload session logs to S3")
                
        except Exception as upload_e:
            print(f"❌ Error uploading session logs: {upload_e}")
            import traceback
            traceback.print_exc()
        
        # ✅ Clean up session file when timer stops
        try:
            import os
            session_file = "data/current_session.json"
            if os.path.exists(session_file):
                os.remove(session_file)
                print("✅ Session file cleaned up")
        except Exception as session_error:
            print(f"⚠️ Could not clean up session file: {session_error}")

        return jsonify({"status": "success", "message": "End task updated and logs uploaded!"})
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
    
    # Stop logging first (disabled old tracker)
    # try:
    #     from moduller.tracker import stop_logging
    #     stop_logging()
    # except Exception as e:
    #     print(f"❌ Error stopping logging: {e}")
    
    # Upload any remaining logs (disabled old tracker system)
    # try:
    #     from moduller.tracker import upload_logs_on_app_close
    #     upload_logs_on_app_close()
    # except Exception as e:
    #     print(f"❌ Error uploading logs on shutdown: {e}")
    
    print("✅ Graceful shutdown complete.")
    exit(0)

# Register signal handlers for graceful shutdown (temporarily disabled for testing)
# signal.signal(signal.SIGINT, signal_handler)   # Ctrl+C
# signal.signal(signal.SIGTERM, signal_handler)  # Termination signal

# Register exit handler
# atexit.register(lambda: upload_logs_on_app_close())  # Disabled old tracker system

if __name__ == "__main__":
    # Arka planda loglama başlat
    # threading.Thread(target=auto_log_every_minute, daemon=True).start()  # Disabled old tracker
    
    try:
        app.run(debug=True, port=5000)
    except KeyboardInterrupt:
        print("\n🛑 Application stopped by user")
        # upload_logs_on_app_close()  # Disabled - function not available
    except Exception as e:
        print(f"❌ Application error: {e}")
        # upload_logs_on_app_close()  # Disabled - function not available
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


@app.route('/generate_daily_logs_report', methods=['POST'])
def generate_daily_logs_report():
    """
    Generate and upload daily logs report for a specific employee
    """
    try:
        data = request.get_json()
        email = data.get('email')
        target_date = data.get('date')  # Optional, defaults to today
        
        if not email:
            return jsonify({
                "status": "error",
                "message": "Email is required"
            }), 400
        
        from moduller.daily_logs_reporter import generate_daily_report_for_employee
        
        result = generate_daily_report_for_employee(email, target_date)
        
        if result["status"] == "success":
            return jsonify(result)
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Error generating daily logs report: {str(e)}"
        }), 500


@app.route('/generate_all_daily_logs_reports', methods=['POST'])
def generate_all_daily_logs_reports():
    """
    Generate and upload daily logs reports for all employees
    """
    try:
        data = request.get_json() or {}
        target_date = data.get('date')  # Optional, defaults to today
        
        from moduller.daily_logs_reporter import generate_daily_reports_for_all_employees
        
        results = generate_daily_reports_for_all_employees(target_date)
        
        successful_uploads = [r for r in results if r.get("status") == "success"]
        failed_uploads = [r for r in results if r.get("status") != "success"]
        
        return jsonify({
            "status": "success",
            "message": f"Processed {len(results)} employees",
            "successful_uploads": len(successful_uploads),
            "failed_uploads": len(failed_uploads),
            "results": results,
            "target_date": target_date or "today"
        })
            
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Error generating all daily logs reports: {str(e)}"
        }), 500


@app.route('/daily_logs_manager')
def daily_logs_manager():
    """Serve the daily logs manager interface"""
    return render_template('daily_logs_manager.html')


@app.route('/upload_activity_log', methods=['POST'])
def upload_activity_log():
    """Upload activity log following the same pattern as screenshots"""
    try:
        data = request.get_json()
        email = data.get('email')
        task_name = data.get('task_name', 'general')
        activity_data = data.get('activity_data')
        
        if not email or not activity_data:
            return jsonify({"status": "error", "message": "Email and activity_data are required"}), 400
            
        # Use the same S3 upload pattern as screenshots
        from moduller.s3_uploader import upload_activity_log_to_s3
        result_url = upload_activity_log_to_s3(email, activity_data, task_name)
        
        if result_url:
            return jsonify({
                "status": "success", 
                "message": "Activity log uploaded", 
                "s3_url": result_url
            })
        else:
            return jsonify({"status": "error", "message": "Failed to upload activity log"}), 500
            
    except Exception as e:
        logging.error(f"❌ Error uploading activity log: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/create_daily_log_file', methods=['POST'])
def create_daily_log_file():
    """Create initial daily log file when user logs in"""
    try:
        data = request.get_json()
        email = data.get('email')
        staff_id = data.get('staff_id') 
        action = data.get('action', 'login')
        timestamp = data.get('timestamp')
        date = data.get('date')
        
        if not email:
            return jsonify({"status": "error", "message": "Email is required"}), 400
            
        # Create initial daily log structure
        daily_log = {
            "date": date,
            "email": email,
            "staff_id": staff_id,
            "created_at": timestamp,
            "activities": [
                {
                    "timestamp": timestamp,
                    "action": action,
                    "details": f"User {email} logged into the system"
                }
            ]
        }
        
        # Upload initial log file to S3
        from moduller.s3_uploader import upload_daily_log_file_to_s3
        upload_result = upload_daily_log_file_to_s3(email, date, daily_log, "login")
        
        if upload_result:
            return jsonify({
                "status": "success", 
                "message": "Daily log file created", 
                "s3_url": upload_result
            })
        else:
            return jsonify({"status": "error", "message": "Failed to create daily log file"}), 500
            
    except Exception as e:
        logging.error(f"❌ Error creating daily log file: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/capture_activity_log', methods=['POST'])
def capture_activity_log():
    """Append activity logs to the existing daily log file"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"status": "error", "message": "No data provided"}), 400
            
        email = data.get('email')
        staff_id = data.get('staff_id') 
        task_id = data.get('task_id')
        project_name = data.get('project_name', 'Unknown Project')
        task_name = data.get('task_name', 'Unknown Task')
        timestamp = data.get('timestamp', datetime.now().isoformat())
        activity_type = data.get('activity_type', 'working')
        timer_seconds = data.get('timer_seconds', 0)
        
        if not email:
            return jsonify({"status": "error", "message": "Email is required"}), 400
            
        print(f"📋 Activity log captured for {email}: {activity_type} on {task_name}")
        
        # Create logs directory if it doesn't exist
        logs_dir = os.path.join("logs", "activity")
        os.makedirs(logs_dir, exist_ok=True)
        
        # Create activity log entry
        activity_entry = {
            "timestamp": timestamp,
            "email": email,
            "staff_id": staff_id,
            "task_id": task_id,
            "project_name": project_name,
            "task_name": task_name,
            "activity_type": activity_type,
            "timer_seconds": timer_seconds,
            "logged_at": datetime.now().isoformat()
        }
        
        # Save to daily activity log file
        safe_email = email.replace('@', '_at_').replace('.', '_')
        today = datetime.now().strftime('%Y-%m-%d')
        log_filename = os.path.join(logs_dir, f"{safe_email}_{today}_activity.json")
        
        # Load existing logs or create new list
        if os.path.exists(log_filename):
            with open(log_filename, 'r', encoding='utf-8') as f:
                daily_logs = json.load(f)
        else:
            daily_logs = []
            
        daily_logs.append(activity_entry)
        
        # Save updated logs
        with open(log_filename, 'w', encoding='utf-8') as f:
            json.dump(daily_logs, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Activity log saved to {log_filename}")
        
        # Simple success response
        return jsonify({
            "status": "success", 
            "message": "Activity logged successfully",
            "logged_activity": {
                "email": email,
                "task": task_name,
                "type": activity_type,
                "timestamp": timestamp
            },
            "log_file": log_filename
        })
            
    except Exception as e:
        print(f"❌ Error capturing activity log: {e}")
        traceback.print_exc()  # Print full stack trace
        logging.error(f"❌ Error capturing activity log: {e}")
        return jsonify({"status": "error", "message": f"Activity log error: {str(e)}"}), 500


@app.route('/get_employee_logs_summary', methods=['POST'])
def get_employee_logs_summary():
    """
    Get employee logs summary for the last N days
    """
    try:
        data = request.get_json()
        email = data.get('email')
        days_back = data.get('days_back', 7)  # Default to 7 days
        
        if not email:
            return jsonify({
                "status": "error",
                "message": "Email is required"
            }), 400
        
        from moduller.daily_logs_reporter import get_employee_weekly_summary
        
        summary = get_employee_weekly_summary(email, days_back)
        
        if summary:
            return jsonify({
                "status": "success",
                "summary": summary
            })
        else:
            return jsonify({
                "status": "error",
                "message": f"No data found for employee: {email}"
            }), 404
            
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Error getting employee logs summary: {str(e)}"
        }), 500


@app.route('/get_active_windows_summary', methods=['GET'])
def get_active_windows_summary():
    """Get current active windows summary"""
    try:
        from moduller.active_window_tracker import get_current_activity_summary
        summary = get_current_activity_summary()
        return jsonify({
            "status": "success",
            "data": summary
        })
    except ImportError:
        return jsonify({
            "status": "error",
            "message": "Active window tracking not available"
        }), 500
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route('/start_window_tracking', methods=['POST'])
def start_window_tracking():
    """Start active window tracking"""
    try:
        from moduller.active_window_tracker import start_active_window_tracking
        start_active_window_tracking()
        return jsonify({
            "status": "success",
            "message": "Active window tracking started"
        })
    except ImportError:
        return jsonify({
            "status": "error",
            "message": "Active window tracking not available (install pywin32)"
        }), 500
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route('/stop_window_tracking', methods=['POST'])
def stop_window_tracking():
    """Stop active window tracking"""
    try:
        from moduller.active_window_tracker import stop_active_window_tracking
        stop_active_window_tracking()
        return jsonify({
            "status": "success",
            "message": "Active window tracking stopped"
        })
    except ImportError:
        return jsonify({
            "status": "error",
            "message": "Active window tracking not available"
        }), 500
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route('/get_user_program_data', methods=['POST'])
def get_user_program_data():
    """Get current program tracking data for a user"""
    try:
        data = request.get_json()
        email = data.get('email')
        task_name = data.get('task_name', 'general')
        
        if not email:
            return jsonify({
                "status": "error",
                "message": "Email is required"
            }), 400
        
        from moduller.user_program_tracker import get_user_program_data
        program_data = get_user_program_data(email, task_name)
        
        if program_data:
            return jsonify({
                "status": "success",
                "data": program_data
            })
        else:
            return jsonify({
                "status": "info",
                "message": "No tracking data found for this user"
            })
            
    except ImportError:
        return jsonify({
            "status": "error",
            "message": "User program tracking not available"
        }), 500
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route('/submit_task_report', methods=['POST'])
def submit_task_report():
    """
    Submit comprehensive task report when user clicks 'Submit Report'
    This uploads all logs and session data to S3
    """
    try:
        # Remove local import since it's now at the top
        data = request.get_json()
        email = data.get('email')
        task_id = data.get('task_id')
        staff_id = data.get('staff_id')
        report_note = data.get('report_note', '')
        
        if not email:
            return jsonify({"status": "error", "message": "Email is required"}), 400
        
        # Get task name from database
        task_name = f"Task_{task_id}"  # Default fallback
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
                cursor.execute("SELECT name FROM tbltasks WHERE id = %s", (task_id,))
                result = cursor.fetchone()
                if result:
                    task_name = result['name']
                    print(f"✅ Found task name: {task_name} for task_id: {task_id}")
            
            connection.close()
        except Exception as db_e:
            print(f"⚠️ Could not get task name from DB: {db_e}, using fallback: {task_name}")
        
        from moduller.s3_uploader import upload_daily_logs_report
        import json
        import os
        
        # Collect comprehensive report data
        report_data = {
            "report_info": {
                "email": email,
                "task_id": task_id,
                "staff_id": staff_id,
                "task_name": task_name,
                "report_note": report_note,
                "submitted_at": datetime.now().isoformat(),
                "report_type": "manual_submit"
            },
            "session_logs": [],
            "task_details": {},
            "program_tracking": {}
        }
        
        # Try to collect session logs
        try:
            if os.path.exists("session_logs.json"):
                with open("session_logs.json", "r", encoding="utf-8") as f:
                    all_session_logs = json.load(f)
                    # Filter logs for this user and today
                    today = datetime.now().date().isoformat()
                    user_logs = [log for log in all_session_logs 
                               if log.get("email") == email and 
                               log.get("startTime", "").startswith(today)]
                    report_data["session_logs"] = user_logs
                    print(f"📋 Found {len(user_logs)} session logs for {email}")
        except Exception as log_e:
            print(f"⚠️ Could not read session logs: {log_e}")
        
        # Try to collect task-specific data file
        try:
            data_filename = os.path.join("data", f"{email.replace('@', '_at_').replace('.', '_')}.json")
            if os.path.exists(data_filename):
                with open(data_filename, "r", encoding="utf-8") as f:
                    task_data = json.load(f)
                    report_data["task_details"] = task_data
                    print(f"📋 Found task details file for {email}")
        except Exception as task_e:
            print(f"⚠️ Could not read task data: {task_e}")
        
        # Try to get current program tracking data if available
        try:
            from moduller.user_program_tracker import get_user_program_data
            program_data = get_user_program_data(email, task_name)
            if program_data:
                report_data["program_tracking"] = program_data
                print(f"📊 Found program tracking data for {email}")
        except Exception as prog_e:
            print(f"⚠️ Could not get program tracking data: {prog_e}")
        
        # Upload comprehensive report to S3 (same pattern as screenshots)
        from moduller.s3_uploader import upload_logs_direct
        s3_url = upload_logs_direct(report_data, email, task_name, "task_report")
        
        if s3_url:
            print(f"📤 Task report uploaded to S3: {s3_url}")
            return jsonify({
                "status": "success", 
                "message": "Task report submitted successfully", 
                "s3_url": s3_url,
                "report_summary": {
                    "session_logs_count": len(report_data["session_logs"]),
                    "has_task_details": bool(report_data["task_details"]),
                    "has_program_tracking": bool(report_data["program_tracking"])
                }
            })
        else:
            return jsonify({
                "status": "error", 
                "message": "Failed to upload task report to S3"
            }), 500
            
    except Exception as e:
        print(f"❌ Error submitting task report: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "status": "error", 
            "message": f"Error submitting task report: {str(e)}"
        }), 500


if __name__ == '__main__':
    try:
        # Start active window tracking when app starts
        from moduller.active_window_tracker import start_active_window_tracking
        start_active_window_tracking()
        print("🔍 Active window tracking started")
    except ImportError:
        print("⚠️ Active window tracking not available (install pywin32)")
    
    app.run(debug=True)


