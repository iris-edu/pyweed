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
        self.selectionTableGroupBox = QtGui.QGroupBox(WaveformDialog)
        self.selectionTableGroupBox.setObjectName(_fromUtf8("selectionTableGroupBox"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.selectionTableGroupBox)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.selectionLabel = QtGui.QLabel(self.selectionTableGroupBox)
        self.selectionLabel.setObjectName(_fromUtf8("selectionLabel"))
        self.verticalLayout_2.addWidget(self.selectionLabel)
        self.selectionTable = QtGui.QTableWidget(self.selectionTableGroupBox)
        self.selectionTable.setMinimumSize(QtCore.QSize(500, 100))
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
        self.waveformTable = QtGui.QTableWidget(self.waveformGroupBox)
        self.waveformTable.setMinimumSize(QtCore.QSize(500, 400))
        self.waveformTable.setObjectName(_fromUtf8("waveformTable"))
        self.waveformTable.setColumnCount(0)
        self.waveformTable.setRowCount(0)
        self.verticalLayout_3.addWidget(self.waveformTable)
        self.verticalLayout.addWidget(self.waveformGroupBox)

        self.retranslateUi(WaveformDialog)
        QtCore.QMetaObject.connectSlotsByName(WaveformDialog)

    def retranslateUi(self, WaveformDialog):
        WaveformDialog.setWindowTitle(_translate("WaveformDialog", "Dialog", None))
        self.selectionLabel.setText(_translate("WaveformDialog", "All Event-SNCL Combinations", None))
        self.waveformLabel.setText(_translate("WaveformDialog", "Waveforms", None))

