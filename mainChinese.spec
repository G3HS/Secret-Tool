# -*- mode: python -*-
a = Analysis(['c:\\Secret-Tool-master\\main.py'],
             pathex=['c:\\Secret-Tool-master\\'])
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
          icon="c:\\Secret-Tool-master\\Icon\\Multi.ico",
          name=os.path.join('dist', 'Gen_III_Suite (Chinese Encoding).exe'),
          debug=False,
          strip=False,
          upx=True,
          console=False)
app = BUNDLE(exe,
             name=os.path.join('dist', 'main.exe.app'))