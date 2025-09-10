#!/usr/bin/env python3
"""
Active Window Tracker Module
Tracks which application/program is currently active and logs time spent
"""

import time
import json
from datetime import datetime
import threading
import psutil
from collections import defaultdict

# Logger setup
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

try:
    import win32gui
    import win32process
except ImportError:
    print("⚠️ Please install pywin32: pip install pywin32")
    win32gui = None
    win32process = None

# Global tracker instance
window_tracker = None

class ActiveWindowTracker:
    def __init__(self):
        self.current_window = None
        self.start_time = None
        self.tracking = False
        self.session_data = defaultdict(lambda: {
            'total_time': 0,
            'window_title': '',
            'process_name': '',
            'sessions': []
        })
        self.tracking_thread = None
        
    def get_active_window_info(self):
        """Get information about the currently active window"""
        if not win32gui:
            return None, None, None
            
        try:
            # Get the currently active window
            hwnd = win32gui.GetForegroundWindow()
            if hwnd == 0:
                return None, None, None
                
            # Get window title
            window_title = win32gui.GetWindowText(hwnd)
            
            # Get process ID
            _, process_id = win32process.GetWindowThreadProcessId(hwnd)
            
            # Get process name
            try:
                process = psutil.Process(process_id)
                process_name = process.name()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                process_name = "Unknown"
                
            return window_title, process_name, process_id
            
        except Exception as e:
            print(f"❌ Error getting active window: {e}")
            return None, None, None
    
    def get_browser_tab_info(self, window_title, process_name):
        """Extract browser tab information if it's a browser"""
        browser_info = {
            'is_browser': False,
            'browser_name': process_name,
            'tab_title': window_title,
            'domain': None
        }
        
        # Check if it's a known browser
        browsers = {
            'chrome.exe': 'Google Chrome',
            'firefox.exe': 'Mozilla Firefox',
            'msedge.exe': 'Microsoft Edge',
            'opera.exe': 'Opera',
            'brave.exe': 'Brave Browser',
            'safari.exe': 'Safari'
        }
        
        if process_name.lower() in browsers:
            browser_info['is_browser'] = True
            browser_info['browser_name'] = browsers[process_name.lower()]
            
            # Try to extract domain from title
            # Browser titles usually format as: "Page Title - Website Name"
            if ' - ' in window_title:
                parts = window_title.split(' - ')
                if len(parts) >= 2:
                    # Last part is usually the domain/site name
                    browser_info['domain'] = parts[-1]
                    browser_info['tab_title'] = ' - '.join(parts[:-1])
                    
        return browser_info
    
    def start_tracking(self):
        """Start tracking active windows"""
        if self.tracking:
            return
            
        self.tracking = True
        self.tracking_thread = threading.Thread(target=self._tracking_loop, daemon=True)
        self.tracking_thread.start()
        print("🔍 Active window tracking started")
    
    def stop_tracking(self):
        """Stop tracking active windows"""
        self.tracking = False
        if self.current_window and self.start_time:
            self._log_window_time()
        print("⏹️ Active window tracking stopped")
    
    def _tracking_loop(self):
        """Main tracking loop"""
        check_interval = 1  # Check every 1 second
        
        while self.tracking:
            try:
                window_title, process_name, process_id = self.get_active_window_info()
                
                if window_title and process_name:
                    current_window_key = f"{process_name}|{window_title}"
                    
                    # If window changed
                    if current_window_key != self.current_window:
                        # Log time for previous window
                        if self.current_window and self.start_time:
                            self._log_window_time()
                        
                        # Start tracking new window
                        self.current_window = current_window_key
                        self.start_time = time.time()
                        
                        # Get browser info if applicable
                        browser_info = self.get_browser_tab_info(window_title, process_name)
                        
                        # Update session data
                        self.session_data[current_window_key].update({
                            'window_title': window_title,
                            'process_name': process_name,
                            'process_id': process_id,
                            'browser_info': browser_info
                        })
                        
                        print(f"🔄 Active window: {process_name} - {window_title[:50]}...")
                
                time.sleep(check_interval)
                
            except Exception as e:
                print(f"❌ Error in tracking loop: {e}")
                time.sleep(check_interval)
    
    def _log_window_time(self):
        """Log time spent on current window"""
        if not self.current_window or not self.start_time:
            return
            
        duration = time.time() - self.start_time
        current_time = datetime.now().isoformat()
        
        # Add to total time
        self.session_data[self.current_window]['total_time'] += duration
        
        # Add session entry
        session_entry = {
            'start_time': datetime.fromtimestamp(self.start_time).isoformat(),
            'end_time': current_time,
            'duration': duration
        }
        
        self.session_data[self.current_window]['sessions'].append(session_entry)
    
    def get_activity_export_data(self):
        """
        Get activity data in S3-ready format for export
        Returns dict with complete session data and summary - FOCUS TIME ONLY
        """
        logger.info("📊 [get_activity_export_data] Preparing activity data for S3 export")
        
        activities = []
        total_duration = 0
        
        # Convert session_data to exportable format (focus time only)
        for window_key, data in self.session_data.items():
            if data['total_time'] > 0:  # Only include windows that had focus time
                
                # Create activity record for each session
                for session in data['sessions']:
                    duration = session['duration']
                    total_duration += duration
                    
                    activity_record = {
                        'window_title': data['window_title'],
                        'process_name': data['process_name'],
                        'browser_url': data['browser_info'].get('domain'),
                        'domain': data['browser_info'].get('domain'),
                        'tab_title': data['browser_info'].get('tab_title'),
                        'start_time': session['start_time'],
                        'end_time': session['end_time'],
                        'duration_seconds': duration,
                        'duration_formatted': self._format_duration(duration)
                    }
                    activities.append(activity_record)
        
        # Get session summary data
        summary = self.get_session_summary()
        
        export_data = {
            'export_timestamp': datetime.now().isoformat(),
            'session_duration_seconds': total_duration,
            'session_duration_formatted': self._format_duration(total_duration),
            'total_applications': len([w for w in self.session_data.values() if w['total_time'] > 0]),
            'focus_time_tracking': True,  # Indicates this tracks only focus time
            'summary_by_application': summary,
            'detailed_activities': activities,
            'tracking_started': self.tracking_start_time.isoformat() if self.tracking_start_time else None,
            'tracking_status': 'active' if self.tracking else 'stopped'
        }
        
        logger.info("📦 Activity export data prepared: %d focus sessions, %.1f minutes total focus time", 
                   len(activities), total_duration/60)
        return export_data

    def get_session_summary(self):
        """Get summary of current tracking session"""
        # Log current window time before generating summary
        if self.current_window and self.start_time:
            self._log_window_time()
            # Restart timing for current window
            self.start_time = time.time()
        
        # Aggregate by process name instead of window key
        program_totals = defaultdict(lambda: {
            'total_time': 0,
            'window_titles': set(),
            'browser_info': {},
            'sessions': []
        })
        
        total_session_time = 0
        
        # Aggregate all window sessions by process name
        for window_key, data in self.session_data.items():
            if data['total_time'] > 0:
                process_name = data['process_name']
                
                # Add time to program total
                program_totals[process_name]['total_time'] += data['total_time']
                program_totals[process_name]['window_titles'].add(data['window_title'])
                program_totals[process_name]['sessions'].extend(data['sessions'])
                
                # Keep browser info if available
                if data.get('browser_info', {}).get('is_browser'):
                    program_totals[process_name]['browser_info'] = data['browser_info']
                
                total_session_time += data['total_time']
        
        # Convert to summary format
        summary = []
        for process_name, data in program_totals.items():
            if data['total_time'] > 0:
                entry = {
                    'process_name': process_name,
                    'window_title': list(data['window_titles'])[0] if data['window_titles'] else '',
                    'all_window_titles': list(data['window_titles']),
                    'total_time_seconds': round(data['total_time'], 2),
                    'total_time_formatted': self._format_duration(data['total_time']),
                    'browser_info': data['browser_info'],
                    'session_count': len(data['sessions'])
                }
                summary.append(entry)
        
        # Sort by total time (descending)
        summary.sort(key=lambda x: x['total_time_seconds'], reverse=True)
        
        return {
            'total_session_time': round(total_session_time, 2),
            'total_session_time_formatted': self._format_duration(total_session_time),
            'applications': summary,
            'tracking_active': self.tracking,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_detailed_report(self):
        """Get detailed report with all sessions"""
        summary = self.get_session_summary()
        
        detailed_apps = []
        for window_key, data in self.session_data.items():
            if data['total_time'] > 0:
                app_detail = {
                    'process_name': data['process_name'],
                    'window_title': data['window_title'],
                    'total_time_seconds': round(data['total_time'], 2),
                    'total_time_formatted': self._format_duration(data['total_time']),
                    'browser_info': data.get('browser_info', {}),
                    'sessions': data['sessions']
                }
                detailed_apps.append(app_detail)
        
        # Sort by total time (descending)
        detailed_apps.sort(key=lambda x: x['total_time_seconds'], reverse=True)
        
        return {
            'summary': summary,
            'detailed_applications': detailed_apps
        }
    
    def _format_duration(self, seconds):
        """Format duration in human readable format"""
        if seconds < 60:
            return f"{int(seconds)}s"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            secs = int(seconds % 60)
            return f"{minutes}m {secs}s"
        else:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            secs = int(seconds % 60)
            return f"{hours}h {minutes}m {secs}s"
    
    def reset_session(self):
        """Reset tracking data for new session"""
        self.session_data.clear()
        self.current_window = None
        self.start_time = None
        print("🔄 Session data reset")

# Global tracker instance
_tracker_instance = None

def get_tracker():
    """Get global tracker instance"""
    global _tracker_instance
    if _tracker_instance is None:
        _tracker_instance = ActiveWindowTracker()
    return _tracker_instance

def start_active_window_tracking():
    """Start active window tracking"""
    global window_tracker
    window_tracker = get_tracker()
    window_tracker.start_tracking()
    return window_tracker

def stop_active_window_tracking():
    """Stop active window tracking"""
    global window_tracker
    if window_tracker:
        window_tracker.stop_tracking()
    return window_tracker

def upload_current_activity_to_s3(email, task_name="General_Activity"):
    """
    Upload current activity tracking data to S3
    
    Args:
        email: User email for S3 path structure
        task_name: Task name for filename (default: "General_Activity")
        
    Returns:
        str: S3 URL if successful, None if failed
    """
    global window_tracker
    
    if window_tracker is None:
        logger.warning("⚠️  Activity tracker not initialized")
        return None
    
    try:
        # Get activity data for export
        activity_data = window_tracker.get_activity_export_data()
        
        # Import here to avoid circular imports
        from .s3_uploader import upload_activity_data_direct
        
        # Upload to S3 with task name
        s3_url = upload_activity_data_direct(activity_data, email, task_name)
        
        if s3_url:
            logger.info("✅ Activity data uploaded to S3: %s", s3_url)
        else:
            logger.error("❌ Failed to upload activity data to S3")
            
        return s3_url
        
    except Exception as e:
        logger.error("❌ Error uploading activity data: %s", e)
        return None


def get_current_activity_summary():
    """Get current activity summary"""
    global window_tracker
    if window_tracker is None:
        window_tracker = get_tracker()
    return window_tracker.get_session_summary()

def get_detailed_activity_report():
    """Get detailed activity report"""
    tracker = get_tracker()
    return tracker.get_detailed_report()

if __name__ == "__main__":
    # Test the tracker
    print("🧪 Testing Active Window Tracker")
    tracker = start_active_window_tracking()
    
    try:
        # Track for 30 seconds
        for i in range(30):
            time.sleep(1)
            if i % 5 == 0:
                summary = get_current_activity_summary()
                print(f"\n📊 Current summary (after {i+1}s):")
                for app in summary['applications'][:3]:  # Top 3
                    print(f"  {app['process_name']}: {app['total_time_formatted']}")
    
    except KeyboardInterrupt:
        print("\n⏹️ Stopping tracker...")
    
    finally:
        stop_active_window_tracking()
        final_report = get_detailed_activity_report()
        print(f"\n📋 Final Report:")
        print(f"Total session time: {final_report['summary']['total_session_time_formatted']}")
        for app in final_report['summary']['applications']:
            print(f"  {app['process_name']}: {app['total_time_formatted']}")
