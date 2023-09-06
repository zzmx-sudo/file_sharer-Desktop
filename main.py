import os
import sys

from PyQt5.QtWidgets import QMainWindow
from PyQt5.Qt import QApplication
from PyQt5.uic import loadUi

from static.ui.main_ui import Ui_MainWindow
from settings import settings

class MainWindow(QMainWindow):

    def __init__(self) -> None:
        super(MainWindow, self).__init__()

        # load ui
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        # ui_path = os.path.join(settings.BASE_DIR, "static", "ui", "main.ui")
        # self.ui = loadUi(ui_path)

        # setup ui_function
        from utils.ui_function import UiFunction
        ui_function = UiFunction(self)
        # ui_function = UiFunction(self.ui)
        ui_function.setup()

        # event connect

        # show window
        self.show()
        # self.ui.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())