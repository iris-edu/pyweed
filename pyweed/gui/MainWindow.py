from PyQt4 import QtGui, QtCore
from gui.uic import MainWindow
from preferences import Preferences
import logging
from gui.LoggingDialog import LoggingDialog
from gui.SplashScreenHandler import SplashScreenHandler
import os
from pyweed_utils import manageCache
from obspy.clients import fdsn
from seismap import Seismap
from events_handler import EventsHandler
from stations_handler import StationsHandler
from gui.WaveformDialog import WaveformDialog
from gui.ConsoleDialog import ConsoleDialog
import numpy as np
from gui.MyNumericTableWidgetItem import MyNumericTableWidgetItem
from gui.EventOptionsWidget import EventOptionsWidget
from gui.StationOptionsWidget import StationOptionsWidget

LOGGER = logging.getLogger(__name__)


class MainWindow(QtGui.QMainWindow, MainWindow.Ui_MainWindow):

    def __init__(self, appName, version, preferences, parent=None):

        self.preferences = preferences

        # Logging
        # see:  http://stackoverflow.com/questions/28655198/best-way-to-display-logs-in-pyqt
        # see:  http://stackoverflow.com/questions/24469662/how-to-redirect-logger-output-into-pyqt-text-widget
        self.loggingDialog = LoggingDialog(self)
        splashScreenHandler = SplashScreenHandler(self)

        super(self.__class__, self).__init__()
        self.setupUi(self)

        # Set MainWindow properties
        self.appName = appName
        self.version = version
        self.setWindowTitle('%s version %s' % (self.appName, self.version))

        # Create StatusBar
        sb = QtGui.QStatusBar()
        sb.setFixedHeight(18)
        self.setStatusBar(sb)

        # Make sure the waveform download directory exists and isn't full
        waveformDownloadDir = self.preferences.Waveforms.downloadDir
        waveformCacheSize = float(self.preferences.Waveforms.cacheSize)
        LOGGER.info('Checking on download directory...')
        if os.path.exists(waveformDownloadDir):
            manageCache(waveformDownloadDir, waveformCacheSize)
        else:
            try:
                os.makedirs(waveformDownloadDir, 0700)
            except Exception as e:
                LOGGER.error("Creation of download directory failed with" + " error: \"%s\'""" % e)
                SystemExit()

        # Set up the ObsPy FDSN client
        # Important preferences
        self.dataCenter = "IRIS" # TODO:  dataCenter should be configurable

        # Instantiate a client
        LOGGER.info("Creating ObsPy client for %s", self.dataCenter)
        self.client = fdsn.Client(self.dataCenter)

        # Get the Figure object from the map_canvas
        LOGGER.info('Setting up main map...')
        self.map_figure = self.map_canvas.fig
        self.map_axes = self.map_figure.add_axes([0.01, 0.01, .98, .98])
        self.map_axes.clear()
        prefs = self.preferences.Map
        self.seismap = Seismap(projection=prefs.projection, ax=self.map_axes) # 'cyl' or 'robin' or 'mill'
        self.map_figure.canvas.draw()

        # Events
        LOGGER.info('Setting up event options dialog...')
        self.eventsHandler = EventsHandler(self.client)
        self.eventsHandler.done.connect(self.onEventsLoaded)

        self.eventOptionsWidget = EventOptionsWidget(self)
        self.eventOptionsDockWidget.setWidget(self.eventOptionsWidget)
        self.toggleEventOptions.toggled.connect(self.eventOptionsDockWidget.setVisible)
        self.eventOptionsDockWidget.visibilityChanged.connect(self.toggleEventOptions.setChecked)

        # Stations
        LOGGER.info('Setting up station options dialog...')
        self.stationsHandler = StationsHandler(self.client)
        self.stationsHandler.done.connect(self.onStationsLoaded)

        self.stationOptionsWidget = StationOptionsWidget(self)
        self.stationOptionsDockWidget.setWidget(self.stationOptionsWidget)
        self.toggleStationOptions.toggled.connect(self.stationOptionsDockWidget.setVisible)
        self.stationOptionsDockWidget.visibilityChanged.connect(self.toggleStationOptions.setChecked)


        # Connect signals associated with table clicks
        # see:  http://zetcode.com/gui/pyqt4/eventsandsignals/
        # see:  https://wiki.python.org/moin/PyQt/Sending%20Python%20values%20with%20signals%20and%20slots
        QtCore.QObject.connect(self.eventsTable, QtCore.SIGNAL('cellClicked(int, int)'), self.eventsTableClicked)
        QtCore.QObject.connect(self.stationsTable, QtCore.SIGNAL('cellClicked(int, int)'), self.stationsTableClicked)

        # Waveforms
        # NOTE:  The WaveformsHandler is created inside waveformsDialog.  It is only relevant to that Dialog.
        LOGGER.info('Setting up waveforms dialog...')
        self.waveformsDialog = WaveformDialog(self)
        self.getWaveformsButton.setEnabled(False)

        LOGGER.info('Setting up main window...')

        # Connect the main window buttons
        self.getEventsButton.clicked.connect(self.getEvents)
        self.getStationsButton.pressed.connect(self.getStations)
        self.getWaveformsButton.pressed.connect(self.getWaveforms)

        # Create menuBar
        # see:  http://doc.qt.io/qt-4.8/qmenubar.html
        # see:  http://zetcode.com/gui/pyqt4/menusandtoolbars/
        # see:  https://pythonprogramming.net/menubar-pyqt-tutorial/
        # see:  http://www.dreamincode.net/forums/topic/261282-a-basic-pyqt-tutorial-notepad/
        mainMenu = self.menuBar()
        # mainMenu.setNativeMenuBar(False)

        fileMenu = mainMenu.addMenu('&File')

        quitAction = QtGui.QAction("&Quit", self)
        quitAction.setShortcut("Ctrl+Q")
        quitAction.triggered.connect(self.closeApplication)
        fileMenu.addAction(quitAction)

        optionsMenu = mainMenu.addMenu('Options')

        eventOptionsAction = QtGui.QAction("Show Event Options", self)
        QtCore.QObject.connect(eventOptionsAction, QtCore.SIGNAL('triggered()'), self.eventOptionsDockWidget.show)
        optionsMenu.addAction(eventOptionsAction)
        stationOptionsAction = QtGui.QAction("Show Station Options", self)
        QtCore.QObject.connect(stationOptionsAction, QtCore.SIGNAL('triggered()'), self.stationOptionsDockWidget.show)
        optionsMenu.addAction(stationOptionsAction)

        helpMenu = mainMenu.addMenu('Help')

        aboutPyweedAction = QtGui.QAction("&About PYWEED", self)
        aboutPyweedAction.triggered.connect(self.aboutPyweed)
        helpMenu.addAction(aboutPyweedAction)
        helpMenu.addSeparator()
        loggingDialogAction = QtGui.QAction("Show Logs", self)
        QtCore.QObject.connect(loggingDialogAction, QtCore.SIGNAL('triggered()'), self.loggingDialog.show)
        helpMenu.addAction(loggingDialogAction)

        console = ConsoleDialog(self)
        console.show()

        # Display MainWindow
        LOGGER.info('Showing main window...')
        self.show()

        splashScreenHandler.close()

    def fillTable(self, table, dataframe, visibleColumns, numericColumns):
        """
        Common code for filling event/station tables with data
        """

        # Clear existing contents
        table.clearSelection() # This is important!
        while (table.rowCount() > 0):
            table.removeRow(0)

        # Column names
        columnNames = dataframe.columns.tolist()

        # Create new table
        table.setRowCount(dataframe.shape[0])
        table.setColumnCount(dataframe.shape[1])
        table.setHorizontalHeaderLabels(columnNames)
        table.verticalHeader().hide()

        # Hidden columns
        for i, column in enumerate(columnNames):
            table.setColumnHidden(i, column not in visibleColumns)

        # Add new contents
        for i in range(dataframe.shape[0]):
            for j in range(dataframe.shape[1]):
                # Guarantee that all elements are converted to strings for display but apply proper sorting
                if columnNames[j] in numericColumns:
                    table.setItem(i, j, MyNumericTableWidgetItem(str(dataframe.iat[i, j])))
                else:
                    table.setItem(i, j, QtGui.QTableWidgetItem(str(dataframe.iat[i, j])))

        # Tighten up the table
        table.resizeColumnsToContents()
        table.resizeRowsToContents()



    @QtCore.pyqtSlot()
    def getEvents(self):
        """
        Get events dataframe from IRIS.
        """
        self.getEventsButton.setEnabled(False)
        LOGGER.info('Loading events...')
        self.statusBar().showMessage('Loading events...')

        # Get events and subset to desired columns
        parameters = self.eventOptionsWidget.getOptions()
        # TODO:  handle errors when querying events
        self.eventsHandler.load_data(parameters=parameters)

    def onEventsLoaded(self, eventsDF):
        """
        Handler triggered when the EventsHandler finishes loading events
        """

        self.getEventsButton.setEnabled(True)

        if isinstance(eventsDF, Exception):
            msg = "Error loading events: %s" % eventsDF
            LOGGER.error(msg)
            self.statusBar().showMessage(msg)
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
            n = float(self.eventOptionsWidget.locationRangeNorthLineEdit.text())
            e = float(self.eventOptionsWidget.locationRangeEastLineEdit.text())
            s = float(self.eventOptionsWidget.locationRangeSouthLineEdit.text())
            w = float(self.eventOptionsWidget.locationRangeWestLineEdit.text())
            self.seismap.add_events_box(n, e, s, w)
        elif self.eventOptionsWidget.locationDistanceFromPointRadioButton.isChecked():
            n = float(self.eventOptionsWidget.distanceFromPointNorthLineEdit.text())
            e = float(self.eventOptionsWidget.distanceFromPointEastLineEdit.text())
            minradius = float(self.eventOptionsWidget.distanceFromPointMinRadiusLineEdit.text())
            maxradius = float(self.eventOptionsWidget.distanceFromPointMaxRadiusLineEdit.text())
            self.seismap.add_events_toroid(n, e, minradius, maxradius)

        LOGGER.info('Loaded %d events', eventsDF.shape[0])
        self.statusBar().showMessage('Loaded %d events' % (eventsDF.shape[0]))

    @QtCore.pyqtSlot()
    def getStations(self):
        """
        Get events dataframe from IRIS.
        """
        self.getStationsButton.setEnabled(False)
        LOGGER.info('Loading channels...')
        self.statusBar().showMessage('Loading channels...')

        # Get stations and subset to desired columns
        parameters = self.stationQueryDialog.getOptions()
        # TODO:  handle errors when querying stations
        self.stationsHandler.load_data(parameters=parameters)

    def onStationsLoaded(self, stationsDF):
        """
        Handler triggered when the StationsHandler finishes loading stations
        """

        self.getStationsButton.setEnabled(True)

        if isinstance(stationsDF, Exception):
            msg = "Error loading stations: %s" % stationsDF
            LOGGER.error(msg)
            self.statusBar().showMessage(msg)
            return

        visibleColumns = [
            'Network', 'Station', 'Location', 'Channel', 'Longitude', 'Latitude',
        ]
        numericColumns = [
            'Longitude', 'Latitude', 'Elevation', 'Depth', 'Azimuth', 'Dip',
            'Scale', 'ScaleFreq', 'ScaleUnits', 'SampleRate',
        ]

        self.fillTable(self.stationsTable, stationsDF, visibleColumns, numericColumns)

        # Add items to the map -------------------------------------------------

        self.seismap.add_stations(stationsDF)

        if self.stationQueryDialog.locationRangeRadioButton.isChecked():
            n = float(self.stationQueryDialog.locationRangeNorthLineEdit.text())
            e = float(self.stationQueryDialog.locationRangeEastLineEdit.text())
            s = float(self.stationQueryDialog.locationRangeSouthLineEdit.text())
            w = float(self.stationQueryDialog.locationRangeWestLineEdit.text())
            self.seismap.add_stations_box(n, e, s, w)
        elif self.stationQueryDialog.locationDistanceFromPointRadioButton.isChecked():
            n = float(self.stationQueryDialog.distanceFromPointNorthLineEdit.text())
            e = float(self.stationQueryDialog.distanceFromPointEastLineEdit.text())
            minradius = float(self.stationQueryDialog.distanceFromPointMinRadiusLineEdit.text())
            maxradius = float(self.stationQueryDialog.distanceFromPointMaxRadiusLineEdit.text())
            self.seismap.add_stations_toroid(n, e, minradius, maxradius)

        LOGGER.info('Loaded %d channels', stationsDF.shape[0])
        self.statusBar().showMessage('Loaded %d channels' % (stationsDF.shape[0]))


    @QtCore.pyqtSlot()
    def getWaveforms(self):
        self.waveformsDialog.show()
        self.waveformsDialog.loadWaveformChoices()


    @QtCore.pyqtSlot(int, int)
    def eventsTableClicked(self, row, col):
        """
        Handle a click anywhere in the table.
        """
        # Get selected rows
        rows = []
        for idx in self.eventsTable.selectionModel().selectedRows():
            rows.append(idx.row())

        LOGGER.debug('%d events currently selected', len(rows))

        # Get lons, lats and
        # TODO:  Automatically detect column indexes
        lons = []
        lats = []
        eventIDs = []
        for row in rows:
            lon = float(self.eventsTable.item(row,2).text())
            lons.append(lon)
            lat = float(self.eventsTable.item(row,3).text())
            lats.append(lat)
            eventID = str(self.eventsTable.item(row,12).text())
            eventIDs.append(eventID)

        # Update the events_handler with the latest selection information
        self.eventsHandler.set_selected_ids(eventIDs)

        self.seismap.add_events_highlighting(lons, lats)

        self.manageGetWaveformsButton()


    @QtCore.pyqtSlot(int, int)
    def stationsTableClicked(self, row, col):
        # Get selected rows
        rows = []
        for idx in self.stationsTable.selectionModel().selectedRows():
            rows.append(idx.row())

        LOGGER.debug('%d stations currently selected', len(rows))

        # Get lons and lats
        # TODO:  Automatically detect longitude and latitude columns
        lons = []
        lats = []
        SNCLs = []
        for row in rows:
            lon = float(self.stationsTable.item(row,4).text())
            lons.append(lon)
            lat = float(self.stationsTable.item(row,5).text())
            lats.append(lat)
            SNCL = str(self.stationsTable.item(row,17).text())
            SNCLs.append(SNCL)

        # Update the stations_handler with the latest selection information
        self.stationsHandler.set_selected_ids(SNCLs)

        self.seismap.add_stations_highlighting(lons, lats)

        self.manageGetWaveformsButton()


    def manageGetWaveformsButton(self):
        """
        Handle enabled/disabled status of the "Get Waveforms" button
        based on the presence/absence of selected events and stations
        """
        # http://stackoverflow.com/questions/3345785/getting-number-of-elements-in-an-iterator-in-python
        selectedEventsCount = sum(1 for idx in self.eventsTable.selectionModel().selectedRows() )
        selectedStationsCount = sum(1 for idx in self.stationsTable.selectionModel().selectedRows() )

        if selectedEventsCount > 0 and selectedStationsCount > 0:
            self.getWaveformsButton.setEnabled(True)
        else:
            self.getWaveformsButton.setEnabled(False)


    def aboutPyweed(self):
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
        msgBox.setWindowTitle(self.tr("About " + self.appName))
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
