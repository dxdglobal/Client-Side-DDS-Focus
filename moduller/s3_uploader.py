from datetime import datetime
from pathlib import Path
import logging
import boto3
import os
import io
import json
from .config_manager import config_manager
import io
import json
from .config_manager import config_manager

logger = logging.getLogger(__name__)

def upload_activity_data_direct(activity_data, email, task_name, file_extension="json"):
    """
    Upload activity tracking data directly to S3 following screenshot pattern
    Structure: logs/{date}/{email}/activity_{task_name}_{timestamp}.json (one file per session)
    
    Args:
        activity_data: Dictionary containing activity tracking data
        email: User email
        task_name: Task name for filename
        file_extension: File extension (default: "json")
    
    Returns:
        str: S3 URL if successful, None if failed
    """
    logger.info("📤 [upload_activity_data_direct] started")

    # Get S3 credentials from configuration manager (same as screenshots)
    s3_config = config_manager.get_s3_credentials()
    access_key = s3_config.get("access_key")
    secret_key = s3_config.get("secret_key")
    bucket = s3_config.get("bucket_name", "ddsfocustime")
    region = s3_config.get("region", "us-east-1")

    logger.info("🔐 Using S3 config from configuration manager")
    logger.info("🪣 S3_BUCKET_NAME: %s", bucket)
    logger.info("🌍 AWS_REGION: %s", region)

    # Check if credentials are missing
    if not all([access_key, secret_key, bucket, region]):
        logger.error("❌ One or more AWS environment variables are missing.")
        return None

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    date_folder = datetime.now().strftime("%Y-%m-%d")
    safe_email = email.replace("@", "_at_")
    safe_task_name = task_name.replace(" ", "_").replace("/", "_")
    filename = f"activity_{safe_task_name}_{timestamp}.{file_extension}"
    
    # Structure: users_logs/{date}/{email}/{task}/activity_{timestamp}.json (consistent with screenshot structure)
    s3_key = f"users_logs/{date_folder}/{safe_email}/{safe_task_name}/{filename}"

    logger.info("👤 Email: %s", email)
    logger.info("📋 Task: %s", task_name)
    logger.info("📊 Activity Data: %d applications tracked", len(activity_data.get('applications', [])))
    logger.info("☁️ S3 key: %s", s3_key)

    try:
        # Convert activity data to JSON
        if isinstance(activity_data, dict) or isinstance(activity_data, list):
            activity_content = json.dumps(activity_data, indent=2, ensure_ascii=False)
        else:
            activity_content = str(activity_data)
        
        activity_bytes = activity_content.encode('utf-8')

        session = boto3.Session(
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region
        )
        s3 = session.client('s3')
        
        # Upload activity data directly to S3
        s3.put_object(
            Bucket=bucket,
            Key=s3_key,
            Body=activity_bytes,
            ContentType='application/json'
        )

        url = f"https://{bucket}.s3.{region}.amazonaws.com/{s3_key}"
        logger.info("✅ Activity data upload successful: %s", url)
        return url
    except Exception as e:
        logger.error("❌ Activity data upload failed: %s", e)
        return None


