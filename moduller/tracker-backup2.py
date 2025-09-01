import os
import json
import logging
from datetime import datetime
from pathlib import Path
import boto3
from typing import Optional, List, Dict

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# AWS Credentials and config from environment variables
ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
BUCKET = os.getenv("S3_BUCKET_NAME", "ddsfocustime")
REGION = os.getenv("AWS_REGION", "us-east-1")


def logs_file(email: str, task_name: str, program_history: List[Dict[str, str]]) -> Optional[str]:
    """
    Processes program usage history, creates a summary JSON file,
    uploads it to AWS S3, and returns the uploaded file URL.

    Args:
        email (str): User email, used in path naming.
        task_name (str): Task name, used in path naming.
        program_history (list): List of dicts with keys 'program', 'start', 'end'.
            'start' and 'end' should be datetime strings in ISO format.

    Returns:
        Optional[str]: S3 URL of uploaded summary JSON or None if failed.
    """

    logger.info("Started processing logs for upload...")

    # 1) Summarize total usage time per program in seconds
    usage_summary = {}

    for entry in program_history:
        program = entry.get('program')
        start_str = entry.get('start')
        end_str = entry.get('end')
        if not program or not start_str or not end_str:
            logger.warning(f"Skipping invalid entry: {entry}")
            continue

        try:
            start_dt = datetime.fromisoformat(start_str)
            end_dt = datetime.fromisoformat(end_str)
        except Exception as e:
            logger.warning(f"Invalid datetime format in entry {entry}: {e}")
            continue

        duration_sec = (end_dt - start_dt).total_seconds()
        if duration_sec < 0:
            logger.warning(f"Negative duration for entry {entry}, skipping.")
            continue

        usage_summary[program] = usage_summary.get(program, 0) + duration_sec

    # 2) Format summary for JSON output (HH:MM:SS)
    def format_seconds(seconds: float) -> str:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"

    formatted_summary = {
        prog: {
            "total_seconds": int(seconds),
            "formatted": format_seconds(seconds)
        }
        for prog, seconds in usage_summary.items()
    }

    # 3) Prepare local JSON file path
    safe_email = email.replace("@", "_at_")
    safe_task = task_name.replace(" ", "_").replace("/", "_")
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"{timestamp}_usage_summary.json"

    base_dir = Path("logs") / safe_email / safe_task
    base_dir.mkdir(parents=True, exist_ok=True)

    local_path = base_dir / filename

    # 4) Write JSON summary locally
    with open(local_path, "w", encoding="utf-8") as f:
        json.dump(formatted_summary, f, indent=2, ensure_ascii=False)

    logger.info(f"Local usage summary JSON saved at {local_path}")

    # 5) Upload to S3
    s3_key = f"logs/{safe_email}/{safe_task}/{filename}"

    try:
        session = boto3.Session(
            aws_access_key_id=ACCESS_KEY,
            aws_secret_access_key=SECRET_KEY,
            region_name=REGION
        )
        s3 = session.client('s3')
        s3.upload_file(str(local_path), BUCKET, s3_key)

        url = f"https://{BUCKET}.s3.{REGION}.amazonaws.com/{s3_key}"
        logger.info(f"✅ Upload successful: {url}")
        return url
    except Exception as e:
        logger.error(f"❌ Upload failed: {e}")
        return None


# Example usage (for testing only)
if __name__ == "__main__":
    sample_history = [
        {"program": "YouTube", "start": "2025-06-10T09:00:00", "end": "2025-06-10T09:30:00"},
        {"program": "Chrome", "start": "2025-06-10T09:30:00", "end": "2025-06-10T10:00:00"},
        {"program": "YouTube", "start": "2025-06-10T10:00:00", "end": "2025-06-10T10:15:00"},
        {"program": "Slack", "start": "2025-06-10T10:15:00", "end": "2025-06-10T10:45:00"},
    ]

    email = "user@example.com"
    task_name = "Daily Task"

    url = logs_file(email, task_name, sample_history)
    print("Uploaded log URL:", url)
