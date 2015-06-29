# -*- mode: python -*-
a = Analysis(['start.py'],
             pathex=['C:\\Workspace\\TutMe'],
             hiddenimports=[],
             hookspath=None,
             runtime_hooks=None)
             
libs_path = Tree('./libs', 'libs')
configs_path = Tree('./configs','configs')
res_path = Tree('./res','res')

pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          libs_path,
		  configs_path,
          res_path,
          name='start.exe',
          debug=False,
          strip=None,
          upx=False,
          console=False )
