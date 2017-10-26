# PyInstaller

__Obsolete!__ This page documents a path that was eventually abandoned

Distributable binaries are built with PyInstaller. This isn't included in the normal environment, so you need to
install it. It's also not available through Anaconda so you need to install it with pip:

```
pip install pyinstaller
```

To create a binary:

```
cd installer
pyinstaller pyweed_gui.spec
```

The binary will be under `installer/dist/pyweed_gui`.

## Mac Binary

To create a Mac `.app` binary, set `ONE_FILE = True` in `pyweed_gui.spec`. This should build the app alongside
the other build products.

To distribute, create a DMG file which the user can mount as its own filesystem, here is a simple version:

    mkdir /tmp/PyWEED
    cp -R installer/dist/PyWEED.app /tmp/PyWEED
    ln -s /Applications /tmp/PyWEED
    hdiutil create /tmp/PyWEED.dmg -srcfolder /tmp/PyWEED -volname "PyWEED"


