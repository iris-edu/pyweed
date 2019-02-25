# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'pyweed/gui/uic/LoggingDialog.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_LoggingDialog(object):
    def setupUi(self, LoggingDialog):
        LoggingDialog.setObjectName("LoggingDialog")
        LoggingDialog.resize(697, 474)
        self.verticalLayout = QtWidgets.QVBoxLayout(LoggingDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.loggingPlainTextEdit = QtWidgets.QPlainTextEdit(LoggingDialog)
        self.loggingPlainTextEdit.setObjectName("loggingPlainTextEdit")
        self.verticalLayout.addWidget(self.loggingPlainTextEdit)

        self.retranslateUi(LoggingDialog)
        QtCore.QMetaObject.connectSlotsByName(LoggingDialog)

    def retranslateUi(self, LoggingDialog):
        _translate = QtCore.QCoreApplication.translate
        LoggingDialog.setWindowTitle(_translate("LoggingDialog", "Dialog"))

