# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'pyweed/gui/uic/PreferencesDialog.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_PreferencesDialog(object):
    def setupUi(self, PreferencesDialog):
        PreferencesDialog.setObjectName("PreferencesDialog")
        PreferencesDialog.setWindowModality(QtCore.Qt.ApplicationModal)
        PreferencesDialog.resize(287, 241)
        PreferencesDialog.setModal(True)
        self.verticalLayout = QtWidgets.QVBoxLayout(PreferencesDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.dataCentersGroupBox = QtWidgets.QGroupBox(PreferencesDialog)
        self.dataCentersGroupBox.setObjectName("dataCentersGroupBox")
        self.formLayout_4 = QtWidgets.QFormLayout(self.dataCentersGroupBox)
        self.formLayout_4.setObjectName("formLayout_4")
        self.label = QtWidgets.QLabel(self.dataCentersGroupBox)
        self.label.setObjectName("label")
        self.formLayout_4.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label)
        self.eventDataCenterComboBox = QtWidgets.QComboBox(self.dataCentersGroupBox)
        self.eventDataCenterComboBox.setObjectName("eventDataCenterComboBox")
        self.formLayout_4.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.eventDataCenterComboBox)
        self.label_2 = QtWidgets.QLabel(self.dataCentersGroupBox)
        self.label_2.setObjectName("label_2")
        self.formLayout_4.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.stationDataCenterComboBox = QtWidgets.QComboBox(self.dataCentersGroupBox)
        self.stationDataCenterComboBox.setObjectName("stationDataCenterComboBox")
        self.formLayout_4.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.stationDataCenterComboBox)
        self.verticalLayout.addWidget(self.dataCentersGroupBox)
        self.groupBox = QtWidgets.QGroupBox(PreferencesDialog)
        self.groupBox.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.groupBox.setObjectName("groupBox")
        self.formLayout_3 = QtWidgets.QFormLayout(self.groupBox)
        self.formLayout_3.setObjectName("formLayout_3")
        self.label_3 = QtWidgets.QLabel(self.groupBox)
        self.label_3.setObjectName("label_3")
        self.formLayout_3.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label_3)
        self.cacheSizeSpinBox = QtWidgets.QSpinBox(self.groupBox)
        self.cacheSizeSpinBox.setMaximum(500)
        self.cacheSizeSpinBox.setObjectName("cacheSizeSpinBox")
        self.formLayout_3.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.cacheSizeSpinBox)
        self.verticalLayout.addWidget(self.groupBox)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setSpacing(2)
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.okButton = QtWidgets.QPushButton(PreferencesDialog)
        self.okButton.setDefault(True)
        self.okButton.setObjectName("okButton")
        self.horizontalLayout.addWidget(self.okButton)
        self.cancelButton = QtWidgets.QPushButton(PreferencesDialog)
        self.cancelButton.setObjectName("cancelButton")
        self.horizontalLayout.addWidget(self.cancelButton)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.verticalLayout.setStretch(2, 1)

        self.retranslateUi(PreferencesDialog)
        QtCore.QMetaObject.connectSlotsByName(PreferencesDialog)

    def retranslateUi(self, PreferencesDialog):
        _translate = QtCore.QCoreApplication.translate
        PreferencesDialog.setWindowTitle(_translate("PreferencesDialog", "Preferences"))
        self.dataCentersGroupBox.setTitle(_translate("PreferencesDialog", "Data Centers"))
        self.label.setText(_translate("PreferencesDialog", "Events"))
        self.label_2.setText(_translate("PreferencesDialog", "Stations"))
        self.groupBox.setTitle(_translate("PreferencesDialog", "Advanced"))
        self.label_3.setText(_translate("PreferencesDialog", "Cache"))
        self.cacheSizeSpinBox.setSuffix(_translate("PreferencesDialog", " Mbytes"))
        self.okButton.setText(_translate("PreferencesDialog", "Save"))
        self.cancelButton.setText(_translate("PreferencesDialog", "Cancel"))

