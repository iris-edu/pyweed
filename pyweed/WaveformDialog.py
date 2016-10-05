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
        WaveformDialog.resize(883, 940)
        self.verticalLayout = QtGui.QVBoxLayout(WaveformDialog)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.filterFrame = QtGui.QFrame(WaveformDialog)
        self.filterFrame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.filterFrame.setFrameShadow(QtGui.QFrame.Raised)
        self.filterFrame.setObjectName(_fromUtf8("filterFrame"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.filterFrame)
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
        self.downloadFrame = QtGui.QFrame(self.filterFrame)
        self.downloadFrame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.downloadFrame.setFrameShadow(QtGui.QFrame.Raised)
        self.downloadFrame.setObjectName(_fromUtf8("downloadFrame"))
        self.horizontalLayout_3 = QtGui.QHBoxLayout(self.downloadFrame)
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.downloadPushButton = QtGui.QPushButton(self.downloadFrame)
        self.downloadPushButton.setObjectName(_fromUtf8("downloadPushButton"))
        self.horizontalLayout_3.addWidget(self.downloadPushButton)
        self.viewPushButton = QtGui.QPushButton(self.downloadFrame)
        self.viewPushButton.setObjectName(_fromUtf8("viewPushButton"))
        self.horizontalLayout_3.addWidget(self.viewPushButton)
        self.horizontalLayout.addWidget(self.downloadFrame)
        self.horizontalLayout.setStretch(0, 3)
        self.horizontalLayout.setStretch(1, 1)
        self.verticalLayout.addWidget(self.filterFrame)
        self.statusFrame = QtGui.QFrame(WaveformDialog)
        self.statusFrame.setObjectName(_fromUtf8("statusFrame"))
        self.verticalLayout_4 = QtGui.QVBoxLayout(self.statusFrame)
        self.verticalLayout_4.setObjectName(_fromUtf8("verticalLayout_4"))
        self.statusLabel = QtGui.QLabel(self.statusFrame)
        self.statusLabel.setObjectName(_fromUtf8("statusLabel"))
        self.verticalLayout_4.addWidget(self.statusLabel)
        self.verticalLayout.addWidget(self.statusFrame)
        self.selectionTableGroupBox = QtGui.QGroupBox(WaveformDialog)
        self.selectionTableGroupBox.setObjectName(_fromUtf8("selectionTableGroupBox"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.selectionTableGroupBox)
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
        self.waveformGroupBox = QtGui.QGroupBox(WaveformDialog)
        self.waveformGroupBox.setObjectName(_fromUtf8("waveformGroupBox"))
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.waveformGroupBox)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.waveformLabel = QtGui.QLabel(self.waveformGroupBox)
        self.waveformLabel.setMinimumSize(QtCore.QSize(0, 0))
        self.waveformLabel.setObjectName(_fromUtf8("waveformLabel"))
        self.verticalLayout_3.addWidget(self.waveformLabel)
        self.canvas1 = Qt4MplCanvas(self.waveformGroupBox)
        self.canvas1.setMinimumSize(QtCore.QSize(0, 200))
        self.canvas1.setObjectName(_fromUtf8("canvas1"))
        self.verticalLayout_3.addWidget(self.canvas1)
        self.waveformTable = QtGui.QTableWidget(self.waveformGroupBox)
        self.waveformTable.setMinimumSize(QtCore.QSize(500, 200))
        self.waveformTable.setObjectName(_fromUtf8("waveformTable"))
        self.waveformTable.setColumnCount(0)
        self.waveformTable.setRowCount(0)
        self.verticalLayout_3.addWidget(self.waveformTable)
        self.verticalLayout.addWidget(self.waveformGroupBox)

        self.retranslateUi(WaveformDialog)
        QtCore.QMetaObject.connectSlotsByName(WaveformDialog)

    def retranslateUi(self, WaveformDialog):
        WaveformDialog.setWindowTitle(_translate("WaveformDialog", "Dialog", None))
        self.filterGroupBox.setTitle(_translate("WaveformDialog", "Filters", None))
        self.downloadPushButton.setText(_translate("WaveformDialog", "Download Selected", None))
        self.viewPushButton.setText(_translate("WaveformDialog", "View Selected", None))
        self.statusLabel.setText(_translate("WaveformDialog", "TextLabel", None))
        self.selectionLabel.setText(_translate("WaveformDialog", "All Event-SNCL Combinations", None))
        self.waveformLabel.setText(_translate("WaveformDialog", "Waveforms", None))

from qt4mplcanvas import Qt4MplCanvas
