__all__ = ["TrayIcon"]


from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QSystemTrayIcon
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt

from model.public_types import ThemeColor as themeColor
from settings import settings


class TrayIcon(QSystemTrayIcon):
    def __init__(self, parent=None):
        """
        系统托盘图标类初始化函数

        Args:
            parent: 主程序窗口对象
        """
        super(TrayIcon, self).__init__(parent)
        self._main_window = parent
        self.is_show_window = True
        self.menu = QtWidgets.QMenu()
        self.rich_share_action = QtWidgets.QAction("打开所有分享", self)
        self.poor_share_action = QtWidgets.QAction("关闭所有分享", self)
        self.show_hide_action = QtWidgets.QAction("隐藏主界面", self)
        self.quit_action = QtWidgets.QAction("退出", self)
        self.menu.addAction(self.rich_share_action)
        self.menu.addAction(self.poor_share_action)
        self.menu.addSeparator()
        self.menu.addAction(self.show_hide_action)
        self.menu.addAction(self.quit_action)
        self.setContextMenu(self.menu)
        self.setIcon(QIcon(":/icons/icon.ico"))

        self.menu.setStyleSheet(self.styleSheet())
        self.menu.setWindowFlag(Qt.FramelessWindowHint)
        self.menu.setAttribute(Qt.WA_TranslucentBackground, True)
        self._setup_event_connect()

    def _setup_event_connect(self) -> None:
        self.rich_share_action.triggered.connect(
            lambda: self._main_window.open_all_share()
        )
        self.poor_share_action.triggered.connect(
            lambda: self._main_window.close_all_share()
        )
        self.show_hide_action.triggered.connect(lambda: self.show_hide_window())
        self.quit_action.triggered.connect(lambda: self.quit())
        self.activated.connect(self.iconClicked)
        self.messageClicked.connect(lambda: self.parent().show())

    def show_hide_window(self) -> None:
        """
        显示/隐藏主界面

        Returns:
            None
        """
        if self.is_show_window:
            self.parent().hide()
            self.show_hide_action.setText("显示主界面")
        else:
            self.parent().show()
            self.show_hide_action.setText("隐藏主界面")

        self.is_show_window = not self.is_show_window

    def iconClicked(self, reason) -> None:
        """
        处理图标点击事件

        Args:
            reason: 点击携带的参数对象

        Returns:
            None
        """
        if reason in [2, 3]:
            self.parent().show()
            self.is_show_window = True
            self.show_hide_action.setText("隐藏主界面")
            if self._main_window.isMaximized():
                self._main_window.showMaximized()
            else:
                self._main_window.showNormal()

    def quit(self) -> None:
        """
        处理点击图标退出按钮事件

        Returns:
            None
        """
        if self._main_window.close():
            self.setVisible(False)

    def resetStyleSheet(self, theme_color: themeColor = settings.THEME_COLOR) -> None:
        """
        重置/修改样式

        Args:
            theme_color: 主题颜色

        Returns:
            None
        """
        self.menu.setStyleSheet(self.styleSheet(theme_color))

    def styleSheet(self, theme_color: themeColor = settings.THEME_COLOR) -> str:
        """
        全局样式表

        Args:
            theme_color: 主题颜色

        Returns:
            str: 全局样式表
        """
        control_color = settings.controlColor(theme_color)
        return f"""
        * {{
            margin: 0;
            padding: 0;
            font-size: 14px;
            background-position: center;
            background-repeat: no-reperat;
            border: none;
            color: rgb(0, 0, 0)
        }}

        QMenu {{
            background-color: rgb({control_color.BaseBgColor});
            padding: 5px;
            border-radius: 10px
        }}

        QMenu::item {{
            padding: 8px 24px;
            background-color: transparent;
        }}

        QMenu::item::selected {{
            background-color: rgb({control_color.BaseColor});
            color: rgb({control_color.SpecialHovColor})
        }}

        QMenu::separator {{
            height: 2px;
            background-color: rgb({control_color.LightBgColor});
            margin: 5px 0px;
            broder-radius: 10%;
        }}
        """
