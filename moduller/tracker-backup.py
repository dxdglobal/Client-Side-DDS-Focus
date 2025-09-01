from datetime import datetime
from pathlib import Path
import logging
import boto3
import os

logger = logging.getLogger(__name__)

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
    safe_email = email.replace("@", "_at_")
    safe_task = task_name.replace(" ", "_").replace("/", "_")
    s3_key = f"logs/{safe_email}/{safe_task}/{timestamp}_{filename}"

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
