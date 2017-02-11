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
from gui.TableItems import TableItems

LOGGER = getLogger(__name__)


# Download/save status values
STATUS_READY = "ready"  # Waiting for user to initiate
STATUS_WORKING = "working"  # Working
STATUS_DONE = "done"  # Finished


class WaveformTableItems(TableItems):
    pass


class WaveformDialog(QtGui.QDialog, WaveformDialog.Ui_WaveformDialog):

    tableItems = None

    """
    Dialog window for selection and display of waveforms.
    """
    def __init__(self, pyweed, parent=None):
        super(self.__class__, self).__init__(parent=parent)
        self.setupUi(self)
        self.setWindowTitle('Waveforms')

        # Keep a reference to globally shared components
        self.pyweed = pyweed
        self.preferences = pyweed.preferences
        self.client = pyweed.client

        # Configured properties
        self.waveformDirectory = pyweed.preferences.Waveforms.saveDir

        # Modify default GUI settings
        self.saveDirectoryPushButton.setText(self.waveformDirectory)
        self.saveDirectoryPushButton.setFocusPolicy(QtCore.Qt.NoFocus)

        # Fill the format combo box
        self.saveFormatComboBox.addItems(['ASCII','GSE2','MSEED','SAC'])
        self.saveFormatComboBox.setCurrentIndex(2)

        LOGGER.debug('Initializing waveform dialog...')

        # Waveforms
        self.waveformsHandler = WaveformsHandler(LOGGER, self.preferences, self.client)
        self.waveformsHandler.progress.connect(self.on_waveform_downloaded)
        self.waveformsHandler.done.connect(self.on_all_downloaded)

        # Displayed waveforms
        self.visibleWaveformsDF = pd.DataFrame()

        # Resize contents after sort
        self.selectionTable.horizontalHeader().sortIndicatorChanged.connect(self.selectionTable.resizeRowsToContents)

        # Connect the Download and Save GUI elements
        self.downloadPushButton.clicked.connect(self.onDownloadPushButton)
        self.savePushButton.clicked.connect(self.onSavePushButton)
        self.saveDirectoryPushButton.clicked.connect(self.getWaveformDirectory)
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

        LOGGER.debug('Finished initializing waveform dialog')

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

    @QtCore.pyqtSlot()
    def loadWaveformChoices(self, filterColumn=None, filterText=None):
        """
        Fill the selectionTable with all SNCL-Event combinations selected in the MainWindow.
        This funciton is triggered whenever the "Get Waveforms" button in the MainWindow is clicked.
        """

        LOGGER.debug('Loading waveform choices...')

        self.resetDownload()

        ## Create a new dataframe with time, source_lat, source_lon, source_mag, source_depth, SNCL, network, station, receiver_lat, receiver_lon -- one for each waveform
        eventsDF = self.pyweed.events_handler.get_selected_dataframe()
        stationsDF = self.pyweed.stations_handler.get_selected_dataframe()

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

        self.resetDownload()

    @QtCore.pyqtSlot()
    def loadSelectionTable(self, waveformsDF):
        """
        Add event-SNCL combinations to the selection table
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

        # Use WaveformTableItems to put the DF into the table
        if not self.tableItems:
            self.tableItems = WaveformTableItems(
                self.selectionTable,
                hidden_column,
                numeric_column
            )
        self.tableItems.build(waveformsDF)

        # Restore table sorting
        self.selectionTable.setSortingEnabled(True)

        # Start downloading the waveform data unless this is a filtered DF
        if waveformsDF == self.waveformsHandler.currentDF:
            LOGGER.debug('Starting download of waveform data')
            self.downloadWaveformData()

        LOGGER.debug('Finished loading waveform selection table')

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

    def onDownloadPushButton(self):
        """
        Triggered when downloadPushButton is clicked.
        """
        if self.waveformsDownloadStatus == STATUS_READY:
            # Start the download
            self.downloadWaveformData()

    def updateToolbars(self):
        """
        Update the UI elements to reflect the download status
        """
        # Download controls
        if self.waveformsDownloadStatus == STATUS_WORKING:
            # Currently downloading, disable most of the UI
            self.downloadGroupBox.setEnabled(False)
            self.downloadPushButton.setChecked(True)
            self.downloadPushButton.setText('Downloading...')
        else:
            self.downloadGroupBox.setEnabled(True)
            self.downloadPushButton.setChecked(False)
            if self.waveformsDownloadStatus == STATUS_READY:
                # Normal operation
                self.downloadPushButton.setText('Download')
                self.downloadPushButton.setEnabled(True)
            else:
                self.downloadPushButton.setText('Download Complete')
                self.downloadPushButton.setEnabled(False)

        # Save controls
        if self.waveformsSaveStatus == STATUS_WORKING:
            # Currently saving
            self.saveGroupBox.setEnabled(False)
            self.savePushButton.setText('Saving...')
            self.savePushButton.setChecked(True)
            if self.waveformsDownloadStatus != STATUS_DONE:
                self.saveStatusLabel.setText('Waiting for downloads to finish')
            else:
                self.saveStatusLabel.setText('')
        else:
            self.savePushButton.setText('Save')
            self.savePushButton.setChecked(False)
            if self.waveformsDownloadStatus == STATUS_READY:
                # Data hasn't been downloaded yet
                self.saveGroupBox.setEnabled(False)
                self.saveStatusLabel.setText('Download waveforms first!')
            else:
                # Available
                self.saveGroupBox.setEnabled(True)
                self.saveStatusLabel.setText('')

    def onSavePushButton(self):
        """
        Triggered after savePushButton is toggled.
        """
        if self.waveformsSaveStatus == STATUS_READY:
            self.waveformsSaveStatus = STATUS_WORKING
            if self.waveformsDownloadStatus == STATUS_DONE:
                self.saveWaveformData()

    @QtCore.pyqtSlot()
    def resetDownload(self):
        """
        This function is triggered whenever the values in secondsBeforeSpinBox or
        secondsAfterSpinBox are changed. Any change means that we need to wipe out
        all the downloads that have occurred and start over.
        """
        LOGGER.debug("Download button reset")
        self.waveformsDownloadStatus = STATUS_READY
        self.resetSave()
        #self.waveformsHandler.currentDF.WaveformImagePath = ''
        #self.loadSelectionTable(self.waveformsHandler.currentDF)


    @QtCore.pyqtSlot()
    def resetSave(self):
        """
        This function is triggered whenever the values in saveDirectory or
        saveFormat elements are changed. Any change means that we need to
        start saving from the beginning.
        """
        LOGGER.debug("Save button reset")
        self.waveformsSaveStatus = STATUS_READY
        self.updateToolbars()


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

        LOGGER.info("Starting download of waveform data")

        # WaveformDialog status text
        statusText = ''
        self.waveformsDownloadStatus = STATUS_WORKING
        self.updateToolbars()

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
        """
        Get the table row for a given waveform
        """
        column_names = self.waveformsHandler.getColumnNames()
        row = 0
        for row in range(self.selectionTable.rowCount()):
            if self.selectionTable.item(row, column_names.index('WaveformID')).text() == waveform_id:
                return row
        return None

    def on_waveform_downloaded(self, result):
        """
        Called each time a waveform request has completed
        """
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
        """
        Called after all waveforms have been downloaded
        """
        LOGGER.debug('COMPLETED all downloads')

        if self.waveformsDownloadStatus == STATUS_WORKING:
            self.waveformsDownloadStatus = STATUS_DONE
            self.updateToolbars()

            # Save data if appropriate
            if self.waveformsSaveStatus == STATUS_WORKING:
                self.saveWaveformData()


    @QtCore.pyqtSlot()
    def saveWaveformData(self):
        """
        Save waveforms after all downloads are complete.
        """

        # Update status
        self.waveformsSaveStatus = STATUS_WORKING
        self.updateToolbars()

        # Update GUI in case we came from an internal call
        QtGui.QApplication.processEvents()

        try:
            outputDir = self.waveformDirectory

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
                raise Exception('Output format "%s" not recognized' % formatChoice)

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

                    # Return early if the user has toggled off the savePushButton
                    if not self.savePushButton.isChecked():
                        break
        except Exception as e:
            LOGGER.error(e)
            self.saveStatusLabel.setText(e.message)
        finally:
            self.waveformsSaveStatus = STATUS_READY
            self.updateToolbars()

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
            self.waveformDirectory,
            QtGui.QFileDialog.ShowDirsOnly))

        if newDirectory != '':
            self.waveformDirectory = newDirectory
            self.saveDirectoryPushButton.setText(self.waveformDirectory)
            self.resetSave()
