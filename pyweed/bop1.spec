# -*- mode: python -*-

block_cipher = None


a = Analysis(['bop1.py'],
             pathex=['/Users/jonathan/Projects/IRIS/pyweed/pyweed'],
             binaries=None,
             datas=None,
             hiddenimports=['six','packaging','packaging.version','packaging.specifiers','packaging.requirements'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='bop1',
          debug=False,
          strip=False,
          upx=True,
          console=True )
