#!/usr/bin/env python3
"""
Test script for DXD Global Styling API
API URL: https://dxdtime.ddsolutions.io/api/styling/global/
"""

import requests
import json
import time
from datetime import datetime

def test_styling_api():
    """Test the global styling API endpoint"""
    
    api_url = "https://dxdtime.ddsolutions.io/api/styling/global/"
    
    print(f"🔍 Testing API: {api_url}")
    print("=" * 60)
    
    try:
        # Test 1: GET Request
        print("📡 Testing GET request...")
        start_time = time.time()
        
        response = requests.get(api_url, timeout=10)
        
        end_time = time.time()
        response_time = round((end_time - start_time) * 1000, 2)
        
        print(f"✅ Status Code: {response.status_code}")
        print(f"⏱️  Response Time: {response_time}ms")
        print(f"📏 Content Length: {len(response.content)} bytes")
        print(f"🌐 Headers: {dict(response.headers)}")
        
        # Try to parse as JSON
        try:
            json_data = response.json()
            print(f"📄 JSON Response:")
            print(json.dumps(json_data, indent=2, ensure_ascii=False))
        except ValueError:
            print(f"📄 Text Response:")
            print(response.text[:1000])  # First 1000 characters
            if len(response.text) > 1000:
                print("... (truncated)")
        
        print("\n" + "=" * 60)
        
        # Test 2: Check if it's a valid API endpoint
        if response.status_code == 200:
            print("✅ API is accessible!")
        elif response.status_code == 404:
            print("❌ API endpoint not found (404)")
        elif response.status_code == 403:
            print("🔒 Access forbidden (403)")
        elif response.status_code == 500:
            print("🚨 Server error (500)")
        else:
            print(f"⚠️  Unexpected status code: {response.status_code}")
            
        # Test 3: Test POST request (if applicable)
        print("\n📡 Testing POST request...")
        try:
            post_response = requests.post(
                api_url, 
                json={"test": "data"}, 
                timeout=10,
                headers={"Content-Type": "application/json"}
            )
            print(f"✅ POST Status Code: {post_response.status_code}")
            print(f"📄 POST Response: {post_response.text[:500]}")
        except Exception as e:
            print(f"❌ POST request failed: {e}")
            
    except requests.exceptions.Timeout:
        print("⏰ Request timed out after 10 seconds")
    except requests.exceptions.ConnectionError:
        print("🌐 Connection error - check your internet or API server")
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
    except Exception as e:
        print(f"🚨 Unexpected error: {e}")

def test_with_authentication():
    """Test the API with potential authentication headers"""
    
    api_url = "https://dxdtime.ddsolutions.io/api/styling/global/"
    
    print(f"\n🔐 Testing with authentication headers...")
    print("=" * 60)
    
    # Common authentication headers to test
    auth_headers = [
        {"Authorization": "Bearer test-token"},
        {"X-API-Key": "test-api-key"},
        {"Authentication": "test-auth"},
    ]
    
    for headers in auth_headers:
        try:
            print(f"🔍 Testing with headers: {headers}")
            response = requests.get(api_url, headers=headers, timeout=5)
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text[:100]}...")
            print()
        except Exception as e:
            print(f"   Error: {e}")
            print()

def test_different_methods():
    """Test different HTTP methods"""
    
    api_url = "https://dxdtime.ddsolutions.io/api/styling/global/"
    
    print(f"\n🔄 Testing different HTTP methods...")
    print("=" * 60)
    
    methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS']
    
    for method in methods:
        try:
            print(f"🔍 Testing {method} method...")
            response = requests.request(method, api_url, timeout=5)
            print(f"   Status: {response.status_code}")
            print(f"   Headers: {dict(response.headers)}")
            print()
        except Exception as e:
            print(f"   Error: {e}")
            print()

if __name__ == "__main__":
    print(f"🚀 API Testing Started at {datetime.now()}")
    print("🌐 Target: DXD Global Styling API")
    print()
    
    # Run all tests
    test_styling_api()
    test_with_authentication()
    test_different_methods()
    
    print(f"\n✅ Testing completed at {datetime.now()}")
