# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Document Summarizer
Native desktop application with CustomTkinter GUI
"""
import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Collect CustomTkinter and tkinterdnd2 data files
datas = []
datas += collect_data_files('customtkinter')
datas += collect_data_files('tkinterdnd2')

# Hidden imports that PyInstaller might miss
hiddenimports = [
    'PIL._tkinter_finder',
    'google.ai.generativelanguage',
    'google.generativeai',
    'customtkinter',
    'tkinterdnd2',
]
hiddenimports += collect_submodules('customtkinter')
hiddenimports += collect_submodules('tkinterdnd2')

a = Analysis(
    ['native_app.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
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
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='DocumentSummarizer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico',  # Application icon
    version_file=None,
)
