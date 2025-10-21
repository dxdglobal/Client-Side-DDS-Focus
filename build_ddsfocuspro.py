# DDS FocusPro - Complete Build Script
# This script builds both the connector and main application

import os
import subprocess
import sys
import shutil
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n🔧 {description}")
    print(f"Command: {command}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} - SUCCESS")
        if result.stdout:
            print(f"Output: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - FAILED")
        print(f"Error: {e.stderr}")
        return False

def clean_build_dirs():
    """Clean previous build directories"""
    print("\n🧹 Cleaning previous builds...")
    
    dirs_to_clean = ['build', 'dist', '__pycache__']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"Removed: {dir_name}")

def build_connector():
    """Build the connector.exe using app.py"""
    print("\n🚀 Building Connector (Backend Flask App)...")
    
    command = [
        "pyinstaller", "--clean", "--noconfirm", "--onefile", "--noconsole",
        "--add-data", "templates;templates",
        "--add-data", "static;static", 
        "--add-data", "moduller;moduller",
        "--add-data", ".env;.",
        "--add-data", "themes.json;.",
        "--add-data", "rules;rules",
        "--add-data", "data;data",
        "--add-data", "user_cache;user_cache",
        "--hidden-import", "flask",
        "--hidden-import", "flask_mail",
        "--hidden-import", "werkzeug",
        "--hidden-import", "jinja2",
        "--hidden-import", "requests",
        "--hidden-import", "pymysql",
        "--hidden-import", "openai",
        "--hidden-import", "boto3",
        "--hidden-import", "dotenv",
        "--hidden-import", "cryptography",
        "--name", "connector",
        "app.py"
    ]
    
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        print(f"✅ Building connector.exe - SUCCESS")
        if result.stdout:
            print(f"Output: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Building connector.exe - FAILED")
        print(f"Error: {e.stderr}")
        return False

def build_desktop():
    """Build the main DDSFocusPro.exe"""
    print("\n🖥️ Building Main Desktop Application...")
    
    command = [
        "pyinstaller", "--clean", "--noconfirm", "--onefile", "--windowed",
        "--add-data", "templates;templates",
        "--add-data", "static;static",
        "--add-data", "moduller;moduller", 
        "--add-data", ".env;.",
        "--add-data", "themes.json;.",
        "--add-data", "rules;rules",
        "--add-data", "data;data",
        "--add-data", "user_cache;user_cache",
        "--add-data", "dist/connector.exe;.",
        "--hidden-import", "webview",
        "--hidden-import", "webview.platforms.edgechromium",
        "--hidden-import", "webview.platforms.mshtml", 
        "--hidden-import", "webview.platforms.cef",
        "--hidden-import", "requests",
        "--hidden-import", "threading",
        "--hidden-import", "signal",
        "--hidden-import", "atexit",
        "--hidden-import", "psutil",
        "--hidden-import", "pathlib",
        "--hidden-import", "subprocess",
        "--hidden-import", "logging",
        "--name", "DDSFocusPro",
        "desktop.py"
    ]
    
    # Add icon - check multiple possible locations
    icon_paths = [
        "static/icon.ico",
        "icon.ico", 
        "static/images/icon.ico"
    ]
    
    icon_found = False
    for icon_path in icon_paths:
        if os.path.exists(icon_path):
            command.extend(["--icon", icon_path])
            print(f"✅ Using icon: {icon_path}")
            icon_found = True
            break
    
    if not icon_found:
        print("⚠️ No icon file found, building without icon")
    
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        print(f"✅ Building DDSFocusPro.exe - SUCCESS")
        if result.stdout:
            print(f"Output: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Building DDSFocusPro.exe - FAILED")
        print(f"Error: {e.stderr}")
        return False

def copy_connector_to_dist():
    """Copy connector.exe to the final dist folder"""
    print("\n📋 Copying connector.exe to dist folder...")
    
    if os.path.exists("dist/connector.exe"):
        # The desktop build should have already included it, but let's ensure it's there
        print("✅ connector.exe is already included in the DDSFocusPro build")
        return True
    else:
        print("❌ connector.exe not found in dist folder")
        return False

def create_installer_package():
    """Create a complete package with all necessary files"""
    print("\n📦 Creating final package...")
    
    package_dir = "DDSFocusPro_Package"
    
    # Create package directory
    if os.path.exists(package_dir):
        shutil.rmtree(package_dir)
    os.makedirs(package_dir)
    
    # Copy main executable
    if os.path.exists("dist/DDSFocusPro.exe"):
        shutil.copy2("dist/DDSFocusPro.exe", package_dir)
        print("✅ Copied DDSFocusPro.exe")
    
    # Copy essential files
    essential_files = [
        ".env.template",
        "README.md", 
        "USER_GUIDE.md",
        "QUICK_BUILD_GUIDE.md"
    ]
    
    for file in essential_files:
        if os.path.exists(file):
            shutil.copy2(file, package_dir)
            print(f"✅ Copied {file}")
    
    print(f"📦 Package created in: {package_dir}")
    return True

def main():
    """Main build process"""
    print("🚀 DDS FocusPro - Complete Build Process")
    print("=" * 50)
    
    # Check if PyInstaller is installed
    try:
        subprocess.run(["pyinstaller", "--version"], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ PyInstaller not found. Installing...")
        if not run_command("pip install pyinstaller", "Installing PyInstaller"):
            print("❌ Failed to install PyInstaller")
            return False
    
    # Step 1: Clean previous builds
    clean_build_dirs()
    
    # Step 2: Build connector
    if not build_connector():
        print("❌ Connector build failed")
        return False
    
    # Step 3: Build desktop app (includes connector)
    if not build_desktop():
        print("❌ Desktop build failed")
        return False
    
    # Step 4: Verify connector is included
    if not copy_connector_to_dist():
        print("❌ Connector verification failed")
        return False
    
    # Step 5: Create final package
    if not create_installer_package():
        print("❌ Package creation failed")
        return False
    
    print("\n✅ BUILD COMPLETED SUCCESSFULLY!")
    print("=" * 50)
    print("📁 Your application is ready in: DDSFocusPro_Package/")
    print("🚀 Run DDSFocusPro.exe to start the application")
    print("🔧 The connector will automatically run in the background")
    
    return True

if __name__ == "__main__":
    if main():
        print("\n🎉 Build process completed successfully!")
        sys.exit(0)
    else:
        print("\n💥 Build process failed!")
        sys.exit(1)