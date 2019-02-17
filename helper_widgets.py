from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication
from ui_command_editor import Ui_CommandEditor


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


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    widget = CommandEditor()
    sys.exit(app.exec_())