def upload_logs_direct(log_data, email, task_name, log_type="session_log", file_extension="json"):
    """
    Upload logs directly to S3 following the same pattern as screenshots
    
    Args:
        log_data: Dictionary or string containing the log data
        email: User email
        task_name: Task name
        log_type: Type of log (default: "session_log")
        file_extension: File extension (default: "json")
    
    Returns:
        str: S3 URL if successful, None if failed
    """
    logger.info("📤 [upload_logs_direct] started")

    # Get S3 credentials from configuration manager (same as screenshots)
    s3_config = config_manager.get_s3_credentials()
    access_key = s3_config.get("access_key")
    secret_key = s3_config.get("secret_key")
    bucket = s3_config.get("bucket_name", "ddsfocustime")
    region = s3_config.get("region", "us-east-1")

    logger.info("🔐 Using S3 config from configuration manager")
    logger.info("🪣 S3_BUCKET_NAME: %s", bucket)
    logger.info("🌍 AWS_REGION: %s", region)

    # Check if credentials are missing
    if not all([access_key, secret_key, bucket, region]):
        logger.error("❌ One or more AWS environment variables are missing.")
        return None

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    date_folder = datetime.now().strftime("%Y-%m-%d")
    safe_email = email.replace("@", "_at_")
    safe_task = task_name.replace(" ", "_").replace("/", "_")
    filename = f"{log_type}_{timestamp}.{file_extension}"
    
    # Use the same structure as users_screenshots but with users_logs
    s3_key = f"users_logs/{date_folder}/{safe_email}/{safe_task}/{filename}"

    logger.info("👤 Email: %s", email)
    logger.info("📝 Task: %s", task_name)
    logger.info("📋 Log Type: %s", log_type)
    logger.info("☁️ S3 key: %s", s3_key)

    try:
        # Convert log data to JSON if it's a dictionary
        if isinstance(log_data, dict) or isinstance(log_data, list):
            log_content = json.dumps(log_data, indent=2, ensure_ascii=False)
        else:
            log_content = str(log_data)
        
        log_bytes = log_content.encode('utf-8')

        session = boto3.Session(
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region
        )
        s3 = session.client('s3')
        
        # Upload log data directly to S3
        s3.put_object(
            Bucket=bucket,
            Key=s3_key,
            Body=log_bytes,
            ContentType='application/json'
        )

        url = f"https://{bucket}.s3.{region}.amazonaws.com/{s3_key}"
        logger.info("✅ Log upload successful: %s", url)
        return url
    except Exception as e:
        logger.error("❌ Log upload failed: %s", e)
        return None


def upload_screenshot_direct(image_bytes, email, task_name, file_extension="webp"):
    """
    Upload screenshot directly to S3 without saving to local file first
    
    Args:
        image_bytes: Raw image bytes (from PIL image.save() or similar)
        email: User email
        task_name: Task name
        file_extension: File extension (default: webp)
    
    Returns:
        str: S3 URL if successful, None if failed
    """
    logger.info("📤 [upload_screenshot_direct] started")

    # Get S3 credentials from configuration manager
    s3_config = config_manager.get_s3_credentials()
    access_key = s3_config.get("access_key")
    secret_key = s3_config.get("secret_key")
    bucket = s3_config.get("bucket_name", "ddsfocustime")
    region = s3_config.get("region", "us-east-1")

    logger.info("🔐 Using S3 config from configuration manager")
    logger.info("🪣 S3_BUCKET_NAME: %s", bucket)
    logger.info("🌍 AWS_REGION: %s", region)
    logger.info("🔑 ACCESS_KEY (first 8 chars): %s***", access_key[:8] if access_key else "None")
    logger.info("🗝️ SECRET_KEY (length): %d chars", len(secret_key) if secret_key else 0)

    # Check if credentials are missing
    if not all([access_key, secret_key, bucket, region]):
        logger.error("❌ One or more AWS environment variables are missing.")
        logger.error("❌ access_key: %s", "Present" if access_key else "Missing")
        logger.error("❌ secret_key: %s", "Present" if secret_key else "Missing")
        logger.error("❌ bucket: %s", "Present" if bucket else "Missing")
        logger.error("❌ region: %s", "Present" if region else "Missing")
        return None

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    date_folder = datetime.now().strftime("%Y-%m-%d")
    safe_email = email.replace("@", "_at_")
    safe_task = task_name.replace(" ", "_").replace("/", "_")
    filename = f"{timestamp}.{file_extension}"
    s3_key = f"users_screenshots/{date_folder}/{safe_email}/{safe_task}/{filename}"

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
        
        # Upload bytes directly to S3
        s3.put_object(
            Bucket=bucket,
            Key=s3_key,
            Body=image_bytes,
            ContentType=f'image/{file_extension}'
        )

        url = f"https://{bucket}.s3.{region}.amazonaws.com/{s3_key}"
        logger.info("✅ Direct upload successful: %s", url)
        return url
    except Exception as e:
        if "InvalidAccessKeyId" in str(e):
            logger.error("❌ AWS ACCESS KEY INVALID: %s", str(e))
            logger.error("🔑 Please update your AWS credentials in .env file:")
            logger.error("   - Generate new Access Key in AWS IAM Console")
            logger.error("   - Update S3_ACCESS_KEY and S3_SECRET_KEY in .env")
            logger.error("   - Restart the application")
        else:
            logger.error("❌ Direct upload failed: %s", e)
        return None

