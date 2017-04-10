# Python Libraries

* PyQt4 is used for all GUI components and handles the event loop
* ObsPy is used for data access other seismic related analysis and plotting

# Qt Creator

The UI is built using Qt Creator. Qt makes this a bit difficult to find, as of 2017-04-10 you can start at
https://www.qt.io/download-open-source/ and click "View All Downloads" to download Qt Creator. It is also bundled
with the full installer, but you don't need the rest of it.

Qt Creator works with XML-based `.ui` files, and PyQt includes a command to generate the relevant Python code from this.

```
pyuic4 MainWindow.ui -o MainWindow.py
```

Note that PyWEED uses Qt 4, which is an older version. (PyQt5 appears not to be fully supported on all platforms.)

# PyInstaller

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


