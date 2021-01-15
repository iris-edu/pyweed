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
import os.path
import platform
from PyQt5 import QtCore, QtWidgets

from obspy.core.event.catalog import read_events
from obspy.core.inventory.inventory import read_inventory

from pyweed import __version__, __app_name__
from pyweed.gui.MainWindow import MainWindow
from pyweed.gui.LoggingDialog import LoggingDialog
from pyweed.events_handler import EventsHandler
from pyweed.stations_handler import StationsHandler
from pyweed.gui.WaveformDialog import WaveformDialog
from pyweed.gui.ConsoleDialog import ConsoleDialog
from pyweed.gui.PreferencesDialog import PreferencesDialog
from pyweed.pyweed_core import PyWeedCore
from pyweed.summary import get_filtered_catalog, get_filtered_inventory

LOGGER = logging.getLogger(__name__)


class PyWeedGUI(PyWeedCore, QtCore.QObject):

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

        # Waveforms
        # NOTE:  The WaveformsHandler is created inside waveformsDialog.  It is only relevant to that Dialog.
        LOGGER.info('Setting up waveforms dialog...')
        self.waveformsDialog = WaveformDialog(self, self.mainWindow)

        # Preferences
        self.preferencesDialog = PreferencesDialog(self, self.mainWindow)

        # Python console
        self.console = ConsoleDialog(self, self.mainWindow)

        self.configureMenu()

        # Display MainWindow
        LOGGER.info('Showing main window...')
        self.mainWindow.initialize()
        self.mainWindow.show()

    ###############
    # Events
    ###############

    def set_event_options(self, options):
        super(PyWeedGUI, self).set_event_options(options)
        if self.mainWindow:
            self.mainWindow.eventOptionsWidget.setOptions()

    def on_events_loaded(self, events):
        super(PyWeedGUI, self).on_events_loaded(events)
        if self.mainWindow:
            self.mainWindow.onEventsLoaded(events)

    ###############
    # Stations
    ###############

    def set_station_options(self, options):
        super(PyWeedGUI, self).set_station_options(options)
        if self.mainWindow:
            self.mainWindow.stationOptionsWidget.setOptions()

    def on_stations_loaded(self, stations):
        super(PyWeedGUI, self).on_stations_loaded(stations)
        if self.mainWindow:
            self.mainWindow.onStationsLoaded(stations)

    ###############
    # Waveforms
    ###############

    def openWaveformsDialog(self):
        self.waveformsDialog.show()
        self.waveformsDialog.loadWaveformChoices()

    ###############
    # Load/Save Summary
    ###############

    def saveSummary(self):
        """
        Save the selected events/stations
        """
        # If the user quits or cancels this dialog, '' is returned
        savePath = str(QtWidgets.QFileDialog.getExistingDirectory(
            parent=self.mainWindow,
            caption="Save Summary to"))
        if savePath != '':
            try:
                catalog = get_filtered_catalog(self.events, self.iter_selected_events())
                catalog.write(os.path.join(savePath, 'events.xml'), format="QUAKEML")
            except Exception as e:
                LOGGER.error("Unable to save event selection! %s", e)
            try:
                inventory = get_filtered_inventory(self.stations, self.iter_selected_stations())
                inventory.write(os.path.join(savePath, 'stations.xml'), format="STATIONXML")
            except Exception as e:
                LOGGER.error("Unable to save station selection! %s", e)

    def loadSummary(self):
        # If the user quits or cancels this dialog, '' is returned
        loadPath = str(QtWidgets.QFileDialog.getExistingDirectory(
            parent=self.mainWindow,
            caption="Load Summary from"))
        if loadPath != '':
            try:
                catalog = read_events(os.path.join(loadPath, 'events.xml'))
                self.on_events_loaded(catalog)
                self.mainWindow.selectAllEvents()
            except Exception as e:
                LOGGER.error("Unable to load events! %s", e)
            try:
                inventory = read_inventory(os.path.join(loadPath, 'stations.xml'))
                self.on_stations_loaded(inventory)
                self.mainWindow.selectAllStations()
            except Exception as e:
                LOGGER.error("Unable to load stations! %s", e)

    ###############
    # Other UI elements
    ###############

    def configureMenu(self):
        # Create menuBar
        # see:  http://doc.qt.io/qt-4.8/qmenubar.html
        # see:  http://zetcode.com/gui/PyQt5/menusandtoolbars/
        # see:  https://pythonprogramming.net/menubar-pyqt-tutorial/
        # see:  http://www.dreamincode.net/forums/topic/261282-a-basic-pyqt-tutorial-notepad/
        mainMenu = QtWidgets.QMenuBar()
        # mainMenu.setNativeMenuBar(False)

        fileMenu = mainMenu.addMenu('&File')

        saveSummaryAction = QtWidgets.QAction("Save Summary", self.mainWindow)
        saveSummaryAction.triggered.connect(self.saveSummary)
        fileMenu.addAction(saveSummaryAction)

        loadSummaryAction = QtWidgets.QAction("Load Summary", self.mainWindow)
        loadSummaryAction.triggered.connect(self.loadSummary)
        fileMenu.addAction(loadSummaryAction)

        quitAction = QtWidgets.QAction("&Quit", self.mainWindow)
        quitAction.setShortcut("Ctrl+Q")
        quitAction.triggered.connect(self.closeApplication)
        fileMenu.addAction(quitAction)

        viewMenu = mainMenu.addMenu('View')

        if ConsoleDialog.enabled:
            showConsoleAction = QtWidgets.QAction("Show Python Console", self)
            showConsoleAction.triggered.connect(self.console.show)
            viewMenu.addAction(showConsoleAction)

        showLogsAction = QtWidgets.QAction("Show Logs", self)
        showLogsAction.triggered.connect(self.loggingDialog.show)
        viewMenu.addAction(showLogsAction)

        optionsMenu = mainMenu.addMenu('Options')

        showPreferencesAction = QtWidgets.QAction("Preferences", self)
        showPreferencesAction.triggered.connect(self.preferencesDialog.exec_)
        optionsMenu.addAction(showPreferencesAction)

        helpMenu = mainMenu.addMenu('Help')

        aboutPyweedAction = QtWidgets.QAction("&About PYWEED", self)
        aboutPyweedAction.triggered.connect(self.showAboutDialog)
        helpMenu.addAction(aboutPyweedAction)
        helpMenu.addSeparator()

        self.mainWindow.setMenuBar(mainMenu)
        # self.waveformsDialog.setMenuBar(mainMenu)

    def showAboutDialog(self):
        """Display About message box."""
        # see:  http://www.programcreek.com/python/example/62361/PyQt5.QtGui.QMessageBox
        website = "https://github.com/iris-edu/pyweed"
        # email = "adam@iris.washington.edu"
        license_link = "https://github.com/iris-edu/pyweed/blob/master/LICENSE"
        license_name = "LGPLv3"
        mazama_link = "http://mazamascience.com"
        mazama_name = "Mazama Science"
        iris_link = "http://ds.iris.edu/ds/nodes/dmc/"
        iris_name = "IRIS"

        msgBox = QtWidgets.QMessageBox()
        msgBox.setWindowTitle("About %s" % __app_name__)
        msgBox.setTextFormat(QtCore.Qt.RichText)
        # msgBox.setIconPixmap(QtGui.QPixmap(ComicTaggerSettings.getGraphic('about.png')))
        msgBox.setText("<br><br><br>" +
                       __app_name__ +
                       " v" +
                       __version__ +
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

        msgBox.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msgBox.exec_()
        # NOTE:  For info on " modalSession has been exited prematurely" error on OS X see:
        # NOTE:    https://forum.qt.io/topic/43618/modal-sessions-with-PyQt5-and-os-x/2

    def closeApplication(self):
        LOGGER.info('Closing application...')
        # Update preferences
        self.mainWindow.savePreferences()
        self.waveformsDialog.savePreferences()
        self.close()
        QtWidgets.QApplication.quit()


if __name__ == "__main__":
    print("Run pyweed_launcher.py instead!")
