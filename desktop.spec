# -- mode: python ; coding: utf-8 --

block_cipher = None

a = Analysis(
    ['desktop.py'],
    pathex=['.'],  # Optional: specify project path
    binaries=[],
    datas=[('templates/*', 'templates')],
    hiddenimports=['qtpy', 'PyQt5','psutil', 'webview', 'requests'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)