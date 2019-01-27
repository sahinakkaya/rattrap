from PyQt5 import QtWidgets

import ratslap
import shortcut
from db_helper import DBHelper, sql  # Change this later
from ui_rattrap import Ui_Rattrap


class WTFException(Exception):
    pass


class RattrapWindow(QtWidgets.QMainWindow, Ui_Rattrap):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.resize(356, 456)
        self.setWindowTitle("Rattrap")
        self.current_mode_name = None

        self.radio_buttons = [i for i in [getattr(self, "radiobtn_mode" + i) for i in "123"]]
        for radio_btn in self.radio_buttons:
            radio_btn.clicked.connect(self.set_current_mode)
        self.radiobtn_mode1.setChecked(True)

        self.color.currentTextChanged.connect(self.color_changed)

        self.not_changeable_items = [getattr(self, "dpi" + i) for i in "1234"] + [self.rate] + [self.dpi_shift]
        print(self.not_changeable_items)
        self.buttons = [self.right, self.middle, self.left]
        self.buttons.extend([getattr(self, "g" + str(i)) for i in range(4, 10)])
        for button in self.buttons:
            button.clicked.connect(self.assign_shortcut)

        self.button_apply.clicked.connect(self.apply_changes)

        self.shortcut_labels = [self.label_left, self.label_right, self.label_middle]
        self.shortcut_labels.extend([getattr(self, "label_g" + str(i)) for i in range(4, 10)])
        self.conn = DBHelper("settings.db")
        self.show()
        try:
            ratslap_path = self.conn.select("file_paths", ("path",), program_name="ratslap").fetchone()[0]
        except sql.OperationalError:
            ratslap_path = self.get_ratslap_path()
        self.ratslap = ratslap.Ratslap(ratslap_path)
        for widget in self.buttons + self.radio_buttons + [self.button_apply]:
            widget.setEnabled(True)
        self.set_current_mode()

    def get_ratslap_path(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select the path to the 'ratslap' program...")
        if path:
            self.conn.create_table("file_paths", ["program_name", "path"])
            self.conn.insert_values("file_paths", **{"program_name": "ratslap", "path": path})
            return path

    def set_current_mode(self):
        self.current_mode_name = "f" + str([i.isChecked() for i in self.radio_buttons].index(True) + 3)  # f3, f4 or f5
        current_mode = self.get_mode(self.current_mode_name)
        self.color.setCurrentText(current_mode["color"].title())
        for key in current_mode:
            for item in self.buttons + self.not_changeable_items:
                if item.objectName() == key:
                    item.setText(current_mode[key])

    def color_changed(self, color):
        self.conn.update_value("profiles", "color", color.lower(), name=self.current_mode_name)

    def assign_shortcut(self):
        button = self.sender()
        widget = AssignShortcutWidget(button, self)
        x, y = self.pos().x(), self.pos().y()
        widget.move(x + 20, y + 10)
        widget.resize(50, 50)

    def apply_changes(self):
        for mode in ["f3", "f4", "f5"]:
            data = self.conn.select("profiles", "*", name=mode).fetchone()
            if data:
                cols = self.conn.get_column_names("profiles")
                changes = dict(zip(cols, data))
                self.ratslap.modify(mode, **changes)

    def get_mode(self, mode):
        column_names = self.conn.get_column_names("defaults")
        self.conn.create_table("profiles", column_names)
        data = self.conn.select("profiles", "*", name=mode).fetchone()
        if data:
            return dict(zip(column_names, data))
        else:
            profile = self.ratslap.parse_mode(mode)
            self.conn.insert_values("profiles", **profile)
            return self.get_mode(mode)

    def closeEvent(self, e):
        self.conn.close()
        super(RattrapWindow, self).closeEvent(e)


class AssignShortcutWidget(QtWidgets.QDialog):
    def __init__(self, button, parent: RattrapWindow):
        super().__init__(parent)
        self.layout = QtWidgets.QVBoxLayout()
        self.button, self.parent = button, parent
        btn_name = button.objectName().title()
        current_shortcut = button.text()
        label_info = QtWidgets.QLabel(f'{btn_name} mouse button is currently assigned to "{current_shortcut}"')
        btn = QtWidgets.QPushButton("Capture Shortcut from Keyboard")
        btn.clicked.connect(lambda: self.get_shortcut())
        self.layout.addWidget(label_info)
        self.layout.addWidget(btn)
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
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    main_window = RattrapWindow()
    sys.exit(app.exec_())
