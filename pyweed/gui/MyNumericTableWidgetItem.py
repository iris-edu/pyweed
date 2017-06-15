# Custom QTableWidgetItem that forces numerical sorting
#
# http://stackoverflow.com/questions/25533140/sorting-qtablewidget-items-numerically

from PyQt4 import QtCore
from PyQt4 import QtGui
from pyweed.gui.utils import CustomTableWidgetItemMixin


class MyNumericTableWidgetItem (CustomTableWidgetItemMixin, QtGui.QTableWidgetItem):
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
            return QtGui.QTableWidgetItem.__lt__(self, other)
