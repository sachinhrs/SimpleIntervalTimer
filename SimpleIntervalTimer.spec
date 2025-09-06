# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['SimpleIntervalTimer.py'],
    pathex=[],
    binaries=[('/opt/homebrew/Cellar/gtk4/4.20.0/lib/libgtk-4.1.dylib', '.')],
    datas=[],
    hiddenimports=[],
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
    [],
    exclude_binaries=True,
    name='SimpleIntervalTimer',
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
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='SimpleIntervalTimer',
)
app = BUNDLE(
    coll,
    name='SimpleIntervalTimer.app',
    icon='icon.png',
    bundle_identifier=None,
)
