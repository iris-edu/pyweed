from PyQt4 import QtGui, QtCore
from gui.uic import WaveformDialog
import os
from waveforms_handler import WaveformsHandler
import multiprocessing
import pandas as pd
import numpy as np
import obspy
from gui.MyTableWidgetImageWidget import MyTableWidgetImageWidget
from logging import getLogger
from gui.MyNumericTableWidgetItem import MyNumericTableWidgetItem
from gui.MyTableWidgetImageItem import MyTableWidgetImageItem

LOGGER = getLogger(__name__)


class WaveformDialog(QtGui.QDialog, WaveformDialog.Ui_WaveformDialog):
    """
    Dialog window for selection and display of waveforms.
    """
    def __init__(self, manager, parent=None):
        super(self.__class__, self).__init__(parent=parent)
        self.setupUi(self)
        self.setWindowTitle('Waveforms')

        # Keep a reference to globally shared components
        self.preferences = manager.pyweed.preferences
        self.client = manager.pyweed.client

        # Configured properties
        self.waveformDirectory = os.path.expanduser('~') # TODO:  get configurable WaveformDirectory

        # Modify default GUI settings
        self.saveDirectoryPushButton.setText(self.waveformDirectory)
        self.saveDirectoryPushButton.setFocusPolicy(QtCore.Qt.NoFocus)

        # Fill the format combo box
        self.saveFormatComboBox.addItems(['ASCII','GSE2','MSEED','SAC'])
        self.saveFormatComboBox.setCurrentIndex(2)

        LOGGER.debug('Initializing waveform dialog...')

        # Waveforms
        self.waveformsHandler = WaveformsHandler(LOGGER, self.preferences, self.client)
        self.waveformsDownloadComplete = False
        self.waveformsSaveComplete = ""
        self.waveformsHandler.progress.connect(self.on_waveform_downloaded)
        self.waveformsHandler.done.connect(self.on_all_downloaded)

