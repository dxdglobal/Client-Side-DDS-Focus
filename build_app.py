#!/usr/bin/env python3
"""
Build script for DDS FocusPro application
Creates both Flask app and Desktop GUI executables
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def main():
    # Ensure we're in the correct directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    print("🔨 DDS FocusPro Build Script")
    print(f"📁 Working directory: {os.getcwd()}")
    
    # Clean previous builds
    if os.path.exists("build"):
        shutil.rmtree("build")
        print("🗑️ Cleaned old build directory")
    
    if os.path.exists("dist"):
        shutil.rmtree("dist")
        print("🗑️ Cleaned old dist directory")
    
    # Build Flask App (Backend Server)
    print("\n🚀 Building Flask App...")
    flask_cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--name", "DDSFocusPro-App",
        "--add-data", "templates;templates",
        "--add-data", "static;static", 
        "--add-data", "moduller;moduller",
        "--add-data", ".env;.",
        "--add-data", "themes.json;.",
        "--add-data", "rules;rules",
        "--console",
        "app.py"
    ]
    
    try:
        result = subprocess.run(flask_cmd, check=True, capture_output=True, text=True)
        print("✅ Flask App built successfully!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Flask App build failed: {e}")
        print(f"Output: {e.stdout}")
        print(f"Error: {e.stderr}")
        return False
    
    # Build Desktop GUI
    print("\n🖥️ Building Desktop GUI...")
    desktop_cmd = [
        sys.executable, "-m", "PyInstaller", 
        "--onefile",
        "--name", "DDSFocusPro-GUI",
        "--add-data", "templates;templates",
        "--add-data", "static;static",
        "--add-data", "moduller;moduller", 
        "--add-data", ".env;.",
        "--add-data", "themes.json;.",
        "--add-data", "app.py;.",
        "--windowed",
        "--icon", "static/icon.ico",
        "desktop.py"
    ]
    
    try:
        result = subprocess.run(desktop_cmd, check=True, capture_output=True, text=True)
        print("✅ Desktop GUI built successfully!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Desktop GUI build failed: {e}")
        print(f"Output: {e.stdout}")
        print(f"Error: {e.stderr}")
        return False
    
    # List built files
    print("\n📦 Build Results:")
    dist_dir = Path("dist")
    if dist_dir.exists():
        for file in dist_dir.iterdir():
            if file.is_file():
                size_mb = file.stat().st_size / (1024 * 1024)
                print(f"  📄 {file.name} ({size_mb:.1f} MB)")
    
    print("\n🎉 Build completed successfully!")
    print("📂 Built files are in the 'dist' directory")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)