def upload_screenshot(local_path, email, task_name):
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
    s3_key = f"users_screenshots/{date_folder}/{safe_email}/{safe_task}/{timestamp}_{filename}"

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


def upload_daily_log_file_to_s3(email, date, daily_log, task_name="general"):
    """
    Upload/create the main daily log file to S3 following users_screenshots pattern
    Structure: logs/{date_folder}/{safe_email}/{safe_task}/{timestamp}_{filename}
    Returns the S3 URL if successful, None if failed
    """
    try:
        s3_client = get_s3_client()
        if not s3_client:
            return None
            
        # Follow the same pattern as users_screenshots
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        date_folder = datetime.now().strftime("%Y-%m-%d")
        safe_email = email.replace('@', '_at_').replace('.', '_')
        
        # Skip the default task selection - use "general" instead
        if task_name in ["-- İş Emri Seçin --", "-- Select a Task --", "--_İş_Emri_Seçin_--"]:
            task_name = "general"
            
        safe_task = task_name.replace(" ", "_").replace("/", "_")
        filename = f"daily_log_{timestamp}.json"
        
        # Use the same structure as users_screenshots but with logs/
        s3_key = f"logs/{date_folder}/{safe_email}/{safe_task}/{filename}"
        
        # Convert daily log to JSON
        log_json = json.dumps(daily_log, indent=2, ensure_ascii=False)
        
        # Upload to S3
        s3_client.put_object(
            Bucket=S3_BUCKET_NAME,
            Key=s3_key,
            Body=log_json.encode('utf-8'),
            ContentType='application/json'
        )
        
        s3_url = f"https://{S3_BUCKET_NAME}.s3.{S3_REGION}.amazonaws.com/{s3_key}"
        print(f"📋 Daily log file created in S3: {s3_url}")
        return s3_url
        
    except Exception as e:
        print(f"❌ Failed to upload daily log file to S3: {e}")
        return None


def append_to_daily_log_file(email, activity_entry):
    """
    Append activity to existing daily log file in S3
    Returns the S3 URL if successful, None if failed
    """
    try:
        s3_client = get_s3_client()
        if not s3_client:
            return None
            
        # Get current date
        current_date = datetime.now().strftime("%Y-%m-%d")
        
        # Convert email to safe filename format
        safe_email = email.replace('@', '_at_').replace('.', '_')
        
        # Create S3 key for daily log file
        s3_key = f"logs/{current_date}/{safe_email}/daily_log_{current_date}.json"
        
        try:
            # Try to get existing file
            response = s3_client.get_object(Bucket=S3_BUCKET_NAME, Key=s3_key)
            existing_log = json.loads(response['Body'].read().decode('utf-8'))
        except s3_client.exceptions.NoSuchKey:
            # File doesn't exist, create new structure
            existing_log = {
                "date": current_date,
                "email": email,
                "created_at": datetime.now().isoformat(),
                "activities": []
            }
        
        # Append new activity
        existing_log["activities"].append(activity_entry)
        existing_log["last_updated"] = datetime.now().isoformat()
        
        # Convert back to JSON
        log_json = json.dumps(existing_log, indent=2, ensure_ascii=False)
        
        # Upload updated file back to S3
        s3_client.put_object(
            Bucket=S3_BUCKET_NAME,
            Key=s3_key,
            Body=log_json.encode('utf-8'),
            ContentType='application/json'
        )
        
        s3_url = f"https://{S3_BUCKET_NAME}.s3.{S3_REGION}.amazonaws.com/{s3_key}"
        print(f"📋 Activity appended to daily log: {s3_url}")
        return s3_url
        
    except Exception as e:
        print(f"❌ Failed to append to daily log file: {e}")
        return None


