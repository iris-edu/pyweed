# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'pyweed/gui/uic/SpinnerWidget.ui'
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

class Ui_SpinnerWidget(object):
    def setupUi(self, SpinnerWidget):
        SpinnerWidget.setObjectName(_fromUtf8("SpinnerWidget"))
        SpinnerWidget.resize(306, 207)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Ignored, QtGui.QSizePolicy.Ignored)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(SpinnerWidget.sizePolicy().hasHeightForWidth())
        SpinnerWidget.setSizePolicy(sizePolicy)
        SpinnerWidget.setStyleSheet(_fromUtf8("QFrame { background-color: rgba(224,224,224,192)} \n"
"QLabel { background-color: transparent }"))
        self.verticalLayout = QtGui.QVBoxLayout(SpinnerWidget)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.icon = QtGui.QLabel(SpinnerWidget)
        self.icon.setText(_fromUtf8(""))
        self.icon.setAlignment(QtCore.Qt.AlignBottom|QtCore.Qt.AlignHCenter)
        self.icon.setObjectName(_fromUtf8("icon"))
        self.verticalLayout.addWidget(self.icon)
        self.label = QtGui.QLabel(SpinnerWidget)
        self.label.setText(_fromUtf8(""))
        self.label.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignTop)
        self.label.setObjectName(_fromUtf8("label"))
        self.verticalLayout.addWidget(self.label)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.cancelButton = QtGui.QPushButton(SpinnerWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cancelButton.sizePolicy().hasHeightForWidth())
        self.cancelButton.setSizePolicy(sizePolicy)
        self.cancelButton.setObjectName(_fromUtf8("cancelButton"))
        self.horizontalLayout.addWidget(self.cancelButton)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.verticalLayout.setStretch(0, 1)
        self.verticalLayout.setStretch(1, 1)

        self.retranslateUi(SpinnerWidget)
        QtCore.QMetaObject.connectSlotsByName(SpinnerWidget)

    def retranslateUi(self, SpinnerWidget):
        SpinnerWidget.setWindowTitle(_translate("SpinnerWidget", "Form", None))
        self.cancelButton.setText(_translate("SpinnerWidget", "Cancel", None))

