__all__ = ["TrayIcon"]


from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QSystemTrayIcon
from PyQt5.QtGui import QIcon


class TrayIcon(QSystemTrayIcon):
    def __init__(self, parent=None):
        super(TrayIcon, self).__init__(parent)
        self.is_show_window = True
        self.menu = QtWidgets.QMenu()
        self.show_hide_action = QtWidgets.QAction("隐藏主界面", self)
        self.quit_action = QtWidgets.QAction("退出", self)
        self.menu.addAction(self.show_hide_action)
        self.menu.addAction(self.quit_action)
        self.setContextMenu(self.menu)
        self.setIcon(QIcon(":/icons/icon.ico"))

        self._setup_event_connect()

    def _setup_event_connect(self):
        """
        注册/初始化各控件事件
        :return: None
        """
        self.show_hide_action.triggered.connect(self.show_hide_window)
        self.quit_action.triggered.connect(self.quit)
        self.activated.connect(self.iconClicked)
        self.messageClicked.connect(self.parent().show)

    def show_hide_window(self) -> None:
        """
        显示/隐藏主界面
        :return: None
        """
        if self.is_show_window:
            self.parent().hide()
            self.show_hide_action.setText("显示主界面")
        else:
            self.parent().show()
            self.show_hide_action.setText("隐藏主界面")

        self.is_show_window = not self.is_show_window

    def iconClicked(self, reason):
        """
        处理图标点击事件
        :param reason:
        :return: None
        """
        if reason in [2, 3]:
            self.parent().show()
            self.is_show_window = True
            self.show_hide_action.setText("隐藏主界面")
            if self.parent().isMaximized():
                self.parent().showMaximized()
            else:
                self.parent().showNormal()

    def quit(self):
        """
        处理点击图标退出按钮事件
        :return: None
        """
        if self.parent().close():
            self.setVisible(False)
