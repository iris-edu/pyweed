# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'WaveformDialog.ui'
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

class Ui_WaveformDialog(object):
    def setupUi(self, WaveformDialog):
        WaveformDialog.setObjectName(_fromUtf8("WaveformDialog"))
        WaveformDialog.resize(1240, 1103)
        self.verticalLayout = QtGui.QVBoxLayout(WaveformDialog)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.filterFrame = QtGui.QFrame(WaveformDialog)
        self.filterFrame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.filterFrame.setFrameShadow(QtGui.QFrame.Raised)
        self.filterFrame.setObjectName(_fromUtf8("filterFrame"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.filterFrame)
        self.horizontalLayout.setMargin(2)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.filterGroupBox = QtGui.QGroupBox(self.filterFrame)
        self.filterGroupBox.setObjectName(_fromUtf8("filterGroupBox"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout(self.filterGroupBox)
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.eventComboBox = QtGui.QComboBox(self.filterGroupBox)
        self.eventComboBox.setObjectName(_fromUtf8("eventComboBox"))
        self.horizontalLayout_2.addWidget(self.eventComboBox)
        self.networkComboBox = QtGui.QComboBox(self.filterGroupBox)
        self.networkComboBox.setObjectName(_fromUtf8("networkComboBox"))
        self.horizontalLayout_2.addWidget(self.networkComboBox)
        self.stationComboBox = QtGui.QComboBox(self.filterGroupBox)
        self.stationComboBox.setObjectName(_fromUtf8("stationComboBox"))
        self.horizontalLayout_2.addWidget(self.stationComboBox)
        self.horizontalLayout_2.setStretch(0, 3)
        self.horizontalLayout_2.setStretch(1, 1)
        self.horizontalLayout_2.setStretch(2, 1)
        self.horizontalLayout.addWidget(self.filterGroupBox)
        self.saveFrame = QtGui.QFrame(self.filterFrame)
        self.saveFrame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.saveFrame.setFrameShadow(QtGui.QFrame.Raised)
        self.saveFrame.setLineWidth(1)
        self.saveFrame.setObjectName(_fromUtf8("saveFrame"))
        self.horizontalLayout_3 = QtGui.QHBoxLayout(self.saveFrame)
        self.horizontalLayout_3.setMargin(2)
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.saveLabelFrame = QtGui.QFrame(self.saveFrame)
        self.saveLabelFrame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.saveLabelFrame.setFrameShadow(QtGui.QFrame.Raised)
        self.saveLabelFrame.setObjectName(_fromUtf8("saveLabelFrame"))
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.saveLabelFrame)
        self.verticalLayout_3.setMargin(2)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.label_1 = QtGui.QLabel(self.saveLabelFrame)
        self.label_1.setText(_fromUtf8(""))
        self.label_1.setObjectName(_fromUtf8("label_1"))
        self.verticalLayout_3.addWidget(self.label_1)
        self.label_2 = QtGui.QLabel(self.saveLabelFrame)
        self.label_2.setBaseSize(QtCore.QSize(0, 0))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.verticalLayout_3.addWidget(self.label_2)
        self.label_3 = QtGui.QLabel(self.saveLabelFrame)
        self.label_3.setBaseSize(QtCore.QSize(0, 0))
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.verticalLayout_3.addWidget(self.label_3)
        self.horizontalLayout_3.addWidget(self.saveLabelFrame)
        self.saveButtonFrame = QtGui.QFrame(self.saveFrame)
        self.saveButtonFrame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.saveButtonFrame.setFrameShadow(QtGui.QFrame.Raised)
        self.saveButtonFrame.setObjectName(_fromUtf8("saveButtonFrame"))
        self.verticalLayout_5 = QtGui.QVBoxLayout(self.saveButtonFrame)
        self.verticalLayout_5.setMargin(2)
        self.verticalLayout_5.setObjectName(_fromUtf8("verticalLayout_5"))
        self.savePushButton = QtGui.QPushButton(self.saveButtonFrame)
        self.savePushButton.setObjectName(_fromUtf8("savePushButton"))
        self.verticalLayout_5.addWidget(self.savePushButton)
        self.directoryPushButton = QtGui.QPushButton(self.saveButtonFrame)
        self.directoryPushButton.setObjectName(_fromUtf8("directoryPushButton"))
        self.verticalLayout_5.addWidget(self.directoryPushButton)
        self.formatComboBox = QtGui.QComboBox(self.saveButtonFrame)
        self.formatComboBox.setObjectName(_fromUtf8("formatComboBox"))
        self.verticalLayout_5.addWidget(self.formatComboBox)
        self.horizontalLayout_3.addWidget(self.saveButtonFrame)
        self.horizontalLayout.addWidget(self.saveFrame)
        self.horizontalLayout.setStretch(0, 3)
        self.horizontalLayout.setStretch(1, 1)
        self.verticalLayout.addWidget(self.filterFrame)
        self.statusFrame = QtGui.QFrame(WaveformDialog)
        self.statusFrame.setObjectName(_fromUtf8("statusFrame"))
        self.verticalLayout_4 = QtGui.QVBoxLayout(self.statusFrame)
        self.verticalLayout_4.setMargin(2)
        self.verticalLayout_4.setObjectName(_fromUtf8("verticalLayout_4"))
        self.statusLabel = QtGui.QLabel(self.statusFrame)
        self.statusLabel.setObjectName(_fromUtf8("statusLabel"))
        self.verticalLayout_4.addWidget(self.statusLabel)
        self.verticalLayout.addWidget(self.statusFrame)
        self.selectionTableGroupBox = QtGui.QGroupBox(WaveformDialog)
        self.selectionTableGroupBox.setObjectName(_fromUtf8("selectionTableGroupBox"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.selectionTableGroupBox)
        self.verticalLayout_2.setMargin(2)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.selectionLabel = QtGui.QLabel(self.selectionTableGroupBox)
        self.selectionLabel.setObjectName(_fromUtf8("selectionLabel"))
        self.verticalLayout_2.addWidget(self.selectionLabel)
        self.selectionTable = QtGui.QTableWidget(self.selectionTableGroupBox)
        self.selectionTable.setMinimumSize(QtCore.QSize(500, 100))
        self.selectionTable.setShowGrid(False)
        self.selectionTable.setGridStyle(QtCore.Qt.NoPen)
        self.selectionTable.setObjectName(_fromUtf8("selectionTable"))
        self.selectionTable.setColumnCount(0)
        self.selectionTable.setRowCount(0)
        self.verticalLayout_2.addWidget(self.selectionTable)
        self.verticalLayout.addWidget(self.selectionTableGroupBox)

        self.retranslateUi(WaveformDialog)
        QtCore.QMetaObject.connectSlotsByName(WaveformDialog)

    def retranslateUi(self, WaveformDialog):
        WaveformDialog.setWindowTitle(_translate("WaveformDialog", "Dialog", None))
        self.filterGroupBox.setTitle(_translate("WaveformDialog", "Filters", None))
        self.label_2.setText(_translate("WaveformDialog", "To:", None))
        self.label_3.setText(_translate("WaveformDialog", "As:", None))
        self.savePushButton.setText(_translate("WaveformDialog", "Save Waveforms", None))
        self.directoryPushButton.setText(_translate("WaveformDialog", "Directory", None))
        self.statusLabel.setText(_translate("WaveformDialog", "TextLabel", None))
        self.selectionLabel.setText(_translate("WaveformDialog", "All Event-SNCL Waveforms", None))

