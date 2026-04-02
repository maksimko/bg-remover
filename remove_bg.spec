# -*- mode: python ; coding: utf-8 -*-
#
# PyInstaller spec file for Remove Background app.
#
# Before building, make sure the model is downloaded:
#   python -c "from rembg import new_session; new_session('isnet-general-use')"
#
# Build command:
#   pyinstaller remove_bg.spec
#

import os

# Path to the cached rembg model
u2net_home = os.path.join(os.path.expanduser("~"), ".u2net")
model_file = os.path.join(u2net_home, "isnet-general-use.onnx")

a = Analysis(
    ["app.py"],
    pathex=[],
    binaries=[],
    datas=[
        (model_file, "models"),
    ],
    hiddenimports=[
        "rembg.sessions.isnet_general_use",
        "onnxruntime",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="RemoveBackground",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # No console window — GUI only
    icon=None,
)
