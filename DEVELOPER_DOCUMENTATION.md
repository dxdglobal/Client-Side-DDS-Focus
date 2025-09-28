# DDS Focus Pro - Developer Documentation

## Development Environment

### Prerequisites
```bash
Python 3.13+
pip install pyinstaller webview flask psutil requests pathlib threading subprocess
```

### Project Structure
```
Client-Side-DDS-Focus/
├── desktop.py              # GUI launcher (main entry point)
├── connector.py            # Backend connector (Flask wrapper)
├── app.py                  # Main Flask application logic
├── desktop.spec            # PyInstaller spec for GUI
├── connector.spec          # PyInstaller spec for backend
├── requirements.txt        # Python dependencies
├── icon.ico               # Application icon
├── templates/
│   └── loader.html        # Loading screen template
├── static/                # Web assets (CSS, JS, images)
├── moduller/              # Application modules
├── logs/                  # Application logs (generated)
└── dist/                  # Built executables (generated)
```

## Code Architecture

### desktop.py - GUI Launcher
**Purpose**: Main entry point that manages the desktop GUI and process lifecycle.

**Key Functions**:
```python
kill_existing_connector()     # Cleanup old processes
start_flask()                # Launch backend connector
wait_until_flask_ready()     # Monitor Flask server status
background_launcher()        # Background thread coordinator
cleanup_and_exit()          # Graceful shutdown handler
```

**Flow**:
1. Initialize logging with UTF-8 encoding
2. Kill any existing DDS processes
3. Start background thread to launch connector
4. Show WebView window with loader.html immediately
5. Monitor Flask server until ready
6. Switch UI to main application
7. Handle window close events and cleanup

**Path Resolution**:
```python
# Handles both PyInstaller executable and script modes
if getattr(sys, 'frozen', False):
    base_path = os.path.dirname(sys.executable)  # Executable mode
else:
    # Script mode - check for dist/ directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    dist_dir = os.path.join(script_dir, "dist")
    base_path = dist_dir if connector_exists_in_dist else script_dir
```

### connector.py - Backend Wrapper
**Purpose**: Minimal wrapper that imports and runs the main Flask application.

```python
if __name__ == '__main__':
    from app import app
    app.run(host='127.0.0.1', port=5000, debug=False)
```

**Design Rationale**:
- Separates Flask server into independent executable
- Allows backend to run without GUI dependencies
- Enables independent scaling and process management
- Simplifies debugging and maintenance

### app.py - Main Application Logic
**Purpose**: Core Flask application with all business logic.

**Key Features**:
- Time tracking and activity monitoring
- Screenshot functionality (optional PIL dependency)
- REST API endpoints for frontend communication
- Data persistence and file management
- Conditional PIL imports for build flexibility

**PIL Handling**:
```python
try:
    from PIL import Image, ImageGrab
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

def take_screenshot():
    if PIL_AVAILABLE:
        return ImageGrab.grab()
    else:
        logging.warning("Screenshot unavailable - PIL not installed")
        return None
```

## Build System

### PyInstaller Specifications

#### desktop.spec Configuration
```python
a = Analysis(['desktop.py'],
    pathex=[],
    binaries=[],
    datas=[('templates', 'templates')],  # Bundle templates
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['PIL', 'cv2'],  # Exclude heavy dependencies
    noarchive=False)
    
pyz = PYZ(a.pure)

exe = EXE(pyz, a.scripts,
    a.binaries, a.datas,
    [],
    name='DDSFocusPro',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico')
```

#### connector.spec Configuration
```python
# Similar structure but excludes GUI dependencies
excludes=['PIL', 'cv2', 'tkinter', 'webview']
console=True  # Backend can show console for debugging
```

### Build Process

#### Automated Build
```bash
# Clean build - removes all cached files
pyinstaller desktop.spec --clean --noconfirm
pyinstaller connector.spec --clean --noconfirm

# Quick rebuild - uses cached analysis
pyinstaller desktop.spec
pyinstaller connector.spec
```

#### Manual Build Steps
1. **Analysis Phase**: PyInstaller analyzes dependencies
2. **Collection Phase**: Gathers all required files and modules
3. **Bundling Phase**: Creates executable with embedded Python interpreter
4. **Optimization Phase**: UPX compression and cleanup

## Debugging and Development

### Development Mode
```bash
# Run as Python script for full debugging
cd "C:\Users\Dell 5400\Desktop\Git-Projects\Client\Client-Side-DDS-Focus"
python desktop.py
```

**Advantages**:
- Full console output and error tracebacks
- Real-time code changes without rebuilding
- Access to all Python debugging tools
- Detailed logging and error information

### Logging System
```python
# UTF-8 logging configuration for Windows compatibility
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(log_file, mode='w', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
```

