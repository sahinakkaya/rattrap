from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication
from ui_command_editor import Ui_CommandEditor
import event_handler


class CommandEditor(QtWidgets.QDialog, Ui_CommandEditor):
    def __init__(self, button, parent):
        super().__init__(parent)
        self.setupUi(self)
        self.button = button
        self.bind_widgets()
        self.show()

    def bind_widgets(self):
        self.pushButton.setText(self.button.text())
        self.pushButton.clicked.connect(self.update_shortcut_label)
        self.buttons_specials_field.setItemText(0, self.button.text())
        self.buttons_specials_field.currentTextChanged.connect(self.update_shortcut_label)

        self.btn_ok.clicked.connect(self.register_shortcut)
        self.btn_cancel.clicked.connect(self.close)

    def update_shortcut_label(self):
        e = event_handler.EventList(self.parent().ratslap.parse_mode(3))
        e.get_events()
        shortcut = e.create_shortcut_from_events()
        if len(shortcut.string) > 0:
            self.current_shortcut.setText(shortcut.string)
            self.pushButton.setText(shortcut.string)
            self.btn_ok.setEnabled(shortcut.valid)
            self.pushButton.setStyleSheet("")
            if not shortcut.valid:
                self.pushButton.setStyleSheet("background-color: rgb(255, 0, 4);")

        # self.current_shortcut.setText(self.buttons_specials_field.currentText())

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
