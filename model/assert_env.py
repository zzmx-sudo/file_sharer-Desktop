import os
from typing import Tuple

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QDialog
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtCore import QPropertyAnimation, QEasingCurve

from settings import settings
from .public_types import VerifyStatus
from utils.public_func import get_config_from_toml


class AssertThread(QThread):
    single = pyqtSignal(tuple)

    def __init__(self):
        super(AssertThread, self).__init__()

    def run(self) -> None:
        # verify pyproject.toml
        self._verify_pyproject_toml()
        # verify local ip
        if not settings.LOCAL_HOST:
            self.single.emit((VerifyStatus.FATAL, "获取本机IP失败, 请确认本机网络正常后再打开"))
            return
        elif settings.LOCAL_HOST == "127.0.0.1":
            self.single.emit((VerifyStatus.WARN, "未发现可与他人通信IP地址, 分享或下载对象仅限本机"))

        self.single.emit((VerifyStatus.INFO, f"本机IP: {settings.LOCAL_HOST}"))
        self.single.emit((VerifyStatus.DONE, "校验完成, 点击按钮后进入"))

    def _verify_pyproject_toml(self):
        """
        校验pyproject.toml文件内容
        :return:
        """
        if not get_config_from_toml():
            self.single.emit((VerifyStatus.WARN, "pyproject.toml文件不存在或损坏, 将使用默认配置"))

        self.single.emit(
            (VerifyStatus.INFO, f"日志路径: {settings.LOGS_PATH}, 如需修改请在设置中配置, 保存后生效")
        )
        self.single.emit(
            (VerifyStatus.INFO, f"下载路径: {settings.DOWNLOAD_DIR}, 如需修改请在设置中配置, 保存后生效")
        )
        self.single.emit((VerifyStatus.INFO, f"预使用HTTP端口: {settings.WSGI_PORT}, 请勿占用"))
        self.single.emit((VerifyStatus.INFO, f"当前使用主题: {settings.THEME_COLOR}"))
        self.single.emit((VerifyStatus.INFO, f"当前使用透明度: {settings.THEME_OPACITY}%"))


class AssertEnvWindow(QDialog):
    all_safe = pyqtSignal()

    def __init__(self):
        super(AssertEnvWindow, self).__init__()
        self.resize(400, 300)
        self.setStyleSheet(self.styleSheet)
        self.verticalLayout = QtWidgets.QVBoxLayout(self)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(5)
        self.verticalLayout.setObjectName("verticalLayout")
        self.text_edit = QtWidgets.QTextEdit(self)
        self.text_edit.setObjectName("text_edit")
        self.verticalLayout.addWidget(self.text_edit)
        self.buttonFrame = QtWidgets.QFrame(self)
        self.buttonFrame.setMinimumSize(QtCore.QSize(0, 40))
        self.buttonFrame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.buttonFrame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.buttonFrame.setObjectName("buttonFrame")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.buttonFrame)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 5)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtWidgets.QSpacerItem(
            281, 0, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum
        )
        self.horizontalLayout.addItem(spacerItem)
        self.button = QtWidgets.QPushButton(self.buttonFrame)
        self.button.setMinimumSize(QtCore.QSize(80, 0))
        self.button.setMaximumSize(QtCore.QSize(16777215, 0))
        self.button.setObjectName("button")
        self.horizontalLayout.addWidget(self.button)
        spacerItem1 = QtWidgets.QSpacerItem(
            280, 0, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum
        )
        self.horizontalLayout.addItem(spacerItem1)
        self.verticalLayout.addWidget(self.buttonFrame)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.assert_thread = None
        self._all_safe = True

        self.show()
        self._verify()

    def _verify(self):
        """
        开启线程校验各类环境参数
        :return: None
        """
        self.assert_thread = AssertThread()
        self.assert_thread.single.connect(self._append_text_edit)
        self.assert_thread.start()

    def _append_text_edit(self, verify_res: Tuple[VerifyStatus, str]) -> None:
        """
        将校验结果追加到text_edit
        :param verify_res: 校验结果
        :return: None
        """
        status, msg = verify_res
        if status is VerifyStatus.INFO:
            self.text_edit.append(self._info_message_format(msg))
        elif status is VerifyStatus.WARN:
            self.text_edit.append(self._warn_message_format(msg))
        elif status is VerifyStatus.FATAL:
            self._all_safe = False
            self.text_edit.append(self._fatal_message_format(msg))
            self.button.setText("确认并退出")
            self._show_button()
            self.button.clicked.connect(lambda: self._quit_app())
        else:
            self.text_edit.append(self._info_message_format(msg))
            self.button.setText("点击进入")
            self._show_button()
            self.button.clicked.connect(lambda: self._enter_mainWindow())

    def _enter_mainWindow(self):
        """
        进入程序窗口
        :return: None
        """
        self.assert_thread.quit()
        self.all_safe.emit()
        self.close()

    def _quit_app(self):
        """
        退出程序
        :return: None
        """
        self.assert_thread.quit()
        self.close()

    def _info_message_format(self, msg: str) -> str:
        """
        INFO级别格式化信息
        :param msg: 原始信息
        :return: 格式化后信息
        """
        return f"""
        <font color="grey">[INFO]: {msg}</font>
        """

    def _warn_message_format(self, msg: str) -> str:
        """
        WARNING级别格式化信息
        :param msg: 原始信息
        :return: 格式化后信息
        """
        return f"""
        <font color="orange">[WARN]: {msg}</font>
        """

    def _fatal_message_format(self, msg: str) -> str:
        """
        FATAL级别格式化信息
        :param msg: 原始信息
        :return: 格式化后信息
        """
        return f"""
        <font color="red">[FATAL]: {msg}</font>
        """

    def _show_button(self):
        """
        显示button按钮
        :return: None
        """
        self.animation = QPropertyAnimation(self.button, b"maximumHeight")
        self.animation.setDuration(500)
        self.animation.setStartValue(0)
        self.animation.setEndValue(40)
        self.animation.setEasingCurve(QEasingCurve.InOutQuart)
        self.animation.start()

    @property
    def styleSheet(self) -> str:
        """
        全局样式表
        :return: str
        """
        return """
        * {
            margin: 0;
            padding: 0;
            font-size: 14px;
            font-family: "KaiTi";
            background-position: center;
            background-repeat: no-reperat;
            border: none;
            color: rgb(0, 0, 0)
        }

        QTextEdit {
            padding-left: 5px;
            border: 2px solid rgb(64, 158, 255);
            background-color: rgb(236, 236, 236);
            font-weight: bold;
            border-radius: 10%
        }

        QPushButton {
            border: none;
            background-color: rgb(64, 158, 255);
            color: rgb(255, 255, 255);
            border-radius: 5%
        }

        QPushButton:hover {
            border: none;
            background-color: rgb(42, 120, 255);
        }

        QPushButton:pressed {
            border: 2px solid rgb(255, 255, 255);
        }
        """
