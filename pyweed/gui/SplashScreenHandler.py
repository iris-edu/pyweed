# -*- coding: utf-8 -*-
"""
Manage the splash screen

:copyright:
    Mazama Science, IRIS
:license:
    GNU Lesser General Public License, Version 3
    (http://www.gnu.org/copyleft/lesser.html)
"""

import logging
from PyQt4 import QtGui, QtCore


class SplashScreenHandler(logging.Handler):

    def __init__(self,):
        super(SplashScreenHandler, self).__init__(level=logging.INFO)
        pixmap = QtGui.QPixmap(":qrc/splash.png")
        self.splash = QtGui.QSplashScreen(pixmap, QtCore.Qt.WindowStaysOnTopHint)

        # Attach as handler to the root logger
        logger = logging.getLogger()
        logger.addHandler(self)

        self.splash.show()
        print("Splash screen should be visible")

    def emit(self, record):
        msg = self.format(record)
        self.splash.showMessage(msg)
        QtGui.QApplication.processEvents()

    def finish(self, mainWin):
        super(SplashScreenHandler, self).close()
        self.splash.finish(mainWin)
        logger = logging.getLogger()
        logger.removeHandler(self)
        print("Splash screen finished")
