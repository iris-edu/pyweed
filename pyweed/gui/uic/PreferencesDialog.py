# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'gui/uic/PreferencesDialog.ui'
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

class Ui_PreferencesDialog(object):
    def setupUi(self, PreferencesDialog):
        PreferencesDialog.setObjectName(_fromUtf8("PreferencesDialog"))
        PreferencesDialog.setModal(True)
        self.verticalLayout = QtGui.QVBoxLayout(PreferencesDialog)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.dataCentersGroupBox = QtGui.QGroupBox(PreferencesDialog)
        self.dataCentersGroupBox.setObjectName(_fromUtf8("dataCentersGroupBox"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.dataCentersGroupBox)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.verticalLayout.addWidget(self.dataCentersGroupBox)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setSpacing(2)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        spacerItem = QtGui.QSpacerItem(0, 0, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.okButton = QtGui.QPushButton(PreferencesDialog)
        self.okButton.setDefault(True)
        self.okButton.setObjectName(_fromUtf8("okButton"))
        self.horizontalLayout.addWidget(self.okButton)
        self.cancelButton = QtGui.QPushButton(PreferencesDialog)
        self.cancelButton.setObjectName(_fromUtf8("cancelButton"))
        self.horizontalLayout.addWidget(self.cancelButton)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(PreferencesDialog)
        QtCore.QMetaObject.connectSlotsByName(PreferencesDialog)

    def retranslateUi(self, PreferencesDialog):
        PreferencesDialog.setWindowTitle(_translate("PreferencesDialog", "Preferences", None))
        self.dataCentersGroupBox.setTitle(_translate("PreferencesDialog", "Data Center", None))
        self.okButton.setText(_translate("PreferencesDialog", "Save", None))
        self.cancelButton.setText(_translate("PreferencesDialog", "Cancel", None))

