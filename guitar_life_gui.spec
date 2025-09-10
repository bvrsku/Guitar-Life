# guitar_life_80_3000_min20.spec
# PyInstaller spec для guitar_life с диапазоном 80-3000 Hz и игнорированием 0-20 Hz

block_cipher = None
from PyInstaller.utils.hooks import collect_dynamic_libs, collect_data_files

# Сбор всех бинарников и данных библиотек
binaries = collect_dynamic_libs('sounddevice') + collect_dynamic_libs('librosa') \
           + collect_dynamic_libs('numpy') + collect_dynamic_libs('pygame') \
           + collect_dynamic_libs('scipy') + collect_dynamic_libs('audioread')

datas = collect_data_files('librosa') + collect_data_files('numpy') \
        + collect_data_files('pygame') + collect_data_files('scipy') \
        + collect_data_files('audioread')
#dwdawdwad
a = Analysis(
    ['guitar_life.py'],   # основной скрипт
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=['numpy','pygame','sounddevice','librosa','scipy','audioread','tkinter'],
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
    name='guitar_life',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,      # False → без консоли
    icon=None,          # Можно вставить .ico
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='guitar_life'
)
