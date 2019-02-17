# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'command_editor.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_CommandEditor(object):
    def setupUi(self, CommandEditor):
        CommandEditor.setObjectName("CommandEditor")
        CommandEditor.resize(294, 144)
        CommandEditor.setMinimumSize(QtCore.QSize(294, 144))
        CommandEditor.setMaximumSize(QtCore.QSize(314, 144))
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(CommandEditor)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.current_shortcut = QtWidgets.QLabel(CommandEditor)
        self.current_shortcut.setVisible(False)
        self.current_shortcut.setText("")
        self.current_shortcut.setObjectName("current_shortcut")
        self.verticalLayout.addWidget(self.current_shortcut)
        self.label = QtWidgets.QLabel(CommandEditor)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.label_2 = QtWidgets.QLabel(CommandEditor)
        self.label_2.setEnabled(True)
        self.label_2.setVisible(False)
        self.label_2.setObjectName("label_2")
        self.verticalLayout.addWidget(self.label_2)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.radioButton1 = QtWidgets.QRadioButton(CommandEditor)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.radioButton1.sizePolicy().hasHeightForWidth())
        self.radioButton1.setSizePolicy(sizePolicy)
        self.radioButton1.setText("")
        self.radioButton1.setChecked(True)
        self.radioButton1.setObjectName("radioButton1")
        self.horizontalLayout.addWidget(self.radioButton1)
        self.keySequenceEdit = QtWidgets.QKeySequenceEdit(CommandEditor)
        self.keySequenceEdit.setObjectName("keySequenceEdit")
        self.horizontalLayout.addWidget(self.keySequenceEdit)
        self.btn_clear = QtWidgets.QPushButton(CommandEditor)
        self.btn_clear.setObjectName("btn_clear")
        self.horizontalLayout.addWidget(self.btn_clear)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.radioButton2 = QtWidgets.QRadioButton(CommandEditor)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.radioButton2.sizePolicy().hasHeightForWidth())
        self.radioButton2.setSizePolicy(sizePolicy)
        self.radioButton2.setText("")
        self.radioButton2.setObjectName("radioButton2")
        self.horizontalLayout_3.addWidget(self.radioButton2)
        self.buttons_specials_field = QtWidgets.QComboBox(CommandEditor)
        self.buttons_specials_field.setEnabled(False)
        self.buttons_specials_field.setMaximumSize(QtCore.QSize(300, 16777215))
        self.buttons_specials_field.setStyleSheet("")
        self.buttons_specials_field.setObjectName("buttons_specials_field")
        self.buttons_specials_field.addItem("")
        self.buttons_specials_field.addItem("")
        self.buttons_specials_field.addItem("")
        self.buttons_specials_field.addItem("")
        self.buttons_specials_field.addItem("")
        self.buttons_specials_field.addItem("")
        self.buttons_specials_field.addItem("")
        self.buttons_specials_field.addItem("")
        self.buttons_specials_field.addItem("")
        self.buttons_specials_field.addItem("")
        self.buttons_specials_field.addItem("")
        self.buttons_specials_field.addItem("")
        self.buttons_specials_field.addItem("")
        self.buttons_specials_field.addItem("")
        self.buttons_specials_field.addItem("")
        self.buttons_specials_field.addItem("")
        self.horizontalLayout_3.addWidget(self.buttons_specials_field)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.btn_ok = QtWidgets.QPushButton(CommandEditor)
        self.btn_ok.setObjectName("btn_ok")
        self.horizontalLayout_2.addWidget(self.btn_ok)
        self.btn_cancel = QtWidgets.QPushButton(CommandEditor)
        self.btn_cancel.setObjectName("btn_cancel")
        self.horizontalLayout_2.addWidget(self.btn_cancel)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.verticalLayout_2.addLayout(self.verticalLayout)

        self.retranslateUi(CommandEditor)
        self.radioButton1.clicked['bool'].connect(self.keySequenceEdit.setEnabled)
        self.radioButton1.clicked['bool'].connect(self.btn_clear.setEnabled)
        self.radioButton1.clicked['bool'].connect(self.buttons_specials_field.setDisabled)
        self.radioButton2.clicked['bool'].connect(self.buttons_specials_field.setEnabled)
        self.radioButton2.clicked['bool'].connect(self.keySequenceEdit.setDisabled)
        self.radioButton2.clicked['bool'].connect(self.btn_clear.setDisabled)
        self.radioButton1.clicked['bool'].connect(self.label.show)
        self.radioButton1.clicked['bool'].connect(self.label_2.hide)
        self.radioButton2.clicked['bool'].connect(self.label.hide)
        self.radioButton2.clicked['bool'].connect(self.label_2.show)
        QtCore.QMetaObject.connectSlotsByName(CommandEditor)

    def retranslateUi(self, CommandEditor):
        _translate = QtCore.QCoreApplication.translate
        CommandEditor.setWindowTitle(_translate("CommandEditor", "Command Editor"))
        self.label.setText(_translate("CommandEditor", "Enter your keystroke including any modifiers:"))
        self.label_2.setText(_translate("CommandEditor", "Select a mouse function from list below:"))
        self.btn_clear.setText(_translate("CommandEditor", "Clear"))
        self.buttons_specials_field.setItemText(0, _translate("CommandEditor", "Current Shortcut"))
        self.buttons_specials_field.setItemText(1, _translate("CommandEditor", "Button1"))
        self.buttons_specials_field.setItemText(2, _translate("CommandEditor", "Button2"))
        self.buttons_specials_field.setItemText(3, _translate("CommandEditor", "Button3"))
        self.buttons_specials_field.setItemText(4, _translate("CommandEditor", "Button6"))
        self.buttons_specials_field.setItemText(5, _translate("CommandEditor", "Button7"))
        self.buttons_specials_field.setItemText(6, _translate("CommandEditor", "Button8"))
        self.buttons_specials_field.setItemText(7, _translate("CommandEditor", "Button9"))
        self.buttons_specials_field.setItemText(8, _translate("CommandEditor", "Button10"))
        self.buttons_specials_field.setItemText(9, _translate("CommandEditor", "Button11"))
        self.buttons_specials_field.setItemText(10, _translate("CommandEditor", "DPIUp"))
        self.buttons_specials_field.setItemText(11, _translate("CommandEditor", "DPIDown"))
        self.buttons_specials_field.setItemText(12, _translate("CommandEditor", "DPICycle"))
        self.buttons_specials_field.setItemText(13, _translate("CommandEditor", "ModeSwitch"))
        self.buttons_specials_field.setItemText(14, _translate("CommandEditor", "DPIShift"))
        self.buttons_specials_field.setItemText(15, _translate("CommandEditor", "DPIDefault"))
        self.btn_ok.setText(_translate("CommandEditor", "OK"))
        self.btn_cancel.setText(_translate("CommandEditor", "Cancel"))

