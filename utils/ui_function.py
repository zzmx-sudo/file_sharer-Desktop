__all__ = [
    "UiFunction"
]

import webbrowser
from typing import Union

from PyQt5 import QtWidgets
from PyQt5.QtCore import (
    QPropertyAnimation, QEasingCurve, Qt, QEvent, QPoint
)
from PyQt5.Qt import QPushButton, QMessageBox, QTableWidget
from PyQt5.QtGui import QMouseEvent
import pyperclip as clip

from main import MainWindow
from . custom_grips import CustomGrip

class UiFunction:

    def __init__(self, window: MainWindow) -> None:

        self._main_window = window
        # self._elements = self._main_window.ui
        self._elements = self._main_window
        self._maximize_flag: bool = False
        self._dragPos: Union[QPoint, None] = None
        self._select_menu_style = """
        border-left: 3px solid #409eff; background-color: rgb(246, 246, 246);
        """
        self._select_setting_style = """
        border: 2px solid #409eff;background-color: #ffffff;
        """
        self._messageBox_normal_style = """
        QMessageBox {background-color: rgb(236, 236, 236); border: 1px solid #409eff; border-radius: 10%;}
        QLabel {border: none; font-size: 14px;}
        QMessageBox QPushButton {width: 60px; height: 40px; border-radius: 10px;}
        """
        self._left_grip = CustomGrip(self._main_window, Qt.LeftEdge)
        self._right_grip = CustomGrip(self._main_window, Qt.RightEdge)
        self._top_grip = CustomGrip(self._main_window, Qt.TopEdge)
        self._bottom_grip = CustomGrip(self._main_window, Qt.BottomEdge)

    def setup(self) -> None:
        # main window event connect
        self._main_window.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self._main_window.mousePressEvent = self._mousePressEvent
        self._main_window.resizeEvent = self._resize_grips
        # elements event connect
        self._setup_event_connect()
        # main window scale

    def _setup_event_connect(self) -> None:
        # window element
        self._elements.minimizeButton.clicked.connect(lambda: self._main_window.showMinimized())
        self._elements.maximizeRestoreButton.clicked.connect(lambda : self._maximize_restore())
        self._elements.closeAppButton.clicked.connect(lambda: self._main_window.close())
        # left menu element
        self._elements.homeButton.clicked.connect(self._menu_button_clicked)
        self._elements.serverButton.clicked.connect(self._menu_button_clicked)
        self._elements.clientButton.clicked.connect(self._menu_button_clicked)
        self._elements.downloadButton.clicked.connect(self._menu_button_clicked)
        self._elements.settingButton.clicked.connect(lambda: self._extra_setting())
        # extra element
        self._elements.shareProjectButton.clicked.connect(lambda : self._save_share_msg())
        self._elements.browseProjectButton.clicked.connect(lambda: self._open_project_code())
        self._elements.closeSettingButton.clicked.connect(lambda : self._extra_setting())
        # content element
        self._elements.contentTopBox.mouseDoubleClickEvent = self._contentTopDpubleClicked
        self._elements.contentTopBox.mouseMoveEvent = self._moveWindow
        # self._elements.shareListTable.verticalHeader().setVisible(False)

    def _maximize_restore(self) -> None:
        maximize_image = "background-image: url(:/icons/images/icon/maximize.png);"
        restore_image = "background-image: url(:/icons/images/icon/restore.png);"
        if not self._maximize_flag:
            self._main_window.showMaximized()
            self._maximize_flag = True
            self._elements.maximizeRestoreButton.setToolTip("缩放窗口")
            self._elements.maximizeRestoreButton.setStyleSheet(
                self._elements.maximizeRestoreButton.styleSheet().replace(maximize_image, restore_image)
            )
        else:
            self._main_window.showNormal()
            self._maximize_flag = False
            self._elements.maximizeRestoreButton.setToolTip("窗口全屏")
            self._elements.maximizeRestoreButton.setStyleSheet(
                self._elements.maximizeRestoreButton.styleSheet().replace(restore_image, maximize_image)
            )

    def _save_share_msg(self):
        msg = "我正在使用file-sharer分享/下载文件, 快一起来玩玩吧, 下载地址: https://github.com/zzmx-sudo/file_sharer-LAN"
        clip.copy(msg)

        self._show_info_messageBox("复制成功, 快发送给小伙伴吧^_^")

    def _open_project_code(self):

        webbrowser.open_new_tab("https://github.com/zzmx-sudo/file_sharer-LAN")

    def _extra_setting(self) -> None:
        style = self._elements.settingButton.styleSheet()
        width = self._elements.extraBox.width()
        maxExtend = 200
        minExtend = 0

        if width == minExtend:
            widthExtended = maxExtend
            self._elements.settingButton.setStyleSheet(style + self._select_setting_style)
        else:
            self._elements.settingButton.setStyleSheet(style.replace(self._select_setting_style, ""))
            widthExtended = minExtend

        self.animation = QPropertyAnimation(self._elements.extraBox, b"minimumWidth")
        self.animation.setDuration(500)
        self.animation.setStartValue(width)
        self.animation.setEndValue(widthExtended)
        self.animation.setEasingCurve(QEasingCurve.InOutQuart)
        self.animation.start()

    def _mousePressEvent(self, event: QMouseEvent) -> None:

        self._dragPos = event.globalPos()

    def _contentTopDpubleClicked(self, event: QMouseEvent) -> None:

        if event.type() == QEvent.MouseButtonDblClick and event.buttons() == Qt.LeftButton:
            self._maximize_restore()

    def _moveWindow(self, event: QMouseEvent) -> None:

        if self._maximize_flag:
            self._maximize_restore()

        if event.buttons() == Qt.LeftButton:
            self._main_window.move(self._main_window.pos() + event.globalPos() - self._dragPos)
            self._dragPos = event.globalPos()
            event.accept()

    def _menu_button_clicked(self) -> None:

        button = self._main_window.sender()
        menu_button_name = button.objectName()

        if menu_button_name == "serverButton":
            stack_widget = self._elements.server
        elif menu_button_name == "clientButton":
            stack_widget = self._elements.client
        elif menu_button_name == "downloadButton":
            stack_widget = self._elements.download
        else:
            stack_widget = self._elements.home

        self._elements.stackedWidget.setCurrentWidget(stack_widget)
        self._reset_menu_handler(menu_button_name)
        button.setStyleSheet(self._select_menu(button.styleSheet()))

    def _select_menu(self, origin_style: str) -> str:
        newStyle = origin_style + self._select_menu_style

        return newStyle

    def _deselect_menu(self, origin_style: str) -> str:
        newStyle = origin_style.replace(self._select_menu_style, "")

        return newStyle

    def _select_menu_handler(self, menu_button_name: str) -> None:

        for button in self._elements.leftTopBox.findChildren(QPushButton):
            if button.objectName() == menu_button_name:
                button.setStyleSheet(self._select_menu(button.styleSheet()))

    def _reset_menu_handler(self, menu_button_name: str) -> None:

        for button in self._elements.leftTopBox.findChildren(QPushButton):
            if button.objectName() != menu_button_name:
                button.setStyleSheet(self._deselect_menu(button.styleSheet()))

    def _resize_grips(self, event: QMouseEvent) -> None:
        self._left_grip.setGeometry(0, 10, 10, self._main_window.height())
        self._right_grip.setGeometry(self._main_window.width() - 10, 10, 10, self._main_window.height())
        self._top_grip.setGeometry(0, 0, self._main_window.width(), 10)
        self._bottom_grip.setGeometry(0, self._main_window.height() - 10, self._main_window.width(), 10)

    def _move_center(self) -> None:
        screen = QtWidgets.QDesktopWidget().screenGeometry()
        window = self._main_window.geometry()

        self._main_window.move(
            (screen.width() - window.width()) / 2,
            (screen.height() - window.height()) / 2
        )

    def _show_info_messageBox(self, msg: str, title: Union[str, None] = None) -> None:
        if title is None:
            title = "消息提示"
        info = QMessageBox(
            QMessageBox.Information,
            title, msg,
            QMessageBox.Ok,
            parent=self._main_window
        )
        info.setStyleSheet(self._messageBox_normal_style + """
            QMessageBox QPushButton {
                border: 1px solid #409eff;
            }
            QMessageBox QPushButton:hover {
                background-color: #ffffff;
            }
        """)
        info.exec_()