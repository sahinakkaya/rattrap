from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication
from ui_command_editor import Ui_CommandEditor
import shortcut


class CommandEditor(QtWidgets.QDialog, Ui_CommandEditor):
    def __init__(self, button, parent):
        super().__init__(parent)
        self.setupUi(self)
        self.button = button
        self.bind_widgets()
        self.show()

    def bind_widgets(self):
        self.keySequenceEdit.setKeySequence(self.button.text())
        self.keySequenceEdit.keySequenceChanged.connect(self.update_shortcut_label)
        self.buttons_specials_field.setItemText(0, self.button.text())
        self.buttons_specials_field.currentTextChanged.connect(self.update_shortcut_label)

        self.btn_clear.clicked.connect(self.keySequenceEdit.clear)
        self.btn_ok.clicked.connect(self.register_shortcut)
        self.btn_cancel.clicked.connect(self.close)

    def update_shortcut_label(self):
        if self.sender().objectName() == "keySequenceEdit":
            self.current_shortcut.setText(self.keySequenceEdit.keySequence().toString())
        else:
            self.current_shortcut.setText(self.buttons_specials_field.currentText())

    def register_shortcut(self):
        new_shortcut = self.current_shortcut.text()
        if new_shortcut != "":
            self.button.setText(new_shortcut)
            self.parent().conn.update_value(
                "profiles", self.button.objectName(), new_shortcut, name=self.parent().current_mode_name)
        self.close()


class AssignShortcutWidget(QtWidgets.QDialog):
    def __init__(self, button, parent):
        super().__init__(parent)
        self.layout = QtWidgets.QVBoxLayout()
        self.button, self.parent = button, parent
        btn_name = button.objectName().title()
        current_shortcut = button.text()
        label_info = QtWidgets.QLabel(f'{btn_name} mouse button is currently assigned to "{current_shortcut}"')
        capture_btn = QtWidgets.QPushButton("Capture Shortcut from Keyboard")
        capture_btn.clicked.connect(lambda: self.get_shortcut())
        self.layout.addWidget(label_info)
        self.layout.addWidget(capture_btn)
        self.setLayout(self.layout)
        self.show()

    def get_shortcut(self):
        try:
            keys, valid, message = shortcut.get_key_combo()
        except shortcut.UndefinedKeyError as e:
            valid = False
            message = e.args[0].capitalize()
            keys = None

        btn, parent = self.button, self.parent
        if valid:
            btn.setText(keys)
            self.parent.conn.update_value("profiles", btn.objectName(), btn.text(), name=parent.current_mode_name)
            self.close()
        else:
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Information)
            if message:
                msg.setText(message)
            else:
                msg.setText(f"{keys} is not a valid combination.")
            msg.setWindowTitle("Not valid combination.")
            msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
            msg.exec_()


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    widget = CommandEditor()
    sys.exit(app.exec_())
