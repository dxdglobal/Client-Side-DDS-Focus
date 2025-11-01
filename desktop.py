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
    """Opens the exec terminal automatically (DISABLED for silent operation)"""
    try:
        # Get the directory where the desktop app is located
        base_path = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.abspath(".")
        
        logging.info(f"[EXEC] Terminal opening disabled for silent operation from: {base_path}")
        
        # DISABLED: Don't open terminal window for silent GUI operation
        # This prevents the command prompt from appearing when starting the GUI
        logging.info("[INFO] Silent mode: Terminal opening disabled")
        
        # No sleep needed since we're not opening anything
        
    except Exception as e:
        logging.warning(f"[WARN] Error in terminal function: {e}")
        logging.info("[INFO] Continuing silently...")

def kill_existing_connector():
    """Kill any existing DDSFocusPro processes"""
    try:
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                proc_name = proc.info['name'].lower()
                cmdline_str = ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ''
                
                # Check for various DDSFocusPro process patterns
                should_kill = (
                    'ddsfocuspro-app.exe' in proc_name or
                    'connector.exe' in proc_name or
                    ('python.exe' in proc_name and 'app.py' in cmdline_str) or
                    ('python' in proc_name and ('app.py' in cmdline_str or 'DDSFocusPro' in cmdline_str))
                )
                
                if should_kill:
                    logging.info(f"[CLEAN] Killing existing process: PID {proc.pid} - {proc_name}")
                    try:
                        proc.terminate()
                        proc.wait(timeout=3)
                    except (psutil.TimeoutExpired, psutil.AccessDenied):
                        try:
                            proc.kill()
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            pass
                    except psutil.NoSuchProcess:
                        pass  # Process already gone
                        
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
            except Exception as e:
                logging.warning(f"[WARN] Could not check/kill process {proc.info.get('pid', 'unknown')}: {e}")
                continue
                
    except Exception as e:
        logging.warning(f"[WARN] Error during existing process cleanup: {e}")

# ------------------ Globals ------------------
connector_process = None
flask_ready = False
cleanup_in_progress = False
flask_pids = set()  # Track all Flask process PIDs
pid_file = "ddsfocus_pids.txt"  # File to persist PIDs

def save_pid(pid):
    """Save a PID to the tracking file"""
    try:
        flask_pids.add(pid)
        with open(pid_file, 'w') as f:
            for saved_pid in flask_pids:
                f.write(f"{saved_pid}\n")
        logging.info(f"📝 Saved PID {pid} to tracking file")
    except Exception as e:
        logging.warning(f"⚠️ Could not save PID {pid}: {e}")

def load_pids():
    """Load PIDs from the tracking file"""
    try:
        if os.path.exists(pid_file):
            with open(pid_file, 'r') as f:
                for line in f:
                    pid = int(line.strip())
                    flask_pids.add(pid)
            logging.info(f"📂 Loaded {len(flask_pids)} PIDs from tracking file")
    except Exception as e:
        logging.warning(f"⚠️ Could not load PIDs: {e}")

def remove_pid(pid):
    """Remove a PID from tracking"""
    try:
        flask_pids.discard(pid)
        with open(pid_file, 'w') as f:
            for saved_pid in flask_pids:
                f.write(f"{saved_pid}\n")
        logging.info(f"🗑️ Removed PID {pid} from tracking")
    except Exception as e:
        logging.warning(f"⚠️ Could not remove PID {pid}: {e}")

def cleanup_pid_file():
    """Clean up the PID file"""
    try:
        if os.path.exists(pid_file):
            os.remove(pid_file)
            logging.info("🧹 PID tracking file cleaned up")
    except Exception as e:
        logging.warning(f"⚠️ Could not clean up PID file: {e}")

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

