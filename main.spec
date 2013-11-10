# -*- mode: python -*-
a = Analysis(['main.py'],
             pathex=['Z:\\home\\roger\\Documents\\python\\asm'],
             hiddenimports=[],
             hookspath=None,
             runtime_hooks=None)
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='main.exe',
          debug=False,
          strip=None,
          upx=True,
          console=False )