#         # Get references to the Events and Stations objects
#         self.eventsHandler = parent.eventsHandler
#         self.stationsHandler = parent.stationsHandler

        # Set up queues to request waveform downloads and respond with a status
        self.waveformRequestQueue = multiprocessing.Queue()
        self.waveformResponseQueue = multiprocessing.Queue()

        # Displayed waveforms
        self.visibleWaveformsDF = pd.DataFrame()

        # Selection table
        self.selectionTable.setSortingEnabled(True)
        self.selectionTable.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.selectionTable.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.selectionTable.setSelectionMode(QtGui.QAbstractItemView.NoSelection)
        self.selectionTable.setVerticalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel)

        # Resize contents after sort
        self.selectionTable.horizontalHeader().sortIndicatorChanged.connect(self.selectionTable.resizeRowsToContents)

        # Connect the Download and Save GUI elements
        self.downloadToolButton.toggled.connect(self.toggledDownloadToolButton)
        self.saveToolButton.toggled.connect(self.toggledSaveToolButton)
        self.saveDirectoryPushButton.pressed.connect(self.getWaveformDirectory)
        self.saveFormatComboBox.activated.connect(self.resetSave)

        # Connect signals associated with comboBoxes
        # NOTE:  http://www.tutorialspoint.com/pyqt/pyqt_qcombobox_widget.htm
        # NOTE:  currentIndexChanged() responds to both user and programmatic changes. Use activated() for user initiated changes
        self.eventComboBox.activated.connect(self.loadFilteredSelectionTable)
        self.networkComboBox.activated.connect(self.loadFilteredSelectionTable)
        self.stationComboBox.activated.connect(self.loadFilteredSelectionTable)
        self.selectionTable.itemClicked.connect(self.handleTableItemClicked)

        # Connect signals associated with spinBoxes
        self.secondsBeforeSpinBox.valueChanged.connect(self.resetDownload)
        self.secondsAfterSpinBox.valueChanged.connect(self.resetDownload)

        # Set up a thread to watch for waveform requests that lasts as long as this dialog is open
        LOGGER.debug('Starting waveformRequestWatcherThread')
        #self.waveformRequestWatcher = waveformRequestWatcherThread(self.waveformRequestQueue)
        #self.waveformRequestWatcher.waveformRequestSignal.connect(self.handleWaveformRequest)
        #self.waveformRequestWatcher.start()

        # Set up a thread to watch for waveforms that lasts as long as this dialog is open
        LOGGER.debug('Starting waveformWatcher thread')
        #self.waveformResponseWatcher = waveformResponseWatcherThread(self.waveformResponseQueue)
        #self.waveformResponseWatcher.waveformResponseSignal.connect(self.handleWaveformResponse)
        #self.waveformResponseWatcher.start()

        LOGGER.debug('Finished initializing waveform dialog')


    def handleWaveformRequest(self):
        """
        This funciton is invoked whenever the waveformRequestWatcherThread emits
        a waveformRequestSignal. This means that a new waveform request has been
        assembled and placed on the waveformRequestQueue.
        """

        # NOTE:  The watcher should guarantee there is something in the queue
        # NOTE:  before emitting the waveformRequestSignal that is connected
        # NOTE:  to this function. But it doesn't hurt to check again.

        if not self.waveformRequestQueue.empty():

            # Get the request
            request = self.waveformRequestQueue.get()

            # Attempt to download a waveform
            secondsBefore = self.secondsBeforeSpinBox.value()
            secondsAfter = self.secondsAfterSpinBox.value()
            (status, waveformID, mseedFile, message) = self.waveformsHandler.handleWaveformRequest(request, secondsBefore, secondsAfter)

            # Update GUI
            QtGui.QApplication.processEvents()

            ## Announce that the downloaded mseedFile is ready for plotting
            ## TODO:  Maybe change the status and message to reflect "MSEED_READY". It should not be up the the downloader to decide what happens next.
            #message = "Plotting %s" % request['waveformID']

            self.waveformResponseQueue.put( {"status":status, "waveformID":waveformID, "mseedFile":mseedFile, "message":message})

        return


    def handleWaveformResponse(self):
        """
        This funciton is invoked whenever the waveformResponseWatcherThread emits
        a waveformResponseSignal. This means that handleWaveformRequest()
        has written a new .MSEED file to disk and it is available for processing.
        """
        if not self.waveformResponseQueue.empty():

            # TODO:  plot_width, plot_height should come from preferences
            plot_width = 600
            plot_height = 200

            # Get selectionTable column names
            column_names = self.waveformsHandler.getColumnNames()

            # Get the message sent by handleWaveformRequest
            item = self.waveformResponseQueue.get()
            status = item['status']
            waveformID = item['waveformID']
            mseedFile = item['mseedFile']
            message = item['message']

            LOGGER.debug("waveformResponseSignal: %s -- %s", status, waveformID)

            # WaveformDialog status text
            statusText = ''

            # Find selectionTable row
            row = 0
            for row in range(self.selectionTable.rowCount()):
                if self.selectionTable.item(row,column_names.index('WaveformID')).text() == waveformID:
                    break


            # Handle different status results
            if status == "MSEED_READY":

                # Update the statusLabel before the potentially slow plotting
                statusText = "Plotting %s" % waveformID
                self.downloadStatusLabel.setText(statusText)
                self.downloadStatusLabel.repaint()
                QtGui.QApplication.processEvents()

                try:
                    # Generate a plot
                    imagePath = mseedFile.replace('MSEED','png')
                    LOGGER.debug('reading %s', mseedFile)
                    st = obspy.core.read(mseedFile)
                    LOGGER.debug('plotting %s', imagePath)
                    st.plot(outfile=imagePath, size=(plot_width,plot_height))

                    # Update the waveforms_handler
                    self.waveformsHandler.setWaveformImagePath(waveformID, imagePath)

                    # Update the Table
                    # Add imagePath to the WaveformImagePath table cell
                    self.selectionTable.setItem(row, column_names.index('WaveformImagePath'), QtGui.QTableWidgetItem(imagePath))
                    # Add a pixmap to the Waveform table cell
                    imageItem = MyTableWidgetImageWidget(self, imagePath)
                    self.selectionTable.setCellWidget(row, column_names.index('Waveform'), imageItem)

                except Exception as e:
                    # Update the selectionTable
                    self.selectionTable.setItem(row, column_names.index('WaveformImagePath'), QtGui.QTableWidgetItem('NO DATA AVAILABLE'))
                    self.selectionTable.setItem(row, column_names.index('Waveform'), QtGui.QTableWidgetItem('NO DATA AVAILABLE'))
                    # Update the waveforms_handler
                    self.waveformsHandler.setWaveformImagePath(waveformID, 'NO DATA AVAILABLE')
                    statusText = "No data available for %s" % waveformID

            else:
                # Problem downloading
                if message.find("No data available") >= 0:
                    statusText = "No data available for %s" % waveformID
                else:
                    statusText = message

                # Update the waveforms_handler
                self.waveformsHandler.setWaveformImagePath(waveformID, 'NO DATA AVAILABLE')

                # Update the Table
                # Set the selectionTable Waveform and WaveformImagePath columns
                self.selectionTable.setItem(row, column_names.index('WaveformImagePath'), QtGui.QTableWidgetItem('NO DATA AVAILABLE'))
                self.selectionTable.setItem(row, column_names.index('Waveform'), QtGui.QTableWidgetItem('NO DATA AVAILABLE'))

            # Tighten up the table
            # self.selectionTable.resizeColumnsToContents()
            self.selectionTable.resizeRowsToContents()

            # Update GUI
            QtGui.QApplication.processEvents()

            if self.downloadToolButton.isChecked():
                # Update status text
                self.downloadStatusLabel.setText(statusText)
                self.downloadStatusLabel.repaint()
                # Request more data
                self.downloadWaveformData()
            else:
                # Update status text
                self.downloadStatusLabel.setText('')
                self.downloadStatusLabel.repaint()

        return


    # NOTE:  http://stackoverflow.com/questions/12366521/pyqt-checkbox-in-qtablewidget
    # NOTE:  http://stackoverflow.com/questions/30462078/using-a-checkbox-in-pyqt
    def handleTableItemClicked(self, item):
        """
        Triggered whenever an item in the waveforms table is clicked.
        """
        # The checkbox column is named 'Keep'
        row = item.row()
        col = item.column()
        column_names = self.waveformsHandler.getColumnNames()
        keepItem = self.selectionTable.item(row, column_names.index('Keep'))

        LOGGER.debug("Clicked on table row")

        # Toggle the and Keep state
        waveformID = str(self.selectionTable.item(row,column_names.index('WaveformID')).text())
        if keepItem.checkState() == QtCore.Qt.Checked:
            keepItem.setCheckState(QtCore.Qt.Unchecked)
            self.waveformsHandler.setWaveformKeep(waveformID, False)
        else:
            keepItem.setCheckState(QtCore.Qt.Checked)
            self.waveformsHandler.setWaveformKeep(waveformID, True)

        return


    @QtCore.pyqtSlot()
    def loadWaveformChoices(self, filterColumn=None, filterText=None):
        """
        Fill the selectionTable with all SNCL-Event combinations selected in the MainWindow.
        This funciton is triggered whenever the "Get Waveforms" button in the MainWindow is clicked.
        """

        LOGGER.debug('Loading waveform choices...')

        self.waveformsDownloadComplete = False

        ## Create a new dataframe with time, source_lat, source_lon, source_mag, source_depth, SNCL, network, station, receiver_lat, receiver_lon -- one for each waveform
        eventsDF = self.eventsHandler.get_selected_dataframe()
        stationsDF = self.stationsHandler.get_selected_dataframe()

        self.downloadStatusLabel.setText("Calculating distances...")
        self.downloadStatusLabel.repaint()

        waveformsDF = self.waveformsHandler.createWaveformsDF(eventsDF, stationsDF)

        self.downloadStatusLabel.setText("")
        self.downloadStatusLabel.repaint()

        LOGGER.debug('Finished building dataframe for %d waveforms', waveformsDF.shape[0])

        # Add event-SNCL combintations to the selection table
        self.loadSelectionTable(waveformsDF)

        # Tighten up the table
        self.selectionTable.resizeColumnsToContents()
        self.selectionTable.horizontalHeader().setStretchLastSection(True)

        # Add unique events to the eventComboBox -------------------------------

        for i in range(self.eventComboBox.count()):
            self.eventComboBox.removeItem(0)

        self.eventComboBox.addItem('All events')
        for i in range(eventsDF.shape[0]):
            self.eventComboBox.addItem(eventsDF.Time.iloc[i])

        # Add unique networks to the networkComboBox ---------------------------

        for i in range(self.networkComboBox.count()):
            self.networkComboBox.removeItem(0)

        self.networkComboBox.addItem('All networks')
        for network in stationsDF.Network.unique().tolist():
            self.networkComboBox.addItem(network)

        # Add unique stations to the stationsComboBox --------------------------

        for i in range(self.stationComboBox.count()):
            self.stationComboBox.removeItem(0)

        self.stationComboBox.addItem('All stations')
        for station in stationsDF.Station.unique().tolist():
            self.stationComboBox.addItem(station)

        LOGGER.debug('Finished loading waveform choices')

        # Initialize saveToolButton to OFF/UP
        self.saveToolButton.setEnabled(True)
        self.saveToolButton.setChecked(False)
        self.saveToolButton.setDown(False)
        self.toggledSaveToolButton() # trigger toggled action

        # Initialize downloadToolButton to ON/DOWN
        self.downloadToolButton.setEnabled(True)
        self.downloadToolButton.setChecked(True)
        self.downloadToolButton.setDown(True)
        self.toggledDownloadToolButton() # trigger toggled action

        return



    @QtCore.pyqtSlot()
    def loadSelectionTable(self, waveformsDF):
        """
        Add event-SNCL combintations to the selection table
        """

        LOGGER.debug('Loading waveform selection table...')

        self.visibleWaveformsDF = waveformsDF

        # NOTE:  You must disable sorting before populating the table. Otherwise rows get
        # NOTE:  sorted as soon as the sortable column gets filled in, thus invalidating
        # NOTE:  the row number
        self.selectionTable.setSortingEnabled(False)

        # Note:  Display information should be in the GUI code but needs to match
        # NOTE:  the columns which are created by the waveforms_handler.
        hidden_column = self.waveformsHandler.getColumnHidden()
        numeric_column = self.waveformsHandler.getColumnNumeric()

        # Clear existing contents
        self.selectionTable.clear() # This is important!
        while (self.selectionTable.rowCount() > 0):
            self.selectionTable.removeRow(0)

        # Create new table
        self.selectionTable.setRowCount(waveformsDF.shape[0])
        self.selectionTable.setColumnCount(waveformsDF.shape[1])
        self.selectionTable.setHorizontalHeaderLabels(waveformsDF.columns.tolist())
        self.selectionTable.horizontalHeader().setStretchLastSection(True)
        self.selectionTable.verticalHeader().hide()
        # Hidden columns
        for i in np.arange(len(hidden_column)):
            if hidden_column[i]:
                self.selectionTable.setColumnHidden(i,True)

        # Add new contents
        for i in range(waveformsDF.shape[0]):
            for j in range(waveformsDF.shape[1]):
                if numeric_column[j]:
                    # Guarantee that all elements are converted to strings for display but apply proper sorting
                    self.selectionTable.setItem(i, j, MyNumericTableWidgetItem(str(waveformsDF.iat[i,j])))

                elif waveformsDF.columns[j] == 'Waveform':
                    # NOTE:  What to put in the Waveform column depends on what is in the WaveformImagePath column.
                    # NOTE:  It could be plain text or an imageWidget.
                    if waveformsDF.WaveformImagePath.iloc[i] == '':
                        self.selectionTable.setItem(i, j, QtGui.QTableWidgetItem(''))
                    elif waveformsDF.WaveformImagePath.iloc[i] == 'NO DATA AVAILABLE':
                        self.selectionTable.setItem(i, j, QtGui.QTableWidgetItem('NO DATA AVAILABLE'))
                    else:
                        imagePath = waveformsDF.WaveformImagePath.iloc[i]
                        imageItem = MyTableWidgetImageItem(imagePath)
                        self.selectionTable.setItem(i, j, imageItem)

                elif waveformsDF.columns[j] == 'Keep':
                    checkBoxItem = QtGui.QTableWidgetItem()
                    checkBoxItem.setFlags(QtCore.Qt.ItemIsEnabled)
                    if self.waveformsHandler.getWaveformKeep(waveformsDF.WaveformID.iloc[i]):
                        checkBoxItem.setCheckState(QtCore.Qt.Checked)
                    else:
                        checkBoxItem.setCheckState(QtCore.Qt.Unchecked)
                    self.selectionTable.setItem(i, j, checkBoxItem)

                else:
                    # Anything else is converted to normal text
                    self.selectionTable.setItem(i, j, QtGui.QTableWidgetItem(str(waveformsDF.iat[i,j])))

        # Tighten up the table
        # self.selectionTable.resizeColumnsToContents()
        self.selectionTable.resizeRowsToContents()

        # Restore table sorting
        self.selectionTable.setSortingEnabled(True)

        LOGGER.debug('Finished loading waveform selection table')

        self.downloadWaveformData()

        return


    @QtCore.pyqtSlot(int)
    def loadFilteredSelectionTable(self):
        """
        Filter waveformsDF based on filter selections and then reload the selectionTable.
        """
        waveformsDF = self.waveformsHandler.currentDF
        time = self.eventComboBox.currentText()
        network = self.networkComboBox.currentText()
        station = self.stationComboBox.currentText()
        LOGGER.debug('Filtering waveformsDF...')
        if not time.startswith('All'):
            waveformsDF = waveformsDF[waveformsDF.Time == time]
        if not network.startswith('All'):
            waveformsDF = waveformsDF[waveformsDF.Network == network]
        if not station.startswith('All'):
            waveformsDF = waveformsDF[waveformsDF.Station == station]
        LOGGER.debug('Finished filtering waveformsDF')
        self.loadSelectionTable(waveformsDF)

        # Tighten up the table
        #self.selectionTable.resizeColumnsToContents()
        #self.selectionTable.resizeRowsToContents()

        return


    @QtCore.pyqtSlot()
    def toggledDownloadToolButton(self):
        """
        Triggered after downloadToolButton is toggled.
        """

        if self.downloadToolButton.isChecked():
            if self.waveformsDownloadComplete:
                # pop the button back up and enable Download GUI elements
                self.downloadToolButton.setText('Download Finished')
                self.downloadGroupBox.setStyleSheet("QGroupBox { background-color: #e7e7e7 } ")
                self.secondsBeforeSpinBox.setEnabled(True)
                self.secondsAfterSpinBox.setEnabled(True)
                self.secondsBeforeLabel.setStyleSheet('color: black')
                self.secondsAfterLabel.setStyleSheet('color: black')
                self.downloadToolButton.setChecked(False)
                self.downloadToolButton.setDown(False)
            else:
                # leave the button down and disable Download GUI elements
                self.downloadToolButton.setText('Downloading...')
                self.downloadGroupBox.setStyleSheet("QGroupBox { background-color: #EEDC82 } ") # light goldenrod 2
                self.secondsBeforeSpinBox.setEnabled(False)
                self.secondsAfterSpinBox.setEnabled(False)
                self.secondsBeforeLabel.setStyleSheet('color: gray')
                self.secondsAfterLabel.setStyleSheet('color: gray')
                # Resume downloading
                self.downloadWaveformData()

        else:
            # leave the button up and enable Download GUI elements
            if self.waveformsDownloadComplete:
                self.downloadToolButton.setText('Download Finished')
            else:
                self.downloadToolButton.setText('Download Stopped')
            self.downloadGroupBox.setStyleSheet("QGroupBox { background-color: #e7e7e7 } ")
            self.secondsBeforeSpinBox.setEnabled(True)
            self.secondsAfterSpinBox.setEnabled(True)
            self.secondsBeforeLabel.setStyleSheet('color: black')
            self.secondsAfterLabel.setStyleSheet('color: black')


        return


    @QtCore.pyqtSlot()
    def toggledSaveToolButton(self):
        """
        Triggered after saveToolButton is toggled.
        """

        formatChoice = str(self.saveFormatComboBox.currentText())

        # Saving down/on
        if self.saveToolButton.isChecked():
            # disable GUI elements
            self.saveDirectoryPushButton.setEnabled(False)
            self.saveFormatComboBox.setEnabled(False)
            self.saveDirectoryLabel.setStyleSheet('color: gray')
            self.saveFormatLabel.setStyleSheet('color: gray')
            if self.waveformsDownloadComplete:
                if self.waveformsSaveComplete.find(formatChoice) >= 0:
                    self.saveToolButton.setText('Save Finished')
                else:
                    self.saveToolButton.setText('Saving...')
                    self.saveWaveformData()
            else:
                self.saveToolButton.setText('Save Scheduled')
                self.saveStatusLabel.setText("Wating for downloads to finish...")

        # Saving up/off
        else:
            # Enable GUI elements
            self.saveDirectoryPushButton.setEnabled(True)
            self.saveFormatComboBox.setEnabled(True)
            self.saveDirectoryLabel.setStyleSheet('color: black')
            self.saveFormatLabel.setStyleSheet('color: black')
            if self.waveformsDownloadComplete:
                if self.waveformsSaveComplete.find(formatChoice) >= 0:
                    self.saveToolButton.setText('Save Finished')
                else:
                    self.saveToolButton.setText('Save Stopped')
            else:
                self.saveToolButton.setText('No Save Scheduled')
                self.saveStatusLabel.setText("")

        return


    @QtCore.pyqtSlot()
    def resetDownload(self):
        """
        This function is triggered whenever the values in secondsBeforeSpinBox or
        secondsAfterSpinBox are changed. Any change means that we need to wipe out
        all the downloads that have occurred and start over.
        """
        self.waveformsDownloadComplete = False
        self.resetSave()
        self.waveformsHandler.currentDF.WaveformImagePath = ''
        self.loadSelectionTable(self.waveformsHandler.currentDF)


    @QtCore.pyqtSlot()
    def resetSave(self):
        """
        This function is triggered whenever the values in saveDirectory or
        saveFormat elements are changed. Any change means that we need to
        start saving from the beginning.
        """
        self.waveformsSaveComplete = ""
        if self.waveformsDownloadComplete:
            self.saveStatusLabel.setText("")
        else:
            self.saveStatusLabel.setText("Waiting for downloads to finish...")


    @QtCore.pyqtSlot()
    def downloadWaveformData(self):
        """
        This function is triggered after the selectionTable is initially loaded
        by loadWaveformChoices() and, after that, by handleWaveformResponse() after
        it has finished handling a waveform.

        This function looks at the current selectionTable view for any waveforms
        that have not yet been downloaded. After that table is exhausted, it goes
        through all not-yet-downloaded data in waveformHandler.currentDF.
        """

        # Update GUI in case we came from an internal call
        QtGui.QApplication.processEvents()

        # WaveformDialog status text
        statusText = ''

        secondsBefore = self.secondsBeforeSpinBox.value()
        secondsAfter = self.secondsAfterSpinBox.value()

        # Priority is given to waveforms shown on the screen
        priority_waveforms = self.visibleWaveformsDF
        all_waveforms = self.waveformsHandler.currentDF
        other_waveforms = all_waveforms[~all_waveforms.WaveformID.isin(priority_waveforms.WaveformID)]

        self.waveformsHandler.download_waveforms(
            priority_waveforms.WaveformID, other_waveforms.WaveformID,
            secondsBefore, secondsAfter)

    def on_log(self, msg):
        LOGGER.error("Uh oh, called WaveformDialog.on_log: %s", msg)

    def get_table_row(self, waveform_id):
        column_names = self.waveformsHandler.getColumnNames()
        row = 0
        for row in range(self.selectionTable.rowCount()):
            if self.selectionTable.item(row, column_names.index('WaveformID')).text() == waveform_id:
                return row
        return None

    def on_waveform_downloaded(self, result):
        waveform_id = result.waveform_id
        LOGGER.debug("Ready to display waveform %s", waveform_id)

        row = self.get_table_row(waveform_id)
        if row is None:
            LOGGER.error("Couldn't find a row for waveform %s", waveform_id)
            return

        column_names = self.waveformsHandler.getColumnNames()

        if isinstance(result.result, Exception):
            LOGGER.error("Error retrieving %s: %s", waveform_id, result.result)
            self.selectionTable.setItem(row, column_names.index('WaveformImagePath'), QtGui.QTableWidgetItem('NO DATA AVAILABLE'))
            self.selectionTable.setItem(row, column_names.index('Waveform'), QtGui.QTableWidgetItem('NO DATA AVAILABLE'))
        else:
            image_path = result.result
            self.selectionTable.setItem(row, column_names.index('WaveformImagePath'), QtGui.QTableWidgetItem(image_path))
            # Add a pixmap to the Waveform table cell
            imageItem = MyTableWidgetImageWidget(self, image_path)
            self.selectionTable.setCellWidget(row, column_names.index('Waveform'), imageItem)

        LOGGER.debug("Displayed waveform %s", waveform_id)

        # Tighten up the table
        self.selectionTable.resizeColumnsToContents()
        self.selectionTable.resizeRowsToContents()
        self.selectionTable.horizontalHeader().setStretchLastSection(True)

    def on_all_downloaded(self, result):
        self.waveformsDownloadComplete = True
        self.downloadToolButton.setEnabled(True) # TODO:  set this to False
        self.downloadToolButton.setChecked(False) # up/off
        self.downloadToolButton.setDown(False) # up/off
        self.toggledDownloadToolButton()
        LOGGER.debug('COMPLETED all downloads')

        statusText = "Completed all downloads"


        # Update GUI
        QtGui.QApplication.processEvents()

        # Update status text
        self.downloadStatusLabel.setText(statusText)
        self.downloadStatusLabel.repaint()

        # Save data if appropriate
        if self.waveformsDownloadComplete:
            if self.saveToolButton.isChecked():
                self.saveWaveformData()

        return


    @QtCore.pyqtSlot()
    def saveWaveformData(self):
        """
        Save waveforms after all downloads are complete.
        """

        inputDir = self.waveformsHandler.downloadDir
        outputDir = self.waveformDirectory # TODO:  change to saveDir

        # Handle user format choice
        formatChoice = str(self.saveFormatComboBox.currentText())
        if formatChoice == 'ASCII':
            outputFormat = 'TSPAIR'
            extension = 'ascii'
        elif formatChoice == 'GSE2':
            outputFormat = 'GSE2'
            extension = 'gse'
        elif formatChoice == 'MSEED':
            outputFormat = 'MSEED'
            extension = 'mseed'
        elif formatChoice == 'SAC':
            outputFormat = 'SAC'
            extension = 'sac'
        else:
            LOGGER.error('Output format "%s" not recognized' % formatChoice)
            self.saveStatusLabel.setText('Output format "%s" not recognized' % formatChoice)
            self.saveStatusLabel.repaint()
            return

        self.saveGroupBox.setStyleSheet("QGroupBox { background-color: #EEDC82 } ") # light goldenrod 2
        self.saveToolButton.setText('Saving...')

        # Total to be saved
        keep = self.waveformsHandler.currentDF.Keep
        waveformImagePath = self.waveformsHandler.currentDF.WaveformImagePath
        waveformAvailable = np.invert( waveformImagePath.str.contains("NO DATA AVAILABLE"))
        totalCount = sum(keep & waveformAvailable)

        # Loop over the table, read in and convert all waveforms that are selected and available
        savedCount = 0
        for row in range(self.waveformsHandler.currentDF.shape[0]):
            keep = self.waveformsHandler.currentDF.Keep.iloc[row]
            waveformID = self.waveformsHandler.currentDF.WaveformID.iloc[row]
            waveformImagePath = self.waveformsHandler.currentDF.WaveformImagePath.iloc[row]
            if keep and (waveformImagePath != "NO DATA AVAILABLE"):
                mseedPath = waveformImagePath.replace('.png','.MSEED')
                mseedFile = os.path.basename(mseedPath)
                outputFile = mseedFile.replace('MSEED',extension)
                outputPath = os.path.join(outputDir,outputFile)
                # Don't repeat any work that has already been done
                if not os.path.exists(outputPath):
                    statusText = "Saving %s " % (outputFile)
                    LOGGER.debug('reading %s', mseedFile)
                    st = obspy.core.read(mseedPath)
                    LOGGER.debug('writing %s', outputPath)
                    st.write(outputPath, format=outputFormat)

                savedCount += 1
                self.saveStatusLabel.setText("Saved %d / %d waveforms as %s" % (savedCount,totalCount,formatChoice))
                self.saveStatusLabel.repaint()
                QtGui.QApplication.processEvents() # update GUI

                # Return early if the user has toggled off the saveToolButton
                if not self.saveToolButton.isChecked():
                    return

        # Toggle saveToolButton state
        self.waveformsSaveComplete += formatChoice + ","
        self.saveToolButton.setEnabled(True)
        self.saveToolButton.setChecked(False) # up/off
        self.saveToolButton.setDown(False) # up/off
        self.toggledSaveToolButton()
        self.saveGroupBox.setStyleSheet("QGroupBox { background-color: #e7e7e7 } ")

        LOGGER.debug('COMPLETED saving all waveforms')


    @QtCore.pyqtSlot()
    def getWaveformDirectory(self):
        """
        This function is triggered whenever the user presses the "to <directory>" button.
        """

        # If the user quits or cancels this dialog, '' is returned
        newDirectory = str(QtGui.QFileDialog.getExistingDirectory(
            self,
            "Waveform Directory",
            os.path.expanduser("~"),
            QtGui.QFileDialog.ShowDirsOnly))

        if newDirectory != '':
            self.waveformDirectory = newDirectory
            self.saveDirectoryPushButton.setText(self.waveformDirectory)
            self.resetSave()

