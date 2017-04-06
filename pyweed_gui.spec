# -*- mode: python -*-

block_cipher = None


a = Analysis(['pyweed/pyweed_gui.py'],
             pathex=['/workspace/test/pyweed'],
             binaries=[],
             datas=[],
             hiddenimports=['ipykernel.datapub'],
             hookspath=['pyinstaller_hooks'],
             runtime_hooks=['pyinstaller_rthooks/qtconsole.py', 'pyinstaller_rthooks/inspect.py'],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          # Next 3 lines make this a one-file app
          a.binaries,
          a.zipfiles,
          a.datas,
          # exclude_binaries=True,
          name='pyweed_gui',
          debug=False,
          strip=False,
          upx=True,
          console=False )
"""
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='pyweed_gui')
"""
app = BUNDLE(exe,
             name='pyweed_gui.app',
             icon='logo.png',
             bundle_identifier='edu.iris.PyWEED')
