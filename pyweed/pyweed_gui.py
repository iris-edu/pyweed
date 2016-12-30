#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Main PyWEED application

:copyright:
    Mazama Science, IRIS
:license:
    GNU Lesser General Public License, Version 3
    (http://www.gnu.org/copyleft/lesser.html)
"""

from __future__ import (absolute_import, division, print_function)

# Basic packages
import sys
import logging

# Configure PyQt4 -- in order for the Python console to work, we need to load a particular
# version of some internal libraries. This must be done before the first import of the PyQt4 libraries.
# See http://stackoverflow.com/questions/11513132/embedding-ipython-qt-console-in-a-pyqt-application/20610786#20610786
import os
os.environ['QT_API'] = 'pyqt'
import sip
sip.setapi("QString", 2)
sip.setapi("QVariant", 2)
from PyQt4 import QtCore
from PyQt4 import QtGui

# Configure matplotlib backend
import matplotlib
matplotlib.use('AGG')

from gui.SplashScreenHandler import SplashScreenHandler

LOGGER = logging.getLogger(__name__)

def start_gui():
    from gui.manager import GUIManager
    return GUIManager()


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    splashScreenHandler = SplashScreenHandler()
    manager = start_gui()
    splashScreenHandler.finish(manager.mainWindow)
    sys.exit(app.exec_())

