# -*- coding: utf-8 -*-
"""
Dialog for selecting and downloading waveform data

:copyright:
    Mazama Science, IRIS
:license:
    GNU Lesser General Public License, Version 3
    (http://www.gnu.org/copyleft/lesser.html)
"""

from PyQt5 import QtWidgets, QtGui, QtCore
from pyweed.gui.uic import WaveformDialog
from pyweed.waveforms_handler import WaveformsHandler
from logging import getLogger
from pyweed.gui.TableItems import TableItems, Column
from pyweed.pyweed_utils import get_event_name, TimeWindow, OUTPUT_FORMATS, PHASES
from pyweed.preferences import safe_int
from pyweed.gui.Adapters import ComboBoxAdapter
from pyweed.gui.BaseDialog import BaseDialog
from pyweed.gui.SpinnerWidget import SpinnerWidget
from pyweed.gui.TableWidget import CustomTableWidgetItemMixin

LOGGER = getLogger(__name__)


# Download/save status values
STATUS_READY = "ready"  # Waiting for user to initiate
STATUS_WORKING = "working"  # Working
STATUS_DONE = "done"  # Finished
STATUS_ERROR = "error"  # Something went wrong


class KeepIndicatorTableWidgetItem(CustomTableWidgetItemMixin, QtWidgets.QTableWidgetItem):
    """
    Custom QTableWidgetItem that indicates whether the row is included in the request

    Note that this uses Unicode characters for the checkboxes, this appears to be the easiest way to
    control the size, and we don't need an actual toggle widget here since that is done at the row level.
    """
    checkedText = '☑'
    checkedIcon = QtGui.QPixmap(':qrc/check-on.png')
    uncheckedText = '☐'
    uncheckedIcon = QtGui.QPixmap(':qrc/check-off.png')
    fontSize = 36
    checkedBackground = QtGui.QBrush(QtGui.QColor(220, 239, 223))
    uncheckedBackground = QtGui.QBrush(QtCore.Qt.NoBrush)

    def __init__(self, value):
        super(KeepIndicatorTableWidgetItem, self).__init__()
        self.setKeep(value)
        # Use a large font size for the checkboxes
        font = QtGui.QFont()
        font.setPointSize(self.fontSize)
        self.setFont(font)

    def keep(self):
        return self.data(QtCore.Qt.UserRole)

    def setKeep(self, value):
        self.setData(QtCore.Qt.UserRole, value)
        # Update as needed to indicate the value to the user
        if value:
            self.setBackground(self.checkedBackground)
            self.setData(QtCore.Qt.DecorationRole, self.checkedIcon)
        else:
            self.setBackground(self.uncheckedBackground)
            self.setData(QtCore.Qt.DecorationRole, self.uncheckedIcon)


class WaveformTableWidgetItem(CustomTableWidgetItemMixin, QtWidgets.QTableWidgetItem):
    """
    Custom QTableWidgetItem that shows a waveform image (or a status message)
    """
    imagePath = None
    errorForeground = QtGui.QBrush(QtGui.QColor(255, 0, 0))
    defaultForeground = None

    def __init__(self, waveform):
        super(WaveformTableWidgetItem, self).__init__()
        self.defaultForeground = self.foreground()
        self.setWaveform(waveform)

    def setWaveform(self, waveform):
        if waveform and waveform.error:
            self.setForeground(self.errorForeground)
        else:
            self.setForeground(self.defaultForeground)
        if waveform:
            if waveform.loading or waveform.error or not waveform.image_exists:
                self.imagePath = None
                self.setData(QtCore.Qt.DecorationRole, None)
                if waveform.loading:
                    self.setText('Loading waveform data...')
                elif waveform.error:
                    self.setText(waveform.error)
                else:
                    self.setText('')
            else:
                if waveform.image_path != self.imagePath:
                    self.imagePath = waveform.image_path
                    pic = QtGui.QPixmap(waveform.image_path)
                    self.setData(QtCore.Qt.DecorationRole, pic)
                    self.setText('')
        else:
            self.imagePath = None
            self.setText('')