def aggressive_cleanup():
    """Ultra-aggressive cleanup that ensures no DDSFocusPro processes remain"""
    logging.info("🔥 Starting aggressive cleanup...")
    
    # Kill all DDSFocusPro processes multiple times
    for round_num in range(5):  # Try 5 rounds of cleanup
        logging.info(f"🔄 Cleanup round {round_num + 1}/5...")
        
        # Method 1: Kill by process name using psutil
        killed_any = False
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    proc_info = proc.info
                    proc_name = proc_info['name'].lower() if proc_info['name'] else ''
                    cmdline_str = ' '.join(proc_info['cmdline']) if proc_info['cmdline'] else ''
                    
                    # Check for DDSFocusPro executables or Python processes running our scripts
                    if (any(name in proc_name for name in ['ddsfocuspro-app.exe', 'ddsfocuspro-gui.exe', 'connector.exe']) or
                        ('python.exe' in proc_name and any(script in cmdline_str for script in ['app.py', 'desktop.py', 'DDSFocusPro']))):
                        
                        # Don't kill ourselves (GUI process)
                        if proc.pid != os.getpid():
                            logging.info(f"🎯 Round {round_num + 1}: Killing {proc_name} (PID: {proc_info['pid']})")
                            try:
                                proc.terminate()
                                proc.wait(timeout=2)
                                killed_any = True
                            except psutil.TimeoutExpired:
                                try:
                                    proc.kill()
                                    killed_any = True
                                except:
                                    pass
                            except (psutil.NoSuchProcess, psutil.AccessDenied):
                                pass
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
        except Exception as e:
            logging.warning(f"⚠️ Error in psutil cleanup round {round_num + 1}: {e}")
        
        # Method 2: Windows taskkill
        try:
            for exe_name in ['DDSFocusPro-App.exe', 'DDSFocusPro-GUI.exe', 'connector.exe']:
                result = subprocess.run(['taskkill', '/f', '/im', exe_name], 
                                      capture_output=True, text=True, timeout=5)
                if "SUCCESS" in result.stdout:
                    logging.info(f"🔨 Round {round_num + 1}: taskkill killed {exe_name}")
                    killed_any = True
        except:
            pass
        
        # Method 3: Kill by port
        try:
            for port in range(5000, 5010):
                result = subprocess.run(['netstat', '-ano'], capture_output=True, text=True, timeout=5)
                for line in result.stdout.split('\n'):
                    if f':{port}' in line and 'LISTENING' in line:
                        parts = line.split()
                        if len(parts) > 4:
                            pid = parts[-1]
                            try:
                                subprocess.run(['taskkill', '/f', '/pid', pid], 
                                             capture_output=True, text=True, timeout=3)
                                logging.info(f"🔌 Round {round_num + 1}: Killed process on port {port} (PID: {pid})")
                                killed_any = True
                            except:
                                pass
        except:
            pass
        
        # If no processes were killed in this round, we're done
        if not killed_any:
            logging.info(f"✅ No more processes found after round {round_num + 1}")
            break
        
        # Wait between rounds
        time.sleep(1)
    
    # Final verification
    time.sleep(2)
    remaining_processes = []
    try:
        for proc in psutil.process_iter(['pid', 'name']):
            proc_name = proc.info['name'].lower() if proc.info['name'] else ''
            if any(name in proc_name for name in ['ddsfocuspro-app.exe', 'ddsfocuspro-gui.exe']) and proc.pid != os.getpid():
                remaining_processes.append(f"{proc.info['name']} (PID: {proc.info['pid']})")
    except:
        pass
    
    if remaining_processes:
        logging.warning(f"⚠️ {len(remaining_processes)} processes still running: {remaining_processes}")
    else:
        logging.info("✅ Aggressive cleanup completed - no DDSFocusPro processes remaining")

