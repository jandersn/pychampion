# -*- mode: python -*-


def Datafiles(*filenames, **kw):
    import os

    def datafile(path, strip_path=True):
        parts = path.split('/')
        path = name = os.path.join(*parts)
        if strip_path:
            name = os.path.basename(path)
        return name, path, 'DATA'

    strip_path = kw.get('strip_path', True)
    return TOC(
        datafile(filename, strip_path=strip_path)
        for filename in filenames
        if os.path.isfile(filename))

templates = Datafiles('templates', strip_path=False)
static_files = Datafiles('static', strip_path=False)
settings = Datafiles('user_settings.pkl', strip_path=False)

block_cipher = None

a = Analysis(['manage.py'],
             pathex=[],
             hiddenimports=[],
             hookspath=None,
             runtime_hooks=None,
             cipher=block_cipher)
pyz = PYZ(a.pure,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='toolkit.exe',
          debug=False,
          strip=None,
          upx=True,
          console=True)
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               templates,
               static_files,
               settings,
               strip=None,
               upx=True,
               name='pychamp')
