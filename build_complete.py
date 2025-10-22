#!/usr/bin/env python3
"""
Complete Build Script for DDSFocusPro with Auto-Connector
This script builds both the connector and the main application with proper auto-startup
"""

import os
import sys
import subprocess
import shutil
import time

def run_command(cmd, description):
    """Run a command and return success status"""
    print(f"\n🔧 {description}")
    print(f"💻 Command: {cmd}")
    print("=" * 60)
    
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print("✅ SUCCESS")
        if result.stdout:
            print(f"📤 Output: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ FAILED: {e}")
        if e.stdout:
            print(f"📤 Output: {e.stdout}")
        if e.stderr:
            print(f"📤 Error: {e.stderr}")
        return False

def clean_build_dirs():
    """Clean previous build directories"""
    dirs_to_clean = ['build', 'dist', '__pycache__']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            print(f"🧹 Cleaning {dir_name}/")
            shutil.rmtree(dir_name)

def ensure_requirements():
    """Ensure all required packages are installed"""
    requirements = ['pyinstaller', 'webview', 'requests', 'psutil', 'flask', 'pymysql']
    
    for req in requirements:
        print(f"📦 Checking {req}...")
        result = subprocess.run([sys.executable, '-c', f'import {req}'], 
                              capture_output=True)
        if result.returncode != 0:
            print(f"⬇️ Installing {req}...")
            subprocess.run([sys.executable, '-m', 'pip', 'install', req])
        else:
            print(f"✅ {req} already installed")

def build_connector():
    """Build the connector executable"""
    print("\n🔗 BUILDING CONNECTOR")
    print("=" * 60)
    
    connector_cmd = (
        "pyinstaller --clean --noconfirm --onefile --noconsole "
        "--name connector "
        "--icon=static/icon.ico "
        "--add-data \"templates;templates\" "
        "--add-data \"static;static\" "
        "--add-data \"moduller;moduller\" "
        "--add-data \".env;.\" "
        "--add-data \"themes.json;.\" "
        "--add-data \"rules;rules\" "
        "--add-data \"data;data\" "
        "--add-data \"user_cache;user_cache\" "
        "--hidden-import=flask "
        "--hidden-import=pymysql "
        "--hidden-import=requests "
        "--hidden-import=threading "
        "app.py"
    )
    
    return run_command(connector_cmd, "Building connector.exe")

def build_main_app():
    """Build the main DDSFocusPro application"""
    print("\n🏗️ BUILDING MAIN APPLICATION")
    print("=" * 60)
    
    # Ensure connector.exe exists before building main app
    connector_path = os.path.join("dist", "connector.exe")
    if not os.path.exists(connector_path):
        print("❌ connector.exe not found! Build connector first.")
        return False
    
    main_cmd = (
        "pyinstaller --clean --noconfirm --onefile --windowed "
        "--name DDSFocusPro "
        "--icon=static/icon.ico "
        "--add-data \"templates;templates\" "
        "--add-data \"static;static\" "
        "--add-data \"moduller;moduller\" "
        "--add-data \".env;.\" "
        "--add-data \"themes.json;.\" "
        "--add-data \"rules;rules\" "
        "--add-data \"data;data\" "
        "--add-data \"user_cache;user_cache\" "
        "--add-data \"dist/connector.exe;.\" "
        "--hidden-import=webview "
        "--hidden-import=webview.platforms.edgechromium "
        "--hidden-import=requests "
        "--hidden-import=threading "
        "--hidden-import=signal "
        "--hidden-import=atexit "
        "--hidden-import=psutil "
        "desktop.py"
    )
    
    return run_command(main_cmd, "Building DDSFocusPro.exe")

def verify_build():
    """Verify that both executables were built successfully"""
    print("\n🔍 VERIFYING BUILD")
    print("=" * 60)
    
    files_to_check = [
        ("dist/DDSFocusPro.exe", "Main Application"),
        ("dist/connector.exe", "Connector")
    ]
    
    all_good = True
    for file_path, description in files_to_check:
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            print(f"✅ {description}: {file_path} ({size:,} bytes)")
        else:
            print(f"❌ Missing: {description} ({file_path})")
            all_good = False
    
    return all_good

def create_deployment_package():
    """Create a deployment package with necessary files"""
    print("\n📦 CREATING DEPLOYMENT PACKAGE")
    print("=" * 60)
    
    package_name = "DDSFocusPro_Package"
    
    # Create package directory
    if os.path.exists(package_name):
        shutil.rmtree(package_name)
    os.makedirs(package_name)
    
    # Copy main executable
    shutil.copy("dist/DDSFocusPro.exe", package_name)
    
    # Copy documentation
    docs_to_copy = ["README.md", "USER_GUIDE.md", "RELEASE_NOTES.md"]
    for doc in docs_to_copy:
        if os.path.exists(doc):
            shutil.copy(doc, package_name)
    
    # Create required folders
    folders_to_create = ["logs", "output", "data", "user_cache"]
    for folder in folders_to_create:
        folder_path = os.path.join(package_name, folder)
        os.makedirs(folder_path, exist_ok=True)
        # Create .gitkeep files
        with open(os.path.join(folder_path, ".gitkeep"), "w") as f:
            f.write("")
    
    print(f"✅ Deployment package created: {package_name}/")
    return True

def main():
    """Main build process"""
    print("🚀 DDSFocusPro Complete Build Process")
    print("=" * 60)
    print(f"📁 Working Directory: {os.getcwd()}")
    print(f"🐍 Python Version: {sys.version}")
    
    # Step 1: Ensure requirements
    print("\n📋 CHECKING REQUIREMENTS")
    ensure_requirements()
    
    # Step 2: Clean previous builds
    print("\n🧹 CLEANING PREVIOUS BUILDS")
    clean_build_dirs()
    
    # Step 3: Build connector
    if not build_connector():
        print("❌ Connector build failed! Aborting.")
        return False
    
    # Step 4: Build main application
    if not build_main_app():
        print("❌ Main application build failed! Aborting.")
        return False
    
    # Step 5: Verify build
    if not verify_build():
        print("❌ Build verification failed!")
        return False
    
    # Step 6: Create deployment package
    create_deployment_package()
    
    print("\n🎉 BUILD COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    print("📋 What was built:")
    print("   • connector.exe (background Flask server)")
    print("   • DDSFocusPro.exe (main application with webview)")
    print("   • Auto-startup: connector runs automatically when DDSFocusPro starts")
    print("   • Icon: Applied to both executables")
    print("   • Package: Ready for deployment in DDSFocusPro_Package/")
    print("\n🚀 To run: Execute DDSFocusPro.exe")
    print("💡 The connector will start automatically in the background")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)