# -*- coding: utf-8 -*-
"""
Base classes for EventOptionsWidet and StationOptionsWidget

:copyright:
    Mazama Science, IRIS
:license:
    GNU Lesser General Public License, Version 3
    (http://www.gnu.org/copyleft/lesser.html)
"""

from PyQt5 import QtWidgets, QtCore
import logging
from distutils.util import strtobool

LOGGER = logging.getLogger(__name__)


class BaseOptionsWidget(QtWidgets.QDialog):
    """
    Base functionality for the EventOptionsWidget and StationOptionsWidget.
    """

    # We want to watch for changes in the widget inputs, but every type of input has a different one so
    # we need to try a bunch of options
    INPUT_CHANGE_SIGNALS = (
        'valueChanged',
        'textChanged',
        'dateTimeChanged',
        'clicked',
        'location_choice',
        'time_choice',
    )

    # Signal to indicate that the options have changed
    changed = QtCore.pyqtSignal(object)
    # Signal indicating that the user changed a location parameter
    changedCoords = QtCore.pyqtSignal(object)
    # Map of the individual inputs by name
    inputs = None

    def __init__(self, parent, options, otherOptions, dockWidget, toggleButton):
        super(BaseOptionsWidget, self).__init__(parent=parent)
        # This function just saves variables and do some low-level widget operations
        # then calls `initialize()` for the higher-level behavior.
        self.setupUi(self)
        self.inputs = self.mapInputs()
        self.options = options
        self.otherOptions = otherOptions

        # Add to dock
        dockWidget.setWidget(self)
        # Connect the toggle switch for hiding the dock
        toggleButton.toggled.connect(dockWidget.setVisible)
        dockWidget.visibilityChanged.connect(toggleButton.setChecked)

        # Call a separate function for the higher-level behavior, so subclasses can extend
        self.initialize()

    def initialize(self):
        """
        Second part of the initialization, subclass initialization should extend this.
        """
        # Push values to the inputs before connecting them
        self.setOptions()
        self.connectInputs()

        # Hook up the shortcut buttons
        self.time30DaysPushButton.clicked.connect(self.setTime30Days)
        self.time1YearPushButton.clicked.connect(self.setTime1Year)

        # Hook up the copy buttons
        self.get_timeFromOtherButton().clicked.connect(self.copyTimeOptions)
        self.get_locationFromOtherButton().clicked.connect(self.copyLocationOptions)

    def mapInputs(self):
        """
        Subclasses override this to provide a map of keys to input widgets

        ex:
        return {
            'network': self.networkLineEdit,
            'station': self.stationLineEdit,
            'location': self.locationLineEdit,
            'channel': self.channelLineEdit,
            ...
        }
        """
        raise NotImplementedError()

    def get_timeFromOtherButton(self):
        """ Return the button that triggers copying time from the other widget """
        raise NotImplementedError()

    def get_locationFromOtherButton(self):
        """ Return the button that triggers copying location from the other widget """
        raise NotImplementedError()

    def connectInput(self, key, one_input):
        # Different widgets emit different signals  :P
        for signal_name in self.INPUT_CHANGE_SIGNALS:
            if hasattr(one_input, signal_name):
                LOGGER.debug("Listening to %s.%s" % (one_input, signal_name))
                getattr(one_input, signal_name).connect(lambda: self.onInputChanged(key))
                return

    def connectInputs(self):
        """
        Set up listeners for the inputs
        """
        for key, one_input in self.inputs.items():
            self.connectInput(key, one_input)

    def onInputChanged(self, key):
        """
        Called when any input is changed
        """
        LOGGER.debug("Input changed: %s" % key)
        # Update the core options object
        self.options.set_options(self.getOptions())
        # Emit a change event
        self.changed.emit(key)
        # Emit a coordinate change event if appropriate
        if self.isCoordinateInput(key):
            self.changedCoords.emit(key)

    def isCoordinateInput(self, key):
        """
        Return true if the given key represents a coordinate input.
        Subclasses may override/extend this.
        """
        for marker in ('latitude', 'longitude', 'radius', '_location', 'distance',):
            if marker in key:
                return True
        return False

    def getInputValue(self, key):
        """
        Get the value of a single input. This is intended to Pythonify the Qt values that come natively
        from the widgets. (ie. return a Python date rather than a QDate).

        This is used internally by getOptions()
        """
        one_input = self.inputs.get(key)
        if one_input:
            if isinstance(one_input, QtWidgets.QDateTimeEdit):
                # DateTime
                return one_input.dateTime().toString(QtCore.Qt.ISODate)
            elif isinstance(one_input, QtWidgets.QAbstractButton):
                # Radio/checkbox button
                return str(one_input.isChecked())
            elif isinstance(one_input, QtWidgets.QComboBox):
                return one_input.currentText()
            elif hasattr(one_input, 'text'):
                return one_input.text()
            raise Exception("Couldn't identify the QWidget type for %s (%s)" % (key, one_input))
        return None

    def setInputValue(self, key, value):
        """
        Set the input value based on a string from the options
        """
        one_input = self.inputs.get(key)
        if one_input:
            if isinstance(one_input, QtWidgets.QDateTimeEdit):
                # Ugh, complicated conversion from UTCDateTime
                dt = QtCore.QDateTime.fromString(value, QtCore.Qt.ISODate)
                one_input.setDateTime(dt)
            elif isinstance(one_input, QtWidgets.QDoubleSpinBox):
                # Float value
                one_input.setValue(float(value))
            elif isinstance(one_input, QtWidgets.QComboBox):
                # Combo box
                index = one_input.findText(value)
                if index > -1:
                    one_input.setCurrentIndex(index)
            elif isinstance(one_input, QtWidgets.QLineEdit):
                # Text input
                one_input.setText(value)
            elif isinstance(one_input, QtWidgets.QAbstractButton):
                # Radio/checkbox button
                one_input.setChecked(strtobool(str(value)))
            else:
                raise Exception("Don't know how to set an input for %s (%s)" % (key, one_input))

    def setOptions(self):
        """
        Put the current set of options into the mapped inputs
        """
        # Get a dictionary of stringified options values
        for key, value in self.optionsToInputs(self.options.get_options(stringify=True)).items():
            try:
                self.setInputValue(key, value)
            except Exception as e:
                LOGGER.warning("Unable to set input value for %s: %s", key, e)

    def optionsToInputs(self, values):
        """
        Hook for subclasses to modify a dictionary of options to map to the input widgets
        """
        return values

    def getOptions(self):
        """
        Return a dictionary containing the input values, formatted as appropriate for a service call.
        """
        inputValues = {}
        for key in self.inputs.keys():
            try:
                inputValues[key] = self.getInputValue(key)
            except Exception as e:
                LOGGER.warning("Unable to get input value %s: %s", key, e)
        return self.inputsToOptions(inputValues)

    def inputsToOptions(self, values):
        """
        Hook for subclasses to modify a dictionary of input values to map to the options
        """
        return values

    def copyTimeOptions(self):
        """
        Copy the time options from event_options/station_options
        """
        LOGGER.info("Copying time")
        time_options = self.otherOptions.get_time_options()
        time_options.update(self.otherOptions.get_options(['time_choice']))
        self.options.set_options(time_options)
        self.setOptions()
        self.changed.emit('time_choice')

    def copyLocationOptions(self):
        """
        Copy the location options from event_options/station_options
        """
        LOGGER.info("Copying location")
        loc_options = self.otherOptions.get_location_options()
        loc_options.update(self.otherOptions.get_options(['location_choice']))
        self.options.set_options(loc_options)
        self.setOptions()
        self.changed.emit('location_choice')
        self.changedCoords.emit('location_choice')

    def setTime30Days(self):
        """
        Set the start/end times to cover the last 30 days
        """
        end = QtCore.QDateTime.currentDateTimeUtc()
        start = end.addDays(-30)
        self.starttimeDateTimeEdit.setDateTime(start)
        self.endtimeDateTimeEdit.setDateTime(end)
        self.changed.emit('time_choice')

    def setTime1Year(self):
        """
        Set the start/end times to cover the last 30 days
        """
        end = QtCore.QDateTime.currentDateTimeUtc()
        start = end.addYears(-1)
        self.starttimeDateTimeEdit.setDateTime(start)
        self.endtimeDateTimeEdit.setDateTime(end)
        self.changed.emit('time_choice')


