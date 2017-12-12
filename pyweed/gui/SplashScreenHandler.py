# -*- coding: utf-8 -*-
"""
Manage the splash screen

:copyright:
    Mazama Science, IRIS
:license:
    GNU Lesser General Public License, Version 3
    (http://www.gnu.org/copyleft/lesser.html)
"""
import pyweed
import logging
from PyQt5 import QtGui, QtWidgets, QtCore


class SplashScreenHandler(logging.Handler):

    def __init__(self,):
        super(SplashScreenHandler, self).__init__(level=logging.INFO)
        pixmap = QtGui.QPixmap(":qrc/splash.png")
        self.splash = QtWidgets.QSplashScreen(pixmap, QtCore.Qt.WindowStaysOnTopHint)

        # Attach as handler to the root logger
        logger = logging.getLogger()
        logger.addHandler(self)

        self.splash.showMessage("Welcome to %s %s" % (pyweed.__app_name__, pyweed.__version__))
        self.splash.show()
        logger.info("Splash screen should be visible")

    def emit(self, record):
        msg = self.format(record)
        self.splash.showMessage(msg)
        QtWidgets.QApplication.processEvents()

    def finish(self, mainWin):
        super(SplashScreenHandler, self).close()
        self.splash.finish(mainWin)
        logger = logging.getLogger()
        logger.removeHandler(self)
        logger.info("Splash screen finished")
