from PyQt4 import QtGui, QtCore
from distutils.util import strtobool
from logging import getLogger

LOGGER = getLogger(__name__)


class Options(object):
    """
    An object representing a set of options, for example EventOptions manages the options for requesting events
    """
    def __init__(self, initial=None):
        """
        @param inputs: a dict mapping option fields to Qt Widgets
        @param initial: a dict of initial values
        """
        # Option values
        self.options = dict(initial or {})
        # Map of option names to Qt inputs
        self.inputs = {}

    def connect_to_widget(self, widget):
        raise NotImplementedError()

    def write_to_widget(self):
        """
        Put the current set of options into the mapped inputs
        """
        for k, v in self.options.iteritems():
            input = self.inputs.get(k)
            if input:
                if isinstance(input, QtGui.QDateTimeEdit):
                    # Ugh, complicated conversion from UTCDateTime
                    dt = QtCore.QDateTime.fromString(v, QtCore.Qt.ISODate)
                    input.setDateTime(dt)
                elif isinstance(input, QtGui.QDoubleSpinBox):
                    # Float value
                    input.setValue(float(v))
                elif isinstance(input, QtGui.QComboBox):
                    # Combo box
                    index = input.findText(v)
                    if index > -1:
                        input.setCurrentIndex(index)
                elif isinstance(input, QtGui.QLineEdit):
                    # Text input
                    input.setText(v)
                elif isinstance(input, QtGui.QAbstractButton):
                    # Radio/checkbox button
                    input.setChecked(strtobool(v))
                else:
                    LOGGER.warning("Don't know how to set an input for %s (%s)", k, input)
            else:
                LOGGER.warning("No input for option %s", k)

    def read_from_widget(self):
        """
        Set the options from the mapped inputs
        """
        for k, input in self.inputs.iteritems():
            if isinstance(input, QtGui.QDateTimeEdit):
                # DateTime
                self.options[k] = input.dateTime().toString(QtCore.Qt.ISODate)
            elif isinstance(input, QtGui.QAbstractButton):
                # Radio/checkbox button
                self.options[k] = str(input.isChecked())
            elif hasattr(input, 'text'):
                self.options[k] = input.text()
            else:
                LOGGER.warning("Don't know how to write input %s (%s)", k, input)


