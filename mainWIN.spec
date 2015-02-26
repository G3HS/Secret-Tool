# -*- mode: python -*-
a = Analysis(['E:\\Secret-Tool\\main.py'],
             pathex=['E:\\Secret-Tool'])
for d in a.datas:
    if 'pyconfig' in d[0]: 
        a.datas.remove(d)
        break
pyz = PYZ(a.pure)
exe = EXE( pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          icon="E:\\Secret-Tool\\Icon\\Multi.ico",
          name=os.path.join('dist', 'Gen_III_Suite.exe'),
          debug=False,
          strip=False,
          upx=True,
          console=False)
app = BUNDLE(exe,
             name=os.path.join('dist', 'main.exe.app'))