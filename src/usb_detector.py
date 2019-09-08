from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
import pyudev
import subprocess


class USBDetector(QObject):
    mouse_state_changed = pyqtSignal(bool)

    def __init__(self):
        super(USBDetector, self).__init__()
        self.mouse_online = False
        self.context = pyudev.Context()
        self.monitor = pyudev.Monitor.from_netlink(self.context)
        self.monitor.filter_by(subsystem="usb")

    @pyqtSlot()
    def work(self):
        self.mouse_online = self.is_mouse_online()
        self.emit_signal()

        self.monitor.start()
        for device in iter(self.monitor.poll, None):
            if device.action in ("bind", "remove"):
                if self.is_mouse_state_changed():
                    self.mouse_online = not self.mouse_online
                    self.emit_signal()

    def emit_signal(self):
        self.mouse_state_changed.emit(self.mouse_online)

    def is_mouse_online(self):
        p = subprocess.run(["lsusb"], capture_output=True)
        output = p.stdout.decode("utf-8")
        return "ID 046d:c246 Logitech, Inc. Gaming Mouse G300" in output

    def is_mouse_state_changed(self):
        return self.is_mouse_online() != self.mouse_online


if __name__ == '__main__':
    from PyQt5.QtCore import QThread
    from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QGridLayout

    import sys


    class Widget(QWidget):

        def __init__(self):
            super().__init__()
            self.label = QLabel("")

            self.usb_detector = USBDetector()
            self.thread = QThread()
            self.usb_detector.mouse_state_changed.connect(self.on_mouse_state_changed)
            self.usb_detector.moveToThread(self.thread)
            self.thread.started.connect(self.usb_detector.work)
            self.thread.start()
            self.initUI()

        def initUI(self):
            grid = QGridLayout()
            self.setLayout(grid)
            grid.addWidget(self.label, 0, 0)

            self.move(300, 150)
            self.setMinimumSize(300, 100)
            self.setWindowTitle('USB Detector Test')
            self.show()

        def on_mouse_state_changed(self, mouse_is_online):
            if mouse_is_online:
                self.label.setText("Online")
            else:
                self.label.setText("Offline")


    app = QApplication(sys.argv)

    widget = Widget()

    sys.exit(app.exec_())
