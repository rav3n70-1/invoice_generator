# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec file for Sneaker Canvas BD Invoice Manager
# Optimized to exclude unnecessary packages

import os

block_cipher = None

# Get the project directory
project_dir = os.path.dirname(os.path.abspath(SPEC))

a = Analysis(
    ['invoice_app.py'],
    pathex=[project_dir],
    binaries=[],
    datas=[
        ('assets', 'assets'),  # Include entire assets folder
    ],
    hiddenimports=[
        'tkcalendar',
        'babel.numbers',
        'PIL',
        'PIL._tkinter_finder',
        'pandas',
        'reportlab',
        'reportlab.graphics',
        'reportlab.lib',
        'reportlab.platypus',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude large ML/scientific packages not needed for invoice app
        'tensorflow',
        'keras',
        'torch',
        'torchvision',
        'scipy',
        'numpy.f2py',
        'matplotlib',
        'IPython',
        'jupyter',
        'notebook',
        'cv2',
        'opencv',
        'sklearn',
        'scikit-learn',
        'transformers',
        'pytest',
        'sphinx',
        'docutils',
        'setuptools',
        'wheel',
        'pip',
        'PyQt5',
        'PyQt6',
        'PySide2',
        'PySide6',
        'wx',
        'gtk',
        'kivy',
        'pygame',
    ],
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
    name='SneakerCanvasBD',
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
    icon='assets/logo.ico',  # Application icon
)
