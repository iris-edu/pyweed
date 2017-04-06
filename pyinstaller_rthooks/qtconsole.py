# Override qtconsole.load_qt
from qtconsole import qt_loaders
def new_load_qt(api):
    from PyQt4 import QtCore, QtGui, QtSvg
    return QtCore, QtGui, QtSvg, 'pyqt'
qt_loaders.load_qt = new_load_qt

