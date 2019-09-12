import sys
import os
from src.single_qapplication import SingleQApplication
from src.rattrap import RattrapWindow

# TODO: Add functionality to manually set shortcuts
# TODO: Make color selection more visual with actual colors
# FIXME: Switch to last edited mode when mouse is replugged
# FIXME: Enable ok button in command editor when entered "assign manually" mode

if __name__ == '__main__':
    app_name = "RatTrap"
    script_dir = os.path.dirname(__file__)
    app = SingleQApplication(sys.argv, app_name)
    main_window = RattrapWindow(script_dir, app_name)
    app.visibility_changed.connect(main_window._set_visible)
    app.send_message(app.visibility)
    sys.exit(app.exec_())
