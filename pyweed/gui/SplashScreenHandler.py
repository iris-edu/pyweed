import logging
from PyQt4 import QtGui


class SplashScreenHandler(logging.Handler):

    def __init__(self, mainWidget):
        super(SplashScreenHandler, self).__init__(level=logging.INFO)
        self.mainWidget = mainWidget
        pixmap = QtGui.QPixmap("splash.png")
        self.splash = QtGui.QSplashScreen(pixmap)
        self.splash.show()
        # self.splash.finish(mainWidget)

    def emit(self, record):
        msg = self.format(record)
        self.splash.showMessage(msg)
        QtGui.QApplication.processEvents()

    def close(self):
        super(SplashScreenHandler, self).close()
        self.splash.finish(self.mainWidget)