class WaveformTableItems(TableItems):

    #: Fixed row height based on the height of the waveform image
    rowHeight = 110

    columns = [
        Column('Id'),
        Column('Keep'),
        Column('Event Time', width=100),
        Column('Location', width=100),
        Column('Magnitude'),
        Column('SNCL'),
        Column('Distance'),
        Column('Waveform', width=600),
    ]

    def keepWidget(self, keep, **props):
        return self.applyProps(KeepIndicatorTableWidgetItem(keep), **props)

    def waveformWidget(self, waveform, **props):
        return self.applyProps(WaveformTableWidgetItem(waveform), **props)

    def rows(self, data):
        """
        Turn the data into rows (an iterable of lists) of QTableWidgetItems
        """
        for waveform in data:
            # Make the time and location wrap
            yield [
                self.stringWidget(waveform.waveform_id),
                self.keepWidget(waveform.keep,
                                textAlignment=QtCore.Qt.AlignCenter),
                self.stringWidget(waveform.event_time_str),
                self.stringWidget(waveform.event_description),
                self.numericWidget(waveform.event_mag_value, waveform.event_mag,
                                   textAlignment=QtCore.Qt.AlignCenter),
                self.stringWidget(waveform.sncl,
                                  textAlignment=QtCore.Qt.AlignCenter),
                self.numericWidget(waveform.distance, '%.02f°',
                                   textAlignment=QtCore.Qt.AlignCenter),
                self.waveformWidget(waveform),
            ]


# Convenience values for some commonly used table column values
_COLUMN_NAMES = [c.label for c in WaveformTableItems.columns]
WAVEFORM_ID_COLUMN = _COLUMN_NAMES.index('Id')
WAVEFORM_KEEP_COLUMN = _COLUMN_NAMES.index('Keep')
WAVEFORM_IMAGE_COLUMN = _COLUMN_NAMES.index('Waveform')


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


