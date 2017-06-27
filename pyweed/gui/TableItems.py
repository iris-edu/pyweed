# -*- coding: utf-8 -*-
"""
Common library for adding data to a QTableWidget.

:copyright:
    Mazama Science, IRIS
:license:
    GNU Lesser General Public License, Version 3
    (http://www.gnu.org/copyleft/lesser.html)
"""

from pyweed.gui.MyNumericTableWidgetItem import MyNumericTableWidgetItem
from PyQt4 import QtGui, QtCore
from logging import getLogger

LOGGER = getLogger(__name__)


class Column(object):
    """ Defines a column for `TableItems` """
    def __init__(self, label, description=None, width=None):
        """
        :param label: The label to display in the column header
        :param description: If set, text will appear when the user hovers over the header
        :param width: Hardcode the column width, this is useful for fields that may have long values that
            would otherwise blow out the table width
        """
        self.label = label
        self.description = description
        self.width = width


class TableItems(object):
    """
    Base helper class for adding a bunch of records to a QTableWidget.

    Subclasses just need to define the columns and how to turn a list of
    records into table cells.

    :example:

    >>> class ExampleTableItems(TableItems):
    >>>     columns = [
    >>>         Column('Id'),
    >>>         Column('Name', width=200),
    >>>         Column('Email'),
    >>>         Column('Age'),
    >>>     ]
    >>>     def rows(self, data):
    >>>         for person in data:
    >>>             yield [
    >>>                 self.stringWidget(person.id),
    >>>                 self.stringWidget(person.name),
    >>>                 self.stringWidget(person.email),
    >>>                 self.numericWidget(person.age),
    >>>             ]

    >>> items = ExampleTableItems(q_table_widget)
    >>> items.fill(list_of_people)

    """

    #: Subclass should define the columns
    columns = None
    #: Table that the items are tied to
    table = None
    #: Subclass can set this to enforce a fixed row height (otherwise it will be sized to fit when it gets filled)
    rowHeight = None

    def __init__(self, table, *args):
        self.table = table

    def rows(self, data):
        """
        Turn the data into rows (an iterable of lists) of QTableWidgetItems
        Subclasses should implement this
        """
        pass

    def applyProps(self, widget, **props):
        """
        Apply props to a newly created widget.

        This is used by the various widget methods to handle arbitrary keyword arguments by
        translating them into Qt setter calls.

        For example, passing `textAlignment=QtCore.Qt.AlignCenter` as a keyword argument will result in
        `widget.setTextAlignment(QtCore.Qt.AlignCenter)`
        """
        # Look for Qt setter for any given prop name
        for prop, value in props.items():
            setter = 'set%s%s' % (prop[:1].capitalize(), prop[1:])
            if hasattr(widget, setter):
                try:
                    getattr(widget, setter)(value)
                except Exception as e:
                    LOGGER.error("Tried and failed to set %s: %s", prop, e)
        return widget

    def stringWidget(self, s, **props):
        """ Create a new item displaying the given string """
        return self.applyProps(QtGui.QTableWidgetItem(s), **props)

    def numericWidget(self, i, text=None, **props):
        """
        Create a new item displaying the given numeric value. Pass a string or a string format as `text` to customize
        how the number is actually displayed. The numeric value will still be used for sorting.
        """
        if text is None:
            text = "%s"
        if '%' in text:
            text = text % i
        return self.applyProps(MyNumericTableWidgetItem(i, text), **props)

    def checkboxWidget(self, b, **props):
        """ Create a new checkbox widget showing the given boolean state """
        checkboxItem = self.applyProps(QtGui.QTableWidgetItem(), **props)
        checkboxItem.setFlags(QtCore.Qt.ItemIsEnabled)
        if b:
            checkboxItem.setCheckState(QtCore.Qt.Checked)
        else:
            checkboxItem.setCheckState(QtCore.Qt.Unchecked)
        return checkboxItem

    def initColumns(self):
        # Only run this if the table columns aren't already set up
        if self.table.columnCount() != len(self.columns):
            self.table.setColumnCount(len(self.columns))

            columnLabels = [c.label for c in self.columns]
            self.table.setHorizontalHeaderLabels(columnLabels)

            # Use the first column for identification
            self.table.setColumnHidden(0, True)

            # Set the tooltips
            for i, column in enumerate(self.columns):
                if column.description:
                    self.table.horizontalHeaderItem(i).setToolTip(column.description)

    def fill(self, data):
        """
        Fill the table
        """
        # Clear existing contents
        self.table.setRowCount(0)

        # Initialize the table columns if needed
        self.initColumns()

        # Need to turn off sorting before inserting items
        self.table.setSortingEnabled(False)

        # Add new contents
        for rowidx, row in enumerate(self.rows(data)):
            self.table.insertRow(rowidx)
            if len(row) != len(self.columns):
                LOGGER.error("Row length doesn't match column count: %s / %s", str(row), str([c.label for c in self.columns]))
            for cellidx, cell in enumerate(row):
                self.table.setItem(rowidx, cellidx, cell)

        # Turn sorting back on
        self.table.setSortingEnabled(True)

        # Adjust the row heights
        if self.rowHeight:
            for i in range(self.table.rowCount()):
                self.table.setRowHeight(i, self.rowHeight)
        else:
            self.table.resizeRowsToContents()

        # Adjust the column widths
        for i, column in enumerate(self.columns):
            if column.width:
                self.table.setColumnWidth(i, column.width)
            else:
                self.table.resizeColumnToContents(i)
