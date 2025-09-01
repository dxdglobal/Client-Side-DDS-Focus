# -- mode: python ; coding: utf-8 --


a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=[
    ('templates', 'templates'),
    ('static', 'static'),
    ('moduller', 'moduller'),  # ✅ Add this line
],
    hiddenimports=[
        'boto3', 'botocore',
        'pygetwindow', 'pyautogui',
        'win32api', 'win32gui', 'win32con', 'ctypes'
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