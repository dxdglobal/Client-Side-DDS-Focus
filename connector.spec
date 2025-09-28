# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['connector.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('templates', 'templates'),
        ('static', 'static'),
        ('moduller', 'moduller'),
        ('.env', '.'),
        ('themes.json', '.'),
        ('rules', 'rules')
    ],
    hiddenimports=[
        'mss',
        'pymysql',
        'boto3'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'PIL',
        'PIL.Image', 
        'PIL.ImageDraw',
        'PIL.ImageFont',
        'cv2',
        'opencv-python',
        'opencv-python-headless',
        'tkinter',
        'webview'
    ],
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
    name='DDSFocusPro Connector',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)