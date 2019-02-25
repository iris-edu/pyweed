# -*- coding: utf-8 -*-
"""
Custom QTableWidgetItem that forces numerical sorting

http://stackoverflow.com/questions/25533140/sorting-qtablewidget-items-numerically

:copyright:
    Mazama Science, IRIS
:license:
    GNU Lesser General Public License, Version 3
    (http://www.gnu.org/copyleft/lesser.html)
"""

from PyQt5 import QtCore
from PyQt5 import QtWidgets
from pyweed.gui.TableWidget import CustomTableWidgetItemMixin


class MyNumericTableWidgetItem (CustomTableWidgetItemMixin, QtWidgets.QTableWidgetItem):
    """
    Custom QTableWidgetItem that forces numerical sorting

    http://stackoverflow.com/questions/25533140/sorting-qtablewidget-items-numerically
    """

    def __init__(self, value, text):
        super(MyNumericTableWidgetItem, self).__init__(text)
        self.setData(QtCore.Qt.UserRole, value)

    def __lt__(self, other):
        if (isinstance(other, MyNumericTableWidgetItem)):
            selfDataValue = float(self.data(QtCore.Qt.UserRole))
            otherDataValue = float(other.data(QtCore.Qt.UserRole))
            return selfDataValue < otherDataValue
        else:
            return QtWidgets.QTableWidgetItem.__lt__(self, other)
