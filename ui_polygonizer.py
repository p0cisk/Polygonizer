# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Documents and Settings\Pocisk\Pulpit\Polygonizer\ui_polygonizer.ui'
#
# Created: Sat Feb 26 12:11:41 2011
#      by: PyQt4 UI code generator 4.8.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName(_fromUtf8("Form"))
        Form.resize(423, 197)
        Form.setAutoFillBackground(False)
        self.btnOK = QtGui.QPushButton(Form)
        self.btnOK.setGeometry(QtCore.QRect(200, 160, 98, 27))
        self.btnOK.setObjectName(_fromUtf8("btnOK"))
        self.btnCancel = QtGui.QPushButton(Form)
        self.btnCancel.setGeometry(QtCore.QRect(310, 160, 98, 27))
        self.btnCancel.setFlat(False)
        self.btnCancel.setObjectName(_fromUtf8("btnCancel"))
        self.label = QtGui.QLabel(Form)
        self.label.setGeometry(QtCore.QRect(10, 10, 151, 17))
        self.label.setObjectName(_fromUtf8("label"))
        self.label_2 = QtGui.QLabel(Form)
        self.label_2.setGeometry(QtCore.QRect(10, 100, 81, 17))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.cmbLayer = QtGui.QComboBox(Form)
        self.cmbLayer.setGeometry(QtCore.QRect(10, 30, 401, 27))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cmbLayer.sizePolicy().hasHeightForWidth())
        self.cmbLayer.setSizePolicy(sizePolicy)
        self.cmbLayer.setObjectName(_fromUtf8("cmbLayer"))
        self.btnBrowse = QtGui.QPushButton(Form)
        self.btnBrowse.setGeometry(QtCore.QRect(310, 120, 98, 27))
        self.btnBrowse.setObjectName(_fromUtf8("btnBrowse"))
        self.eOutput = QtGui.QLineEdit(Form)
        self.eOutput.setGeometry(QtCore.QRect(10, 120, 291, 27))
        self.eOutput.setObjectName(_fromUtf8("eOutput"))
        self.cbGeometry = QtGui.QCheckBox(Form)
        self.cbGeometry.setGeometry(QtCore.QRect(10, 70, 211, 22))
        self.cbGeometry.setChecked(True)
        self.cbGeometry.setObjectName(_fromUtf8("cbGeometry"))
        self.pbProgress = QtGui.QProgressBar(Form)
        self.pbProgress.setGeometry(QtCore.QRect(10, 160, 181, 23))
        self.pbProgress.setProperty(_fromUtf8("value"), 0)
        self.pbProgress.setObjectName(_fromUtf8("pbProgress"))

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QtGui.QApplication.translate("Form", "Polygonizer", None, QtGui.QApplication.UnicodeUTF8))
        self.btnOK.setText(QtGui.QApplication.translate("Form", "OK", None, QtGui.QApplication.UnicodeUTF8))
        self.btnCancel.setText(QtGui.QApplication.translate("Form", "Cancel", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Form", "Input line vector layer:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("Form", "Output file:", None, QtGui.QApplication.UnicodeUTF8))
        self.btnBrowse.setText(QtGui.QApplication.translate("Form", "Browse", None, QtGui.QApplication.UnicodeUTF8))
        self.cbGeometry.setText(QtGui.QApplication.translate("Form", "Create geometry columns", None, QtGui.QApplication.UnicodeUTF8))

