# -*- mode: python -*-
a = Analysis(['--PUT PATH TO MAIN.PY--'],
             pathex=['--PUT PATH TO WHERE YOU WANT OUTPUT'])
             
pyz = PYZ(a.pure)
exe = EXE( pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name=os.path.join('dist', 'Gen_III_Suite'),
          debug=False,
          strip=False,
          upx=True,
          console=False)
app = BUNDLE(exe,
             name=os.path.join('dist', 'Gen_III_Suite.app'))
