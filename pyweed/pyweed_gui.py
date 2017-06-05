#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
PyWEED GUI

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
from PyQt4 import QtCore
from PyQt4 import QtGui

# Configure matplotlib backend
import matplotlib
matplotlib.use('AGG')

# import gui.qrc  # NOQA: F401
from pyweed.gui.MainWindow import MainWindow
from pyweed.gui.LoggingDialog import LoggingDialog
from pyweed.events_handler import EventsHandler
from pyweed.stations_handler import StationsHandler
from pyweed.gui.WaveformDialog import WaveformDialog
from pyweed.gui.ConsoleDialog import ConsoleDialog
from pyweed.gui.PreferencesDialog import PreferencesDialog
from pyweed.pyweed import PyWeed

LOGGER = logging.getLogger(__name__)


class PyWeedGUI(PyWeed, QtCore.QObject):

    # We need to define mainWindow since we may check it before we are fully initialized
    mainWindow = None

    def __init__(self):
        super(PyWeedGUI, self).__init__()

        LOGGER.info('Setting up main window...')
        self.mainWindow = MainWindow(self)

        # Logging
        # see:  http://stackoverflow.com/questions/28655198/best-way-to-display-logs-in-pyqt
        # see:  http://stackoverflow.com/questions/24469662/how-to-redirect-logger-output-into-pyqt-text-widget
        self.loggingDialog = LoggingDialog(self.mainWindow)

        # Events
        LOGGER.info('Setting up event options dialog...')
        self.events_handler = EventsHandler(self)
        self.events_handler.done.connect(self.on_events_loaded)

        # Stations
        LOGGER.info('Setting up station options dialog...')
        self.stations_handler = StationsHandler(self)
        self.stations_handler.done.connect(self.on_stations_loaded)

        # Waveforms
        # NOTE:  The WaveformsHandler is created inside waveformsDialog.  It is only relevant to that Dialog.
        LOGGER.info('Setting up waveforms dialog...')
        self.waveformsDialog = WaveformDialog(self)

        # Preferences
        self.preferencesDialog = PreferencesDialog(self)

        # Python console
        self.console = ConsoleDialog(self, self.mainWindow)

        self.configure_menu()

        # Display MainWindow
        LOGGER.info('Showing main window...')
        self.mainWindow.initialize()
        self.mainWindow.show()

    ###############
    # Events
    ###############

    def fetch_events(self, options=None):
        """
        Load events
        """
        # TODO: this is a patch for https://github.com/obspy/obspy/issues/1629
        if self.events:
            self.events.clear()

        if not options:
            options = self.get_event_obspy_options()
        LOGGER.info("Fetching events with parameters: %s" % repr(options))
        self.events_handler.load_catalog(parameters=options)

    def set_event_options(self, options):
        super(PyWeedGUI, self).set_event_options(options)
        if self.mainWindow:
            self.mainWindow.eventOptionsWidget.setOptions(self.event_options)

    def on_events_loaded(self, events):
        """
        Handler triggered when the EventsHandler finishes loading events
        """
        if isinstance(events, Exception):
            msg = "Error loading events: %s" % events
            LOGGER.error(msg)
        else:
            self.set_events(events)
        self.mainWindow.onEventsLoaded(events)

    ###############
    # Stations
    ###############

    def fetch_stations(self, options=None):
        """
        Load stations
        """
        if not options:
            options = self.get_station_obspy_options()
        LOGGER.info("Fetching stations with parameters: %s" % repr(options))
        self.stations_handler.load_inventory(parameters=options)

    def set_station_options(self, options):
        super(PyWeedGUI, self).set_station_options(options)
        if self.mainWindow:
            self.mainWindow.stationOptionsWidget.setOptions(self.station_options)

    def on_stations_loaded(self, stations):
        """
        Handler triggered when the StationsHandler finishes loading stations
        """
        if isinstance(stations, Exception):
            msg = "Error loading stations: %s" % stations
            LOGGER.error(msg)
        else:
            self.set_stations(stations)
        self.mainWindow.onStationsLoaded(stations)

    ###############
    # Waveforms
    ###############

    def open_waveforms_dialog(self):
        self.waveformsDialog.show()
        self.waveformsDialog.loadWaveformChoices()

    ###############
    # Other UI elements
    ###############

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

        viewMenu = mainMenu.addMenu('View')

        showConsoleAction = QtGui.QAction("Show Python Console", self)
        showConsoleAction.triggered.connect(self.console.show)
        viewMenu.addAction(showConsoleAction)

        showLogsAction = QtGui.QAction("Show Logs", self)
        showLogsAction.triggered.connect(self.loggingDialog.show)
        viewMenu.addAction(showLogsAction)

        optionsMenu = mainMenu.addMenu('Options')

        showPreferencesAction = QtGui.QAction("Preferences", self)
        showPreferencesAction.triggered.connect(self.preferencesDialog.exec_)
        optionsMenu.addAction(showPreferencesAction)

        helpMenu = mainMenu.addMenu('Help')

        aboutPyweedAction = QtGui.QAction("&About PYWEED", self)
        aboutPyweedAction.triggered.connect(self.showAboutDialog)
        helpMenu.addAction(aboutPyweedAction)
        helpMenu.addSeparator()

    def showAboutDialog(self):
        """Display About message box."""
        # see:  http://www.programcreek.com/python/example/62361/PyQt4.QtGui.QMessageBox
        website = "https://github.com/iris-edu/pyweed"
        # email = "adam@iris.washington.edu"
        license_link = "https://github.com/iris-edu/pyweed/blob/master/LICENSE"
        license_name = "MIT"
        mazama_link = "http://mazamascience.com"
        mazama_name = "Mazama Science"
        iris_link = "http://ds.iris.edu/ds/nodes/dmc/"
        iris_name = "IRIS"

        msgBox = QtGui.QMessageBox()
        msgBox.setWindowTitle("About %s" % self.app_name)
        msgBox.setTextFormat(QtCore.Qt.RichText)
        # msgBox.setIconPixmap(QtGui.QPixmap(ComicTaggerSettings.getGraphic('about.png')))
        msgBox.setText("<br><br><br>" +
                       self.app_name +
                       " v" +
                       self.app_version +
                       "<br><br>" +
                       "Pyweed is a cross-platform GUI application for retrieving event-based seismic data." +
                       "<br><br>" +
                       "<a href='{0}'>{0}</a><br><br>".format(website) +
                       # "<a href='mailto:{0}'>{0}</a><br><br>".format(email) +
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
        # Update preferences
        self.mainWindow.savePreferences()
        self.waveformsDialog.savePreferences()
        self.close()
        QtGui.QApplication.quit()


if __name__ == "__main__":
    print("Run pyweed_launcher.py instead!")
