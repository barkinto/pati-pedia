# -*- mode: python ; coding: utf-8 -*-
import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Hidden imports needed for dependencies
hidden_imports = [
    'engineio.async_drivers.threading',
    'uvicorn',
    'sklearn.utils._typedefs',
    'sklearn.neighbors._partition_nodes',
    'sklearn.tree._utils',
    'scipy.special.cython_special',
    'torch',
    'torchvision',
    'ultralytics',
    'PIL',
    'cv2',
    'flask_cors',
    'flask_socketio'
]

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('frontend/dist', 'frontend/dist'),
        ('yolo11n.pt', '.'),
        ('runs/resnet50_v2/weights/best.pth', 'runs/resnet50_v2/weights/'),
        ('cat_breed_info.json', '.'),
        ('cat_breed_info.py', '.'),
        ('api.py', '.'),
        ('app.py', '.')
    ],
    hiddenimports=hidden_imports,
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
    name='PatiPedia',
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
    name='PatiPedia',
)
