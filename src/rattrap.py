import os
import PyQt5.QtWidgets as QtWidgets
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import QThread, Qt
from json import dump, loads
import src.ratslap as ratslap
from src.db_helper import DBHelper, OperationalError
from src.helper_widgets import CommandEditor
from UI.ui_rattrap import Ui_Rattrap
from src.usb_detector import USBDetector


class RattrapWindow(QMainWindow, Ui_Rattrap):
    def __init__(self, path):
        super().__init__()
        self.setupUi(self)
        self.path = path
        self.current_mode_name = None
        self.conn = DBHelper(self.get_path("settings.db"))
        self.tray_icon = QtWidgets.QSystemTrayIcon(self)
        self.usb_detector = USBDetector()
        self.thread = QThread()

        # Grouping similar items together.
        self.radio_buttons = [getattr(self, f"mode{i}") for i in "123"]
        self.combo_boxes = [self.color, self.rate]
        self.unchangeable_items = [getattr(self, f"dpi{i}") for i in "1234"] + [self.dpi_shift]
        self.buttons = [self.right, self.middle, self.left]
        self.buttons.extend([getattr(self, f"g{str(i)}") for i in range(4, 10)])
        self.action_names = ["reset", "import", "export", "apply"]

        try:
            ratslap_path = self.conn.select("file_paths", ("path",), program_name="ratslap").fetchone()[0]

        except OperationalError:
            ratslap_path = self.get_ratslap_path()
        else:
            try:
                ratslap.Ratslap(ratslap_path)
            except ratslap.NonValidPathError:
                ratslap_path = self.get_new_path(ratslap_path)
        self.ratslap = ratslap.Ratslap(ratslap_path)
        setattr(self.ratslap, 'run', self.catch_exceptions(getattr(self.ratslap, 'run')))

        self.mode1.setChecked(True)
        self.set_current_mode()

        # Enable widgets, set icons for them, create actions
        self.setup_ui_design()

        # Connect signals and slots
        self.setup_ui_logic()

        self.thread.start()

    def get_path(self, *p):
        return os.path.join(self.path, *p)

    def catch_exceptions(self, function):
        def wrapper(*args, **kwargs):
            try:
                result = function(*args, **kwargs)
            except ratslap.NonValidPathError:
                self.ratslap.path = self.get_new_path(self.ratslap.path)
                result = function(*args, **kwargs)
            return result

        return wrapper

    def get_new_path(self, previous_path):
        text = f"The previous path to ratslap program: '{previous_path}' is unreachable. If you want to " \
            f"continue using Rattrap please specify the path to 'ratslap'"
        QtWidgets.QMessageBox.information(self, "Unable to reach 'ratslap'", text, QtWidgets.QMessageBox.Ok)
        return self.get_ratslap_path()

    def setup_ui_design(self):
        self.resize(303, 477)
        self.move(QApplication.desktop().screen().rect().center() - self.rect().center())

        for widget in self.buttons + self.radio_buttons + [self.button_apply]:
            widget.setEnabled(True)

        self.set_icons_for_widgets()
        actions = {"show": "Open Rattrap",
                   "hide": "Minimize to tray",
                   "quit": "Quit Rattrap"}
        self.add_actions_to_tray(actions)
        self.tray_icon.show()

    def setup_ui_logic(self):
        self.bind_functions_to_buttons()
        self.connect_signals_and_slots_of_thread()
        self.bind_functions_to_actions()

    def set_icons_for_widgets(self):
        for action_name in self.action_names:
            button = getattr(self, f"button_{action_name}")
            image_path = self.get_path("images", f"{action_name}_icon.png")
            icon = QIcon()
            icon.addPixmap(QPixmap(image_path))
            button.setIcon(icon)

        app_icon = QIcon(self.get_path("images", "logo.png"))
        self.tray_icon.setIcon(app_icon)
        self.setWindowIcon(app_icon)

    def add_actions_to_tray(self, actions):
        tray_menu = QtWidgets.QMenu(self, objectName="tray_menu")
        for action_name, desc in actions.items():
            action = QtWidgets.QAction(desc, self, objectName=action_name)
            tray_menu.addAction(action)

        self.tray_icon.setContextMenu(tray_menu)

    def bind_functions_to_buttons(self):
        for radio_btn in self.radio_buttons:
            radio_btn.clicked.connect(self.set_current_mode)
        for combo_box in self.combo_boxes:
            combo_box.currentTextChanged.connect(self.combo_box_changed)
        for button in self.buttons:
            button.clicked.connect(self.assign_shortcut)
        for name in self.action_names:
            button = getattr(self, f"button_{name}")
            function = getattr(self, f"on_{name}")
            button.clicked.connect(function)

    def bind_functions_to_actions(self):
        for action in self.tray_icon.contextMenu().actions():
            action_name = action.objectName()
            action.triggered.connect(getattr(self, action_name))

    def on_reset(self):
        for i in range(3, 6):
            msg_box = QtWidgets.QMessageBox
            title = f"Reset F{i}?"
            text = f"Do you want to reset profile F{i} to its defaults?"
            response = msg_box.question(self, title, text,
                                        msg_box.No | msg_box.NoToAll | msg_box.YesToAll | msg_box.Yes)
            if response == msg_box.YesToAll:
                self.ratslap.reset("all")
                self.conn.drop_table("profiles")
                self.set_current_mode()
                break
            elif response == msg_box.Yes:
                self.ratslap.reset(i)
                self.conn.delete_row("profiles", name=f"f{str(i)}")
                self.set_current_mode()
            elif response == msg_box.NoToAll:
                break

    def on_import(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Import from file")
        if path:
            with open(path) as f:
                for i in range(3, 6):
                    self.ratslap.modify(i, **loads(f.readline()))
                    self.conn.delete_row("profiles", name=f"f{str(i)}")
                    self.set_current_mode()

    def on_export(self):
        path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Export to a file")
        if path:
            with open(f"{path}.rat", "w") as f:
                for i in range(3, 6):
                    dump(self.ratslap.parse_mode(i), f)
                    f.write("\n")

    def on_apply(self):
        for mode in ["f3", "f4", "f5"]:
            data = self.conn.select("profiles", "*", name=mode).fetchone()
            if data:
                cols = self.conn.get_column_names("profiles")
                changes = dict(zip(cols, data))
                self.ratslap.modify(mode, **changes)

    def assign_shortcut(self):
        button = self.sender()
        command_editor = CommandEditor(button, self)
        command_editor.setWindowModality(Qt.ApplicationModal)
        command_editor.show()

    def get_ratslap_path(self):
        path_valid, first_try = False, True
        path = None
        while not path_valid:
            if not first_try:
                title = "Non valid path"
                text = "The path you specified is not valid. Try again"
                QtWidgets.QMessageBox.information(self, title, text, QtWidgets.QMessageBox.Ok)
            caption = "Select the path to the 'ratslap' program..."
            path, _ = QtWidgets.QFileDialog.getOpenFileName(self, caption)
            if path:
                try:
                    ratslap.Ratslap(path)
                except ratslap.NonValidPathError:
                    first_try = False
                else:
                    path_valid = True
                    self.conn.drop_table("file_paths")
                    self.conn.create_table("file_paths", ["program_name", "path"])
                    self.conn.insert_values("file_paths", **{"program_name": "ratslap", "path": path})
            else:
                exit()

        return path

    def connect_signals_and_slots_of_thread(self):
        self.usb_detector.mouse_state_changed.connect(self.toggle_ui_state)
        self.usb_detector.moveToThread(self.thread)
        self.thread.started.connect(self.usb_detector.work)

    def toggle_ui_state(self, mouse_online):
        for radio_btn in self.radio_buttons:
            if not radio_btn.isChecked():
                radio_btn.setEnabled(mouse_online)

        for name in self.action_names:
            button = getattr(self, f"button_{name}")
            button.setEnabled(mouse_online)

        text = "Please plug in your Logitech G300s mouse to continue using Rattrap"
        mouse_offline_message_box = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information,
                                                          "Unable to reach mouse",
                                                          text, QtWidgets.QMessageBox.Ok,
                                                          self)
        if mouse_online:
            if self.isHidden():
                self.show_tray_message("Mouse connected")
            mouse_offline_message_box.hide()
        else:
            if self.isVisible():
                mouse_offline_message_box.show()
            else:
                self.show_tray_message("Mouse disconnected")

    def set_current_mode(self):
        current_mode_index = [i.isChecked() for i in self.radio_buttons].index(True) + 3
        self.current_mode_name = "f" + str(current_mode_index)  # f3, f4 or f5
        self.ratslap.select_mode(self.current_mode_name)
        current_mode = self.get_mode(self.current_mode_name)

        for item in self.combo_boxes + self.unchangeable_items + self.buttons:
            name = item.objectName()
            try:
                item.setText(current_mode[name])
            except AttributeError:
                item.setCurrentText(current_mode[name].title())

    def combo_box_changed(self, value):
        property_name = self.sender().objectName()
        self.conn.update_value("profiles", property_name, value.lower(), name=self.current_mode_name)

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

    def show_tray_message(self, message, title="Rattrap"):
        self.tray_icon.showMessage(title, message, QIcon(self.get_path("images", "logo.png")), 1000)

    def closeEvent(self, e):
        e.ignore()
        self.hide()
        self.show_tray_message("Rattrap was minimized to tray")

    def quit(self):
        self.conn.close()
        QtWidgets.qApp.quit()
