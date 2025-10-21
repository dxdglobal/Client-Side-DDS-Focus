# -*- mode: python ; coding: utf-8 -*-
# FocusProapp.spec - Desktop GUI Application (FocusProapp.exe)

import os
from pathlib import Path

current_dir = os.path.dirname(os.path.abspath('desktop.py'))

block_cipher = None

a = Analysis(
    ['desktop.py'],
    pathex=[current_dir],
    binaries=[],
    datas=[
        ('templates', 'templates'),
        ('static', 'static'),
        ('moduller', 'moduller'),
        ('.env', '.'),
        ('.env.template', '.'),
        ('themes.json', '.'),
        ('rules', 'rules'),
        ('data', 'data'),
        ('user_cache', 'user_cache'),
    ],
    hiddenimports=[
        'webview',
        'webview.platforms',
        'webview.platforms.cef',
        'webview.platforms.mshtml',
        'webview.platforms.edgechromium',
        'tkinter',
        'tkinter.messagebox',
        'tkinter.simpledialog',
        'tkinter.filedialog',
        'requests',
        'urllib3',
        'certifi',
        'psutil',
        'threading',
        'subprocess',
        'logging',
        'pathlib',
        'webbrowser',
        'os',
        'sys',
        'time',
        'signal',
        'traceback',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'flask',
        'flask_mail',
        'werkzeug',
        'jinja2',
        'openai',
        'pymysql',
        'boto3',
        'botocore',
        'aiohttp',
        'websockets',
        'uvloop',
        'uvicorn',
        'fastapi',
        'matplotlib',
        'pandas',
        'scipy',
        'tensorflow',
        'torch',
        'cv2',
        'numpy',
        'PIL',
        'pyautogui',
        'mss',
    ],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='FocusProapp',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console for GUI
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico',  # Add icon to executable
)