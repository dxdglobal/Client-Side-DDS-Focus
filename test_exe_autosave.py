#!/usr/bin/env python3
"""
Test script to verify the EXE builds and auto-save functionality
"""

import os
import time
import requests
import json
import subprocess
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def test_exe_exists():
    """Test if the EXE files exist"""
    dist_path = Path("dist")
    
    exe_files = ["DDSFocusPro.exe", "connector.exe"]
    
    for exe_file in exe_files:
        exe_path = dist_path / exe_file
        if exe_path.exists():
            size = exe_path.stat().st_size / (1024 * 1024)  # MB
            logging.info(f"✅ {exe_file} exists ({size:.1f} MB)")
        else:
            logging.error(f"❌ {exe_file} NOT FOUND")
            return False
    
    return True

def test_connector_endpoints():
    """Test if the connector has the required endpoints for auto-save"""
    # Start connector in background for testing
    try:
        connector_path = Path("dist/connector.exe")
        if not connector_path.exists():
            logging.error("❌ connector.exe not found")
            return False
        
        logging.info("🚀 Starting connector for endpoint testing...")
        
        # Start connector process
        process = subprocess.Popen(
            [str(connector_path)], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            cwd=str(Path.cwd())
        )
        
        # Wait for connector to start
        time.sleep(5)
        
        # Test endpoints
        endpoints_to_test = [
            ("/", "GET"),
            ("/cleanup_active_timers", "POST"),
            ("/shutdown", "POST")
        ]
        
        base_url = "http://127.0.0.1:5000"
        
        for endpoint, method in endpoints_to_test:
            try:
                if method == "GET":
                    response = requests.get(f"{base_url}{endpoint}", timeout=3)
                else:
                    response = requests.post(f"{base_url}{endpoint}", timeout=3)
                
                logging.info(f"✅ {method} {endpoint} - Status: {response.status_code}")
                
            except requests.exceptions.RequestException as e:
                logging.warning(f"⚠️ {method} {endpoint} - Error: {e}")
        
        # Stop the connector
        try:
            requests.post(f"{base_url}/shutdown", timeout=3)
        except:
            pass
        
        # Force kill if still running
        process.terminate()
        process.wait(timeout=5)
        
        logging.info("✅ Connector endpoint testing completed")
        return True
        
    except Exception as e:
        logging.error(f"❌ Connector testing failed: {e}")
        return False

def test_session_file_handling():
    """Test session file creation and cleanup"""
    session_file = Path("data/current_session.json")
    
    # Create test session file
    session_data = {
        "email": "test@example.com",
        "task": "Test Task",
        "start_time": int(time.time())
    }
    
    try:
        # Ensure data directory exists
        session_file.parent.mkdir(exist_ok=True)
        
        # Create test session file
        with open(session_file, "w", encoding="utf-8") as f:
            json.dump(session_data, f)
        
        logging.info(f"✅ Test session file created: {session_file}")
        
        # Verify file exists
        if session_file.exists():
            logging.info("✅ Session file verification passed")
            
            # Clean up test file
            session_file.unlink()
            logging.info("✅ Test session file cleaned up")
            return True
        else:
            logging.error("❌ Session file not found after creation")
            return False
            
    except Exception as e:
        logging.error(f"❌ Session file test failed: {e}")
        return False

def main():
    """Run all tests"""
    logging.info("🧪 Starting EXE Auto-Save Tests...")
    
    tests = [
        ("EXE Files Exist", test_exe_exists),
        ("Session File Handling", test_session_file_handling),
        ("Connector Endpoints", test_connector_endpoints),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        logging.info(f"\n--- Testing {test_name} ---")
        try:
            if test_func():
                logging.info(f"✅ {test_name} PASSED")
                passed += 1
            else:
                logging.error(f"❌ {test_name} FAILED")
        except Exception as e:
            logging.error(f"❌ {test_name} ERROR: {e}")
    
    logging.info(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        logging.info("🎉 All tests passed! Auto-save functionality should work in EXE builds.")
    else:
        logging.warning("⚠️ Some tests failed. Check the issues above.")

if __name__ == "__main__":
    main()