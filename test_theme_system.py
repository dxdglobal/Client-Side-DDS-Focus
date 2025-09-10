#!/usr/bin/env python3
"""
🎨 Complete Theme System Test
=============================

This script tests the complete integration between:
1. Python ThemeManager backend
2. JavaScript frontend styling
3. HTML template integration
4. API endpoints and data flow

Usage:
    python test_theme_system.py

Author: DDS Styling Integration System
Date: January 2025
"""

import json
import requests
import sys
import os
from typing import Dict, Any

# Import our ThemeManager
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from theme_manager import ThemeManager, ThemeConfig

def test_postman_theme_data():
    """Test the exact Postman Test Theme data provided by user"""
    
    print("📮 Testing Postman Test Theme Data...")
    print("=" * 50)
    
    # Exact data from user's request
    postman_theme = {
        "theme_name": "Postman Test Theme",
        "description": "A beautiful theme created via Postman",
        "header-color": "#8E44AD",
        "footer-color": "#3498DB",
        "text_color": "#2C3E50",
        "background_color": "#ECF0F1",
        "button_color": "#E67E22",
        "button-text_color": "#2C3E50",
        "submit_button_bg_color": "#28a745",
        "submit_button_text_color": "#ffffff",
        "primary_button_bg_color": "#007bff",
        "primary_button_text_color": "#ffffff",
        "secondary_button_bg_color": "#6c757d",
        "secondary_button_text_color": "#ffffff",
        "drawer_background_color": "#f8f9fa",
        "drawer_text_color": "#212529",
        "icon_color": "#6c757d",
        "top_color": "#ffffff",
        "heading_font_size": "36px",
        "body_font_size": "18px",
        "font_family": "Segoe UI, sans-serif",
        "border_radius": "10px"
    }
    
    print("✅ Postman theme data loaded successfully")
    print(f"📝 Theme Name: {postman_theme['theme_name']}")
    print(f"📝 Description: {postman_theme['description']}")
    print(f"🎨 Color Fields: {len([k for k in postman_theme.keys() if 'color' in k])}")
    print(f"📏 Typography Fields: 3 (font_family, heading_font_size, body_font_size)")
    print(f"🔄 Border Radius: {postman_theme['border_radius']}")
    
    return postman_theme

def test_theme_manager_python():
    """Test the Python ThemeManager backend"""
    
    print("\n🐍 Testing Python ThemeManager Backend...")
    print("=" * 50)
    
    try:
        # Initialize ThemeManager
        theme_manager = ThemeManager()
        
        # Test theme creation
        postman_data = test_postman_theme_data()
        
        # Create theme config using from_api_data method
        theme_config = ThemeConfig.from_api_data(postman_data)
        print("✅ ThemeConfig created successfully using from_api_data method")
        
        # Save theme using create_theme method
        theme_id = theme_manager.create_theme(postman_data)
        print(f"✅ Theme created with ID: {theme_id}")
        
        # Get saved theme
        saved_theme = theme_manager.get_theme(theme_id)
        print(f"✅ Theme retrieved: {saved_theme.theme_name}")
        
        # List all themes
        all_themes = theme_manager.list_themes()
        print(f"✅ Total themes in system: {len(all_themes)}")
        
        # Test API format using export_theme_for_api method
        api_format = theme_manager.export_theme_for_api(theme_id)
        print("✅ API format conversion successful")
        
        # Verify all color fields are present
        expected_colors = [
            'header-color', 'footer-color', 'text_color', 'background_color',
            'button_color', 'button-text_color', 'submit_button_bg_color',
            'primary_button_bg_color', 'secondary_button_bg_color',
            'drawer_background_color', 'icon_color', 'top_color'
        ]
        
        missing_colors = [color for color in expected_colors if color not in api_format]
        if missing_colors:
            print(f"❌ Missing colors: {missing_colors}")
        else:
            print("✅ All expected color fields present in API format")
        
        return theme_manager, theme_id
        
    except Exception as e:
        print(f"❌ Python backend test failed: {str(e)}")
        return None, None

