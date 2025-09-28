#!/usr/bin/env python3
"""
AWS S3 Credentials Test Script
Test your AWS credentials before using them in the main application
"""

import boto3
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_aws_credentials():
    """Test AWS S3 credentials"""
    print("🔐 Testing AWS S3 Credentials...")
    print("=" * 50)
    
    # Get credentials from environment
    access_key = os.getenv('S3_ACCESS_KEY')
    secret_key = os.getenv('S3_SECRET_KEY')
    region = os.getenv('S3_REGION', 'us-east-1')
    bucket = os.getenv('S3_BUCKET_NAME', 'ddsfocustime')
    
    # Show credential info (masked)
    print(f"🔑 Access Key: {access_key[:8]}*** (length: {len(access_key)})")
    print(f"🗝️  Secret Key: ****** (length: {len(secret_key)})")
    print(f"🌍 Region: {region}")
    print(f"🪣 Bucket: {bucket}")
    print("-" * 50)
    
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
        
        # Test S3 connection
        s3 = session.client('s3')
        
        print("🔄 Testing S3 connection...")
        
        # Try to list bucket contents (this tests both auth and permissions)
        response = s3.list_objects_v2(Bucket=bucket, MaxKeys=1)
        
        print("✅ SUCCESS: AWS credentials are valid!")
        print(f"✅ S3 bucket '{bucket}' is accessible")
        print(f"✅ Found {response.get('KeyCount', 0)} objects in bucket")
        
        # Test upload permission by uploading a tiny test file
        test_key = "test_credentials_check.txt"
        test_content = "AWS credentials test - you can delete this file"
        
        s3.put_object(
            Bucket=bucket,
            Key=test_key,
            Body=test_content.encode(),
            ContentType='text/plain'
        )
        
        print("✅ SUCCESS: Upload permission confirmed!")
        print(f"✅ Test file uploaded: {test_key}")
        
        # Clean up test file
        s3.delete_object(Bucket=bucket, Key=test_key)
        print("✅ Test file cleaned up")
        
        return True
        
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        
        if "InvalidAccessKeyId" in str(e):
            print("💡 Solution: Your Access Key ID is invalid or doesn't exist")
            print("   1. Go to AWS Console → IAM → Users")
            print("   2. Select your user → Security Credentials")
            print("   3. Create new Access Key")
            print("   4. Update S3_ACCESS_KEY in .env file")
            
        elif "SignatureDoesNotMatch" in str(e):
            print("💡 Solution: Your Secret Access Key is incorrect")
            print("   1. Double-check S3_SECRET_KEY in .env file")
            print("   2. Generate new credentials if needed")
            
        elif "AccessDenied" in str(e):
            print("💡 Solution: Your AWS user lacks S3 permissions")
            print("   1. Add S3 policy to your IAM user:")
            print("   2. AmazonS3FullAccess (or custom S3 policy)")
            
        elif "NoSuchBucket" in str(e):
            print("💡 Solution: S3 bucket doesn't exist")
            print(f"   1. Create bucket '{bucket}' in AWS Console")
            print(f"   2. Or update S3_BUCKET_NAME in .env file")
            
        return False

if __name__ == "__main__":
    test_aws_credentials()