def upload_activity_log_to_s3(email, activity_log, task_name="general"):
    """
    Upload real-time activity log to S3 following users_screenshots pattern
    Structure: logs/{date_folder}/{safe_email}/{safe_task}/{timestamp}_{filename}
    Returns the S3 URL if successful, None if failed
    """
    try:
        s3_client = get_s3_client()
        if not s3_client:
            return None
            
        # Follow the same pattern as users_screenshots
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        date_folder = datetime.now().strftime("%Y-%m-%d")
        safe_email = email.replace('@', '_at_').replace('.', '_')
        
        # Skip the default task selection - use "general" instead
        if task_name in ["-- İş Emri Seçin --", "-- Select a Task --", "--_İş_Emri_Seçin_--"]:
            task_name = "general"
            
        safe_task = task_name.replace(" ", "_").replace("/", "_")
        filename = f"activity_log_{timestamp}.json"
        
        # Add active window information if available
        try:
            from .active_window_tracker import get_current_activity_summary
            window_summary = get_current_activity_summary()
            activity_log['active_windows_summary'] = window_summary
        except ImportError:
            activity_log['active_windows_summary'] = None
        
        # Use the same structure as users_screenshots but with logs/
        s3_key = f"logs/{date_folder}/{safe_email}/{safe_task}/{filename}"
        
        # Convert activity log to JSON
        log_json = json.dumps(activity_log, indent=2, ensure_ascii=False)
        
        # Upload to S3
        s3_client.put_object(
            Bucket=S3_BUCKET_NAME,
            Key=s3_key,
            Body=log_json.encode('utf-8'),
            ContentType='application/json'
        )
        
        s3_url = f"https://{S3_BUCKET_NAME}.s3.{S3_REGION}.amazonaws.com/{s3_key}"
        print(f"📋 Activity log uploaded to S3: {s3_url}")
        return s3_url
        
    except Exception as e:
        print(f"❌ Failed to upload activity log to S3: {e}")
        return None


def upload_program_tracking_to_s3(email, tracking_data, task_name="general"):
    """
    Upload program tracking data to S3 following exact users_screenshots pattern
    Structure: logs/{date_folder}/{safe_email}/{safe_task}/session_{start_time}_to_{end_time}.json
    Returns the S3 URL if successful, None if failed
    """
    try:
        # Get S3 credentials from configuration manager (same as other functions)
        s3_config = config_manager.get_s3_credentials()
        access_key = s3_config.get("access_key")
        secret_key = s3_config.get("secret_key")
        bucket = s3_config.get("bucket_name", "ddsfocustime")
        region = s3_config.get("region", "us-east-1")

        # Check if credentials are missing
        if not all([access_key, secret_key, bucket, region]):
            print("❌ One or more AWS credentials are missing.")
            return None
            
        # Skip the default task selection - use "general" instead
        if task_name in ["-- İş Emri Seçin --", "-- Select a Task --", "--_İş_Emri_Seçin_--"]:
            task_name = "general"
            
        # Create meaningful filename for single session
        date_folder = datetime.now().strftime("%Y-%m-%d")
        safe_email = email.replace('@', '_at_').replace('.', '_')
        safe_task = task_name.replace(" ", "_").replace("/", "_").replace("-", "_")
        
        # Use session start/end times for filename if available
        session_start = tracking_data.get('session_start', datetime.now().isoformat())
        session_end = tracking_data.get('session_end', datetime.now().isoformat())
        
        try:
            start_time = datetime.fromisoformat(session_start.replace('Z', '')).strftime("%H-%M-%S")
            end_time = datetime.fromisoformat(session_end.replace('Z', '')).strftime("%H-%M-%S")
            filename = f"session_{start_time}_to_{end_time}.json"
        except:
            # Fallback to timestamp if parsing fails
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = f"session_{timestamp}.json"
        
        # Use the same structure as users_screenshots but with logs/
        s3_key = f"logs/{date_folder}/{safe_email}/{safe_task}/{filename}"
        
        # Convert tracking data to JSON
        tracking_json = json.dumps(tracking_data, indent=2, ensure_ascii=False)
        
        # Create S3 client and upload
        s3_client = boto3.client(
            's3',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region
        )
        
        # Upload to S3
        s3_client.put_object(
            Bucket=bucket,
            Key=s3_key,
            Body=tracking_json.encode('utf-8'),
            ContentType='application/json'
        )
        
        s3_url = f"https://{bucket}.s3.{region}.amazonaws.com/{s3_key}"
        print(f"📊 Program tracking uploaded to S3: {s3_url}")
        return s3_url
        
    except Exception as e:
        print(f"❌ Failed to upload program tracking to S3: {e}")
        import traceback
        traceback.print_exc()
        return None


