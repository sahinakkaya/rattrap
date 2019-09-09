import subprocess
import re
import sys
from collections import OrderedDict
from src.error_message_templates import *


class PermissionDeniedError(Exception):
    pass


class MouseIsOfflineError(Exception):
    pass


class NonValidPathError(Exception):
    pass


class UnknownRatslapError(Exception):
    pass


class Ratslap:
    defaults = OrderedDict({
        "f3": {'name': 'f3', 'color': 'cyan', 'rate': '500', 'dpi1': '500', 'dpi2': '(DEF) 1000',
               'dpi3': '1500', 'dpi4': '2500', 'dpi_shift': 'NOT SET', 'left': 'Button1', 'right': 'Button2',
               'middle': 'Button3', 'g4': 'Button6', 'g5': 'Button7', 'g6': 'LeftCtrl +', 'g7': 'LeftAlt +',
               'g8': 'ModeSwitch', 'g9': 'DPICycle'},
        "f4": {'name': 'f4', 'color': 'white', 'rate': '1000', 'dpi1': '500', 'dpi2': '(DEF) 1000',
               'dpi3': '1500', 'dpi4': '2500', 'dpi_shift': '500', 'left': 'Button1', 'right': 'Button2',
               'middle': 'Button3', 'g4': 'Button6', 'g5': 'Button7', 'g6': 'DPIDown', 'g7': 'DPIUp',
               'g8': 'ModeSwitch', 'g9': 'DPIShift'},
        "f5": {'name': 'f5', 'color': 'blue', 'rate': '500', 'dpi1': '(DEF) 1000', 'dpi2': '1000',
               'dpi3': '1000', 'dpi4': '1000', 'dpi_shift': 'NOT SET', 'left': 'Button1', 'right': 'Button2',
               'middle': 'Button3', 'g4': 'Button6', 'g5': 'Button7', 'g6': 'LeftCtrl + C',
               'g7': 'LeftCtrl + V', 'g8': 'ModeSwitch', 'g9': 'LeftCtrl + X'}})

    def __init__(self, path_to_ratslap, skip_test=False):
        self.path = path_to_ratslap
        if not skip_test:
            try:
                self.test_ratslap()
            except Exception as e:
                self.print_error_message(e)
                raise e

    def test_ratslap(self):
        try:
            process = subprocess.run([self.path, '-h'], capture_output=True, timeout=0.1)
            assert "Linux configuration tool for Logitech mice" in process.stdout.decode("utf-8")
        except Exception as e:
            raise NonValidPathError(e)
        else:
            process = subprocess.run([self.path, '-p', 'f3'], capture_output=True)
            if process.stderr:
                self.handle_stderr(process.stderr)

    @staticmethod
    def handle_stderr(stderr):
        stderr = stderr.decode("utf-8")
        permission_denied = re.search(r"libusb couldn't open USB device .*: Permission denied", stderr)
        mouse_is_offline = re.search(r"Failed to find Logitech G300s \(046d:c246\)", stderr)
        if permission_denied:
            raise PermissionDeniedError(permission_denied.group(0))
        elif mouse_is_offline:
            raise MouseIsOfflineError(mouse_is_offline.group(0))
        else:
            raise UnknownRatslapError(stderr)

    def run(self, arg, val=None, pretty=False):
        if self.path_is_valid():
            dash_num = len(arg)
            if val:
                process = subprocess.run([self.path, '-' * dash_num + arg, self.mode(val)],
                                         capture_output=True)
            else:
                process = subprocess.run([self.path, '-' * dash_num + arg], capture_output=True)
            if process.stderr:
                self.handle_stderr(process.stderr)

            output = process.stdout.decode("utf-8")
            if pretty:
                for line in output.splitlines()[4:]:
                    print(line)
            else:
                return process
        else:
            raise NonValidPathError

    def path_is_valid(self):
        try:
            process = subprocess.run([self.path, '-h'], capture_output=True, timeout=0.1)
            assert "Linux configuration tool for Logitech mice" in process.stdout.decode("utf-8")
        except Exception as e:
            print(e.args)
            return False
        else:
            return True

    @staticmethod
    def mode(val):
        val = str(val).lower()
        if val[0] == 'f':
            return val
        else:
            return f"f{val}"

    def pretty_run(self, arg, val=None):
        self.run(arg, val, True)

    def select_mode(self, mode_index=3, pretty=False):
        self.run('s', mode_index, pretty)

    def print_mode(self, mode_index=3):
        self.pretty_run('p', mode_index)

    def parse_mode(self, mode_index=3) -> dict:
        output = self.run("p", mode_index).stdout.decode("utf-8")
        mode = OrderedDict({"name": self.mode(mode_index)})
        normalized_options = {'Colour': 'color', 'Report Rate': 'rate', 'DPI #1': 'dpi1', 'DPI #2': 'dpi2',
                              'DPI #3': 'dpi3', 'DPI #4': 'dpi4', 'DPI Shift': 'dpi_shift',
                              'Left Click (But1)': 'left', 'Right Click (But2)': 'right',
                              'Middle Click (But3)': 'middle', 'G4': 'g4', 'G5': 'g5', 'G6': 'g6', 'G7': 'g7',
                              'G8': 'g8', 'G9': 'g9'}
        for line in output.splitlines()[7:-1]:
            option, value = map(str.strip, line.split(":", 1))
            mode[normalized_options[option]] = value

        return mode

    def modify(self, mode_index=3, **kwargs):
        distinct_options = self.get_difference(mode_index, **kwargs)
        distinct_options.pop("dpi_shift", None)  # Don't know how I even managed to change my dpi shift value
        if distinct_options:
            command = f"--modify {self.mode(mode_index)} "
            options = " ".join(
                [f"--{key} {''.join(distinct_options[key].split())}" for key in distinct_options])
            subprocess.run([self.path] + (command + options).split())

    def get_difference(self, mode, **kwargs):
        current_mode = self.parse_mode(mode)
        different_items = {}
        for key in kwargs:
            if kwargs[key] != current_mode[key]:
                different_items[key] = kwargs[key]

        return different_items

    def reset(self, mode):
        for mode_index in range(3, 6):
            if str(mode).lower() == 'all' or mode == mode_index:
                args = self.defaults[self.mode(mode_index)]
                self.modify(mode_index, **args)

    def get_valid(self, option):
        if option == "keys":
            return list(map(str.strip, self.run("li").stdout.decode("utf-8").splitlines()[5:]))

        output = self.run("h").stdout.decode("utf-8")
        for line in output.splitlines():
            if line.startswith(f"<{option}>"):
                raw = line.split(":", 1)[1].strip().replace(" or", ",")
                return raw.split(", ")

    def print_error_message(self, e):
        error = Error(e, self.path)
        print(error.get_full_error_message(), file=sys.stderr)


class Error:
    def __init__(self, e, path_to_ratslap):
        self.e = e
        self.path_to_ratslap = path_to_ratslap

    def get_name(self):
        error_name = self.e.__class__.__name__
        return " ".join(re.findall(r"[A-Z][^A-Z]*", error_name)[:-1])

    def get_full_error_message(self):
        return full_error_message.format(self.get_general_message(),
                                         self.get_original_error_message(),
                                         self.get_details(False))

    def get_general_message(self):
        return general_error_message.format(self.path_to_ratslap)

    def get_original_error_message(self):
        return original_error_message.format(self.e.args[0])

    def get_details(self, include_original_error_message=True):
        if include_original_error_message:
            error_message = self.get_original_error_message()
            error_message += "\n"
        else:
            error_message = ""
        if self.e.__class__.__name__ == "PermissionDeniedError":
            error_message += permission_denied_message
        elif self.e.__class__.__name__ == "MouseIsOfflineError":
            error_message += mouse_is_offline_message
        return error_message
