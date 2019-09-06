import sys
import os
from PyQt5.QtWidgets import QApplication
from src.rattrap import RattrapWindow
from src.ratslap import PermissionDeniedError, MouseIsOfflineError

# TODO: Add functionality to manually set shortcuts
# TODO: Make color selection more visual with actual colors
# FIXME: Switch to last edited mode when mouse is replugged
# FIXME: Enable ok button in command editor when entered "assign manually" mode

if __name__ == '__main__':
    app = QApplication(sys.argv)
    script_dir = os.path.dirname(__file__)
    try:
        main_window = RattrapWindow(script_dir)
        sys.exit(app.exec_())
    except (PermissionDeniedError, MouseIsOfflineError):
        pass
