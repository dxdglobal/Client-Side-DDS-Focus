# Quick Build Reference

## One-Command Build
```bash
cd "C:\Users\Dell 5400\Desktop\Git-Projects\Client\Client-Side-DDS-Focus"
pyinstaller desktop.spec --clean --noconfirm && pyinstaller connector.spec --clean --noconfirm
```

## Individual Builds
```bash
# Desktop GUI
pyinstaller desktop.spec --clean --noconfirm

# Backend Connector  
pyinstaller connector.spec --clean --noconfirm
```

## Quick Test
```bash
cd dist
.\DDSFocusPro.exe
```

## Build Outputs
- `dist/DDSFocusPro.exe` (22.7 MB) - GUI Launcher
- `dist/DDSFocusPro Connector.exe` (44.5 MB) - Backend Server
- `dist/logs/` - Application logs (auto-created)

## Debug Mode
```bash
python desktop.py  # Full console output for debugging
```

## Common Issues
- **"File not found"** → Ensure both .exe files in same folder
- **"Flask timeout"** → Check connector.exe starts successfully  
- **Unicode errors** → Fixed in current build (text-only logs)
- **Path issues** → Fixed with dynamic path resolution

## Build Status: ✅ WORKING
Last successful build: 2025-09-28
- Two-executable architecture: ✅ 
- Path resolution: ✅
- Unicode logging: ✅
- Process management: ✅
- UI display: ✅