a = Analysis(['zip_extract.py'],
             pathex=[],
             hiddenimports=[],
             hookspath=None,
             runtime_hooks=None)
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='extract.exe',
          debug=False,
          strip=None,
          upx=True,
          console=True )