# -*- mode: python ; coding: utf-8 -*-
# Desktop.spec - Desktop GUI Application Build Configuration

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
        ('app.py', '.'),  # Include the Flask app
    ],
    hiddenimports=[
        # Desktop app imports
        'tkinter',
        'tkinter.ttk',
        'tkinter.messagebox',
        'tkinter.filedialog',
        # Flask app imports  
        'flask',
        'flask_mail',
        'werkzeug',
        'jinja2',
        'click',
        'itsdangerous',
        'markupsafe',
        'requests',
        'urllib3',
        'certifi',
        'charset_normalizer',
        'idna',
        'openai',
        'pymysql',
        'cryptography',
        'boto3',
        'botocore',
        'dotenv',
        'email',
        'email.mime',
        'email.mime.text',
        'email.mime.multipart',
        'smtplib',
        'threading',
        'subprocess',
        'os',
        'sys',
        'time',
        'logging',
        'webbrowser',
        'psutil',
        'multiprocessing',
        'pathlib',
        'mss',
        'mss.tools',
        'signal',
        'traceback',
        'datetime',
        'json',
        'hashlib',
        'base64',
        'uuid',
        'tempfile',
        'shutil',
        'socket',
        'ssl',
        'platform',
        'concurrent',
        'concurrent.futures',
        'io',
        'importlib',
        'importlib.util',
        # Visual libraries
        'PIL',
        'PIL.Image',
        'pyautogui',
        'cv2',
        'numpy',
        'io',
        'tempfile',
        'shutil',
        'socket',
        'platform',
        'concurrent',
        'concurrent.futures',
        'base64',
        'uuid',
        'hashlib',
        'ssl',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'pandas',
        'scipy',
        'tensorflow',
        'torch',
        'aiohttp',
        'websockets',
        'uvloop',
        'uvicorn',
        'fastapi',
        'flask',
        'flask_mail',
        'werkzeug',
        'jinja2',
        'boto3',
        'botocore',
        'pymysql',
        'cryptography',
        'openai',
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
    name='DDSFocusPro',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Windowed GUI application
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='static/icon.ico',  # Use custom icon
)

# Create macOS app bundle
app = BUNDLE(
    exe,
    name='DDSFocusPro.app',
    icon='static/icon.ico',
    bundle_identifier='com.dds.focuspro',
    info_plist={
        'NSPrincipalClass': 'NSApplication',
        'NSAppleScriptEnabled': False,
        'CFBundleDisplayName': 'DDSFocusPro',
        'CFBundleName': 'DDSFocusPro',
        'CFBundleDocumentTypes': [
            {
                'CFBundleTypeName': 'DDS Focus Pro',
                'CFBundleTypeIconFile': 'icon.ico',
                'LSItemContentTypes': ['public.plain-text'],
                'LSHandlerRank': 'Owner'
            }
        ]
    },
)
