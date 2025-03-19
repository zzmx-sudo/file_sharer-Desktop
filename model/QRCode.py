__all__ = ["QRCodeWindow"]


import io
from typing import Union

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QDialog
from PyQt5.QtCore import Qt
import qrcode
from qrcode.main import GenericImage
from PIL import Image, ImageDraw

from model.public_types import ThemeColor as themeColor
from model.file import FileModel, DirModel
from settings import settings
from utils.logger import sysLogger


class QRCodeWindow(QDialog):
    def __init__(self, parent=None):
        """
        校验环境窗口初始化函数
        """
        super(QRCodeWindow, self).__init__(parent)
        self._fileObj: Union[FileModel, DirModel, None] = None
        self.resize(300, 350)
        self.setStyleSheet(self.styleSheet())
        self.verticalLayout = QtWidgets.QVBoxLayout(self)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(5)
        self.verticalLayout.setObjectName("verticalLayout")
        self.qrcode_label = QtWidgets.QLabel(self)
        self.qrcode_label.setMinimumSize(QtCore.QSize(300, 300))
        self.qrcode_label.setMaximumSize(QtCore.QSize(300, 300))
        self.qrcode_label.setObjectName("qrcode_label")
        self.verticalLayout.addWidget(self.qrcode_label)
        self.buttonFrame = QtWidgets.QFrame(self)
        self.buttonFrame.setMinimumSize(QtCore.QSize(0, 40))
        self.buttonFrame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.buttonFrame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.buttonFrame.setObjectName("buttonFrame")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.buttonFrame)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 5)
        self.horizontalLayout.setSpacing(5)
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtWidgets.QSpacerItem(
            281, 0, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum
        )
        self.horizontalLayout.addItem(spacerItem)
        self.freeSecretButton = QtWidgets.QPushButton(self.buttonFrame)
        self.freeSecretButton.setMinimumSize(QtCore.QSize(90, 30))
        self.freeSecretButton.setMaximumSize(QtCore.QSize(16777215, 30))
        self.freeSecretButton.setObjectName("freeSecretButton")
        self.freeSecretButton.setText("打开临时免密")
        self.horizontalLayout.addWidget(self.freeSecretButton)
        self.closeButton = QtWidgets.QPushButton(self.buttonFrame)
        self.closeButton.setMinimumSize(QtCore.QSize(90, 30))
        self.closeButton.setMaximumSize(QtCore.QSize(16777215, 30))
        self.closeButton.setText("关闭")
        self.closeButton.clicked.connect(lambda: self.close())
        self.horizontalLayout.addWidget(self.closeButton)
        spacerItem1 = QtWidgets.QSpacerItem(
            280, 0, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum
        )
        self.horizontalLayout.addItem(spacerItem1)
        self.verticalLayout.addWidget(self.buttonFrame)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)

    def show_qrcode(self, fileObj: Union[FileModel, DirModel]) -> None:
        """
        显示二维码

        Args:
            browse_url: 二维码的内容

        Returns:
            None
        """
        self._fileObj = fileObj
        browse_url = fileObj.mobile_browse_url
        sysLogger.debug(f"开始显示二维码, 浏览URL: {browse_url}")
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=8,
            border=2,
        )
        qr.add_data(browse_url)
        qr_img = qr.make_image(fill_color="black", back_color="white")
        qr_img = qr_img.convert("RGBA")
        qr_img = self.add_rounded_corners(qr_img, 12)
        fp = io.BytesIO()
        qr_img.save(fp, "PNG")
        image = QtGui.QImage()
        image.loadFromData(fp.getvalue(), "PNG")
        pixmap = QtGui.QPixmap.fromImage(image)
        self.qrcode_label.setPixmap(pixmap)
        sysLogger.debug("二维码插入成功")

    @staticmethod
    def add_rounded_corners(image: GenericImage, radius: int = 12) -> GenericImage:
        """
        给二维码图像添加圆角遮罩

        Args:
            image: 二维码图像对象
            radius: 圆角半径

        Returns:
            GenericImage: 添加圆角遮罩后的二维码图像
        """
        # 创建一个遮罩
        mask = Image.new("L", image.size, 0)
        draw = ImageDraw.Draw(mask)
        # 绘制圆角矩形
        draw.rounded_rectangle((0, 0, image.size[0], image.size[1]), radius, fill=255)
        # 将遮罩盖在二维码图像上
        image.putalpha(mask)
        return image

    def free_secret_button_clicked(self, fileObj: Union[FileModel, DirModel]) -> None:
        """
        临时免密按钮点击回调

        Args:
            需修改临时免密状态的文件/文件夹对象

        Returns:
            None
        """
        sysLogger.debug("正在修改临时免密按钮样式")
        if self._fileObj is None or fileObj.uuid != self._fileObj.uuid:
            sysLogger.error("系统错误, 欲修改免密状态的文件/文件夹对象与当前二维码显示的不一致")
            return

        self._fileObj.free_secret = not self._fileObj.free_secret
        button_text = "关闭临时免密" if self._fileObj.free_secret else "打开临时免密"
        self.freeSecretButton.setText(button_text)
        self.freeSecretButton.setStyleSheet(self.free_secret_button_style())
        sysLogger.debug("临时免密按钮样式修改完成")

    def reset_free_secret(self) -> None:
        """
        关闭二维码窗口或点击其他二维码显示时, 需关闭当前分享对象的临时免密

        Returns:
            None
        """
        sysLogger.debug("正在重置(关闭)上一分享文件的临时免密")
        if self._fileObj is None:
            sysLogger.debug("无历史分享, 退出关闭临时免密")
            return

        if self._fileObj.free_secret:
            self._fileObj.free_secret = False
            self.freeSecretButton.setText("打开临时免密")
            self.freeSecretButton.setStyleSheet(self.free_secret_button_style())
            self.parent().change_free_secret(self._fileObj)
        sysLogger.debug("重置(关闭)上一分享文件的临时免密完成")

    def close(self) -> bool:
        """
        二维码窗口关闭时, 应关闭当前分享对象的临时免密

        Returns:
            bool: QT窗口关闭时的返回值
        """
        self.reset_free_secret()
        return super(QRCodeWindow, self).close()

    def resetStyleSheet(self, theme_color: themeColor) -> None:
        """
        重置/修改样式

        Args:
            theme_color: 主题颜色

        Returns:
            None
        """
        self.setStyleSheet(self.styleSheet(theme_color))

    def styleSheet(self, theme_color: themeColor = settings.THEME_COLOR) -> str:
        """
        二维码窗口全局样式表

        Args:
            theme_color: 主题颜色

        Returns:
            str: 二维码窗口全局样式表
        """
        control_color = settings.controlColor(theme_color)
        return f"""
        * {{
            margin: 0;
            padding: 0;
            font-size: 14px;
            font-family: "KaiTi";
            background-position: center;
            background-repeat: no-reperat;
            border: none;
            color: rgb({control_color.TextColor})
        }}

        QLabel {{
            border: 2px solid rgb({control_color.BaseColor});
            background-color: rgb({control_color.BaseBgColor});
            font-weight: bold;
            border-radius: 10%
        }}

        {self.free_secret_button_style(theme_color)}
        """

    def free_secret_button_style(
        self, theme_color: themeColor = settings.THEME_COLOR
    ) -> str:
        """
        免密浏览按钮的样式

        Args:
            theme_color: 主题颜色

        Returns:
            str: 免密浏览按钮的样式
        """
        control_color = settings.controlColor(theme_color)
        if self._fileObj is not None and self._fileObj.free_secret:
            return f"""
            QPushButton {{
                border: none;
                background-color: rgb({control_color.DeepBgColor});
                color: rgb({control_color.TextColor});
                border-radius: 5%
            }}

            QPushButton:hover {{
                border: none;
                background-color: rgb({control_color.Deep2BgColor});
            }}

            QPushButton:pressed {{
                border: 2px solid rgb({control_color.TextColor});
            }}
            """
        else:
            return f"""
            QPushButton {{
                border: none;
                background-color: rgb({control_color.BaseColor});
                color: rgb({control_color.SpecialHovColor});
                border-radius: 5%
            }}

            QPushButton:hover {{
                border: none;
                background-color: rgb({control_color.DeepColor});
            }}

            QPushButton:pressed {{
                border: 2px solid rgb({control_color.SpecialHovColor});
            }}
            """
