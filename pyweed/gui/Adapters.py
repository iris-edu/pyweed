# -*- coding: utf-8 -*-
"""
Various Qt widget utilities

:copyright:
    Mazama Science, IRIS
:license:
    GNU Lesser General Public License, Version 3
    (http://www.gnu.org/copyleft/lesser.html)
"""

from PyQt5 import QtGui, QtCore
from logging import getLogger
from PyQt5.QtCore import pyqtSlot

LOGGER = getLogger(__name__)


class ComboBoxAdapter(QtCore.QObject):
    """
    Adapter for handling the fact that QComboBox can only display strings, but usually the "real" value
    is something else.
    """

    #: Signal emitted when the QComboBox value changes, passing the actual value
    changed = QtCore.pyqtSignal(object)

    def __init__(self, comboBox, options, default=None):
        """
        :param comboBox: A QComboBox
        :param options: A list of options in the form of (value, label)
        :param default: If nothing is selected, what should be returned?
        """
        super(ComboBoxAdapter, self).__init__()
        self.comboBox = comboBox
        self.values = [option[0] for option in options]
        if default is None:
            default = self.values[0]
        self.default = default
        labels = [option[1] for option in options]
        self.comboBox.addItems(labels)
        self.comboBox.currentIndexChanged.connect(self.onChanged)

    def setValue(self, value):
        self.comboBox.setCurrentIndex(self.values.index(value))

    def getValue(self, index=None):
        if index is None:
            index = self.comboBox.currentIndex()
        if index < 0:
            return self.default
        else:
            return self.values[index]

    @pyqtSlot(int)
    def onChanged(self, index):
        self.changed.emit(self.getValue(index))
