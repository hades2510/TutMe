# -*- mode: python -*-
a = Analysis(['start.py'],
             pathex=['/Users/macpro/Documents/tut'],
             hiddenimports=[],
             hookspath=None,
             runtime_hooks=None)
#cef_simple_app=Tree('./cefsimple.app', 'cefsimple.app')
libs_path=Tree('./libs', 'libs')

pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
	  #cef_simple_app,
          libs_path,
          a.zipfiles,
          a.datas,
          name='start',
          debug=False,
          strip=None,
          upx=True,
          console=True )
