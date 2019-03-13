import sys
from PyQt5.QtWidgets import QApplication
from src.rattrap import RattrapWindow

if __name__ == '__main__':
    app = QApplication(sys.argv)
    try:
        main_window = RattrapWindow()
    except Exception as e:
        print(e)
        sys.exit(-1)
    sys.exit(app.exec_())
