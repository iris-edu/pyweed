# -*- coding: utf-8 -*-
"""
Widgets for use with a QTableWidgetItem

:copyright:
    Mazama Science, IRIS
:license:
    GNU Lesser General Public License, Version 3
    (http://www.gnu.org/copyleft/lesser.html)
"""

from PyQt5 import QtWidgets, QtCore

# QTableWidgetItem subclass type iterator
_next_type = QtWidgets.QTableWidgetItem.UserType


class CustomTableWidgetItemMixin(object):
    def __init__(self, *args, **kwargs):
        global _next_type
        _next_type += 1
        return super(CustomTableWidgetItemMixin, self).__init__(*args, **kwargs, type=_next_type)