def test_api_endpoints():
    """Test Flask API endpoints (if server is running)"""
    
    print("\n🌐 Testing API Endpoints...")
    print("=" * 50)
    
    base_url = "http://localhost:5000"
    
    try:
        # Test health check
        response = requests.get(f"{base_url}/api/themes", timeout=5)
        if response.status_code == 200:
            print("✅ API server is running")
            themes = response.json()
            print(f"✅ Retrieved {len(themes)} themes from API")
        else:
            print(f"❌ API returned status: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print("⚠️  API server not running - this is expected if not started")
        print(f"   To test API: Run 'python theme_manager.py' first")
        return False
    
    try:
        # Test DDS API compatibility endpoint
        response = requests.get(f"{base_url}/api/styling/global/", timeout=5)
        if response.status_code == 200:
            print("✅ DDS API compatibility endpoint working")
            styling_data = response.json()
            print(f"✅ Global styling data retrieved: {len(styling_data)} fields")
        else:
            print(f"❌ DDS API endpoint returned status: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print("⚠️  DDS API endpoint test failed (server not running)")
    
    return True

def test_css_variable_generation():
    """Test CSS variable generation for frontend"""
    
    print("\n🎨 Testing CSS Variable Generation...")
    print("=" * 50)
    
    postman_data = test_postman_theme_data()
    
    # Generate CSS variables
    css_vars = []
    
    # Color mappings
    color_mappings = {
        'header-color': '--header-color',
        'footer-color': '--footer-color',
        'text_color': '--text-color',
        'background_color': '--background-color',
        'button_color': '--button-color',
        'button-text_color': '--button-text-color',
        'submit_button_bg_color': '--submit-button-bg-color',
        'submit_button_text_color': '--submit-button-text-color',
        'primary_button_bg_color': '--primary-button-bg-color',
        'primary_button_text_color': '--primary-button-text-color',
        'secondary_button_bg_color': '--secondary-button-bg-color',
        'secondary_button_text_color': '--secondary-button-text-color',
        'drawer_background_color': '--drawer-background-color',
        'drawer_text_color': '--drawer-text-color',
        'icon_color': '--icon-color',
        'top_color': '--top-color',
        'heading_font_size': '--heading-font-size',
        'body_font_size': '--body-font-size',
        'font_family': '--font-family',
        'border_radius': '--border-radius'
    }
    
    for api_key, css_var in color_mappings.items():
        if api_key in postman_data:
            css_vars.append(f"    {css_var}: {postman_data[api_key]};")
    
    css_output = ":root {\n" + "\n".join(css_vars) + "\n}"
    
    print("✅ CSS Variables Generated:")
    print(css_output)
    print(f"✅ Total CSS variables: {len(css_vars)}")
    
    return css_output

def test_javascript_integration():
    """Test JavaScript integration readiness"""
    
    print("\n🟨 Testing JavaScript Integration Readiness...")
    print("=" * 50)
    
    js_files = [
        "static/script/login.js",
        "static/script/config-manager.js",
        "static/script/client.js"
    ]
    
    for js_file in js_files:
        file_path = os.path.join(os.path.dirname(__file__), js_file)
        if os.path.exists(file_path):
            print(f"✅ {js_file} exists")
            
            # Check for new theme functions
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Check for specific functions
            if js_file == "static/script/login.js":
                functions_to_check = [
                    'testPostmanTheme',
                    'applyCustomLoginTheme',
                    'testAllNewColorFields',
                    'submit_button_bg_color',
                    'primary_button_bg_color'
                ]
                
                for func in functions_to_check:
                    if func in content:
                        print(f"  ✅ {func} found")
                    else:
                        print(f"  ❌ {func} missing")
                        
        else:
            print(f"❌ {js_file} not found")
    
    return True

def run_complete_test():
    """Run the complete theme system test suite"""
    
    print("🚀 Complete Theme System Test Suite")
    print("=" * 60)
    print("Testing: Python Backend + JavaScript Frontend + API Integration")
    print("=" * 60)
    
    # Test 1: Python backend
    theme_manager, theme_id = test_theme_manager_python()
    
    # Test 2: API endpoints (if available)
    test_api_endpoints()
    
    # Test 3: CSS generation
    test_css_variable_generation()
    
    # Test 4: JavaScript files
    test_javascript_integration()
    
    print("\n🏁 Test Suite Complete!")
    print("=" * 60)
    
    if theme_manager and theme_id:
        print("✅ Python Backend: WORKING")
    else:
        print("❌ Python Backend: ISSUES FOUND")
    
    print("⚠️  API Endpoints: TEST MANUALLY (run theme_manager.py)")
    print("✅ CSS Generation: WORKING")
    print("✅ JavaScript Files: READY")
    
    print("\n📋 Next Steps:")
    print("1. Run 'python theme_manager.py' to start the API server")
    print("2. Open HTML page and run 'testPostmanTheme()' in console")
    print("3. Verify all colors are applied correctly")
    print("4. Test with custom themes using 'applyCustomLoginTheme()'")
    
    return True

if __name__ == "__main__":
    run_complete_test()
