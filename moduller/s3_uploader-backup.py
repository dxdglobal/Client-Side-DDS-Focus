from datetime import datetime
from pathlib import Path
import logging
import boto3, os

logger = logging.getLogger(__name__)
def upload_screenshot(local_path, email, task_name):
    logger.info("📤 [upload_screenshot] started")


    try:
        import boto3
        logger.info("✅ boto3 import: OK")
    except Exception as e:
        logger.error("❌ boto3 import failed: %s", e)
        return None



    access_key = os.getenv("AWS_ACCESS_KEY_ID")
    secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    bucket = os.getenv("S3_BUCKET_NAME")
    region = os.getenv("AWS_REGION")

    filename = Path(local_path).name
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    safe_email = email.replace("@", "_at_")
    safe_task = task_name.replace(" ", "_").replace("/", "_")

    s3_key = f"screenshots/{safe_email}/{safe_task}/{timestamp}_{filename}"

    print(f" Uploading: {local_path}")
    print(f" Email: {email}")
    print(f" Task Name: {task_name}")
    print(f" Bucket: {bucket}")
    print(f" S3 Key: {s3_key}")

    try:
        session = boto3.Session(
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region
        )
        s3 = session.client('s3')
        s3.upload_file(str(local_path), bucket, s3_key)

        url = f"https://{bucket}.s3.{region}.amazonaws.com/{s3_key}"
        print(f" Successfully uploaded to: {url}")
        return url
    except Exception as e:
        print(f" Upload failed: {e}")
        return None

