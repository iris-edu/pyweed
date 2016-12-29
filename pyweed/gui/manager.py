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

LOGGER = getLogger(__name__)


class GUIManager(QtCore.QObject):

    def __init__(self, pyweed):
        self.pyweed = pyweed
        self.event_catalog = None
        self.event_options = None
        self.station_inventory = None

    def initialize(self):
        self.mainWindow = MainWindow(self)

        prefs = self.pyweed.preferences

        # Logging
        # see:  http://stackoverflow.com/questions/28655198/best-way-to-display-logs-in-pyqt
        # see:  http://stackoverflow.com/questions/24469662/how-to-redirect-logger-output-into-pyqt-text-widget
        self.loggingDialog = LoggingDialog(self.mainWindow)
        splashScreenHandler = SplashScreenHandler(self.mainWindow)

        # Events
        LOGGER.info('Setting up event options dialog...')
        self.eventsHandler = EventsHandler(self.pyweed)
        self.eventsHandler.catalog_loaded.connect(self.onEventCatalogLoaded)
        self.eventsHandler.done.connect(self.onEventsLoaded)

        # Waveforms
        # NOTE:  The WaveformsHandler is created inside waveformsDialog.  It is only relevant to that Dialog.
        LOGGER.info('Setting up waveforms dialog...')
        self.waveformsDialog = WaveformDialog(self.mainWindow)

        LOGGER.info('Setting up main window...')

        # Python console
        self.console = ConsoleDialog(self)

        self.configure_menu()

        self.mainWindow.initialize()

        # Display MainWindow
        LOGGER.info('Showing main window...')
        self.mainWindow.show()

        splashScreenHandler.close()

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
        quitAction.triggered.connect(self.mainWindow.closeApplication)
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

    def getEvents(self, parameters):
        """
        Load events
        """
        self.eventsHandler.load_data(parameters=parameters)

    def onEventCatalogLoaded(self, catalog):
        self.event_catalog = catalog

    def onEventsLoaded(self, eventsDF):
        """
        Handler triggered when the EventsHandler finishes loading events
        """

        self.getEventsButton.setEnabled(True)

        if isinstance(eventsDF, Exception):
            msg = "Error loading events: %s" % eventsDF
            LOGGER.error(msg)
            self.statusBar.showMessage(msg)
            return

        visibleColumns = [
            'Time', 'Magnitude', 'Longitude', 'Latitude', 'Depth/km',
            'MagType', 'EventLocationName',
        ]
        numericColumns = [
            'Magnitude', 'Longitude', 'Latitude', 'Depth/km',
        ]

        self.fillTable(self.eventsTable, eventsDF, visibleColumns, numericColumns)

        # Add items to the map -------------------------------------------------

        self.seismap.add_events(eventsDF)

        if self.eventOptionsWidget.locationRangeRadioButton.isChecked():
            n = self.eventOptionsWidget.locationRangeNorthDoubleSpinBox.value()
            e = self.eventOptionsWidget.locationRangeEastDoubleSpinBox.value()
            s = self.eventOptionsWidget.locationRangeSouthDoubleSpinBox.value()
            w = self.eventOptionsWidget.locationRangeWestDoubleSpinBox.value()
            self.seismap.add_events_box(n, e, s, w)
        elif self.eventOptionsWidget.locationDistanceFromPointRadioButton.isChecked():
            n = self.eventOptionsWidget.distanceFromPointNorthDoubleSpinBox.value()
            e = self.eventOptionsWidget.distanceFromPointEastDoubleSpinBox.value()
            minradius = self.eventOptionsWidget.distanceFromPointMinRadiusDoubleSpinBox.value()
            maxradius = self.eventOptionsWidget.distanceFromPointMaxRadiusDoubleSpinBox.value()
            self.seismap.add_events_toroid(n, e, minradius, maxradius)

        LOGGER.info('Loaded %d events', eventsDF.shape[0])
        self.statusBar.showMessage('Loaded %d events' % (eventsDF.shape[0]))

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
        # Manage the waveform cache
        waveformDownloadDir = self.preferences.Waveforms.downloadDir
        waveformCacheSize = self.preferences.Waveforms.cacheSize
        LOGGER.debug('Managing the waveform cache...')
        if os.path.exists(waveformDownloadDir):
            manageCache(waveformDownloadDir, waveformCacheSize)

        self.preferences.save()

        LOGGER.info('Closing application...')
        QtGui.QApplication.quit()