class WaveformDialog(BaseDialog, WaveformDialog.Ui_WaveformDialog):

    tableItems = None

    """
    Dialog window for selection and display of waveforms.
    """
    def __init__(self, pyweed, parent=None):
        super(WaveformDialog, self).__init__(parent=parent)

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
        self.waveforms_handler = WaveformsHandler(LOGGER, pyweed.preferences, pyweed.station_client)
        # The callbacks here are expensive, so use QueuedConnection to run them asynchronously
        self.waveforms_handler.progress.connect(self.onWaveformDownloaded, QtCore.Qt.QueuedConnection)
        self.waveforms_handler.done.connect(self.onAllDownloaded, QtCore.Qt.QueuedConnection)

        # Spinner overlays for downloading and saving
        self.downloadSpinner = SpinnerWidget("Downloading...", parent=self.downloadGroupBox)
        self.downloadSpinner.cancelled.connect(self.onDownloadCancel)
        self.saveSpinner = SpinnerWidget("Saving...", cancellable=False, parent=self.saveGroupBox)

        # Connect signals associated with the main table
        # self.selectionTable.horizontalHeader().sortIndicatorChanged.connect(self.selectionTable.resizeRowsToContents)
        self.selectionTable.itemClicked.connect(self.handleTableItemClicked)

        # Connect the Download and Save GUI elements
        self.downloadPushButton.clicked.connect(self.onDownloadPushButton)
        self.savePushButton.clicked.connect(self.onSavePushButton)
        self.saveDirectoryPushButton.clicked.connect(self.getWaveformDirectory)
        self.saveDirectoryBrowseToolButton.clicked.connect(self.browseWaveformDirectory)

        self.saveFormatAdapter.changed.connect(self.resetSave)

        # Connect signals associated with comboBoxes
        # NOTE:  http://www.tutorialspoint.com/pyqt/pyqt_qcombobox_widget.htm
        # NOTE:  currentIndexChanged() responds to both user and programmatic changes.
        #        Use activated() for user initiated changes
        self.eventComboBox.activated.connect(self.onFilterChanged)
        self.networkComboBox.activated.connect(self.onFilterChanged)
        self.stationComboBox.activated.connect(self.onFilterChanged)

        # Connect the timewindow signals
        self.timeWindowAdapter.changed.connect(self.resetDownload)

        # Dictionary of filter values
        self.filters = {}

        # Information about download progress
        self.downloadCount = 0
        self.downloadCompleted = 0

        LOGGER.debug('Finished initializing waveform dialog')

    # NOTE:  http://stackoverflow.com/questions/12366521/pyqt-checkbox-in-qtablewidget
    # NOTE:  http://stackoverflow.com/questions/30462078/using-a-checkbox-in-pyqt
    @QtCore.pyqtSlot(QtWidgets.QTableWidgetItem)
    def handleTableItemClicked(self, item):
        """
        Triggered whenever an item in the waveforms table is clicked.
        """
        row = item.row()

        LOGGER.debug("Clicked on table row")

        # Toggle the Keep state
        waveformID = str(self.selectionTable.item(row, WAVEFORM_ID_COLUMN).text())
        waveform = self.waveforms_handler.get_waveform(waveformID)
        waveform.keep = not waveform.keep
        keepItem = self.selectionTable.item(row, WAVEFORM_KEEP_COLUMN)
        keepItem.setKeep(waveform.keep)

    @QtCore.pyqtSlot()
    def loadWaveformChoices(self):
        """
        Fill the selectionTable with all SNCL-Event combinations selected in the MainWindow.
        This function is triggered whenever the "Get Waveforms" button in the MainWindow is clicked.
        """

        LOGGER.debug('Loading waveform choices...')

        self.resetDownload()

        self.waveforms_handler.create_waveforms(self.pyweed)

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

        foundNetworks = set()
        foundStations = set()
        for (network, station, _channel) in self.pyweed.iter_selected_stations():
            if network.code not in foundNetworks:
                foundNetworks.add(network.code)
                self.networkComboBox.addItem(network.code)
            netstaCode = '.'.join((network.code, station.code))
            if netstaCode not in foundStations:
                foundStations.add(netstaCode)
                self.stationComboBox.addItem(netstaCode)

        self.loadSelectionTable()

        # Start downloading data
        self.downloadWaveformData()

        LOGGER.debug('Finished loading waveform choices')

    @QtCore.pyqtSlot()
    def loadSelectionTable(self):
        """
        Add event-SNCL combinations to the selection table
        """

        LOGGER.debug('Loading waveform selection table...')

        # Use WaveformTableItems to put the data into the table
        if not self.tableItems:
            self.tableItems = WaveformTableItems(
                self.selectionTable
            )
        self.tableItems.fill(self.iterWaveforms())

        self.filterSelectionTable()

        LOGGER.debug('Finished loading waveform selection table')

    @QtCore.pyqtSlot(int)
    def onFilterChanged(self):
        self.filters = {}
        self.filterSelectionTable()

    def filterSelectionTable(self):
        """
        Filter the selection table based on the currently defined filters
        """
        if self.tableItems:

            if not self.filters:
                self.filters = {
                    'event': self.eventComboBox.currentText(),
                    'network': self.networkComboBox.currentText(),
                    'station': self.stationComboBox.currentText(),
                }

            filterResults = dict(
                (waveform.waveform_id, self.applyFilter(waveform))
                for waveform in self.iterWaveforms()
            )

            def filterFn(row):
                waveformID = str(self.selectionTable.item(row, WAVEFORM_ID_COLUMN).text())
                return filterResults.get(waveformID)

            self.tableItems.filter(filterFn)

    def iterWaveforms(self, saveable_only=False):
        """
        Iterate through the waveforms, optionally yielding only the saveable ones
        """
        for waveform in self.waveforms_handler.waveforms:
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

    @QtCore.pyqtSlot()
    def onDownloadCancel(self):
        if self.waveformsDownloadStatus == STATUS_WORKING:
            # Cancel running download
            self.waveforms_handler.cancel_download()

    def updateToolbars(self):
        """
        Update the UI elements to reflect the current status
        """
        self.downloadPushButton.setEnabled(self.waveformsDownloadStatus == STATUS_READY)

    @QtCore.pyqtSlot()
    def onSavePushButton(self):
        """
        Triggered after savePushButton is toggled.
        """
        if self.waveformsSaveStatus != STATUS_WORKING:
            self.waveformsSaveStatus = STATUS_WORKING
            self.saveSpinner.show()
            if self.waveformsDownloadStatus == STATUS_DONE:
                # If any downloads are complete, we can trigger the save now
                self.saveWaveformData()
            else:
                # Otherwise we have to wait until the download is done, indicate this to the user
                self.saveSpinner.setLabel("Waiting for downloads to finish")
                # If not already downloading, try to start
                if self.waveformsDownloadStatus != STATUS_WORKING:
                    self.downloadWaveformData()

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
        self.downloadCount = len(self.waveforms_handler.waveforms)
        self.downloadCompleted = 0
        self.downloadSpinner.show()
        self.updateToolbars()

        # Priority is given to waveforms shown on the screen
        priority_ids = [waveform.waveform_id for waveform in self.waveforms_handler.waveforms]
        other_ids = []

        self.waveforms_handler.download_waveforms(
            priority_ids, other_ids, self.timeWindowAdapter.timeWindow)

        # Update the table rows
        for row in range(self.selectionTable.rowCount()):
            waveform_id = self.selectionTable.item(row, WAVEFORM_ID_COLUMN).text()
            waveform = self.waveforms_handler.waveforms_by_id.get(waveform_id)
            self.selectionTable.item(row, WAVEFORM_IMAGE_COLUMN).setWaveform(waveform)

    def getTableRow(self, waveform_id):
        """
        Get the table row for a given waveform
        """
        for row in range(self.selectionTable.rowCount()):
            if self.selectionTable.item(row, WAVEFORM_ID_COLUMN).text() == waveform_id:
                return row
        return None

    @QtCore.pyqtSlot(object)
    def onWaveformDownloaded(self, result):
        """
        Called each time a waveform request has completed
        """
        waveform_id = result.waveform_id
        LOGGER.debug("Ready to display waveform %s (%s)", waveform_id, QtCore.QThread.currentThreadId())

        self.downloadCompleted += 1
        msg = "Downloaded %d of %d" % (self.downloadCompleted, self.downloadCount)
        # self.downloadStatusLabel.setText(msg)
        self.downloadSpinner.setLabel(msg)

        row = self.getTableRow(waveform_id)
        if row is None:
            LOGGER.error("Couldn't find a row for waveform %s", waveform_id)
            return

        waveform = self.waveforms_handler.waveforms_by_id.get(waveform_id)
        self.selectionTable.item(row, WAVEFORM_IMAGE_COLUMN).setWaveform(waveform)
        self.selectionTable.item(row, WAVEFORM_KEEP_COLUMN).setKeep(waveform.keep)

        LOGGER.debug("Displayed waveform %s", waveform_id)

    @QtCore.pyqtSlot(object)
    def onAllDownloaded(self, result):
        """
        Called after all waveforms have been downloaded
        """
        LOGGER.debug('COMPLETED all downloads')

        if self.waveformsDownloadStatus == STATUS_WORKING:
            self.downloadSpinner.hide()

            # If normal result, mark as done. If an error, mark as ready (ie. user can download again)
            if isinstance(result, Exception):
                self.waveformsDownloadStatus = STATUS_READY
            else:
                self.waveformsDownloadStatus = STATUS_DONE
                self.downloadStatusLabel.setText("Downloaded %d waveforms" % len(self.waveforms_handler.waveforms))

                # Initiate save if that was queued
                if self.waveformsSaveStatus == STATUS_WORKING:
                    self.saveWaveformData()

            self.updateToolbars()

    @QtCore.pyqtSlot()
    def saveWaveformData(self):
        """
        Save waveforms after all downloads are complete.
        """

        # Update status
        self.waveformsSaveStatus = STATUS_WORKING
        self.updateToolbars()

        # Update GUI in case we came from an internal call
        QtWidgets.QApplication.processEvents()

        errors = []
        savedCount = 0
        skippedCount = 0

        try:
            waveforms = self.iterWaveforms(saveable_only=True)
            outputDir = self.waveformDirectory
            outputFormat = self.saveFormatAdapter.getValue()

            for result in self.waveforms_handler.save_waveforms_iter(outputDir, outputFormat, waveforms):
                if isinstance(result.result, Exception):
                    LOGGER.error("Failed to save waveform %s: %s", result.waveform_id, result.result)
                    errors.append("%s: %s" % (result.waveform_id, result.result))
                elif result.result:
                    savedCount += 1
                    self.saveSpinner.setLabel("Saved %d waveforms" % savedCount)
                    QtWidgets.QApplication.processEvents()  # update GUI
                else:
                    skippedCount += 1
            self.saveStatusLabel.setText("Saved %d waveforms" % savedCount)
            self.saveStatusLabel.repaint()

            LOGGER.info("Save complete: %d saved, %d already existed, %d errors", savedCount, skippedCount, len(errors))

            if errors:
                # Truncate the list of errors if it's very long
                errorCount = len(errors)
                if errorCount > 20:
                    errors = errors[:20]
                    errors.append("(see log for full list)")
                raise Exception("%d waveforms couldn't be saved:\n%s" % (errorCount, "\n".join(errors)))

            self.waveformsSaveStatus = STATUS_DONE
        except Exception as e:
            LOGGER.error(e)
            self.waveformsSaveStatus = STATUS_ERROR
            QtWidgets.QMessageBox.critical(
                self,
                "Error",
                str(e)
            )
        finally:
            self.updateToolbars()

        self.saveSpinner.hide()
        LOGGER.debug('COMPLETED saving all waveforms')

    @QtCore.pyqtSlot()
    def getWaveformDirectory(self):
        """
        This function is triggered whenever the user presses the "to <directory>" button.
        """
        # If the user quits or cancels this dialog, '' is returned
        newDirectory = str(QtWidgets.QFileDialog.getExistingDirectory(
            self,
            "Waveform Directory",
            self.waveformDirectory,
            QtWidgets.QFileDialog.ShowDirsOnly))

        if newDirectory != '':
            self.waveformDirectory = newDirectory
            self.saveDirectoryPushButton.setText(self.waveformDirectory)
            self.resetSave()

    @QtCore.pyqtSlot()
    def browseWaveformDirectory(self):
        """
        This function is triggered whenever the user presses the "browse" button.
        """
        url = QtCore.QUrl.fromLocalFile(self.waveformDirectory)
        QtGui.QDesktopServices.openUrl(url)

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
