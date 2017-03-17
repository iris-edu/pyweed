from PyQt4 import QtGui, QtCore
from gui.uic import WaveformDialog
from waveforms_handler import WaveformsHandler
from logging import getLogger
from gui.MyTableWidgetImageItem import MyTableWidgetImageItem
from gui.TableItems import TableItems
from pyweed_utils import get_event_name, TimeWindow, OUTPUT_FORMATS, PHASES
from preferences import safe_int
from PyQt4.QtGui import QTableWidgetItem
from gui.utils import ComboBoxAdapter

LOGGER = getLogger(__name__)


# Download/save status values
STATUS_READY = "ready"  # Waiting for user to initiate
STATUS_WORKING = "working"  # Working
STATUS_DONE = "done"  # Finished
STATUS_ERROR = "error"  # Something went wrong


class WaveformTableItems(TableItems):

    columnNames = [
        'Id',
        'Keep',
        'Event Name',
        'SNCL',
        'Distance',
        'Waveform',
    ]

    def imageWidget(self, waveform):
        if waveform.image_exists:
            return MyTableWidgetImageItem(waveform.image_path)
        elif waveform.error:
            return self.stringWidget(waveform.error)
        else:
            return self.stringWidget('')

    def rows(self, data):
        """
        Turn the data into rows (an iterable of lists) of QTableWidgetItems
        """
        for waveform in data:
            yield [
                self.stringWidget(waveform.waveform_id),
                self.checkboxWidget(waveform.keep),
                self.stringWidget(waveform.event_name),
                self.stringWidget(waveform.sncl),
                self.numericWidget(round(waveform.distances.distance, 2)),
                self.imageWidget(waveform),
            ]


# Convenience values for some commonly used table column values
WAVEFORM_ID_COLUMN = WaveformTableItems.columnNames.index('Id')
WAVEFORM_KEEP_COLUMN = WaveformTableItems.columnNames.index('Keep')
WAVEFORM_IMAGE_COLUMN = WaveformTableItems.columnNames.index('Waveform')


class TimeWindowAdapter(QtCore.QObject):
    """
    Adapter tying a set of inputs to a TimeWindow
    """

    # Signal indicating that the time window has changed
    changed = QtCore.pyqtSignal()

    def __init__(self, secondsBeforeSpinBox, secondsAfterSpinBox,
                 secondsBeforePhaseComboBox, secondsAfterPhaseComboBox):
        super(TimeWindowAdapter, self).__init__()

        self.timeWindow = TimeWindow()
        # Phase options
        phaseOptions = [(phase.name, phase.label) for phase in PHASES]

        self.secondsBeforeSpinBox = secondsBeforeSpinBox
        self.secondsAfterSpinBox = secondsAfterSpinBox
        self.secondsBeforePhaseAdapter = ComboBoxAdapter(
            secondsBeforePhaseComboBox, phaseOptions)
        self.secondsAfterPhaseAdapter = ComboBoxAdapter(
            secondsAfterPhaseComboBox, phaseOptions)

        # Connect input signals
        self.secondsBeforeSpinBox.valueChanged.connect(self.onTimeWindowChanged)
        self.secondsAfterSpinBox.valueChanged.connect(self.onTimeWindowChanged)
        self.secondsBeforePhaseAdapter.changed.connect(self.onTimeWindowChanged)
        self.secondsAfterPhaseAdapter.changed.connect(self.onTimeWindowChanged)

    def onTimeWindowChanged(self):
        """
        When an input changes, update the time window and emit a notification
        """
        self.timeWindow.update(
            self.secondsBeforeSpinBox.value(),
            self.secondsAfterSpinBox.value(),
            self.secondsBeforePhaseAdapter.getValue(),
            self.secondsAfterPhaseAdapter.getValue()
        )
        self.changed.emit()

    def setValues(self, start_offset, end_offset, start_phase, end_phase):
        """
        This should be called on startup to set the initial values
        """
        self.timeWindow.update(
            start_offset, end_offset, start_phase, end_phase
        )
        self.updateInputs()

    def updateInputs(self):
        """
        Update the inputs to reflect the current state
        """
        self.secondsBeforeSpinBox.setValue(self.timeWindow.start_offset)
        self.secondsAfterSpinBox.setValue(self.timeWindow.end_offset)
        self.secondsBeforePhaseAdapter.setValue(self.timeWindow.start_phase)
        self.secondsAfterPhaseAdapter.setValue(self.timeWindow.end_phase)


