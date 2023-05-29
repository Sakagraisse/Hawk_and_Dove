# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(['main.py'],
             pathex=[],
             binaries=[],
             datas=[('welcome.jpg', '.'), ('icon.ico', '.'), ('background.jpg', '.')],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=['tkinter'],
             cipher=block_cipher,
             noarchive=True)

pyz = PYZ(a.pure, a.zipped_data,
          cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='hawk_dove',
          debug=False,
          strip=False,
          upx=False,
          runtime_tmpdir=None,
          console=False,
          icon='icon.ico')

app = BUNDLE(exe,
             name='hawk_dove.app',
             icon='icon.ico',
             bundle_identifier=None)
