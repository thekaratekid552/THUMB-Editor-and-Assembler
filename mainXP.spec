# -*- mode: python -*-
a = Analysis(['C:\\Documents and Settings\\Roger.IPOD\\Desktop\\THUMB-Editor-and-Assembler\\main.py'],
             pathex=['C:\\Documents and Settings\\Roger.IPOD\Desktop\\THUMB-Editor-and-Assembler'])
pyz = PYZ(a.pure)
exe = EXE( pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name=os.path.join('dist', 'main.exe'),
          debug=False,
          strip=False,
          upx=True,
          console=True )
app = BUNDLE(exe,
             name=os.path.join('dist', 'main.exe.app'))