def upload_daily_logs_report(email, report_data, report_type="session_complete"):
    """
    Upload daily logs report to S3 in JSON format
    
    S3 Structure: logs/{date}/{email}/daily_activity_report_{timestamp}.json
    
    Args:
        email: User email
        report_data: Dictionary or list containing the log data
        report_type: Type of report (default: "session_complete")
    
    Returns:
        str: S3 URL if successful, None if failed
    """
    logger.info("📤 [upload_daily_logs_report] started")

    # Try to get S3 credentials from configuration manager first
    try:
        s3_config = config_manager.get_s3_credentials()
        access_key = s3_config.get("access_key")
        secret_key = s3_config.get("secret_key")
        bucket = s3_config.get("bucket_name", "ddsfocustime")
        region = s3_config.get("region", "us-east-1")
        logger.info("🔐 Using S3 config from configuration manager")
    except:
        # Fallback to environment variables with standard AWS names
        access_key = os.getenv("AWS_ACCESS_KEY_ID")
        secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        bucket = os.getenv("S3_BUCKET_NAME", "ddsfocustime")
        region = os.getenv("AWS_REGION", "us-east-1")
        logger.info("🔐 Using S3 config from environment variables")

    logger.info("🪣 S3_BUCKET_NAME: %s", bucket)
    logger.info("🌍 AWS_REGION: %s", region)

    # Check if credentials are missing
    if not all([access_key, secret_key, bucket, region]):
        logger.error("❌ One or more AWS environment variables are missing.")
        return None

    # Create timestamp and date folder
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    date_folder = datetime.now().strftime("%Y-%m-%d")
    safe_email = email.replace("@", "_at_").replace(".", "_")
    filename = f"{report_type}_report_{timestamp}.json"
    
    # S3 key structure: logs/date/email/filename.json
    s3_key = f"logs/{date_folder}/{safe_email}/{filename}"

    logger.info("👤 Email: %s", email)
    logger.info("📊 Report Type: %s", report_type)
    logger.info("☁️ S3 key: %s", s3_key)

    try:
        import json
        
        # Convert report data to JSON string
        json_data = json.dumps(report_data, indent=2, ensure_ascii=False)
        json_bytes = json_data.encode('utf-8')

        session = boto3.Session(
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region
        )
        s3 = session.client('s3')
        
        # Upload JSON data directly to S3
        s3.put_object(
            Bucket=bucket,
            Key=s3_key,
            Body=json_bytes,
            ContentType='application/json'
        )

        url = f"https://{bucket}.s3.{region}.amazonaws.com/{s3_key}"
        logger.info("✅ Daily logs report upload successful: %s", url)
        return url
    except Exception as e:
        logger.error("❌ Daily logs report upload failed: %s", e)
        return None


def upload_employee_logs_batch(employees_logs_data, report_date=None):
    """
    Upload logs for multiple employees in batch
    
    Args:
        employees_logs_data: Dict with email as key and logs data as value
        report_date: Date string (YYYY-MM-DD), defaults to today
    
    Returns:
        list: List of uploaded URLs and status
    """
    logger.info("📤 [upload_employee_logs_batch] started")
    
    if report_date is None:
        report_date = datetime.now().strftime("%Y-%m-%d")
    
    results = []
    
    for email, logs_data in employees_logs_data.items():
        try:
            # Add metadata to logs
            enhanced_logs = {
                "report_date": report_date,
                "employee_email": email,
                "generated_at": datetime.now().isoformat(),
                "total_entries": len(logs_data) if isinstance(logs_data, list) else 1,
                "data": logs_data
            }
            
            url = upload_daily_logs_report(enhanced_logs, email, "daily_activity")
            
            if url:
                results.append({
                    "email": email,
                    "status": "success",
                    "url": url,
                    "entries_count": enhanced_logs["total_entries"]
                })
                logger.info("✅ Uploaded logs for %s: %d entries", email, enhanced_logs["total_entries"])
            else:
                results.append({
                    "email": email,
                    "status": "failed",
                    "url": None,
                    "error": "Upload failed"
                })
                logger.error("❌ Failed to upload logs for %s", email)
                
        except Exception as e:
            results.append({
                "email": email,
                "status": "error",
                "url": None,
                "error": str(e)
            })
            logger.error("❌ Error processing logs for %s: %s", email, e)
    
    logger.info("📊 Batch upload complete: %d employees processed", len(results))
    return results
