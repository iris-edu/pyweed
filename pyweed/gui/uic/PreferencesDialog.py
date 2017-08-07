# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'pyweed/gui/uic/PreferencesDialog.ui'
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
        PreferencesDialog.setWindowModality(QtCore.Qt.ApplicationModal)
        PreferencesDialog.resize(287, 241)
        PreferencesDialog.setModal(True)
        self.verticalLayout = QtGui.QVBoxLayout(PreferencesDialog)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.dataCentersGroupBox = QtGui.QGroupBox(PreferencesDialog)
        self.dataCentersGroupBox.setObjectName(_fromUtf8("dataCentersGroupBox"))
        self.formLayout_4 = QtGui.QFormLayout(self.dataCentersGroupBox)
        self.formLayout_4.setObjectName(_fromUtf8("formLayout_4"))
        self.label = QtGui.QLabel(self.dataCentersGroupBox)
        self.label.setObjectName(_fromUtf8("label"))
        self.formLayout_4.setWidget(0, QtGui.QFormLayout.LabelRole, self.label)
        self.eventDataCenterComboBox = QtGui.QComboBox(self.dataCentersGroupBox)
        self.eventDataCenterComboBox.setObjectName(_fromUtf8("eventDataCenterComboBox"))
        self.formLayout_4.setWidget(0, QtGui.QFormLayout.FieldRole, self.eventDataCenterComboBox)
        self.label_2 = QtGui.QLabel(self.dataCentersGroupBox)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.formLayout_4.setWidget(1, QtGui.QFormLayout.LabelRole, self.label_2)
        self.stationDataCenterComboBox = QtGui.QComboBox(self.dataCentersGroupBox)
        self.stationDataCenterComboBox.setObjectName(_fromUtf8("stationDataCenterComboBox"))
        self.formLayout_4.setWidget(1, QtGui.QFormLayout.FieldRole, self.stationDataCenterComboBox)
        self.verticalLayout.addWidget(self.dataCentersGroupBox)
        self.groupBox = QtGui.QGroupBox(PreferencesDialog)
        self.groupBox.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.formLayout_3 = QtGui.QFormLayout(self.groupBox)
        self.formLayout_3.setObjectName(_fromUtf8("formLayout_3"))
        self.label_3 = QtGui.QLabel(self.groupBox)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.formLayout_3.setWidget(0, QtGui.QFormLayout.LabelRole, self.label_3)
        self.cacheSizeSpinBox = QtGui.QSpinBox(self.groupBox)
        self.cacheSizeSpinBox.setMaximum(500)
        self.cacheSizeSpinBox.setObjectName(_fromUtf8("cacheSizeSpinBox"))
        self.formLayout_3.setWidget(0, QtGui.QFormLayout.FieldRole, self.cacheSizeSpinBox)
        self.verticalLayout.addWidget(self.groupBox)
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
        self.verticalLayout.setStretch(2, 1)

        self.retranslateUi(PreferencesDialog)
        QtCore.QMetaObject.connectSlotsByName(PreferencesDialog)

    def retranslateUi(self, PreferencesDialog):
        PreferencesDialog.setWindowTitle(_translate("PreferencesDialog", "Preferences", None))
        self.dataCentersGroupBox.setTitle(_translate("PreferencesDialog", "Data Centers", None))
        self.label.setText(_translate("PreferencesDialog", "Events", None))
        self.label_2.setText(_translate("PreferencesDialog", "Stations", None))
        self.groupBox.setTitle(_translate("PreferencesDialog", "Advanced", None))
        self.label_3.setText(_translate("PreferencesDialog", "Cache", None))
        self.cacheSizeSpinBox.setSuffix(_translate("PreferencesDialog", " Mbytes", None))
        self.okButton.setText(_translate("PreferencesDialog", "Save", None))
        self.cancelButton.setText(_translate("PreferencesDialog", "Cancel", None))

