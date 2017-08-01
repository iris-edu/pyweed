# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'pyweed/gui/uic/LoggingDialog.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_LoggingDialog(object):
    def setupUi(self, LoggingDialog):
        LoggingDialog.setObjectName(_fromUtf8("LoggingDialog"))
        LoggingDialog.resize(697, 474)
        self.verticalLayout = QtGui.QVBoxLayout(LoggingDialog)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.loggingPlainTextEdit = QtGui.QPlainTextEdit(LoggingDialog)
        self.loggingPlainTextEdit.setObjectName(_fromUtf8("loggingPlainTextEdit"))
        self.verticalLayout.addWidget(self.loggingPlainTextEdit)

        self.retranslateUi(LoggingDialog)
        QtCore.QMetaObject.connectSlotsByName(LoggingDialog)

    def retranslateUi(self, LoggingDialog):
        LoggingDialog.setWindowTitle(_translate("LoggingDialog", "Dialog", None))

