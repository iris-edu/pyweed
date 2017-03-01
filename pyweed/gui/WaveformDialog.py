from PyQt4 import QtGui, QtCore
from gui.uic import WaveformDialog
import os
from waveforms_handler import WaveformsHandler
import obspy
from logging import getLogger
from gui.MyTableWidgetImageItem import MyTableWidgetImageItem
from gui.TableItems import TableItems
from obspy.io.sac.sactrace import SACTrace
from pyweed_utils import get_event_name, get_preferred_magnitude, get_preferred_origin

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
        self.saveFormatComboBox.addItems(['ASCII', 'GSE2', 'MSEED', 'SAC'])
        self.saveFormatComboBox.setCurrentIndex(2)

        LOGGER.debug('Initializing waveform dialog...')

        # Waveforms
        self.waveformsHandler = WaveformsHandler(LOGGER, self.preferences, self.client)
        self.waveformsHandler.progress.connect(self.on_waveform_downloaded)
        self.waveformsHandler.done.connect(self.on_all_downloaded)

        # Connect signals associated with the main table
        self.selectionTable.horizontalHeader().sortIndicatorChanged.connect(self.selectionTable.resizeRowsToContents)
        self.selectionTable.itemClicked.connect(self.handleTableItemClicked)

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

        # Dictionary of filter values
        self.filters = {}

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

        for i in range(self.eventComboBox.count()):
            self.eventComboBox.removeItem(0)

        self.eventComboBox.addItem('All events')
        for event in self.pyweed.iter_selected_events():
            self.eventComboBox.addItem(get_event_name(event))

        # Add networks/stations to the networkComboBox and stationsComboBox ---------------------------

        for i in range(self.networkComboBox.count()):
            self.networkComboBox.removeItem(0)
        self.networkComboBox.addItem('All networks')

        for i in range(self.stationComboBox.count()):
            self.stationComboBox.removeItem(0)
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

        # NOTE:  You must disable sorting before populating the table. Otherwise rows get
        # NOTE:  sorted as soon as the sortable column gets filled in, thus invalidating
        # NOTE:  the row number
        self.selectionTable.setSortingEnabled(False)

        # Use WaveformTableItems to put the data into the table
        if not self.tableItems:
            self.tableItems = WaveformTableItems(
                self.selectionTable,
                self.filters
            )
        self.tableItems.fill(self.iterWaveforms(visible_only=True))

        # Restore table sorting
        self.selectionTable.setSortingEnabled(True)

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
            if self.waveformsSaveStatus == STATUS_READY:
                self.saveStatusLabel.setText('')
            elif self.waveformsSaveStatus == STATUS_DONE:
                self.saveStatusLabel.setText('Data saved')

    def onSavePushButton(self):
        """
        Triggered after savePushButton is toggled.
        """
        if self.waveformsSaveStatus != STATUS_WORKING:
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

        self.waveformsDownloadStatus = STATUS_WORKING
        self.updateToolbars()

        secondsBefore = self.secondsBeforeSpinBox.value()
        secondsAfter = self.secondsAfterSpinBox.value()

        # Priority is given to waveforms shown on the screen
        priority_ids = [waveform.waveform_id for waveform in self.waveformsHandler.waveforms]
        other_ids = []

        self.waveformsHandler.download_waveforms(
            priority_ids, other_ids,
            secondsBefore, secondsAfter)

    def on_log(self, msg):
        LOGGER.error("Uh oh, called WaveformDialog.on_log: %s", msg)

    def get_table_row(self, waveform_id):
        """
        Get the table row for a given waveform
        """
        row = 0
        for row in range(self.selectionTable.rowCount()):
            if self.selectionTable.item(row, 0).text() == waveform_id:
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

            if not os.path.exists(outputDir):
                try:
                    os.makedirs(outputDir, 0700)
                except Exception as e:
                    raise Exception("Could not create the output path: %s" % str(e))

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

            savedCount = 0
            for waveform in self.iterWaveforms(saveable_only=True):
                try:
                    outputFile = os.path.extsep.join((waveform.base_filename, extension))
                    outputPath = os.path.join(outputDir, outputFile)
                    # Don't repeat any work that has already been done
                    if not os.path.exists(outputPath):
                        LOGGER.debug('reading %s', waveform.mseed_path)
                        st = obspy.read(waveform.mseed_path)
                        self.saveOneWaveform(st, outputPath, outputFormat, waveform)
                except Exception as e:
                    LOGGER.error("Failed to save waveform %s: %s", waveform.waveform_id, e)
                savedCount += 1
                self.saveStatusLabel.setText("Saved %d waveforms as %s" % (savedCount, formatChoice))
                self.saveStatusLabel.repaint()
                QtGui.QApplication.processEvents() # update GUI

                # Return early if the user has toggled off the savePushButton (TODO: nonworking!)
                # time.sleep(1)  # Need a delay to test this
                if not self.savePushButton.isChecked():
                    raise Exception("Cancelled")

            self.waveformsSaveStatus = STATUS_DONE
        except Exception as e:
            LOGGER.error(e)
            self.waveformsSaveStatus = STATUS_ERROR
            self.saveStatusLabel.setText(e.message)
        finally:
            self.updateToolbars()

        LOGGER.debug('COMPLETED saving all waveforms')

    def saveOneWaveform(self, st, outputPath, outputFormat, waveform):
        """
        Save a single waveform. This should handle any special output features (eg. SAC metadata)
        """
        LOGGER.debug('writing %s', outputPath)
        if outputFormat == 'SAC':
            # For SAC output, we need to pull header data from the waveform record
            st = self.getSACTrace(st, waveform)
        st.write(outputPath, format=outputFormat)

    def getSACTrace(self, st, waveform):
        """
        Return a SACTrace based on the given stream, containing metadata headers from the waveform
        """
        st = SACTrace.from_obspy_trace(st[0])
        st.kevnm = waveform.event_name[:16]
        event = waveform.event_ref()
        if not event:
            LOGGER.warn("Lost reference to event %s", waveform.event_name)
        else:
            origin = get_preferred_origin(waveform.event_ref())
            if origin:
                st.evla = origin.latitude
                st.evlo = origin.longitude
                st.evdp = origin.depth / 1000
                st.o = origin.time - waveform.start_time
            magnitude = get_preferred_magnitude(waveform.event_ref())
            if magnitude:
                st.mag = magnitude.mag
        channel = waveform.channel_ref()
        if not channel:
            LOGGER.warn("Lost reference to channel %s", waveform.sncl)
        else:
            st.stla = channel.latitude
            st.stlo = channel.longitude
            st.stdp = channel.depth
            st.stel = channel.elevation
            st.cmpaz = channel.azimuth
            st.cmpinc = channel.dip + 90
            st.kinst = channel.sensor.description[:8]
        return st

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
