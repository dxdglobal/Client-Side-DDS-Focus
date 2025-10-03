#!/bin/bash
# DDS Focus Pro - Complete Launcher
# This script starts the desktop application with exec terminal and all dependencies

echo "🚀 Starting DDS Focus Pro with Exec Terminal..."

# Get script directory
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Change to dist directory
cd "$DIR/dist"

# Kill any existing processes
pkill -f "DDSFocusPro" 2>/dev/null || true

# Start the desktop application (it will auto-open exec terminal)
echo "📱 Opening Desktop Application..."
echo "🖥️  The app will automatically:"
echo "   1. Open the exec terminal"
echo "   2. Start the backend connector"
echo "   3. Launch the web interface"
open DDSFocusPro-Desktop.app

echo "✅ DDS Focus Pro Started!"
echo "💡 Exec terminal will open automatically."
echo "⏳ Please wait a moment for the app to fully load..."