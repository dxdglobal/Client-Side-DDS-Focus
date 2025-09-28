# DDS Focus Pro - Time Tracking & Productivity Management System

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/release/python-313/)
[![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)](https://flask.palletsprojects.com/)
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)](https://github.com/dxdglobal/Client-Side-DDS-Focus)

## 🚀 Quick Start

### 📦 Pre-built Executables (Recommended)
1. **Download** both executables:
   - `DDSFocusPro.exe` (GUI Launcher - 22.7 MB)
   - `DDSFocusPro Connector.exe` (Backend Server - 44.5 MB)
2. **Place** both files in the same folder
3. **Launch** `DDSFocusPro.exe`
4. **Wait** 2-3 seconds for initialization
5. **Start** tracking your productivity!

### 💻 System Requirements
- Windows 10/11 (64-bit)
- ~100MB free disk space
- No additional software required (all dependencies bundled)

## ✨ Features

### 🖥️ Core Functionality
- **Real-time Activity Tracking**: Monitor active applications and windows with precision
- **Screenshot Capture**: Privacy-focused automated screenshot functionality (optional)
- **Program Usage Analytics**: Detailed time analysis across all applications
- **Idle Time Detection**: Smart detection and handling of user idle periods
- **Local Data Storage**: All data remains on your computer for privacy
- **Instant UI Loading**: Modern loading screen with background initialization

### 🤖 AI-Powered Features
- **Intelligent Project Filtering**: AI-powered project categorization and filtering
- **Smart Summarization**: Automatic generation of detailed activity summaries
- **Natural Language Queries**: Generate SQL from natural language prompts
- **Activity Classification**: Automatic categorization of user activities
- **Productivity Insights**: AI-driven recommendations for productivity improvement

### 🌐 Modern Web Interface
- **Responsive Dashboard**: Clean, modern web-based user interface
- **Real-time Updates**: Live monitoring with instant data refresh
- **Interactive Reports**: Comprehensive reporting with visual analytics
- **Multi-user Support**: Email-based authentication and user management
- **Mobile-Friendly**: Fully responsive design for all screen sizes

## 🏗️ Architecture 2.0

### Two-Executable Design
Our latest architecture separates concerns for better performance and maintainability:

#### 📱 DDSFocusPro.exe (GUI Launcher)
- **Size**: 22.7 MB
- **Purpose**: Desktop GUI management and user interface
- **Technology**: Python + WebView (EdgeChromium)
- **Features**:
  - Instant startup with loading screen
  - Process lifecycle management
  - WebView window handling
  - Automatic cleanup on exit

#### ⚙️ DDSFocusPro Connector.exe (Backend Server)
- **Size**: 44.5 MB  
- **Purpose**: Flask backend server and data processing
- **Technology**: Flask web framework + SQLAlchemy
- **Features**:
  - HTTP API endpoints
  - Database operations
  - Screenshot processing
  - Activity monitoring logic

#### 🔄 Communication Flow
```
User → DDSFocusPro.exe → WebView UI → HTTP (localhost:5000) → DDSFocusPro Connector.exe
```

### Benefits of Two-Executable Design
- ✅ **Process Isolation**: GUI and backend run independently
- ✅ **Better Performance**: Optimized resource usage
- ✅ **Easier Debugging**: Separate logs and error handling
- ✅ **Modular Updates**: Update components independently
- ✅ **Improved Stability**: One component failure doesn't crash the other

## 🛠️ Development

### Build from Source
```bash
# Prerequisites
pip install pyinstaller webview flask psutil requests sqlalchemy

# Clone repository
git clone https://github.com/dxdglobal/Client-Side-DDS-Focus.git
cd Client-Side-DDS-Focus

# Build both executables (clean build)
pyinstaller desktop.spec --clean --noconfirm
pyinstaller connector.spec --clean --noconfirm

# Quick build (uses cache)
pyinstaller desktop.spec && pyinstaller connector.spec

# Test the build
cd dist
.\DDSFocusPro.exe
```

### Development Mode
```bash
# Run as Python script for full debugging
python desktop.py

# Run individual components
python app.py          # Backend only
python connector.py    # Backend wrapper
```

### Project Structure
```
Client-Side-DDS-Focus/
├── 🖥️  desktop.py              # GUI launcher (main entry)
├── 🔌  connector.py            # Backend connector
├── 🌐  app.py                  # Main Flask application
├── ⚙️   desktop.spec            # PyInstaller spec (GUI)
├── ⚙️   connector.spec          # PyInstaller spec (backend)
├── 📋  requirements.txt        # Python dependencies
├── 🎨  icon.ico               # Application icon
├── 📁  templates/             # HTML templates
├── 📁  static/               # Web assets (CSS/JS/images)
├── 📁  moduller/             # Application modules
├── 📁  logs/                 # Runtime logs (generated)
└── 📁  dist/                 # Built executables (generated)
```

## 📚 Documentation

| Document | Description |
|----------|-------------|
| **[BUILD_DOCUMENTATION.md](BUILD_DOCUMENTATION.md)** | Complete build system and architecture guide |
| **[USER_GUIDE.md](USER_GUIDE.md)** | End-user instructions and troubleshooting |
| **[DEVELOPER_DOCUMENTATION.md](DEVELOPER_DOCUMENTATION.md)** | Technical details and contribution guidelines |
| **[QUICK_BUILD_GUIDE.md](QUICK_BUILD_GUIDE.md)** | Fast reference for building executables |
| **[RELEASE_NOTES.md](RELEASE_NOTES.md)** | Version history and changelog |

## 🐛 Troubleshooting

### Common Issues & Solutions

#### 🚫 Application Won't Start
- **Check files**: Ensure both `.exe` files are in the same folder
- **Windows Security**: Allow through Windows Defender/antivirus
- **Permissions**: Try running as Administrator
- **Port conflict**: Ensure port 5000 isn't used by other apps

#### ⏳ Loading Screen Stuck
- **Wait**: Initial startup can take up to 30 seconds
- **Check logs**: Look at `logs/desktop.log` for error messages
- **Restart**: Close completely (check Task Manager) and relaunch

#### 🔍 Debug Mode
```bash
# Run with full console output for debugging
python desktop.py
```

### Log Files
Application creates detailed logs in the `logs/` directory:
- `desktop.log` - GUI launcher logs and process management
- `flask.log` - Backend server startup and HTTP requests  
- `app.log` - Application logic and business operations

## 🎯 Version 2.0 Highlights

### ✅ What's New
- **Two-executable architecture** for enhanced stability and performance
- **Fixed Unicode logging** issues that caused crashes on Windows systems
- **Improved path resolution** for PyInstaller executable environments  
- **Enhanced error handling** with comprehensive logging throughout
- **Instant UI loading** with proper background initialization
- **Robust process management** with automatic cleanup of old instances
- **Developer-friendly** debugging and build system improvements

### 🔄 Breaking Changes from v1.0
- Now requires **both executables** to be present in same directory
- Log file formats updated with new structured messaging
- Build process split into two separate PyInstaller specifications
- Backend server now runs as independent process rather than embedded

## 🤝 Contributing

We welcome contributions! Here's how to get started:

1. **Fork** the repository on GitHub
2. **Clone** your fork locally
3. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
4. **Make** your changes with appropriate tests
5. **Update** documentation as needed
6. **Commit** your changes (`git commit -m 'Add amazing feature'`)
7. **Push** to the branch (`git push origin feature/amazing-feature`)
8. **Open** a Pull Request

See [DEVELOPER_DOCUMENTATION.md](DEVELOPER_DOCUMENTATION.md) for detailed guidelines.

## 📊 Technical Specifications

### Performance Metrics
- **Startup Time**: 2-3 seconds (including process cleanup)
- **Memory Usage**: 100-200MB total (both processes)
- **CPU Impact**: <1% when idle, scales with monitoring frequency
- **Disk Usage**: ~100MB for executables + logs

### Supported Features Matrix
| Feature | Windows 10/11 | Planned: Linux | Planned: macOS |
|---------|---------------|----------------|----------------|
| Activity Tracking | ✅ Full | 🔄 In Progress | 🔄 Planned |
| Screenshots | ✅ Full | 🔄 In Progress | 🔄 Planned |
| Web Dashboard | ✅ Full | ✅ Full | ✅ Full |
| Database Integration | ✅ Full | ✅ Full | ✅ Full |

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support & Community

### Getting Help
- 📖 **Documentation**: Start with our comprehensive guides
- 📊 **Logs**: Check `logs/` directory for diagnostic information  
- 🐛 **Issues**: Report bugs on GitHub Issues
- 💡 **Discussions**: Join GitHub Discussions for questions

### Reporting Issues
When reporting issues, please include:
- Application version and build date
- Operating system and version
- Relevant log files from `logs/` directory
- Steps to reproduce the issue
- Screenshots if applicable

---

<div align="center">

**Made with ❤️ by DXD Global**

[Website](https://dxdglobal.com) • [GitHub](https://github.com/dxdglobal) • [Documentation](./BUILD_DOCUMENTATION.md)

</div>