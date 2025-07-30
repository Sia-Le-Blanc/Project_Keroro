# main.spec

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('./brand_priority_list.txt', '.'),
        ('./builders_list.txt', '.'),
        ('./image.png', '.'), 
        ('./risk_predictor.py', '.'),
        ('./vacancy_predictor.py', '.'),
        ('./prediction_result.py', '.'),
        ('./vacancy_result.py', '.'),
        ('./help_dialog.py', '.')
    ],
    hiddenimports=[],
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
    [],
    exclude_binaries=True,
    name='부동산_PF_예측_시스템',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon='image.ico', # .ico 파일로 지정
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='부동산_PF_예측_시스템_배포판',
)