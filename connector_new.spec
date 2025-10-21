# -*- mode: python ; coding: utf-8 -*-
# connector.spec - Backend Flask Server (connector.exe)

import os
from pathlib import Path

current_dir = os.path.dirname(os.path.abspath('app.py'))

block_cipher = None

# Add folder creation code
folder_creation_code = '''
import os
import sys

# Create necessary folders
folders_to_create = ["logs", "output", "data", "user_cache"]
for folder in folders_to_create:
    if not os.path.exists(folder):
        os.makedirs(folder, exist_ok=True)
        print(f"✅ Created folder: {folder}")
'''

a = Analysis(
    ['app.py'],
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
        'aiohttp',
        'aiohttp.client',
        'aiohttp.connector',
        'aiohttp.hdrs',
        'aiohttp.http',
        'aiohttp.streams',
        'multidict',
        'multidict._multidict',
        'yarl',
        'yarl._url',
        'async_timeout',
        'aiosignal',
        'frozenlist',
        'frozenlist._frozenlist',
        'pymysql',
        'cryptography',
        'boto3',
        'botocore',
        'dotenv',
        'python-dotenv',
        'email',
        'email.mime',
        'email.mime.text',
        'email.mime.multipart',
        'smtplib',
        'threading',
        'json',
        'datetime',
        'os',
        'sys',
        'time',
        'logging',
        'subprocess',
        'psutil',
        'multiprocessing',
        'pathlib',
        'mss',
        'mss.tools',
        'signal',
        'traceback',
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
        'cv2',
        'numpy',
        'PIL',
        'PIL.Image',
        'pyautogui',
        'io',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'websockets',
        'uvloop',
        'uvicorn',
        'fastapi',
        'tkinter',
        'webview',
        'matplotlib',
        'pandas',
        'scipy',
        'tensorflow',
        'torch',
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
    name='connector',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Console for backend monitoring
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico',  # Add icon to executable
)