# Global cleanup function that terminates all processes
def cleanup_and_exit():
    """Global cleanup function that terminates all processes"""
    global connector_process, cleanup_in_progress
    
    # Prevent multiple cleanup executions
    if cleanup_in_progress:
        logging.info("[CLEANUP] Cleanup already in progress, skipping...")
        return
    
    cleanup_in_progress = True
    logging.info("[CLEANUP] UI closed by user. Cleaning up...")

    # Step 0: Load any previously tracked PIDs
    load_pids()

    # Step 1: Kill tracked Flask processes by PID
    try:
        if flask_pids:
            logging.info(f"🎯 Killing tracked Flask processes: {flask_pids}")
            for pid in flask_pids.copy():
                try:
                    process = psutil.Process(pid)
                    process.terminate()
                    process.wait(timeout=3)
                    logging.info(f"✅ Terminated tracked process PID {pid}")
                    remove_pid(pid)
                except psutil.TimeoutExpired:
                    try:
                        process.kill()
                        logging.info(f"🔨 Force killed tracked process PID {pid}")
                        remove_pid(pid)
                    except:
                        pass
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    logging.info(f"📝 Process PID {pid} already gone")
                    remove_pid(pid)
                except Exception as e:
                    logging.warning(f"⚠️ Error killing tracked PID {pid}: {e}")
    except Exception as e:
        logging.warning(f"⚠️ Error in tracked PID cleanup: {e}")

    # Step 2: Try to gracefully shut down Flask app via API
    try:
        logging.info("🛑 Sending shutdown signal to Flask app...")
        
        # Try multiple ports since the Flask app finds free ports
        ports_to_try = [5000, 5001, 5002, 5003, 5004, 5005]
        shutdown_success = False
        
        for port in ports_to_try:
            try:
                import requests
                response = requests.post(f"http://127.0.0.1:{port}/shutdown", timeout=3)
                if response.status_code == 200:
                    logging.info(f"✅ Flask app shutdown successfully on port {port}")
                    shutdown_success = True
                    break
            except requests.exceptions.RequestException:
                continue  # Try next port
        
        if shutdown_success:
            logging.info("⏳ Waiting for Flask app to shutdown...")
            time.sleep(2)  # Give Flask time to cleanup
        else:
            logging.warning("⚠️ Could not reach Flask app via API")
            
    except Exception as e:
        logging.warning(f"[WARN] Error during graceful shutdown: {e}")

    # Step 2: Force kill the process if it's still running
    if connector_process and connector_process.poll() is None:
        try:
            logging.info("🔄 Force terminating Flask process...")
            connector_process.terminate()
            
            # Wait up to 5 seconds for graceful termination
            try:
                connector_process.wait(timeout=5)
                logging.info("✅ Flask process terminated gracefully")
            except subprocess.TimeoutExpired:
                logging.info("⚠️ Process didn't terminate gracefully, force killing...")
                connector_process.kill()
                connector_process.wait()
                logging.info("✅ Flask process force killed")
                
        except Exception as e:
            logging.error(f"❌ Error terminating Flask process: {e}")

    # Step 3: Comprehensive background process cleanup
    try:
        logging.info("🧹 Performing comprehensive background process cleanup...")
        
        # Method 1: Aggressive process killing using multiple approaches
        killed_processes = []
        
        # First, try to kill using psutil with more aggressive matching
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                proc_info = proc.info
                proc_name = proc_info['name'].lower() if proc_info['name'] else ""
                cmdline_str = ' '.join(proc_info['cmdline']) if proc_info['cmdline'] else ""
                
                # Check for DDSFocusPro executables and related processes
                should_kill = False
                if any(name in proc_name for name in [
                    'ddsfocuspro-app.exe', 'ddsfocuspro-gui.exe', 'connector.exe'
                ]):
                    should_kill = True
                elif 'python.exe' in proc_name and any(script in cmdline_str for script in [
                    'app.py', 'desktop.py', 'connector.py'
                ]):
                    should_kill = True
                elif 'python' in proc_name and 'ddsfocuspro' in cmdline_str.lower():
                    should_kill = True
                
                if should_kill and proc.pid != os.getpid():  # Don't kill ourselves
                    logging.info(f"🗑️ Killing background process: {proc_name} (PID: {proc_info['pid']})")
                    try:
                        proc.terminate()
                        proc.wait(timeout=3)
                        logging.info(f"✅ Process {proc_name} terminated gracefully")
                    except (psutil.TimeoutExpired, psutil.AccessDenied):
                        try:
                            proc.kill()
                            logging.info(f"� Process {proc_name} force killed")
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            pass
                    except psutil.NoSuchProcess:
                        pass  # Process already gone
                        
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
            except Exception as e:
                logging.warning(f"⚠️ Error checking process: {e}")
                continue
        
        # Method 2: Use Windows taskkill as backup - Multiple attempts
        try:
            logging.info("🔄 Using Windows taskkill for additional cleanup...")
            
            # Kill by executable name with multiple attempts
            for exe_name in ['DDSFocusPro-App.exe', 'DDSFocusPro-GUI.exe', 'connector.exe']:
                for attempt in range(3):  # Try 3 times
                    try:
                        result = subprocess.run(['taskkill', '/f', '/im', exe_name], 
                                              capture_output=True, text=True, timeout=5)
                        if "SUCCESS" in result.stdout:
                            logging.info(f"✅ Killed {exe_name} (attempt {attempt + 1})")
                            break
                    except:
                        continue
            
            # Kill any process with DDSFocusPro in the name
            try:
                result = subprocess.run(['wmic', 'process', 'where', 'name like "%DDSFocusPro%"', 'delete'], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    logging.info("✅ WMIC cleanup completed")
            except:
                pass
                
            logging.info("✅ Windows taskkill cleanup completed")
        except Exception as e:
            logging.warning(f"⚠️ Windows taskkill error: {e}")
            
        # Method 3: Kill processes by port (Flask servers) - Enhanced
        try:
            logging.info("🔄 Killing processes by port...")
            for port in [5000, 5001, 5002, 5003, 5004, 5005]:
                try:
                    # Method 3a: Use netstat to find PIDs
                    result = subprocess.run(['netstat', '-ano'], capture_output=True, text=True, timeout=10)
                    lines = result.stdout.split('\n')
                    for line in lines:
                        if f':{port}' in line and ('LISTENING' in line or 'ESTABLISHED' in line):
                            parts = line.split()
                            if len(parts) >= 5:
                                pid = parts[-1]
                                try:
                                    subprocess.run(['taskkill', '/f', '/pid', pid], 
                                                  capture_output=True, text=True, timeout=5)
                                    logging.info(f"🗑️ Killed process on port {port} (PID: {pid})")
                                except:
                                    pass
                    
                    # Method 3b: Use PowerShell to find and kill processes on ports
                    ps_cmd = f'Get-NetTCPConnection -LocalPort {port} -ErrorAction SilentlyContinue | ForEach-Object {{ Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }}'
                    subprocess.run(['powershell', '-Command', ps_cmd], 
                                 capture_output=True, text=True, timeout=5)
                    
                except Exception as e:
                    continue
        except Exception as e:
            logging.warning(f"⚠️ Port-based cleanup error: {e}")
            
        # Method 4: Final aggressive cleanup - Kill any remaining processes
        try:
            logging.info("🔄 Final aggressive process cleanup...")
            time.sleep(1)  # Give previous methods time to complete
            
            # One more sweep for any remaining DDSFocusPro processes
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    proc_name = proc.info['name'].lower() if proc.info['name'] else ""
                    if ('ddsfocuspro' in proc_name or 'ddsfocus' in proc_name) and proc.pid != os.getpid():
                        try:
                            proc.kill()
                            logging.info(f"🔥 Force killed remaining process: {proc_name} (PID: {proc.info['pid']})")
                        except:
                            pass
                except:
                    continue
                    
        except Exception as e:
            logging.warning(f"⚠️ Final cleanup error: {e}")
            
    except Exception as e:
        logging.warning(f"[WARN] Error during comprehensive cleanup: {e}")

    logging.info("🏁 All background processes cleanup completed. Exiting...")
    
    # Final aggressive cleanup to ensure nothing remains
    aggressive_cleanup()
    
    # Final step: Clean up PID tracking file
    cleanup_pid_file()
    
    # Final exit
    try:
        sys.exit(0)
    except:
        try:
            os._exit(0)
        except:
            # Last resort - Windows specific
            try:
                subprocess.run(['taskkill', '/f', '/pid', str(os.getpid())], 
                             capture_output=True, text=True, timeout=2)
            except:
                pass

def watchdog_cleanup():
    """Background watchdog that periodically kills orphaned DDSFocusPro processes"""
    gui_pid = os.getpid()
    logging.info(f"🐕 Watchdog started - monitoring for orphaned processes (GUI PID: {gui_pid})")
    
    while True:
        try:
            time.sleep(15)  # Check every 15 seconds
            
            # Check if GUI process still exists
            try:
                gui_process = psutil.Process(gui_pid)
                if not gui_process.is_running():
                    logging.info("🐕 GUI process no longer running, watchdog exiting")
                    break
            except psutil.NoSuchProcess:
                logging.info("🐕 GUI process no longer exists, watchdog exiting")
                break
            
            # Look for orphaned DDSFocusPro processes
            orphaned_processes = []
            try:
                for proc in psutil.process_iter(['pid', 'name', 'ppid']):
                    try:
                        proc_info = proc.info
                        proc_name = proc_info['name'].lower() if proc_info['name'] else ''
                        
                        # Check for DDSFocusPro processes
                        if 'ddsfocuspro-app.exe' in proc_name:
                            # Check if it's an orphan (parent process doesn't exist or is not our GUI)
                            try:
                                parent = psutil.Process(proc_info['ppid'])
                                parent_name = parent.name().lower()
                                
                                # If parent is not our GUI or parent is not DDSFocusPro-GUI, it might be orphaned
                                if proc_info['ppid'] != gui_pid and 'ddsfocuspro-gui.exe' not in parent_name:
                                    orphaned_processes.append(proc)
                            except psutil.NoSuchProcess:
                                # Parent doesn't exist, definitely orphaned
                                orphaned_processes.append(proc)
                                
                    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                        continue
                        
                # Kill orphaned processes
                if orphaned_processes:
                    logging.info(f"🐕 Found {len(orphaned_processes)} orphaned processes, cleaning up...")
                    for proc in orphaned_processes:
                        try:
                            logging.info(f"🗑️ Watchdog killing orphaned process: {proc.name()} (PID: {proc.pid})")
                            proc.terminate()
                            proc.wait(timeout=3)
                        except psutil.TimeoutExpired:
                            try:
                                proc.kill()
                            except:
                                pass
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            pass
                            
            except Exception as e:
                logging.warning(f"🐕 Watchdog error: {e}")
                
        except Exception as e:
            logging.warning(f"🐕 Watchdog critical error: {e}")
            
    logging.info("🐕 Watchdog terminated")

def monitor_main_process():
    """Monitor if the main GUI process is still alive and cleanup if not"""
    current_pid = os.getpid()
    
    while True:
        try:
            time.sleep(3)  # Check every 3 seconds (more frequent)
            
            # Check if our own process is still running normally
            if not psutil.pid_exists(current_pid):
                logging.info("[MONITOR] Main process no longer exists, triggering cleanup")
                cleanup_background_processes()
                break
                
            # Check if we should exit (this can be set by other parts of the code)
            if cleanup_in_progress:
                break
                
            # Proactive cleanup: Check for orphaned DDSFocusPro processes
            orphaned_count = 0
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    proc_name = proc.info['name'].lower() if proc.info['name'] else ""
                    if 'ddsfocuspro-app.exe' in proc_name and proc.pid != current_pid:
                        orphaned_count += 1
                except:
                    continue
            
            # If we find too many orphaned processes, clean them up
            if orphaned_count > 2:  # More than 2 background processes is suspicious
                logging.info(f"[MONITOR] Found {orphaned_count} orphaned DDSFocusPro processes, cleaning up...")
                cleanup_background_processes()
                
        except Exception as e:
            logging.warning(f"[MONITOR] Error in process monitoring: {e}")
            continue

def cleanup_background_processes():
    """Cleanup only background processes without exiting the main process"""
    try:
        logging.info("🧹 Emergency cleanup of background processes...")
        
        # Method 1: Kill DDSFocusPro-App processes using multiple approaches
        for attempt in range(3):
            try:
                result = subprocess.run(['taskkill', '/f', '/im', 'DDSFocusPro-App.exe'], 
                                      capture_output=True, text=True, timeout=5)
                if "SUCCESS" in result.stdout:
                    logging.info(f"✅ Emergency taskkill successful (attempt {attempt + 1})")
                    break
            except:
                continue
        
        # Method 2: Kill by process name using psutil - More aggressive
        killed_count = 0
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                proc_info = proc.info
                proc_name = proc_info['name'].lower() if proc_info['name'] else ""
                
                if ('ddsfocuspro-app.exe' in proc_name or 'ddsfocus' in proc_name) and proc.pid != os.getpid():
                    proc.kill()
                    killed_count += 1
                    logging.info(f"🗑️ Emergency killed: {proc_name} (PID: {proc_info['pid']})")
                    
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        logging.info(f"🧹 Emergency cleanup completed. Killed {killed_count} background processes.")
                    
    except Exception as e:
        logging.warning(f"⚠️ Error during emergency cleanup: {e}")

# Signal handlers for proper cleanup
def signal_handler(signum, frame):
    logging.info(f"[SIGNAL] Received signal {signum}, cleaning up...")
    cleanup_and_exit()

# Register signal handlers (Windows compatible)
try:
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    logging.info("[OK] Signal handlers registered")
except Exception as e:
    logging.warning(f"[WARN] Could not register signal handlers: {e}")

# Register atexit handler for additional safety
try:
    atexit.register(cleanup_and_exit)
    logging.info("[OK] Exit handler registered")
except Exception as e:
    logging.warning(f"[WARN] Could not register exit handler: {e}")

def start_flask():
    global connector_process
    base_path = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.abspath(".")
    current_dir = os.getcwd()
    
    logging.info(f"[FLASK] Starting Flask server...")
    logging.info(f"[DEBUG] Base path: {base_path}")
    logging.info(f"[DEBUG] Current working directory: {current_dir}")
    
    try:
        # Look for DDSFocusPro-App.exe executable
        possible_executables = [
            os.path.join(current_dir, "DDSFocusPro-App.exe"),  # Current working directory
            os.path.join(base_path, "DDSFocusPro-App.exe"),    # Executable directory
            os.path.join(os.path.dirname(base_path), "DDSFocusPro-App.exe"),  # Parent directory
            os.path.join(current_dir, "dist", "DDSFocusPro-App.exe"),  # Dist folder
            os.path.join(base_path, "dist", "DDSFocusPro-App.exe"),    # Dist folder from base
        ]
        
        app_executable = None
        for exe_path in possible_executables:
            logging.info(f"[DEBUG] Checking for DDSFocusPro-App.exe at: {exe_path}")
            if os.path.exists(exe_path):
                app_executable = exe_path
                logging.info(f"[FOUND] DDSFocusPro-App.exe found at: {app_executable}")
                break
        
        if app_executable:
            logging.info(f"[FLASK] Starting Flask executable: {app_executable}")
            
            # Windows-specific: Hide the process window completely
            import subprocess
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
            
            connector_process = subprocess.Popen(
                [app_executable],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=os.path.dirname(app_executable),
                startupinfo=startupinfo,  # Hide the window
                creationflags=subprocess.CREATE_NO_WINDOW  # Don't create a console window
            )
            logging.info(f"[OK] Flask executable started with PID: {connector_process.pid} (HIDDEN)")
            save_pid(connector_process.pid)  # Track this PID
        else:
            # Fallback: Try to run app.py directly if executable not found
            logging.warning("[WARN] DDSFocusPro-App.exe not found, trying app.py...")
            
            possible_app_paths = [
                os.path.join(current_dir, "app.py"),
                os.path.join(base_path, "app.py"),
            ]
            
            app_path = None
            for path in possible_app_paths:
                if os.path.exists(path):
                    app_path = path
                    break
            
            if app_path:
                logging.info(f"[FLASK] Starting Flask from app.py: {app_path}")
                
                # Windows-specific: Hide the process window completely
                import subprocess
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE
                
                connector_process = subprocess.Popen(
                    [sys.executable, app_path],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    cwd=os.path.dirname(app_path),
                    startupinfo=startupinfo,  # Hide the window
                    creationflags=subprocess.CREATE_NO_WINDOW  # Don't create a console window
                )
                logging.info(f"[OK] Flask app.py started with PID: {connector_process.pid} (HIDDEN)")
                save_pid(connector_process.pid)  # Track this PID
            else:
                logging.error("[ERROR] No Flask app found (neither executable nor app.py)!")
                return
                
    except Exception as e:
        logging.error(f"[ERROR] Failed to start Flask: {e}")

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




# ------------------ Main Launcher ------------------
if __name__ == '__main__':
    # Step 1: Open exec terminal first
    logging.info("🚀 Starting DDS Focus Pro with exec terminal...")
    open_exec_terminal()
    
    # Step 2: Clean up existing processes
    kill_existing_connector()
    
    # Step 2.5: Clean up any orphaned processes from previous runs
    load_pids()
    if flask_pids:
        logging.info(f"🧹 Cleaning up {len(flask_pids)} orphaned processes from previous runs")
        cleanup_and_exit()
        flask_pids.clear()  # Reset for new session
        cleanup_in_progress = False  # Reset flag
    
    # Step 3: Start background launcher
    threading.Thread(target=background_launcher, daemon=True).start()
    
    # Step 4: Start process monitoring for cleanup
    threading.Thread(target=monitor_main_process, daemon=True).start()
    logging.info("🔍 Process monitoring started")
    
    # Step 5: Start watchdog for orphaned process cleanup
    threading.Thread(target=watchdog_cleanup, daemon=True).start()
    logging.info("🐕 Watchdog started")

    # Step 5: Show UI immediately (no wait)
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
            on_top=False,
            resizable=True
        )

        # [OK] Attach cleanup after window opens
        def after_window_created():
            try:
                if webview.windows:
                    # Set up proper window close event handler
                    def on_window_close():
                        logging.info("[OK] Window close event triggered by user")
                        cleanup_and_exit()
                    
                    webview.windows[0].events.closed += on_window_close
                    logging.info("[OK] Window close event handler attached")
                else:
                    logging.warning("[WARN] No webview windows found for event attachment")
            except Exception as e:
                logging.error(f"[ERROR] Failed to attach window close handler: {e}")

        webview.start(gui='edgechromium', debug=False, func=after_window_created)
        
        # If webview.start() returns normally (window was closed), cleanup
        logging.info("[INFO] WebView window closed normally")
        cleanup_and_exit()

    except Exception as e:
        logging.error(f"[ERROR] WebView failed: {e}")
        # Ensure cleanup happens even if webview fails
        cleanup_and_exit()