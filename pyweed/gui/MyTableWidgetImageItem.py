# -*- coding: utf-8 -*-
"""
Custom QTableWidgetItem that embeds an image

To be inserted into the QTableWidget with setItem().

http://stackoverflow.com/questions/14365875/qt-cannot-put-an-image-in-a-table

:copyright:
    Mazama Science, IRIS
:license:
    GNU Lesser General Public License, Version 3
    (http://www.gnu.org/copyleft/lesser.html)
"""

from PyQt5 import QtCore, QtGui, QtWidgets
from pyweed.gui.TableWidget import CustomTableWidgetItemMixin


class MyTableWidgetImageItem(CustomTableWidgetItemMixin, QtWidgets.QTableWidgetItem):
    def __init__(self, imagePath=None):
        super(MyTableWidgetImageItem, self).__init__()
        pic = QtGui.QPixmap(imagePath)
        # NOTE:  From QPixmap we could use scaledToWidth() but the resulting images aren't so pretty
        # pic = pic.scaledToWidth(500)
        self.setData(QtCore.Qt.DecorationRole, pic)
        # NOTE:  From QLabel we could use setScaledContents() but this doesn't preserve the aspect ratio
        # self.setScaledContents(True)
