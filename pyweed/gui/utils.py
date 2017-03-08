from PyQt4 import QtGui, QtCore
from distutils.util import strtobool
from logging import getLogger

LOGGER = getLogger(__name__)


class OptionsAdapter(object):
    """
    An adapter object that pairs an Options object with a set of Qt Widget fields
    """
    def __init__(self):
        # Map of option names to Qt inputs
        self.inputs = {}

    def connect_to_widget(self, widget):
        """
        This should be called on initialization, passing in the widget to work on.
        Subclasses should implement this to set up self.inputs
        """
        raise NotImplementedError()

    def options_to_inputs(self, options):
        """
        Transform the given Options object into a set of string-string mappings
        Subclasses should override this to implement any special handling.
        """
        # By default, include everything that's defined in both places
        keys = set(options.keys()) | set(self.inputs.keys())
        return options.get_options(keys=list(keys), stringify=True)

    def write_to_widget(self, options):
        """
        Put the current set of options into the mapped inputs
        """
        inputs = self.options_to_inputs(options)
        for k, v in inputs.iteritems():
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

    def inputs_to_options(self, inputs):
        """
        Transform a set of input values into input for Options.set_options.
        Subclasses should override this to implement any special handling.
        """
        return inputs

    def read_from_widget(self):
        """
        Set the options from the mapped inputs
        """
        inputs = {}
        for k, input in self.inputs.iteritems():
            if isinstance(input, QtGui.QDateTimeEdit):
                # DateTime
                inputs[k] = input.dateTime().toString(QtCore.Qt.ISODate)
            elif isinstance(input, QtGui.QAbstractButton):
                # Radio/checkbox button
                inputs[k] = str(input.isChecked())
            elif isinstance(input, QtGui.QComboBox):
                inputs[k] = input.currentText()
            elif hasattr(input, 'text'):
                inputs[k] = input.text()
            else:
                LOGGER.warning("Don't know how to write input %s (%s)", k, input)
        return self.inputs_to_options(inputs)
