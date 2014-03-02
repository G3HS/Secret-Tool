# -*- mode: python -*-
a = Analysis(['main.py'],
             pathex=['/Users/homedepot326/Desktop/Secret-Tool-master'],
             hiddenimports=[],
             hookspath=None,
             runtime_hooks=None)
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          icon="/Users/homedepot326/Desktop/Secret-Tool-master/Icon/Ring256x256.icns",
          name="Gen_III_Suite",
          debug=False,
          strip=None,
          upx=True,
          console=False )
app = BUNDLE(exe,
             name='Gen_III_Suite.app',
             icon="/Users/homedepot326/Desktop/Secret-Tool-master/Icon/Ring256x256.icns")
