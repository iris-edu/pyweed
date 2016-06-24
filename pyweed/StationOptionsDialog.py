# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'StationOptionsDialog.ui'
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

class Ui_StationOptionsDialog(object):
    def setupUi(self, StationOptionsDialog):
        StationOptionsDialog.setObjectName(_fromUtf8("StationOptionsDialog"))
        StationOptionsDialog.resize(320, 381)
        StationOptionsDialog.setMinimumSize(QtCore.QSize(320, 0))
        self.verticalLayout = QtGui.QVBoxLayout(StationOptionsDialog)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.timeGroupBox = QtGui.QGroupBox(StationOptionsDialog)
        self.timeGroupBox.setMinimumSize(QtCore.QSize(0, 0))
        self.timeGroupBox.setStyleSheet(_fromUtf8(""))
        self.timeGroupBox.setObjectName(_fromUtf8("timeGroupBox"))
        self.formLayout_2 = QtGui.QFormLayout(self.timeGroupBox)
        self.formLayout_2.setFieldGrowthPolicy(QtGui.QFormLayout.FieldsStayAtSizeHint)
        self.formLayout_2.setObjectName(_fromUtf8("formLayout_2"))
        self.endtimeDateTimeEdit = QtGui.QDateTimeEdit(self.timeGroupBox)
        self.endtimeDateTimeEdit.setObjectName(_fromUtf8("endtimeDateTimeEdit"))
        self.formLayout_2.setWidget(1, QtGui.QFormLayout.FieldRole, self.endtimeDateTimeEdit)
        self.endtimeLabel = QtGui.QLabel(self.timeGroupBox)
        self.endtimeLabel.setObjectName(_fromUtf8("endtimeLabel"))
        self.formLayout_2.setWidget(1, QtGui.QFormLayout.LabelRole, self.endtimeLabel)
        self.starttimeDateTimeEdit = QtGui.QDateTimeEdit(self.timeGroupBox)
        self.starttimeDateTimeEdit.setObjectName(_fromUtf8("starttimeDateTimeEdit"))
        self.formLayout_2.setWidget(2, QtGui.QFormLayout.FieldRole, self.starttimeDateTimeEdit)
        self.starttimeLabel = QtGui.QLabel(self.timeGroupBox)
        self.starttimeLabel.setObjectName(_fromUtf8("starttimeLabel"))
        self.formLayout_2.setWidget(2, QtGui.QFormLayout.LabelRole, self.starttimeLabel)
        self.verticalLayout.addWidget(self.timeGroupBox)
        self.snclGroupBox = QtGui.QGroupBox(StationOptionsDialog)
        self.snclGroupBox.setObjectName(_fromUtf8("snclGroupBox"))
        self.gridLayout_2 = QtGui.QGridLayout(self.snclGroupBox)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.stationLineEdit = QtGui.QLineEdit(self.snclGroupBox)
        self.stationLineEdit.setObjectName(_fromUtf8("stationLineEdit"))
        self.gridLayout_2.addWidget(self.stationLineEdit, 1, 2, 1, 1)
        self.networkLabel = QtGui.QLabel(self.snclGroupBox)
        self.networkLabel.setObjectName(_fromUtf8("networkLabel"))
        self.gridLayout_2.addWidget(self.networkLabel, 0, 1, 1, 1)
        self.networkLineEdit = QtGui.QLineEdit(self.snclGroupBox)
        self.networkLineEdit.setObjectName(_fromUtf8("networkLineEdit"))
        self.gridLayout_2.addWidget(self.networkLineEdit, 1, 1, 1, 1)
        self.stationLabel = QtGui.QLabel(self.snclGroupBox)
        self.stationLabel.setObjectName(_fromUtf8("stationLabel"))
        self.gridLayout_2.addWidget(self.stationLabel, 0, 2, 1, 1)
        self.locationLineEdit = QtGui.QLineEdit(self.snclGroupBox)
        self.locationLineEdit.setObjectName(_fromUtf8("locationLineEdit"))
        self.gridLayout_2.addWidget(self.locationLineEdit, 1, 3, 1, 1)
        self.channelLineEdit = QtGui.QLineEdit(self.snclGroupBox)
        self.channelLineEdit.setObjectName(_fromUtf8("channelLineEdit"))
        self.gridLayout_2.addWidget(self.channelLineEdit, 1, 4, 1, 1)
        self.locationLabel = QtGui.QLabel(self.snclGroupBox)
        self.locationLabel.setObjectName(_fromUtf8("locationLabel"))
        self.gridLayout_2.addWidget(self.locationLabel, 0, 3, 1, 1)
        self.channelLabel = QtGui.QLabel(self.snclGroupBox)
        self.channelLabel.setObjectName(_fromUtf8("channelLabel"))
        self.gridLayout_2.addWidget(self.channelLabel, 0, 4, 1, 1)
        self.verticalLayout.addWidget(self.snclGroupBox)
        self.locationGroupBox = QtGui.QGroupBox(StationOptionsDialog)
        self.locationGroupBox.setObjectName(_fromUtf8("locationGroupBox"))
        self.gridLayout_3 = QtGui.QGridLayout(self.locationGroupBox)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.minlonLineEdit = QtGui.QLineEdit(self.locationGroupBox)
        self.minlonLineEdit.setObjectName(_fromUtf8("minlonLineEdit"))
        self.gridLayout_3.addWidget(self.minlonLineEdit, 2, 0, 1, 1)
        self.maxlonLineEdit = QtGui.QLineEdit(self.locationGroupBox)
        self.maxlonLineEdit.setObjectName(_fromUtf8("maxlonLineEdit"))
        self.gridLayout_3.addWidget(self.maxlonLineEdit, 2, 2, 1, 1)
        self.centerLabel = QtGui.QLabel(self.locationGroupBox)
        self.centerLabel.setObjectName(_fromUtf8("centerLabel"))
        self.gridLayout_3.addWidget(self.centerLabel, 2, 1, 1, 1, QtCore.Qt.AlignHCenter)
        self.minlatLineEdit = QtGui.QLineEdit(self.locationGroupBox)
        self.minlatLineEdit.setObjectName(_fromUtf8("minlatLineEdit"))
        self.gridLayout_3.addWidget(self.minlatLineEdit, 3, 1, 1, 1)
        self.maxlatLineEdit = QtGui.QLineEdit(self.locationGroupBox)
        self.maxlatLineEdit.setObjectName(_fromUtf8("maxlatLineEdit"))
        self.gridLayout_3.addWidget(self.maxlatLineEdit, 0, 1, 1, 1)
        self.verticalLayout.addWidget(self.locationGroupBox)
        self.closeButton = QtGui.QPushButton(StationOptionsDialog)
        self.closeButton.setObjectName(_fromUtf8("closeButton"))
        self.verticalLayout.addWidget(self.closeButton)

        self.retranslateUi(StationOptionsDialog)
        QtCore.QMetaObject.connectSlotsByName(StationOptionsDialog)

    def retranslateUi(self, StationOptionsDialog):
        StationOptionsDialog.setWindowTitle(_translate("StationOptionsDialog", "Dialog", None))
        self.timeGroupBox.setTitle(_translate("StationOptionsDialog", "Station Time Interval", None))
        self.endtimeLabel.setText(_translate("StationOptionsDialog", "End Time", None))
        self.starttimeLabel.setText(_translate("StationOptionsDialog", "Start Time", None))
        self.snclGroupBox.setTitle(_translate("StationOptionsDialog", "SNCL", None))
        self.networkLabel.setText(_translate("StationOptionsDialog", "Network", None))
        self.stationLabel.setText(_translate("StationOptionsDialog", "Station", None))
        self.locationLabel.setText(_translate("StationOptionsDialog", "Locaion", None))
        self.channelLabel.setText(_translate("StationOptionsDialog", "Channel", None))
        self.locationGroupBox.setTitle(_translate("StationOptionsDialog", "Location Box", None))
        self.centerLabel.setText(_translate("StationOptionsDialog", "Location", None))
        self.closeButton.setText(_translate("StationOptionsDialog", "Close Window", None))

