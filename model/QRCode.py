__all__ = ["QRCodeWindow"]


import io

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QDialog
from PyQt5.QtCore import Qt
import qrcode
from qrcode.main import GenericImage
from PIL import Image, ImageDraw

from utils.logger import sysLogger


class QRCodeWindow(QDialog):
    def __init__(self):
        """
        校验环境窗口初始化函数
        """
        super(QRCodeWindow, self).__init__()
        self.resize(300, 350)
        self.setStyleSheet(self.styleSheet)
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
        self.setAttribute(Qt.WA_TranslucentBackground, True)

        self.show_qrcode("https://www.baidu.com")
        self.show()

    def show_qrcode(self, browse_url: str) -> None:
        """
        显示二维码

        Args:
            browse_url: 二维码的内容

        Returns:
            None
        """
        sysLogger.debug(f"开始显示二维码, 浏览URL: {browse_url}")
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=9,
            border=4,
        )
        qr.add_data(browse_url)
        qr_img = qr.make_image(fill_color="black", back_color="white")
        qr_img = qr_img.convert("RGBA")
        qr_img = self.add_rounded_corners(qr_img, 15)
        fp = io.BytesIO()
        qr_img.save(fp, "PNG")
        image = QtGui.QImage()
        image.loadFromData(fp.getvalue(), "PNG")
        pixmap = QtGui.QPixmap.fromImage(image)
        self.qrcode_label.setPixmap(pixmap)
        sysLogger.debug("二维码插入成功")

    @staticmethod
    def add_rounded_corners(image: GenericImage, radius: int = 15) -> GenericImage:
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

    @property
    def styleSheet(self) -> str:
        """
        二维码窗口全局样式表

        Returns:
            str: 二维码窗口全局样式表
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

        QLabel {
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