**Log Categories**:
- `[MAIN]` - Application startup and lifecycle
- `[CLEANUP]` - Process management and shutdown
- `[LAUNCH]` - Backend connector launching
- `[UI]` - WebView and user interface events
- `[SUCCESS]` - Successful operations
- `[ERROR]` - Error conditions and exceptions
- `[WARNING]` - Non-critical issues
- `[DEBUG]` - Detailed diagnostic information

### Common Development Issues

#### Unicode Encoding Problems
**Issue**: Emoji characters in log messages cause crashes on Windows
**Solution**: Replace all emoji with text tags
```python
# Before (causes crashes)
logging.info("✅ Success")
logging.error("❌ Error")

# After (works correctly)
logging.info("[SUCCESS] Operation completed")
logging.error("[ERROR] Operation failed")
```

#### Path Resolution Issues
**Issue**: Different paths in script vs executable modes
**Solution**: Dynamic path detection
```python
if getattr(sys, 'frozen', False):
    # PyInstaller executable
    base_path = os.path.dirname(sys.executable)
    template_path = sys._MEIPASS  # Temporary extraction directory
else:
    # Python script
    base_path = os.path.dirname(os.path.abspath(__file__))
    template_path = base_path
```

#### Process Management
**Issue**: Multiple instances causing conflicts
**Solution**: Automatic cleanup on startup
```python
def kill_existing_connector():
    for proc in psutil.process_iter(['name']):
        try:
            if 'DDSFocusPro' in proc.info['name']:
                proc.kill()
        except Exception:
            pass  # Process may have already terminated
```

## Testing and Quality Assurance

### Testing Checklist

#### Build Testing
- [ ] Both executables build without errors
- [ ] File sizes are reasonable (~20-50MB each)
- [ ] No missing dependencies in build warnings
- [ ] Icon appears correctly on executables

#### Functionality Testing
- [ ] Desktop app launches without errors
- [ ] Loading screen appears immediately
- [ ] Backend connector starts automatically
- [ ] Flask server becomes ready within 10 seconds
- [ ] Main UI loads after backend is ready
- [ ] Application closes cleanly
- [ ] Old processes are cleaned up on restart

#### Error Handling Testing
- [ ] Missing connector executable handled gracefully
- [ ] Port conflicts detected and logged
- [ ] Network errors don't crash the application
- [ ] File permission errors are logged clearly
- [ ] Unicode characters in logs don't cause crashes

#### Performance Testing
- [ ] Startup time under 5 seconds
- [ ] Memory usage under 200MB total
- [ ] CPU usage minimal when idle
- [ ] Responsive UI during background operations

### Automated Testing
```python
# Unit tests for core functions
import unittest

class TestDesktopApp(unittest.TestCase):
    def test_path_resolution(self):
        # Test path resolution logic
        pass
    
    def test_process_cleanup(self):
        # Test process management
        pass
    
    def test_flask_connection(self):
        # Test backend connectivity
        pass
```

## Deployment and Distribution

### Release Process
1. **Code Review**: Ensure all changes are tested
2. **Build Testing**: Verify clean builds on target systems
3. **Integration Testing**: Test full application workflow
4. **Performance Testing**: Verify acceptable performance
5. **Documentation Update**: Update user and developer docs
6. **Release Build**: Create final executables
7. **Distribution**: Package and distribute files

### Distribution Package
```
DDSFocusPro_v1.0/
├── DDSFocusPro.exe
├── DDSFocusPro Connector.exe
├── USER_GUIDE.md
├── README.txt
└── CHANGELOG.txt
```

### Version Management
- Update version numbers in source files
- Maintain CHANGELOG.md with release notes
- Tag releases in version control
- Archive previous versions for rollback

## Contributing

### Code Style
- Follow PEP 8 Python style guidelines
- Use descriptive variable and function names
- Add comments for complex logic
- Include docstrings for public functions

### Pull Request Process
1. Fork repository and create feature branch
2. Implement changes with appropriate testing
3. Update documentation as needed
4. Test builds and functionality
5. Submit pull request with clear description

### Issue Reporting
- Provide detailed reproduction steps
- Include log files and error messages
- Specify operating system and Python version
- Attach screenshots for UI issues

## Performance Optimization

### Startup Optimization
- Minimize imports in main modules
- Lazy load heavy dependencies
- Cache expensive operations
- Optimize PyInstaller excludes

### Runtime Optimization
- Use appropriate data structures
- Minimize file I/O operations
- Implement efficient algorithms
- Monitor memory usage patterns

### Build Optimization
- Exclude unnecessary modules
- Enable UPX compression
- Minimize bundled data files
- Optimize import structure