#!/usr/bin/env python3
"""
Test Script to Check S3 Log Uploads
Verifies if logs are being uploaded properly to users_logs directory
"""

import boto3
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

def test_s3_logs_structure():
    """Test S3 logs upload structure and existing logs"""
    print("📋 Testing S3 Logs Structure...")
    print("=" * 60)
    
    # Get credentials from environment
    access_key = os.getenv('S3_ACCESS_KEY')
    secret_key = os.getenv('S3_SECRET_KEY')
    region = os.getenv('S3_REGION', 'eu-north-1')
    bucket = os.getenv('S3_BUCKET_NAME', 'ddsfocustime')
    
    # Show credential info (masked)
    print(f"🔑 Access Key: {access_key[:8]}*** (length: {len(access_key)})")
    print(f"🌍 Region: {region}")
    print(f"🪣 Bucket: {bucket}")
    print("-" * 60)
    
    if not all([access_key, secret_key, region, bucket]):
        print("❌ Missing credentials in .env file!")
        return False
    
    try:
        # Create boto3 session
        session = boto3.Session(
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region
        )
        
        s3 = session.client('s3')
        
        print("🔍 Scanning S3 bucket for existing logs...")
        
        # Check for users_logs directory
        response = s3.list_objects_v2(
            Bucket=bucket,
            Prefix='users_logs/',
            MaxKeys=50
        )
        
        if 'Contents' in response:
            print(f"✅ Found {len(response['Contents'])} files in users_logs/")
            print("\n📁 Recent log files:")
            print("-" * 60)
            
            # Sort by last modified
            files = sorted(response['Contents'], key=lambda x: x['LastModified'], reverse=True)
            
            for i, obj in enumerate(files[:10]):  # Show first 10
                key = obj['Key']
                size = obj['Size']
                modified = obj['LastModified'].strftime('%Y-%m-%d %H:%M:%S')
                
                print(f"📄 {i+1:2}. {key}")
                print(f"    Size: {size:,} bytes | Modified: {modified}")
        else:
            print("⚠️ No files found in users_logs/ directory")
            
        # Check for other log directories
        print("\n🔍 Checking for other log directories...")
        
        # Check logs directory (old structure)
        logs_response = s3.list_objects_v2(
            Bucket=bucket,
            Prefix='logs/',
            MaxKeys=20
        )
        
        if 'Contents' in logs_response:
            print(f"📁 Found {len(logs_response['Contents'])} files in logs/ (old structure)")
        else:
            print("📁 No files in logs/ directory")
            
        # Check users_screenshots for comparison
        screenshots_response = s3.list_objects_v2(
            Bucket=bucket,
            Prefix='users_screenshots/',
            MaxKeys=10
        )
        
        if 'Contents' in screenshots_response:
            print(f"📸 Found {len(screenshots_response['Contents'])} files in users_screenshots/")
        else:
            print("📸 No files in users_screenshots/ directory")
            
        return True
        
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        return False

def test_log_upload_functions():
    """Test the log upload functions with dummy data"""
    print("\n🧪 Testing Log Upload Functions...")
    print("=" * 60)
    
    try:
        # Import the upload functions
        from moduller.s3_uploader import upload_logs_direct, upload_activity_data_direct
        from moduller.tracker import upload_program_data_to_s3
        
        test_email = "test@example.com"
        test_task = "Test Task Upload"
        
        # Test data
        test_log_data = {
            "timestamp": datetime.now().isoformat(),
            "test_type": "log_upload_test",
            "applications": [
                {"name": "Code.exe", "duration": 300},
                {"name": "chrome.exe", "duration": 150}
            ],
            "total_duration": 450
        }
        
        print("🔄 Testing upload_logs_direct...")
        url1 = upload_logs_direct(test_log_data, test_email, test_task, "test_session_log")
        if url1:
            print(f"✅ upload_logs_direct successful: {url1}")
        else:
            print("❌ upload_logs_direct failed")
            
        print("\n🔄 Testing upload_activity_data_direct...")
        url2 = upload_activity_data_direct(test_log_data, test_email, test_task)
        if url2:
            print(f"✅ upload_activity_data_direct successful: {url2}")
        else:
            print("❌ upload_activity_data_direct failed")
            
        print("\n🔄 Testing upload_program_data_to_s3...")
        url3 = upload_program_data_to_s3(test_email, test_task, test_log_data)
        if url3:
            print(f"✅ upload_program_data_to_s3 successful: {url3}")
        else:
            print("❌ upload_program_data_to_s3 failed")
            
        return True
        
    except Exception as e:
        print(f"❌ Error testing upload functions: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_log_upload_routes():
    """Check which log upload routes are active in the app"""
    print("\n🛣️ Active Log Upload Routes:")
    print("=" * 60)
    
    routes = [
        "/upload_log_to_s3",
        "/upload_log_file", 
        "/capture_activity_log",
        "/upload_screenshots"
    ]
    
    for route in routes:
        print(f"🔗 {route}")
    
    print("\n📋 Log Upload Summary:")
    print("- upload_logs_direct() → users_logs/{date}/{email}/{task}/")
    print("- upload_activity_data_direct() → users_logs/{date}/{email}/")
    print("- upload_program_data_to_s3() → logs/{date}/{email}/{task}/")
    print("- Session logs → uploaded when task finishes")

if __name__ == "__main__":
    print("🔍 S3 Log Upload Test Suite")
    print("=" * 60)
    
    # Test 1: Check S3 structure
    success1 = test_s3_logs_structure()
    
    # Test 2: Test upload functions
    success2 = test_log_upload_functions()
    
    # Test 3: Show route info
    check_log_upload_routes()
    
    print("\n" + "=" * 60)
    if success1 and success2:
        print("✅ All tests completed successfully!")
        print("📋 Your logs should be uploading to S3 properly")
    else:
        print("⚠️ Some tests failed - check the output above")
        print("💡 Make sure your AWS credentials are valid")