class WaveformDialog(QtGui.QDialog, WaveformDialog.Ui_WaveformDialog):

    tableItems = None

    """
    Dialog window for selection and display of waveforms.
    """
    def __init__(self, pyweed, parent=None):
        super(self.__class__, self).__init__(parent=parent)

        LOGGER.debug('Initializing waveform dialog...')

        self.setupUi(self)
        self.setWindowTitle('Waveforms')

        # Keep a reference to globally shared components
        self.pyweed = pyweed

        # Time window for waveform selection
        self.timeWindowAdapter = TimeWindowAdapter(
            self.secondsBeforeSpinBox,
            self.secondsAfterSpinBox,
            self.secondsBeforePhaseComboBox,
            self.secondsAfterPhaseComboBox
        )

        self.saveFormatAdapter = ComboBoxAdapter(
            self.saveFormatComboBox,
            [(f.value, f.label) for f in OUTPUT_FORMATS]
        )

        # Initialize any preference-based settings
        self.loadPreferences()

        # Modify default GUI settings
        self.saveDirectoryPushButton.setText(self.waveformDirectory)
        self.saveDirectoryPushButton.setFocusPolicy(QtCore.Qt.NoFocus)

        # Waveforms
        self.waveformsHandler = WaveformsHandler(LOGGER, pyweed.preferences, pyweed.client)
        self.waveformsHandler.progress.connect(self.onWaveformDownloaded)
        self.waveformsHandler.done.connect(self.onAllDownloaded)

        # Connect signals associated with the main table
        self.selectionTable.horizontalHeader().sortIndicatorChanged.connect(self.selectionTable.resizeRowsToContents)
        self.selectionTable.itemClicked.connect(self.handleTableItemClicked)

        # Connect the Download and Save GUI elements
        self.downloadPushButton.clicked.connect(self.onDownloadPushButton)
        self.savePushButton.clicked.connect(self.onSavePushButton)
        self.saveDirectoryPushButton.clicked.connect(self.getWaveformDirectory)

        self.saveFormatAdapter.changed.connect(self.resetSave)

        # Connect signals associated with comboBoxes
        # NOTE:  http://www.tutorialspoint.com/pyqt/pyqt_qcombobox_widget.htm
        # NOTE:  currentIndexChanged() responds to both user and programmatic changes.
        #        Use activated() for user initiated changes
        self.eventComboBox.activated.connect(self.loadFilteredSelectionTable)
        self.networkComboBox.activated.connect(self.loadFilteredSelectionTable)
        self.stationComboBox.activated.connect(self.loadFilteredSelectionTable)

        # Connect the timewindow signals
        self.timeWindowAdapter.changed.connect(self.resetDownload)

        # Dictionary of filter values
        self.filters = {}

        LOGGER.debug('Finished initializing waveform dialog')

    # NOTE:  http://stackoverflow.com/questions/12366521/pyqt-checkbox-in-qtablewidget
    # NOTE:  http://stackoverflow.com/questions/30462078/using-a-checkbox-in-pyqt
    @QtCore.pyqtSlot(QTableWidgetItem)
    def handleTableItemClicked(self, item):
        """
        Triggered whenever an item in the waveforms table is clicked.
        """
        row = item.row()

        LOGGER.debug("Clicked on table row")

        # Toggle the Keep state
        waveformID = str(self.selectionTable.item(row, WAVEFORM_ID_COLUMN).text())
        waveform = self.waveformsHandler.get_waveform(waveformID)
        waveform.keep = not waveform.keep
        keepItem = self.selectionTable.item(row, WAVEFORM_KEEP_COLUMN)
        if waveform.keep:
            keepItem.setCheckState(QtCore.Qt.Checked)
        else:
            keepItem.setCheckState(QtCore.Qt.Unchecked)

    @QtCore.pyqtSlot()
    def loadWaveformChoices(self, filterColumn=None, filterText=None):
        """
        Fill the selectionTable with all SNCL-Event combinations selected in the MainWindow.
        This function is triggered whenever the "Get Waveforms" button in the MainWindow is clicked.
        """

        LOGGER.debug('Loading waveform choices...')

        self.resetDownload()

        self.downloadStatusLabel.setText("Calculating distances...")
        self.downloadStatusLabel.repaint()

        self.waveformsHandler.create_waveforms(self.pyweed)
        waveforms = self.waveformsHandler.waveforms

        self.downloadStatusLabel.setText("")
        self.downloadStatusLabel.repaint()

        LOGGER.debug('Finished building dataframe for %d waveforms', len(waveforms))

        # Add event-SNCL combinations to the selection table
        self.loadSelectionTable(initial=True)

        # Tighten up the table
        self.selectionTable.resizeColumnsToContents()
        self.selectionTable.horizontalHeader().setStretchLastSection(True)

        # Add events to the eventComboBox -------------------------------

        self.eventComboBox.clear()

        self.eventComboBox.addItem('All events')
        for event in self.pyweed.iter_selected_events():
            self.eventComboBox.addItem(get_event_name(event))

        # Add networks/stations to the networkComboBox and stationsComboBox ---------------------------

        self.networkComboBox.clear()
        self.networkComboBox.addItem('All networks')

        self.stationComboBox.clear()
        self.stationComboBox.addItem('All stations')

        found_networks = set()
        found_stations = set()
        for (network, station, _channel) in self.pyweed.iter_selected_stations():
            if network.code not in found_networks:
                found_networks.add(network.code)
                self.networkComboBox.addItem(network.code)
            netsta_code = '.'.join((network.code, station.code))
            if netsta_code not in found_stations:
                found_stations.add(netsta_code)
                self.stationComboBox.addItem(netsta_code)

        LOGGER.debug('Finished loading waveform choices')

    @QtCore.pyqtSlot()
    def loadSelectionTable(self, initial=False):
        """
        Add event-SNCL combinations to the selection table

        @param initial: True if this is the initial load (ie. not filtering existing data)
        """

        LOGGER.debug('Loading waveform selection table...')

        # Use WaveformTableItems to put the data into the table
        if not self.tableItems:
            self.tableItems = WaveformTableItems(
                self.selectionTable,
                self.filters
            )
        self.tableItems.fill(self.iterWaveforms(visible_only=True))

        # Start downloading the waveform data if this is an initial load
        if initial:
            self.downloadWaveformData()

        LOGGER.debug('Finished loading waveform selection table')

    @QtCore.pyqtSlot(int)
    def loadFilteredSelectionTable(self):
        """
        Filter waveformsDF based on filter selections and then reload the selectionTable.
        """
        LOGGER.debug('Filtering...')
        self.filters = {
            'event': self.eventComboBox.currentText(),
            'network': self.networkComboBox.currentText(),
            'station': self.stationComboBox.currentText(),
        }
        self.loadSelectionTable()
        LOGGER.debug('Finished filtering waveformsDF')

    def iterWaveforms(self, visible_only=False, saveable_only=False):
        """
        Iterate through the waveforms, optionally yielding only visible and/or saveable ones
        """
        for waveform in self.waveformsHandler.waveforms:
            if visible_only and not self.applyFilter(waveform):
                continue
            if saveable_only and not (waveform.keep and waveform.mseed_exists):
                continue
            yield waveform

    def applyFilter(self, waveform):
        """
        Apply self.filters to the given waveform
        @return True iff the waveform should be included
        """
        # Get the values from the waveform to match against the filter value
        sncl_parts = waveform.sncl.split('.')
        net_code = sncl_parts[0]
        netsta_code = '.'.join(sncl_parts[:2])
        filter_values = {
            'event': get_event_name(waveform.event_ref()),
            'network': net_code,
            'station': netsta_code
        }
        for (fname, fval) in self.filters.items():
            if not fval.startswith('All') and fval != filter_values[fname]:
                return False
        return True

    @QtCore.pyqtSlot()
    def onDownloadPushButton(self):
        """
        Triggered when downloadPushButton is clicked.
        """
        if self.waveformsDownloadStatus == STATUS_READY:
            # Start the download
            self.downloadWaveformData()

    def updateToolbars(self):
        """
        Update the UI elements to reflect the current status
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
            if self.waveformsDownloadStatus == STATUS_DONE:
                # Disabled if download has finished (and nothing has changed)
                self.downloadPushButton.setEnabled(False)
                self.downloadPushButton.setText('Download Complete')
            else:
                self.downloadPushButton.setEnabled(True)
                self.downloadPushButton.setText('Download')

        # Save controls
        if self.waveformsSaveStatus == STATUS_WORKING:
            # Currently saving
            self.saveGroupBox.setEnabled(False)
            self.savePushButton.setText('Saving...')
            self.savePushButton.setChecked(True)
            # May be waiting for download to finish
            if self.waveformsDownloadStatus != STATUS_DONE:
                self.saveStatusLabel.setText('Waiting for downloads')
            else:
                self.saveStatusLabel.setText('Saving...')
        else:
            # Available
            self.saveGroupBox.setEnabled(True)
            self.savePushButton.setText('Save')
            self.savePushButton.setChecked(False)
            # When the save is complete the status will be put in the label, don't change it
            # unless the process is reset (ie. we return to READY status)
            if self.waveformsSaveStatus == STATUS_READY:
                self.saveStatusLabel.setText('')

    @QtCore.pyqtSlot()
    def onSavePushButton(self):
        """
        Triggered after savePushButton is toggled.
        """
        if self.waveformsSaveStatus != STATUS_WORKING:
            self.waveformsSaveStatus = STATUS_WORKING
            if self.waveformsDownloadStatus == STATUS_DONE:
                # If any downloads are complete, we can trigger the save now
                self.saveWaveformData()
            else:
                # Otherwise, we have to wait -- update to indicate this to the user
                self.updateToolbars()

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

        self.waveformsDownloadStatus = STATUS_WORKING
        self.updateToolbars()

        # Priority is given to waveforms shown on the screen
        priority_ids = [waveform.waveform_id for waveform in self.waveformsHandler.waveforms]
        other_ids = []

        self.waveformsHandler.download_waveforms(
            priority_ids, other_ids, self.timeWindowAdapter.timeWindow)

    def get_table_row(self, waveform_id):
        """
        Get the table row for a given waveform
        """
        row = 0
        for row in range(self.selectionTable.rowCount()):
            if self.selectionTable.item(row, 0).text() == waveform_id:
                return row
        return None

    @QtCore.pyqtSlot(object)
    def onWaveformDownloaded(self, result):
        """
        Called each time a waveform request has completed
        """
        waveform_id = result.waveform_id
        LOGGER.debug("Ready to display waveform %s", waveform_id)

        row = self.get_table_row(waveform_id)
        if row is None:
            LOGGER.error("Couldn't find a row for waveform %s", waveform_id)
            return

        waveform = self.waveformsHandler.waveforms_by_id.get(waveform_id)
        if not waveform:
            LOGGER.error("Couldn't find waveform %s", waveform_id)
            return

        if isinstance(result.result, Exception):
            # Most common error is "no data" TODO: see https://github.com/obspy/obspy/issues/1656
            if result.result.message.startswith("No data"):
                waveform.error = "No data available"
            else:
                waveform.error = str(result.result)
        else:
            waveform.image_path = result.result
            waveform.check_files()
        self.selectionTable.setItem(row, WAVEFORM_IMAGE_COLUMN, self.tableItems.imageWidget(waveform))

        LOGGER.debug("Displayed waveform %s", waveform_id)

        # Tighten up the table
        self.selectionTable.resizeColumnsToContents()
        self.selectionTable.resizeRowsToContents()
        self.selectionTable.horizontalHeader().setStretchLastSection(True)

    @QtCore.pyqtSlot(object)
    def onAllDownloaded(self, result):
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

        errorCount = 0
        savedCount = 0
        skippedCount = 0

        try:
            waveforms = self.iterWaveforms(saveable_only=True)
            outputDir = self.waveformDirectory
            outputFormat = self.saveFormatAdapter.getValue()

            for result in self.waveformsHandler.save_waveforms_iter(outputDir, outputFormat, waveforms):
                if isinstance(result.result, Exception):
                    LOGGER.error("Failed to save waveform %s: %s", result.waveform_id, result.result)
                    errorCount += 1
                elif result.result:
                    savedCount += 1
                else:
                    skippedCount += 1
                self.saveStatusLabel.setText("%d saved, %d skipped, %d errors" % (savedCount, skippedCount, errorCount))
                self.saveStatusLabel.repaint()
                QtGui.QApplication.processEvents()  # update GUI

                # Return early if the user has toggled off the savePushButton (TODO: nonworking!)
                # time.sleep(1)  # Need a delay to test this
                if not self.savePushButton.isChecked():
                    raise Exception("Cancelled")

            message = "%d waveforms saved" % (savedCount + skippedCount)
            if skippedCount > 0:
                message = "%s (%d new)" % (message, savedCount)

            if errorCount > 0:
                raise Exception("%d errors! %s", errorCount, message)

            self.waveformsSaveStatus = STATUS_DONE
            self.saveStatusLabel.setText(message)
        except Exception as e:
            LOGGER.error(e)
            self.waveformsSaveStatus = STATUS_ERROR
            self.saveStatusLabel.setText(e.message)
        finally:
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

    def loadPreferences(self):
        """
        Load preferences relevant to this widget
        """
        prefs = self.pyweed.preferences

        self.waveformDirectory = prefs.Waveforms.saveDir

        self.timeWindowAdapter.setValues(
            safe_int(prefs.Waveforms.timeWindowBefore, 60),
            safe_int(prefs.Waveforms.timeWindowAfter, 600),
            prefs.Waveforms.timeWindowBeforePhase,
            prefs.Waveforms.timeWindowAfterPhase
        )

        self.saveFormatAdapter.setValue(prefs.Waveforms.saveFormat)

    def savePreferences(self):
        """
        Save preferences related to the controls on this widget
        """
        prefs = self.pyweed.preferences

        prefs.Waveforms.saveDir = self.waveformDirectory
        timeWindow = self.timeWindowAdapter.timeWindow
        prefs.Waveforms.timeWindowBefore = timeWindow.start_offset
        prefs.Waveforms.timeWindowAfter = timeWindow.end_offset
        prefs.Waveforms.timeWindowBeforePhase = timeWindow.start_phase
        prefs.Waveforms.timeWindowAfterPhase = timeWindow.end_phase

        prefs.Waveforms.saveFormat = self.saveFormatAdapter.getValue()
