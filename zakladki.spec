# -*- mode: python ; coding: utf-8 -*-
"""Konfiguracja PyInstaller dla aplikacji 'Zakladki'.

Buduje pojedynczy, okienkowy plik .exe (Windows). UWAGA: plik .exe dla
Windows mozna zbudowac TYLKO na Windows - nie da sie go utworzyc na Linux.

Budowanie (w katalogu repozytorium, w systemie Windows):

    pip install pyinstaller
    pyinstaller --noconfirm zakladki.spec

Rownowazne polecenie bez pliku .spec:

    pyinstaller --noconfirm --windowed --onefile --name Zakladki \
        --add-data "zakladki_app/fonts/DejaVuSans-Bold.ttf;zakladki_app/fonts" run.py

Wbudowana czcionka DejaVuSans-Bold.ttf jest obowiazkowa dla poprawnego
wyswietlania polskich znakow w PDF, dlatego dolaczamy ja przez 'datas'.
"""

block_cipher = None


a = Analysis(
    ['run.py'],
    pathex=[],
    binaries=[],
    datas=[('zakladki_app/fonts/DejaVuSans-Bold.ttf', 'zakladki_app/fonts')],
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
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Zakladki',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
