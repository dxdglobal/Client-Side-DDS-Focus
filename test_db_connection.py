#!/usr/bin/env python3
"""
Simple database connection test for DDSFocusPro
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("=== DDSFocusPro Database Connection Test ===")
print(f"Current working directory: {os.getcwd()}")
print(f"Python executable: {sys.executable}")

# Check if .env file exists
env_file = '.env'
if os.path.exists(env_file):
    print(f"[SUCCESS] .env file found at: {os.path.abspath(env_file)}")
else:
    print(f"[ERROR] .env file not found at: {os.path.abspath(env_file)}")

# Print environment variables
print("\n=== Environment Variables ===")
env_vars = ['DB_HOST', 'DB_USER', 'DB_PASSWORD', 'DB_NAME', 'DB_PORT']
for var in env_vars:
    value = os.getenv(var)
    if value:
        if var == 'DB_PASSWORD':
            print(f"{var}: {'*' * len(value)}")  # Hide password
        else:
            print(f"{var}: {value}")
    else:
        print(f"{var}: [NOT SET]")

# Test database connection
print("\n=== Database Connection Test ===")
try:
    from moduller.veritabani_yoneticisi import VeritabaniYoneticisi
    
    print("Attempting to create database connection...")
    db = VeritabaniYoneticisi()
    
    print("Attempting to connect to database...")
    db.baglanti_olustur()
    
    if db.baglanti_testi():
        print("[SUCCESS] Database connection successful!")
        
        # Test a simple query
        try:
            result = db.sorgu_calistir("SELECT 1 as test")
            if result:
                print(f"[SUCCESS] Test query executed successfully: {result}")
            else:
                print("[WARNING] Test query returned no results")
        except Exception as query_error:
            print(f"[ERROR] Test query failed: {query_error}")
        
        db.kapat()
    else:
        print("[ERROR] Database connection failed")
        
except ImportError as e:
    print(f"[ERROR] Failed to import database module: {e}")
except Exception as e:
    print(f"[ERROR] Database connection test failed: {e}")

print("\n=== Test Complete ===")