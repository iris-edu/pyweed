#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
PyWEED GUI Launcher

This exists mainly to show the splash screen as quickly as possible, by deferring lots of the expensive
library imports required for the application itself.

:copyright:
    Mazama Science, IRIS
:license:
    GNU Lesser General Public License, Version 3
    (http://www.gnu.org/copyleft/lesser.html)
"""

from __future__ import (absolute_import, division, print_function)

import sys

from future.utils import PY2
if PY2:
    # Configure PyQt4 -- in order for the Python console to work in Python 2, we need to load a particular
    # version of some internal libraries. This must be done before the first import of the PyQt4 libraries.
    # See http://stackoverflow.com/questions/11513132/embedding-ipython-qt-console-in-a-pyqt-application/20610786#20610786
    import os
    os.environ['QT_API'] = 'pyqt'
    import sip
    sip.setapi("QString", 2)
    sip.setapi("QVariant", 2)

from PyQt4 import QtGui
from pyweed.gui.SplashScreenHandler import SplashScreenHandler
import pyweed.gui.qrc


def get_pyweed():
    from pyweed.pyweed_gui import PyWeedGUI
    return PyWeedGUI()


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    splashScreenHandler = SplashScreenHandler()
    app.processEvents()
    pyweed = get_pyweed()
    splashScreenHandler.finish(pyweed.mainWindow)
    sys.exit(app.exec_())
