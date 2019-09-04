import PyQt5.QtWidgets as QtWidgets
from UI.ui_command_editor import Ui_CommandEditor
from . import event_handler


class CommandEditor(QtWidgets.QDialog, Ui_CommandEditor):
    def __init__(self, button, parent):
        super().__init__(parent)
        self.setupUi(self)
        self.button = button
        self.pushButton.setText(self.button.text())
        self.setup_ui_logic()

    def setup_ui_logic(self):
        self.pushButton.clicked.connect(self.update_shortcut_label)
        self.buttons_specials_field.setItemText(0, self.button.text())
        self.buttons_specials_field.currentTextChanged.connect(self.update_shortcut_label)

        self.btn_ok.clicked.connect(self.register_shortcut)
        self.btn_cancel.clicked.connect(self.close)

    def update_shortcut_label(self):
        parent = self.parent()
        if self.sender().objectName() == "pushButton":
            e = event_handler.EventList(parent.ratslap.parse_mode(parent.current_mode_name))
            e.get_events()
            shortcut = e.create_shortcut_from_events()
            if len(shortcut.string) > 0:
                self.current_shortcut.setText(shortcut.string)
                self.pushButton.setText(shortcut.string)
                self.btn_ok.setEnabled(shortcut.valid)  # FIXME: Also check if user is trying to assign manually
                self.pushButton.setStyleSheet("")
                if not shortcut.valid:
                    self.pushButton.setStyleSheet("background-color: rgb(255, 0, 4);")

        else:
            self.current_shortcut.setText(self.buttons_specials_field.currentText())

    def register_shortcut(self):
        new_shortcut = self.current_shortcut.text()
        if new_shortcut != "":
            self.button.setText(new_shortcut)
            self.parent().conn.update_value(
                "profiles", self.button.objectName(), new_shortcut, name=self.parent().current_mode_name)
        self.close()
