import sys
from PyQt5.QtWidgets import QApplication
from src.rattrap import RattrapWindow
from src.ratslap import PermissionDeniedError

# TODO: Add functionality to manually set shortcuts
# TODO: Make color selection more visual with actual colors
        

if __name__ == '__main__':
    app = QApplication(sys.argv)
    try:
        main_window = RattrapWindow()
        sys.exit(app.exec_())
    except PermissionDeniedError:
        pass
    except Exception as e:
        print(e)
        exit(-1)
