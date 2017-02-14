"""
Common library for adding data to a QTableWidget.
"""

import numpy as np
from gui.MyNumericTableWidgetItem import MyNumericTableWidgetItem
from PyQt4 import QtGui, QtCore
from gui.MyTableWidgetImageItem import MyTableWidgetImageItem


class TableItems(object):

    def __init__(self, table, visibleColumns, numericColumns):
        self.table = table
        self.visibleColumns = visibleColumns
        self.numericColumns = numericColumns
        self.columnNames = []

    def build(self, df):
        """
        Build table contents from the given dataframe
        """

        # Clear existing contents
        self.table.clear() # This is important!
        while (self.table.rowCount() > 0):
            self.table.removeRow(0)

        # Column names
        self.columnNames = df.columns.tolist()

        # Create new table
        self.table.setRowCount(df.shape[0])
        self.table.setColumnCount(df.shape[1])
        self.table.setHorizontalHeaderLabels(self.columnNames)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().hide()

        # Hidden columns
        for i, column in enumerate(self.columnNames):
            self.table.setColumnHidden(i, column not in self.visibleColumns)

        # Add new contents
        for i in range(df.shape[0]):
            for j in range(df.shape[1]):
                self.buildOne(df, i, j)

        # Tighten up the table
        self.table.resizeColumnsToContents()
        self.table.resizeRowsToContents()

    def buildOne(self, df, i, j):
        """
        Fill in a single cell of the table from the dataframe
        Subclasses should extend this to handle any unusual data type
        """
        if self.columnNames[j] in self.numericColumns:
            # Guarantee that all elements are converted to strings for display but apply proper sorting
            self.table.setItem(i, j, MyNumericTableWidgetItem(str(df.iat[i,j])))
        else:
            # Anything else is converted to normal text
            self.table.setItem(i, j, QtGui.QTableWidgetItem(str(df.iat[i,j])))
