import sys
from PyQt5.QtWidgets import QApplication
from src.rattrap import RattrapWindow

# TODO: Add functionality to manually set shortcuts
# TODO: Make color selection more visual with actual colors
        



if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = RattrapWindow()
    sys.exit(app.exec_())
