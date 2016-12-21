# Custom QTableWidgetItem that forces numerical sorting
#
# http://stackoverflow.com/questions/25533140/sorting-qtablewidget-items-numerically

from PyQt4 import QtCore
from PyQt4 import QtGui

class MyNumericTableWidgetItem (QtGui.QTableWidgetItem):
    """
    Custom QTableWidgetItem that forces numerical sorting

    http://stackoverflow.com/questions/25533140/sorting-qtablewidget-items-numerically
    """

    def __init__ (self, value):
        super(MyNumericTableWidgetItem, self).__init__('%s' % value)

    def __lt__ (self, other):
        if (isinstance(other, MyNumericTableWidgetItem)):
            selfDataValue  = float(self.data(QtCore.Qt.EditRole))
            otherDataValue = float(other.data(QtCore.Qt.EditRole))
            return selfDataValue < otherDataValue
        else:
            return QtGui.QTableWidgetItem.__lt__(self, other)

