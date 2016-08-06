# QTableWidgetItem that forces numerical sorting
#
# http://stackoverflow.com/questions/25533140/sorting-qtablewidget-items-numerically

from PyQt4 import QtCore
from PyQt4 import QtGui

class MyNumericTableWidgetItem (QtGui.QTableWidgetItem):
    def __init__ (self, value):
        super(MyNumericTableWidgetItem, self).__init__(QtCore.QString('%s' % value))

    def __lt__ (self, other):
        if (isinstance(other, MyNumericTableWidgetItem)):
            selfDataValue  = float(self.data(QtCore.Qt.EditRole).toString())
            otherDataValue = float(other.data(QtCore.Qt.EditRole).toString())
            return selfDataValue < otherDataValue
        else:
            return QtGui.QTableWidgetItem.__lt__(self, other)
