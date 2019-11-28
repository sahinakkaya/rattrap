import os
import sys
import PyQt5.QtWidgets as QtWidgets
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import QThread, Qt, QSettings
from json import dump, loads
from time import sleep
import src.ratslap as ratslap
from src.db_helper import DBHelper, OperationalError
from src.helper_widgets import CommandEditor
from UI.ui_rattrap import Ui_Rattrap
from src.usb_detector import USBDetector


class RattrapWindow(QMainWindow, Ui_Rattrap):
    def __init__(self, path, app_name):
        super().__init__()
        self.setupUi(self)
        self.path = path
        self.app_name = app_name
        self.settings = QSettings("Asocia", self.app_name)
        self.ratslap_name = ratslap.RatSlap.name()
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

        # Enable widgets, set icons for them, create actions
        self.setup_ui_design()

        # Connect signals and slots
        self.setup_ui_logic()

        skip_test_for_ratslap = False
        self.permission_granted = True
        self.mouse_connected = True
        try:
            ratslap_path = self.conn.select("file_paths", ("path",), program_name="ratslap").fetchone()[0]
        except OperationalError:
            ratslap_path = self.get_ratslap_path()
        else:
            try:
                ratslap.RatSlap(ratslap_path, skip_test_for_ratslap)
            except ratslap.NonValidPathError:
                ratslap_path = self.get_new_path(ratslap_path)
            except ratslap.MouseIsOfflineError:
                self.mouse_connected = False
            except ratslap.PermissionDeniedError:
                self.permission_granted = False
            finally:
                skip_test_for_ratslap = True

        self.ratslap = ratslap.RatSlap(ratslap_path, skip_test_for_ratslap)
        setattr(self.ratslap, 'run', self.catch_exceptions(getattr(self.ratslap, 'run')))
        self.mode1.setChecked(True)
        self.current_mode_is_set = False
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
            except ratslap.PermissionDeniedError as e:
                self.handle_permission_denied_error(e)
                result = function(*args, **kwargs)
                self.permission_granted = True
            except ratslap.UnknownRatSlapError as e:
                # Maybe it's because computers are fast
                sleep(0.1)  # Let's wait a bit
                try:
                    result = function(*args, **kwargs)
                except Exception as e:
                    text = f"Error message was:\n{str(e)}\n{self.app_name} will now close."
                    self.exec_message_box("An error occured", text, icon_name="Critical")
                    self.quit()
                else:
                    print(f"An error was occurred but it's gone after 0.1 seconds; "
                          f"time heals everything :) \nIf you are curious, the error was:\n{e}")
            except Exception as e:
                text = f"Error message was:\n{str(e)}\n{self.app_name} will now close."
                self.exec_message_box("An error occurred", text, icon_name="Critical")
                self.quit()
            return result

        return wrapper

    def get_new_path(self, previous_path):
        text = f"The previous path to '{self.ratslap_name}' program: '{previous_path}' is unreachable. " \
            f"If you want to continue using {self.app_name} please specify the path to '{self.ratslap_name}'"
        self.exec_message_box(f"Unable to reach '{self.ratslap_name}'", text, icon_name="Warning")
        return self.get_ratslap_path()

    def setup_ui_design(self):
        self.setWindowTitle(self.app_name)
        self.resize(303, 477)
        self.move(QApplication.desktop().screen().rect().center() - self.rect().center())
        minimize_to_tray = self.settings.value("minimize_to_tray_when_closing", True, type=bool)
        self.action_minimize_to_tray.setChecked(minimize_to_tray)
        auto_start = self.settings.value("auto_start_on_boot", False, type=bool)
        auto_start_script_exists = os.path.exists(os.path.join(os.path.expanduser("~"),
                                                               f".config/autostart/{self.app_name}.desktop"))
        self.action_autostart.setChecked(auto_start and auto_start_script_exists)
        for widget in self.buttons + self.radio_buttons + [self.button_apply]:
            widget.setEnabled(True)

        self.set_icons_for_widgets()
        actions = {"show": f"Open {self.app_name}",
                   "hide": "Minimize to tray",
                   "quit": f"Quit {self.app_name}"}
        self.add_actions_to_tray(actions)
        self.tray_icon.show()

    def setup_ui_logic(self):
        self.bind_functions_to_buttons()
        self.connect_signals_and_slots_of_thread()
        self.bind_functions_to_actions()
        self.action_autostart.toggled.connect(self.create_or_remove_autostart_file)
        self.action_create_desktop_shortcut.triggered.connect(self.create_desktop_shortcut)

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
            title = f"Reset F{i}?"
            text = f"Do you want to reset profile F{i} to its defaults?"

            response = self.exec_message_box(title, text, ["No", "NoToAll", "YesToAll", "Yes"], "Question",
                                             special_buttons={"EscapeButton": 2, "DefaultButton": 4})
            if response == "YesToAll":
                self.ratslap.reset("all")
                self.conn.drop_table("profiles")
                self.set_current_mode()
                break
            elif response == "Yes":
                self.ratslap.reset(i)
                self.conn.delete_row("profiles", name=f"f{str(i)}")
                self.set_current_mode()
            elif response == "NoToAll":
                break

    def on_import(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Import from file", self.path,
                                                        f"All files (*);;{self.app_name} files (*.rat)",
                                                        f"{self.app_name} files (*.rat)")
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
                self.exec_message_box(title, text)
            caption = f"Select the path to the '{self.ratslap_name}' program..."
            path, _ = QtWidgets.QFileDialog.getOpenFileName(self, caption)
            if path:
                try:
                    ratslap.RatSlap(path)
                except ratslap.NonValidPathError:
                    first_try = False
                except (ratslap.MouseIsOfflineError,
                        ratslap.PermissionDeniedError,
                        ratslap.UnknownRatSlapError):
                    path_valid = True
                else:
                    path_valid = True

            else:
                exit()
        self.conn.drop_table("file_paths")
        self.conn.create_table("file_paths", ["program_name", "path"])
        self.conn.insert_values("file_paths", **{"program_name": "ratslap", "path": path})
        return path

    def connect_signals_and_slots_of_thread(self):
        self.usb_detector.mouse_state_changed.connect(self.toggle_ui_state)
        self.usb_detector.moveToThread(self.thread)
        self.thread.started.connect(self.usb_detector.work)

    def toggle_ui_state(self, mouse_online):
        self.mouse_connected = mouse_online
        mouse_offline_message_box = self.findChild(QtWidgets.QMessageBox, "mouse_offline_message_box")
        if mouse_online:
            self.tray_icon.setToolTip(f"{self.app_name}\nMouse is online")
            if mouse_offline_message_box is not None:
                mouse_offline_message_box.hide()
            if self.isVisible():
                try:
                    self.set_current_mode()
                    self.permission_granted = True
                    self.current_mode_is_set = True
                except ratslap.PermissionDeniedError:
                    self.permission_granted = False
                except ratslap.MouseIsOfflineError:
                    pass

        for radio_btn in self.radio_buttons:
            if not radio_btn.isChecked():
                radio_btn.setEnabled(mouse_online and self.permission_granted)

        for name in self.action_names:
            button = getattr(self, f"button_{name}")
            button.setEnabled(mouse_online and self.permission_granted)

        if mouse_online and self.isHidden():
            self.show_tray_message("Mouse connected")

        elif not mouse_online:
            self.tray_icon.setToolTip(f"{self.app_name}\nMouse is offline")
            if self.isVisible():
                text = f"Please plug in your Logitech G300s mouse to continue using {self.app_name}"
                if mouse_offline_message_box is not None:
                    mouse_offline_message_box.show()
                else:
                    self.exec_message_box("Failed to find Logitech G300s",
                                          text, ["Ok"], "Information", objectName="mouse_offline_message_box")
            else:
                if self.current_mode_is_set:
                    self.show_tray_message("Mouse disconnected")
                else:
                    self.show_tray_message("Failed to find Logitech G300s")

    def handle_permission_denied_error(self, e):
        self.permission_granted = False
        error = ratslap.Error(e, self.ratslap.path)
        title = error.get_name()
        text = "You do not have write access to the mouse."
        informative_text = f"Would you like {self.app_name} to help you with this?"
        details = error.get_full_error_message()
        response = self.exec_message_box(title, text, icon_name="Warning", button_names=["Yes", "No"],
                                         special_buttons={"DefaultButton": 1, "EscapeButton": 2},
                                         informativeText=informative_text, detailedText=details)
        if response == "Yes":
            file_name = "10-ratslap.rules"
            self.create_udev_rule_for_ratslap(file_name)
            self.prompt_user_to_move_the_file(file_name)
            self.exec_message_box("Replug your mouse", "If you have done with moving the file and reloading"
                                                       " the rules, plug out your mouse and replug it for "
                                                       "changes to take the effect.")

    def prompt_user_to_move_the_file(self, file_name):
        title = "Move the file and reload the rules"
        text = f'A file named "{file_name}" created under {self.path}\n\n' \
            f'Move it to the path: /etc/udev/rules.d/ \n' \
            f'and then reload udevadm rules.'
        informative_text = "If you don't know how to do it, press Show Details button."
        details = f"Run the command below on terminal and then press Ok\n\n" \
            f"sudo mv {self.get_path(file_name)} /etc/udev/rules.d && " \
            f"sudo udevadm control --reload-rules"
        self.exec_message_box(title, text, informativeText=informative_text, detailedText=details)

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

    def show_tray_message(self, message, title=None):
        if title is None:
            title = self.app_name
        self.tray_icon.showMessage(title, message, QIcon(self.get_path("images", "logo.png")), 1000)

    def exec_message_box(self, title, text, button_names=None, icon_name=None,
                         special_buttons=None, **kwargs):
        msg_box = QtWidgets.QMessageBox(self, **kwargs)
        if not button_names:
            button_names = ["Ok"]

        for button_name in button_names:
            try:
                msg_box.addButton(getattr(QtWidgets.QMessageBox, button_name))
            except AttributeError as e:
                print(e, file=sys.stderr)
        if icon_name:
            icon = getattr(QtWidgets.QMessageBox, icon_name)
        else:
            icon = QtWidgets.QMessageBox.Information
        msg_box.setIcon(icon)
        msg_box.setWindowTitle(title)
        msg_box.setText(text)
        if special_buttons is not None:
            for button_name, index in special_buttons.items():
                method = getattr(msg_box, f"set{button_name}")
                button = getattr(msg_box, button_names[index - 1])
                method(button)

        response = msg_box.exec()
        for button_name in button_names:
            if response == getattr(msg_box, button_name):
                return button_name

    def create_udev_rule_for_ratslap(self, file_name):
        with open(self.get_path(file_name), "w") as f:
            rule = 'DRIVER=="usb", ' \
                   'ATTR{idProduct}=="c246", ' \
                   'ATTR{idVendor}=="046d", ' \
                   'ATTR{product}=="G300s Optical Gaming Mouse", ' \
                   'MODE="0666", ' \
                   'GROUP="%s"' % (os.getenv("USER"))
            f.write(rule)

    def create_or_remove_autostart_file(self):
        path = self.get_path(os.path.expanduser("~"), ".config/autostart/")
        file_name = f"{self.app_name}.desktop"
        if self.action_autostart.isChecked():
            if os.path.exists(path):
                option = "--run-in-background"
                self.create_dot_desktop_file(file_name, path, f"Autostart {self.app_name} on startup", option)
            else:

                self.exec_message_box("Sorry", "We do not know how to perform this operation on your system.",
                                      icon_name="Information")
                self.action_autostart.setChecked(False)
        else:
            if os.path.exists(self.get_path(path, file_name)):
                os.remove(self.get_path(path, file_name))

    def create_desktop_shortcut(self):
        path = self.get_path(os.path.expanduser("~"), "Desktop")
        file_name = f"{self.app_name}.desktop"
        if os.path.exists(os.path.join(path, file_name)):
            self.exec_message_box("Info", "Desktop shortcut already exists")
        else:
            self.create_dot_desktop_file(file_name, path, f"Launch {self.app_name}")
            self.exec_message_box("Info",
                                  f"A file named {file_name} created on your desktop. "
                                  f"Right click on it and follow\n"
                                  f"Properties->Permissions->Allow executing file as program")

    def create_dot_desktop_file(self, file_name, path, comment, run_in_background=""):
        with open(os.path.join(path, file_name), "w") as f:
            f.write(f"[Desktop Entry]\n"
                    f"Version=1.0\n"
                    f"Type=Application\n"
                    f"Exec={sys.executable} {self.get_path('main.py')} {run_in_background}\n"
                    f"Hidden=false\n"
                    f"NoDisplay=false\n"
                    f"X-GNOME-Autostart-enabled=true\n"
                    f"Name[en]={self.app_name}\n"
                    f"Name={self.app_name}\n"
                    f"Comment[en]={comment}\n"
                    f"Comment={comment}\n"
                    f"Icon={self.get_path('images', 'logo.png')}\n")

    def save_settings(self):
        minimize_to_tray = self.action_minimize_to_tray.isChecked()
        self.settings.setValue("minimize_to_tray_when_closing", minimize_to_tray)

        auto_start = self.action_autostart.isChecked()
        self.settings.setValue("auto_start_on_boot", auto_start)
        self.settings.sync()

    def show(self):
        super().show()
        self.toggle_ui_state(self.mouse_connected)

    def _set_visible(self, visible):
        if visible:
            self.show()
        else:
            super().setVisible(False)

    def closeEvent(self, e):
        if not self.action_minimize_to_tray.isChecked():
            self.quit()
        else:
            e.ignore()
            self.hide()
            self.show_tray_message(f"{self.app_name} was minimized to tray")

    def quit(self):
        self.save_settings()
        self.conn.close()
        QtWidgets.qApp.quit()
