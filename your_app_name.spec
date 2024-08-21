# -*- mode: python ; coding: utf-8 -*-


from PyInstaller.utils.hooks import collect_data_files
import os

a = Analysis(
    ['app.py'],
    pathex=[r'C:\Users\Emanuel Camacho\Documents\Est-gio-ANAC-Emanuel-Camacho'],  # Use the absolute path to your project directory
    binaries=[],
    datas=[
        ('DATASHEET.xlsx', 'data'),  # Source path and destination path
        ('templates/', 'templates'),  # Include all files from the templates directory
        ('Unitconversions.py', '.'),  # Include Unitconversions.py in the root
        ('Ballisticpy.py', '.'),  # Include Ballisticpy.py in the root
        ('Glidecharpy.py', '.'),  # Include Glidecharpy.py in the root
        ('Simmpy.py', '.')  # Include Simmpy.py in the root
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[]
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='UASfail',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
