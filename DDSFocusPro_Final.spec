# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for DDSFocusPro with Auto-Connector
This builds the main application that automatically starts the connector
"""

import os

# Get the current directory
current_dir = os.path.abspath('.')

a = Analysis(
    ['desktop.py'],  # Main application entry point
    pathex=[current_dir],
    binaries=[],
    datas=[
        ('templates', 'templates'),
        ('static', 'static'),
        ('moduller', 'moduller'),
        ('.env', '.'),
        ('themes.json', '.'),
        ('rules', 'rules'),
        ('data', 'data'),
        ('user_cache', 'user_cache'),
        ('dist/connector.exe', '.'),  # Include the connector executable
    ],
    hiddenimports=[
        'webview',
        'webview.platforms.edgechromium',
        'requests',
        'threading',
        'signal',
        'atexit',
        'psutil',
        'tkinter',
        'pathlib',
        'logging',
        'webbrowser',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='DDSFocusPro',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Windowed application (no console)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='static/icon.ico',  # Application icon
    version=None,
)