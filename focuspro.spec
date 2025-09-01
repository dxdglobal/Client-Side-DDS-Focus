# focuspro.spec
# Build using: pyinstaller focuspro.spec --noconfirm

block_cipher = None

a = Analysis(
    ['focuspro.py'],  # ✅ Main file now includes both Flask + UI logic
    pathex=[],
    binaries=[],               # ❌ No external executables anymore
    datas=[
        ('templates', 'templates'),  # ✅ Ensure HTML files are bundled
        ('static', 'static'),        # ✅ Bundle CSS/JS/images if used
    ],
    hiddenimports=['webview', 'requests', 'tkinter', 'mss', 'pymysql', 'boto3', 'dotenv'],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='DDSFocusPro',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,  # ✅ If you don't want the black console window
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    name='DDSFocusPro'
)
