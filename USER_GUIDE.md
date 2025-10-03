# DDS Focus Pro - User Guide

## Quick Start

### System Requirements
- Windows 10/11
- No additional software required (all dependencies bundled)

### Installation
1. Download both executable files:
   - `DDSFocusPro.exe`
   - `DDSFocusPro Connector.exe`
2. Place both files in the same folder
3. Double-click `DDSFocusPro.exe` to launch

### First Launch
1. The application will show a loading screen
2. Wait 2-3 seconds for the backend to initialize
3. The main application interface will appear
4. You can now use all DDS Focus Pro features

## Features

### Activity Tracking
- Automatic time tracking for applications
- Window focus monitoring
- Productivity analytics
- Daily/weekly reports

### Screenshot Functionality
- Optional screenshot capture
- Privacy-focused (local only)
- Configurable intervals

### Data Management
- Local data storage
- Export capabilities
- Backup and restore options

## User Interface

### Main Window
- **Size**: 1024x750 pixels
- **Technology**: Modern web-based interface
- **Navigation**: Tabbed interface with multiple sections

### Loading Screen
- Appears during startup
- Shows while backend initializes
- Automatically transitions to main app

## Settings and Configuration

### Accessing Settings
1. Launch the application
2. Navigate to Settings tab
3. Modify preferences as needed
4. Changes are saved automatically

### Available Options
- Tracking intervals
- Screenshot settings
- Data retention policies
- Privacy preferences

## Data and Privacy

### Local Storage
- All data stored locally on your computer
- No cloud synchronization by default
- Full user control over data

### Privacy Features
- No external network connections (except optional features)
- Screenshot capture is optional
- User consent for all data collection

## Troubleshooting

### Application Won't Start
1. **Check both executables are present**:
   - Verify `DDSFocusPro.exe` exists
   - Verify `DDSFocusPro Connector.exe` exists
   - Both must be in the same folder

2. **Windows Security**:
   - Allow applications through Windows Defender
   - Run as Administrator if needed
   - Check antivirus exclusions

3. **Port Conflicts**:
   - Ensure port 5000 is not used by other applications
   - Close other DDS Focus Pro instances

### Loading Screen Stuck
1. **Wait 30 seconds** - Initial startup can be slow
2. **Check logs**:
   - Look for `logs\desktop.log` in application folder
   - Check for error messages
3. **Restart application**:
   - Close completely (check Task Manager)
   - Launch again

### Performance Issues
1. **System Resources**:
   - Ensure sufficient RAM (4GB+ recommended)
   - Close unnecessary applications
2. **Disk Space**:
   - Ensure adequate free disk space
   - Clear old log files if needed

## Logs and Diagnostics

### Log Locations
```
application_folder/
└── logs/
    ├── desktop.log     # GUI application logs
    ├── flask.log       # Backend server logs
    └── app.log         # Application logic logs
```

### Reading Logs
- Open log files with any text editor
- Look for `[ERROR]` entries for problems
- `[SUCCESS]` entries indicate normal operation
- Timestamps help identify when issues occurred

### Common Log Messages
- `[MAIN] Starting DDSFocusPro desktop application` - Normal startup
- `[SUCCESS] Flask ready` - Backend initialized successfully
- `[ERROR] File not found` - Missing executable file
- `[CLEANUP] UI closed by user` - Normal shutdown

## Updates and Maintenance

### Updating the Application
1. Download new executable files
2. Close the current application completely
3. Replace old .exe files with new ones
4. Launch the updated application

### Data Backup
1. Locate your data files (check Settings for location)
2. Copy data files to a backup location
3. Store backup in a safe location

### Clearing Application Data
1. Close the application completely
2. Delete the `logs` folder
3. Remove application data folder (location in Settings)
4. Restart application for clean start

## Support

### Self-Help
1. Check this user guide
2. Review log files for error messages
3. Try restarting the application
4. Ensure both executable files are present

### Getting Help
1. **Check Logs**: Always check log files first
2. **Provide Details**: Include system information and error messages
3. **Screenshots**: Include screenshots of any error dialogs

## Advanced Usage

### Command Line Options
```bash
# Run with debug output (requires Python installation)
python desktop.py

# Check application paths
dir *.exe
```

### Network Configuration
- Default port: 5000 (localhost only)
- No external connections required
- Firewall exceptions may be needed

### Performance Tuning
- Close unused applications to free resources
- Ensure adequate disk space for logs
- Monitor system resource usage

## Frequently Asked Questions

**Q: Why are there two .exe files?**
A: The application uses a two-component architecture for better performance and maintainability. Both files are required.

**Q: Does the application connect to the internet?**
A: The core application runs locally only. Some optional features may require internet connectivity.

**Q: Where is my data stored?**
A: All data is stored locally on your computer. Check the Settings tab for exact locations.

**Q: Can I run multiple instances?**
A: No, the application automatically closes old instances when starting to prevent conflicts.

**Q: How do I uninstall the application?**
A: Simply delete the executable files and optionally remove the data folder (location shown in Settings).