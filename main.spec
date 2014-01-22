# -*- mode: python -*-
a = Analysis(['Z:\\media\\Storage\\Secret-Tool\\main.py'],
             pathex=['Z:\\media\\Storage\\Secret-Tool'])
             
pyz = PYZ(a.pure)
exe = EXE( pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name=os.path.join('dist', 'Gen_III_Suite.exe'),
          debug=False,
          strip=False,
          upx=True,
          console=False)
app = BUNDLE(exe,
             name=os.path.join('dist', 'main.exe.app'))
