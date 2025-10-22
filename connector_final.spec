# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Connector (Flask backend)
This builds the background server that handles the actual time tracking
"""

import os

# Get the current directory
current_dir = os.path.abspath('.')

a = Analysis(
    ['app.py'],  # Flask application entry point
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
    ],
    hiddenimports=[
        'flask',
        'pymysql',
        'requests',
        'threading',
        'datetime',
        'json',
        'os',
        'sys',
        'time',
        'logging',
        'functools',
        'hashlib',
        'base64',
        'hmac',
        'urllib.parse',
        'pathlib',
        'subprocess',
        'psutil',
        'ctypes',
        'signal',
        'atexit',
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
    name='connector',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window for the background process
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='static/icon.ico',  # Same icon as main app
    version=None,
)