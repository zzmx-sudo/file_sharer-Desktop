import sys

from PyQt5.QtWidgets import QMainWindow
from PyQt5.Qt import QApplication

from static.ui.main_ui import Ui_MainWindow

class MainWindow(QMainWindow):

    def __init__(self) -> None:
        super(MainWindow, self).__init__()

        # load ui
        from utils.ui_function import UiFunction
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # setup ui_function
        ui_function = UiFunction(self)
        ui_function.setup()

        # event connect

        # show window
        self.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())