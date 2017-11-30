# Developer Info

## Python Libraries

* PyQt4 is used for all GUI components and handles the event loop
* ObsPy is used for data access other seismic related analysis and plotting

## Qt Creator

The UI is built using Qt Creator. Qt makes this a bit difficult to find, as of 2017-04-10 you can start at
https://www.qt.io/download-open-source/ and click "View All Downloads" to download Qt Creator. It is also bundled
with the full installer, but you don't need the rest of it.

Qt Creator works with XML-based `.ui` files, and PyQt includes a command to generate the relevant Python code from this.

```
pyuic4 MainWindow.ui -o MainWindow.py
```

Note that PyWEED uses Qt 4, which is an older version. (PyQt5 appears not to be fully supported on all platforms.)

## [Deployment](Deployment.md)


# Old docs

For reference:

[PyInstaller](PyInstaller.md)
