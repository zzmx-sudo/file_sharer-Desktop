__all__ = ["AssertEnvWindow"]


from typing import Tuple

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QDialog
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtCore import QPropertyAnimation, QEasingCurve

from settings import settings
from .public_types import VerifyStatus
from utils.public_func import get_config_from_toml, resize_window
from utils.logger import sysLogger


class AssertThread(QThread):
    single = pyqtSignal(tuple)

    def __init__(self):
        """
        校验环境线程类初始化函数
        """
        super(AssertThread, self).__init__()

    def run(self) -> None:
        """
        检验环境线程入口函数

        Returns:
            None
        """
        self.single.emit((VerifyStatus.WARN, "本软件永久免费, 如果您进行了付费, 请直接给差评!"))
        # verify pyproject.toml
        self._verify_pyproject_toml()
        # verify local ip
        if not settings.LOCAL_HOST:
            self.single.emit((VerifyStatus.FATAL, "获取本机IP失败, 请确认本机网络正常后再打开"))
            sysLogger.error("获取本机IP失败, 已发射对应FATAL信息")
            return
        elif settings.LOCAL_HOST == "127.0.0.1":
            self.single.emit((VerifyStatus.WARN, "未发现可与他人通信IP地址, 分享或下载对象仅限本机"))
            sysLogger.debug("未发现可与他人通信IP地址, 已发射对应WARN信息")

        self.single.emit((VerifyStatus.INFO, f"本机IP: {settings.LOCAL_HOST}"))
        sysLogger.debug("已发射追加本机IP INFO信息")
        self.single.emit((VerifyStatus.DONE, "校验完成, 点击按钮后进入"))
        sysLogger.debug("已发射校验完成DONE信息")

    def _verify_pyproject_toml(self) -> None:
        """
        校验配置文件是否正常

        Returns:
            None
        """
        sysLogger.debug("开始校验配置文件")
        if not get_config_from_toml():
            self.single.emit(
                (VerifyStatus.WARN, "customize.toml和pyproject.toml文件不存在或损坏, 将使用默认配置")
            )
            sysLogger.debug("配置文件不存在或损坏, 已发射对应WARN信息")

        self.single.emit(
            (VerifyStatus.INFO, f"日志路径: {settings.LOGS_PATH}, 如需修改请在设置中配置, 保存后生效")
        )
        sysLogger.debug("已发射日志路径INFO信息")
        self.single.emit(
            (VerifyStatus.INFO, f"下载路径: {settings.DOWNLOAD_DIR}, 如需修改请在设置中配置, 保存后生效")
        )
        sysLogger.debug("已发射下载路径INFO信息")
        self.single.emit(
            (VerifyStatus.INFO, f"预使用HTTP端口: {settings.init_wsgi_port()}, 请勿占用")
        )
        sysLogger.debug("已发射预使用HTTP端口INFO信息")
        self.single.emit((VerifyStatus.INFO, f"当前使用主题: {settings.THEME_COLOR}"))
        sysLogger.debug("已发射当前使用主题INFO信息")
        self.single.emit((VerifyStatus.INFO, f"当前使用透明度: {settings.THEME_OPACITY}%"))
        sysLogger.debug("已发射当前使用透明度INFO信息")
        sysLogger.debug("配置文件校验完成")


class AssertEnvWindow(QDialog):
    all_safe = pyqtSignal()

    def __init__(self):
        """
        校验环境窗口初始化函数
        """
        super(AssertEnvWindow, self).__init__()
        self.resize(400, 300)
        self.setStyleSheet(self.styleSheet)
        self.verticalLayout = QtWidgets.QVBoxLayout(self)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(5)
        self.verticalLayout.setObjectName("verticalLayout")
        self.text_edit = QtWidgets.QTextEdit(self)
        self.text_edit.setObjectName("text_edit")
        self.text_edit.setReadOnly(True)
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

    def resize(self, *args: int) -> None:
        """
        重置窗口大小

        Args:
            *args: 需重置大小的宽高, 为空时根据屏幕分辨率自适应

        Returns:
            None
        """
        if args:
            super(AssertEnvWindow, self).resize(*args)
            return

        resize_window(self, (400, 300), settings.CURR_RESOLUTION)

        sysLogger.debug("开启Assert窗口")
        self.show()
        self._verify()

    def _verify(self) -> None:
        """
        开启校验

        Returns:
            None
        """
        sysLogger.debug("开始校验环境")
        self.assert_thread = AssertThread()
        self.assert_thread.single.connect(self._append_text_edit)
        self.assert_thread.start()

    def _append_text_edit(self, verify_res: Tuple[VerifyStatus, str]) -> None:
        """
        将校验结果追加到text_edit控件中

        Args:
            verify_res: 校验的结果

        Returns:
            None
        """
        status, msg = verify_res
        if status is VerifyStatus.INFO:
            self.text_edit.append(self._info_message_format(msg))
            sysLogger.debug(f"收到INFO信息[{msg}], 已追加至文本框")
        elif status is VerifyStatus.WARN:
            self.text_edit.append(self._warn_message_format(msg))
            sysLogger.debug(f"收到WARN信息[{msg}], 已追加至文本框")
        elif status is VerifyStatus.FATAL:
            self._all_safe = False
            self.text_edit.append(self._fatal_message_format(msg))
            sysLogger.debug(f"收到FATAL信息[{msg}], 已追加至文本框")
            self.button.setText("确认并退出")
            sysLogger.debug("按钮改为[确认并退出], 并绑定点击事件")
            self._show_button()
            self.button.clicked.connect(lambda: self._quit_app())
        else:
            self.text_edit.append(self._info_message_format(msg))
            sysLogger.debug(f"收到DONE信息[{msg}], 已追加至文本框")
            self.button.setText("点击进入")
            sysLogger.debug("按钮改为[点击进入], 并绑定点击事件")
            self._show_button()
            self.button.clicked.connect(lambda: self._enter_mainWindow())

    def _enter_mainWindow(self) -> None:
        """
        进入主程序窗口

        Returns:
            None
        """
        sysLogger.debug("用户点击进入, 正在发射打开主窗口事件")
        self.assert_thread.quit()
        self.all_safe.emit()
        self.close()

    def _quit_app(self) -> None:
        """
        退出主程序

        Returns:
            None
        """
        sysLogger.debug("用户点击确认并退出, 正在退出程序")
        self.assert_thread.quit()
        self.close()

    def _info_message_format(self, msg: str) -> str:
        """
        INFO级别格式化信息

        Args:
            msg: 原始信息(待格式化信息)

        Returns:
            str: 格式化后的信息
        """
        return f"""
        <font color="grey">[INFO]: {msg}</font>
        """

    def _warn_message_format(self, msg: str) -> str:
        """
        WARNING级别格式化信息

        Args:
            msg: 原始信息(待格式化信息)

        Returns:
            str: 格式化后的信息
        """
        return f"""
        <font color="orange">[WARN]: {msg}</font>
        """

    def _fatal_message_format(self, msg: str) -> str:
        """
        FATAL级别格式化信息

        Args:
            msg: 原始信息(待格式化信息)

        Returns:
            str: 格式化后的信息
        """
        return f"""
        <font color="red">[FATAL]: {msg}</font>
        """

    def _show_button(self) -> None:
        """
        显示button按钮

        Returns:
            None
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
        校验环境窗口全局样式表

        Returns:
            str: 校验环境窗口全局样式表
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
