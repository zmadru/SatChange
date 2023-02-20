# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(
    ['satchange.py'],
    pathex=[],
    binaries=[],
    datas=[('c:\\users\\madru\\appdata\\local\\packages\\pythonsoftwarefoundation.python.3.9_qbz5n2kfra8p0\\localcache\\local-packages\\python39\\site-packages\\customtkinter', 'customtkinter\\'), ('C:\\Users\\madru\\OneDrive - Universidad Politécnica de Madrid\\Practicum\\Scripts para teledeteccion\\SatChange\\img\\convenio.png', 'convenio.png'), ('C:\\Users\\madru\\OneDrive - Universidad Politécnica de Madrid\\Practicum\\Scripts para teledeteccion\\SatChange\\img\\Logo2.png', 'Logo2.png'), ('C:\\Users\\madru\\OneDrive - Universidad Politécnica de Madrid\\Practicum\\Scripts para teledeteccion\\SatChange\\img\\satelliteicon.png', 'satelliteicon.png'), ('C:\\Users\\madru\\OneDrive - Universidad Politécnica de Madrid\\Practicum\\Scripts para teledeteccion\\SatChange\\img\\Windows_Terminal_Logo.png', 'Windows_Terminal_Logo.png')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='satchange',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='satchange',
)
