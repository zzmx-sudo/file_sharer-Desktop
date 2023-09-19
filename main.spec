# -*- mode: python ; coding: utf-8 -*-


block_cipher = None

PROJECT_PATH = "F:\\GitSource\\file_sharer-LAN\\"

a = Analysis(
    [
        'main.py',
        PROJECT_PATH + "command\\manage.py",
        PROJECT_PATH + "command\\services\\__init__.py",
        PROJECT_PATH + "command\\services\\_base_service.py",
        PROJECT_PATH + "command\\services\\ftp_service.py",
        PROJECT_PATH + "command\\services\\http_service.py",
        PROJECT_PATH + "exceptions\\__init__.py",
        PROJECT_PATH + "model\\browse.py",
        PROJECT_PATH + "model\\download.py",
        PROJECT_PATH + "model\\file.py",
        PROJECT_PATH + "model\\public_types.py",
        PROJECT_PATH + "model\\qt_thread.py",
        PROJECT_PATH + "model\\sharing.py",
        PROJECT_PATH + "settings\\__init__.py",
        PROJECT_PATH + "settings\\_base.py",
        PROJECT_PATH + "settings\\development.py",
        PROJECT_PATH + "settings\\production.py",
        PROJECT_PATH + "static\\ui\\main_ui.py",
        PROJECT_PATH + "static\\ui\\main_qrc.py",
        PROJECT_PATH + "utils\\custom_grips.py",
        PROJECT_PATH + "utils\\logger.py",
        PROJECT_PATH + "utils\\public_func.py",
        PROJECT_PATH + "utils\\ui_function.py",
    ],
    pathex=[PROJECT_PATH],
    binaries=[],
    datas=[],
    hiddenimports=["settings.development", "settings.production"],
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
    name='file-sharer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
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
    name='file-sharer',
)