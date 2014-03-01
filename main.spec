# -*- mode: python -*-
a = Analysis(['main.py'],
             pathex=['/media/Storage/Secret-Tool'],
             hiddenimports=[],
             hookspath=None,
             runtime_hooks=None)
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='Gen_III_Suite',
          icon="/media/Storage/Secret-Tool/Icon/Multi.ico",
          debug=False,
          strip=None,
          upx=True,
          console=False )
