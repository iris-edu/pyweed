"""
Manager for the GUI components

:copyright:
    Mazama Science, IRIS
:license:
    GNU Lesser General Public License, Version 3
    (http://www.gnu.org/copyleft/lesser.html)
"""

from __future__ import (absolute_import, division, print_function)

from gui.MainWindow import MainWindow
from gui.LoggingDialog import LoggingDialog
from gui.SplashScreenHandler import SplashScreenHandler
from logging import getLogger
from seismap import Seismap
from events_handler import EventsHandler
from gui.EventOptionsWidget import EventOptionsWidget
from gui.WaveformDialog import WaveformDialog
from gui.ConsoleDialog import ConsoleDialog
from PyQt4 import QtGui, QtCore
import os
from pyweed_utils import manageCache
from pyweed import PyWEED

LOGGER = getLogger(__name__)


class GUIManager(QtCore.QObject):

    def __init__(self):
        super(GUIManager, self).__init__()

        self.pyweed = PyWEED()

        self.mainWindow = MainWindow(self)

        # Logging
        # see:  http://stackoverflow.com/questions/28655198/best-way-to-display-logs-in-pyqt
        # see:  http://stackoverflow.com/questions/24469662/how-to-redirect-logger-output-into-pyqt-text-widget
        self.loggingDialog = LoggingDialog(self.mainWindow)

        # Events
        LOGGER.info('Setting up event options dialog...')
        self.eventsHandler = EventsHandler(self.pyweed)
        self.eventsHandler.catalog_loaded.connect(self.onEventCatalogLoaded)
        self.eventsHandler.done.connect(self.onEventsLoaded)

        # Waveforms
        # NOTE:  The WaveformsHandler is created inside waveformsDialog.  It is only relevant to that Dialog.
        LOGGER.info('Setting up waveforms dialog...')
        self.waveformsDialog = WaveformDialog(self)

        LOGGER.info('Setting up main window...')

        # Python console
        self.console = ConsoleDialog(self, self.mainWindow)

        self.configure_menu()

        # Display MainWindow
        LOGGER.info('Showing main window...')
        self.mainWindow.initialize()
        self.mainWindow.show()

    def configure_menu(self):
        # Create menuBar
        # see:  http://doc.qt.io/qt-4.8/qmenubar.html
        # see:  http://zetcode.com/gui/pyqt4/menusandtoolbars/
        # see:  https://pythonprogramming.net/menubar-pyqt-tutorial/
        # see:  http://www.dreamincode.net/forums/topic/261282-a-basic-pyqt-tutorial-notepad/
        mainMenu = self.mainWindow.menuBar()
        # mainMenu.setNativeMenuBar(False)

        fileMenu = mainMenu.addMenu('&File')

        quitAction = QtGui.QAction("&Quit", self.mainWindow)
        quitAction.setShortcut("Ctrl+Q")
        quitAction.triggered.connect(self.closeApplication)
        fileMenu.addAction(quitAction)

        optionsMenu = mainMenu.addMenu('Options')

        showConsoleAction = QtGui.QAction("Show Python Console", self)
        showConsoleAction.triggered.connect(self.console.show)
        optionsMenu.addAction(showConsoleAction)

        helpMenu = mainMenu.addMenu('Help')

        aboutPyweedAction = QtGui.QAction("&About PYWEED", self)
        aboutPyweedAction.triggered.connect(self.showAboutDialog)
        helpMenu.addAction(aboutPyweedAction)
        helpMenu.addSeparator()
        loggingDialogAction = QtGui.QAction("Show Logs", self)
        QtCore.QObject.connect(loggingDialogAction, QtCore.SIGNAL('triggered()'), self.loggingDialog.show)
        helpMenu.addAction(loggingDialogAction)

    def fetch_events(self):
        """
        Load events
        """
        self.eventsHandler.load_data(parameters=self.pyweed.event_options)

    def getEvents(self, options):
        """
        Load events
        """
        self.pyweed.event_options.set_options(options)
        self.eventsHandler.load_data()

    def onEventCatalogLoaded(self, catalog):
        self.pyweed.set_events(catalog)

    def onEventsLoaded(self, eventsDF):
        """
        Handler triggered when the EventsHandler finishes loading events
        """
        if isinstance(eventsDF, Exception):
            msg = "Error loading events: %s" % eventsDF
            LOGGER.error(msg)
        self.mainWindow.onEventsLoaded(eventsDF)

    def showAboutDialog(self):
        """Display About message box."""
        # see:  http://www.programcreek.com/python/example/62361/PyQt4.QtGui.QMessageBox
        website = "https://github.com/iris-edu-int/pyweed"
        ###email = "adam@iris.washington.edu"
        license_link = "https://github.com/iris-edu-int/pyweed/blob/master/LICENSE"
        license_name = "MIT"
        mazama_link = "http://mazamascience.com"
        mazama_name = "Mazama Science"
        iris_link = "http://ds.iris.edu/ds/nodes/dmc/"
        iris_name = "IRIS"

        msgBox = QtGui.QMessageBox()
        msgBox.setWindowTitle("About %s" % self.preferences.App.name)
        msgBox.setTextFormat(QtCore.Qt.RichText)
        ###msgBox.setIconPixmap(QtGui.QPixmap(ComicTaggerSettings.getGraphic('about.png')))
        msgBox.setText("<br><br><br>" +
                       self.appName +
                       " v" +
                       self.version +
                       "<br><br>" +
                       "Pyweed is a cross-platform GUI application for retrieving event-based seismic data." +
                       "<br><br>" +
                       "<a href='{0}'>{0}</a><br><br>".format(website) +
                       ###"<a href='mailto:{0}'>{0}</a><br><br>".format(email) +
                       "License: <a href='{0}'>{1}</a>".format(license_link, license_name) +
                       "<br><br>" +
                       "Developed by <a href='{0}'>{1}</a>".format(mazama_link, mazama_name) +
                       " for <a href='{0}'>{1}</a>".format(iris_link, iris_name) +
                       ".")

        msgBox.setStandardButtons(QtGui.QMessageBox.Ok)
        msgBox.exec_()
        # NOTE:  For info on " modalSession has been exited prematurely" error on OS X see:
        # NOTE:    https://forum.qt.io/topic/43618/modal-sessions-with-pyqt4-and-os-x/2

    def closeApplication(self):
        LOGGER.info('Closing application...')
        self.pyweed.close()
        QtGui.QApplication.quit()
