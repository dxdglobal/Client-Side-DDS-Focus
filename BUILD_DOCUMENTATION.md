# DDS Focus Pro - Build Documentation

## Overview

DDS Focus Pro is a desktop application with a two-executable architecture:
- **DDSFocusPro.exe** - Desktop GUI launcher (22.7 MB)
- **DDSFocusPro Connector.exe** - Backend Flask server (44.5 MB)

## Architecture

### Two-Executable Design
The application is split into two separate executables to:
1. Separate GUI concerns from backend processing
2. Allow independent scaling and maintenance
3. Provide better process isolation
4. Enable modular updates

### Components

#### 1. Desktop GUI (DDSFocusPro.exe)
- **Source**: `desktop.py`
- **Purpose**: Launches and manages the user interface
- **Technology**: Python + WebView (EdgeChromium)
- **Dependencies**: webview, psutil, requests, pathlib
- **Features**:
  - Process management (kills old instances)
  - WebView window creation with loader.html
  - Background Flask monitoring
  - Automatic cleanup on exit

#### 2. Backend Connector (DDSFocusPro Connector.exe)
- **Source**: `connector.py` (imports and runs `app.py`)
- **Purpose**: Flask backend server and data processing
- **Technology**: Flask web framework
- **Port**: 5000 (localhost)
- **Features**:
  - Time tracking and activity monitoring
  - Screenshot functionality (optional PIL dependency)
  - API endpoints for frontend communication
  - Data persistence and logging

## Build Process

### Prerequisites
```bash
pip install pyinstaller webview flask psutil requests pathlib
```

### Build Commands

#### Clean Build (Recommended)
```bash
# Navigate to project directory
cd "C:\Users\Dell 5400\Desktop\Git-Projects\Client\Client-Side-DDS-Focus"

# Build Desktop GUI
pyinstaller desktop.spec --clean --noconfirm

# Build Backend Connector
pyinstaller connector.spec --clean --noconfirm
```

#### Quick Rebuild
```bash
pyinstaller desktop.spec
pyinstaller connector.spec
```

### Build Specifications

#### desktop.spec
- **Entry Point**: desktop.py
- **GUI Mode**: Windowed (--windowed)
- **Icon**: icon.ico
- **Data Files**: templates/ directory (contains loader.html)
- **Excludes**: PIL, OpenCV (not needed for GUI)
- **Output**: dist/DDSFocusPro.exe

#### connector.spec
- **Entry Point**: connector.py
- **Console Mode**: Hidden console (--noconsole)
- **Icon**: icon.ico
- **Excludes**: PIL, OpenCV (optional dependencies)
- **Output**: dist/DDSFocusPro Connector.exe

## File Structure

```
dist/
├── DDSFocusPro.exe              # Desktop GUI launcher (22.7 MB)
├── DDSFocusPro Connector.exe    # Backend server (44.5 MB)
└── logs/                        # Application logs
    ├── desktop.log              # GUI launcher logs
    ├── flask.log                # Backend server logs
    └── app.log                  # Application logic logs
```

## Execution Flow

1. **Startup**:
   - User launches `DDSFocusPro.exe`
   - Desktop app kills any existing DDS processes
   - Background thread starts `DDSFocusPro Connector.exe`
   - WebView window displays loader.html immediately

2. **Backend Connection**:
   - Desktop app monitors Flask server on localhost:5000
   - Once Flask is ready, loads main application URL
   - User interface switches from loader to main app

3. **Runtime**:
   - Frontend (WebView) communicates with Backend (Flask) via HTTP
   - Backend handles all data processing, file operations, and monitoring
   - Desktop app manages window events and cleanup

4. **Shutdown**:
   - User closes window or exits application
   - Desktop app terminates connector process gracefully
   - All processes cleaned up before exit

## Logging

### Desktop Logs (desktop.log)
```
[MAIN] Starting DDSFocusPro desktop application
[CLEANUP] Killing old connector: PID 12184
[LAUNCH] Base path: C:\...\dist
[LAUNCH] Starting: C:\...\dist\DDSFocusPro Connector.exe
[SUCCESS] Connector started
[UI] Creating webview window
[SUCCESS] Flask ready
[UI] Opening main app window
```

### Backend Logs (flask.log)
- Flask server startup and shutdown
- HTTP request/response logging
- Error handling and debugging

## Troubleshooting

### Common Issues

#### 1. "File not found: DDSFocusPro Connector.exe"
- **Cause**: Path resolution issue
- **Solution**: Ensure both executables are in the same directory
- **Check**: Verify `DDSFocusPro Connector.exe` exists in dist/ folder

#### 2. "Flask did not respond in time"
- **Cause**: Backend server failed to start
- **Solution**: Check flask.log for backend errors
- **Check**: Verify port 5000 is available

#### 3. UI window not showing
- **Cause**: WebView or template loading issues
- **Solution**: Check desktop.log for template path errors
- **Check**: Verify loader.html exists in bundled resources

#### 4. Unicode encoding errors
- **Cause**: Emoji characters in log messages
- **Solution**: All emojis replaced with text tags [SUCCESS], [ERROR], etc.
- **Fixed**: UTF-8 encoding configured for all log handlers

### Debug Mode

To run in debug mode with full console output:
```bash
python desktop.py  # Run as script for full error visibility
```

## Performance Notes

- **Startup Time**: ~2-3 seconds (includes process cleanup and Flask initialization)
- **Memory Usage**: 
  - Desktop GUI: ~50-80 MB
  - Backend Connector: ~80-120 MB
- **CPU Usage**: Minimal when idle, scales with activity monitoring features

## Security Considerations

- Local-only communication (localhost:5000)
- No external network dependencies for core functionality
- Process isolation between GUI and backend
- Automatic cleanup of sensitive processes on exit

## Maintenance

### Updating Components
1. Modify source files (desktop.py, connector.py, app.py)
2. Test with `python desktop.py`
3. Rebuild executables with PyInstaller
4. Distribute updated dist/ folder contents

### Log Management
- Logs are overwritten on each application start
- For persistent logging, modify logging configuration in desktop.py
- Log files location: same directory as executables

## Distribution

### Required Files
```
DDSFocusPro.exe
DDSFocusPro Connector.exe
```

### Optional Files
```
logs/ (created automatically)
icon.ico (embedded in executables)
```

### Installation
1. Copy both .exe files to desired directory
2. Run DDSFocusPro.exe
3. Logs directory will be created automatically

No additional installation or dependencies required on target machines.