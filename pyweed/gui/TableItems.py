"""
Common library for adding data to a QTableWidget.
"""

import numpy as np
from gui.MyNumericTableWidgetItem import MyNumericTableWidgetItem
from PyQt4 import QtGui, QtCore
from gui.MyTableWidgetImageItem import MyTableWidgetImageItem
from logging import getLogger

LOGGER = getLogger(__name__)


class TableItems(object):

    columnNames = None
    table = None

    def __init__(self, table, *args):
        self.table = table

    def rows(self, data):
        """
        Turn the data into rows (an iterable of lists) of QTableWidgetItems
        Subclasses should implement this
        """
        pass

    def stringWidget(self, s):
        return QtGui.QTableWidgetItem(s)

    def numericWidget(self, i):
        return MyNumericTableWidgetItem(str(i))

    def checkboxWidget(self, b):
        checkboxItem = QtGui.QTableWidgetItem()
        checkboxItem.setFlags(QtCore.Qt.ItemIsEnabled)
        if b:
            checkboxItem.setCheckState(QtCore.Qt.Checked)
        else:
            checkboxItem.setCheckState(QtCore.Qt.Unchecked)
        return checkboxItem

    def fill(self, data):
        """
        Fill the table
        """
        # Clear existing contents
        self.table.clear() # This is important!
        while (self.table.rowCount() > 0):
            self.table.removeRow(0)

        # Create new table
        self.table.setColumnCount(len(self.columnNames))
        self.table.setHorizontalHeaderLabels(self.columnNames)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().hide()

        # Use the first column for identification
        self.table.setColumnHidden(0, True)

        # Add new contents
        for rowidx, row in enumerate(self.rows(data)):
            self.table.insertRow(rowidx)
            if len(row) != len(self.columnNames):
                LOGGER.error("Row length doesn't match column count: %s / %s", str(row), str(self.columnNames))
            for cellidx, cell in enumerate(row):
                self.table.setItem(rowidx, cellidx, cell)

        # Tighten up the table
        self.table.resizeColumnsToContents()
        self.table.resizeRowsToContents()
