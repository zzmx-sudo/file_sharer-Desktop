# ///////////////////////////////////////////////////////////////
# BY: WANDERSON M.PIMENTA
# ///////////////////////////////////////////////////////////////

__all__ = ["CustomGrip"]

from PyQt5.QtCore import Qt, QSize, QRect
from PyQt5.QtGui import QCursor, QMouseEvent
from PyQt5.QtWidgets import QMainWindow, QWidget, QFrame, QHBoxLayout, QSizeGrip


class CustomGrip(QWidget):
    def __init__(self, parent: QMainWindow, position: Qt.Edge) -> None:
        # SETUP UI
        QWidget.__init__(self)
        self.parent = parent
        self.setParent(parent)
        self.wi: Widgets = Widgets()

        # SHOW TOP GRIP
        if position == Qt.TopEdge:
            self.wi.top_func(self)
            self.setGeometry(0, 0, self.parent.width(), 10)
            self.setMaximumHeight(10)

            # GRIPS
            top_left = QSizeGrip(self.wi.top_left)
            top_right = QSizeGrip(self.wi.top_right)

            # RESIZE TOP
            def resize_top(event: QMouseEvent) -> None:
                delta = event.pos()
                height = max(
                    self.parent.minimumHeight(), self.parent.height() - delta.y()
                )
                geo = self.parent.geometry()
                geo.setTop(geo.bottom() - height)
                self.parent.setGeometry(geo)
                event.accept()

            self.wi.top.mouseMoveEvent = resize_top
            self.wi.top_left.setStyleSheet("background: transparent")
            self.wi.top_right.setStyleSheet("background: transparent")
            self.wi.top.setStyleSheet("background: transparent")

        # SHOW BOTTOM GRIP
        elif position == Qt.BottomEdge:
            self.wi.bottom_func(self)
            self.setGeometry(0, self.parent.height() - 10, self.parent.width(), 10)
            self.setMaximumHeight(10)

            # GRIPS
            bottom_left = QSizeGrip(self.wi.bottom_left)
            bottom_right = QSizeGrip(self.wi.bottom_right)

            # RESIZE BOTTOM
            def resize_bottom(event: QMouseEvent) -> None:
                delta = event.pos()
                height = max(
                    self.parent.minimumHeight(), self.parent.height() + delta.y()
                )
                self.parent.resize(self.parent.width(), height)
                event.accept()

            self.wi.bottom.mouseMoveEvent = resize_bottom
            self.wi.bottom_left.setStyleSheet("background: transparent")
            self.wi.bottom_right.setStyleSheet("background: transparent")
            self.wi.bottom.setStyleSheet("background: transparent")

        # SHOW LEFT GRIP
        elif position == Qt.LeftEdge:
            self.wi.left_func(self)
            self.setGeometry(0, 10, 10, self.parent.height())
            self.setMaximumWidth(10)

            # RESIZE LEFT
            def resize_left(event: QMouseEvent) -> None:
                delta = event.pos()
                width = max(self.parent.minimumWidth(), self.parent.width() - delta.x())
                geo = self.parent.geometry()
                geo.setLeft(geo.right() - width)
                self.parent.setGeometry(geo)
                event.accept()

            self.wi.leftgrip.mouseMoveEvent = resize_left
            self.wi.leftgrip.setStyleSheet("background: transparent")

        # RESIZE RIGHT
        elif position == Qt.RightEdge:
            self.wi.right_func(self)
            self.setGeometry(self.parent.width() - 10, 10, 10, self.parent.height())
            self.setMaximumWidth(10)

            def resize_right(event: QMouseEvent) -> None:
                delta = event.pos()
                width = max(self.parent.minimumWidth(), self.parent.width() + delta.x())
                self.parent.resize(width, self.parent.height())
                event.accept()

            self.wi.rightgrip.mouseMoveEvent = resize_right
            self.wi.rightgrip.setStyleSheet("background: transparent")

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        self.mousePos = None

    def resizeEvent(self, event: QMouseEvent) -> None:
        if hasattr(self.wi, "container_top"):
            self.wi.container_top.setGeometry(0, 0, self.width(), 10)

        elif hasattr(self.wi, "container_bottom"):
            self.wi.container_bottom.setGeometry(0, 0, self.width(), 10)

        elif hasattr(self.wi, "leftgrip"):
            self.wi.leftgrip.setGeometry(0, 0, 10, self.height() - 20)

        elif hasattr(self.wi, "rightgrip"):
            self.wi.rightgrip.setGeometry(0, 0, 10, self.height() - 20)


class Widgets(object):
    def top_func(self, Form):
        if not Form.objectName():
            Form.setObjectName("Form")
        self.container_top = QFrame(Form)
        self.container_top.setObjectName("container_top")
        self.container_top.setGeometry(QRect(0, 0, 500, 10))
        self.container_top.setMinimumSize(QSize(0, 10))
        self.container_top.setMaximumSize(QSize(16777215, 10))
        self.container_top.setFrameShape(QFrame.NoFrame)
        self.container_top.setFrameShadow(QFrame.Raised)
        self.top_layout = QHBoxLayout(self.container_top)
        self.top_layout.setSpacing(0)
        self.top_layout.setObjectName("top_layout")
        self.top_layout.setContentsMargins(0, 0, 0, 0)
        self.top_left = QFrame(self.container_top)
        self.top_left.setObjectName("top_left")
        self.top_left.setMinimumSize(QSize(10, 10))
        self.top_left.setMaximumSize(QSize(10, 10))
        self.top_left.setCursor(QCursor(Qt.SizeFDiagCursor))
        self.top_left.setStyleSheet("background-color: rgb(33, 37, 43);")
        self.top_left.setFrameShape(QFrame.NoFrame)
        self.top_left.setFrameShadow(QFrame.Raised)
        self.top_layout.addWidget(self.top_left)
        self.top = QFrame(self.container_top)
        self.top.setObjectName("top")
        self.top.setCursor(QCursor(Qt.SizeVerCursor))
        self.top.setStyleSheet("background-color: rgb(85, 255, 255);")
        self.top.setFrameShape(QFrame.NoFrame)
        self.top.setFrameShadow(QFrame.Raised)
        self.top_layout.addWidget(self.top)
        self.top_right = QFrame(self.container_top)
        self.top_right.setObjectName("top_right")
        self.top_right.setMinimumSize(QSize(10, 10))
        self.top_right.setMaximumSize(QSize(10, 10))
        self.top_right.setCursor(QCursor(Qt.SizeBDiagCursor))
        self.top_right.setStyleSheet("background-color: rgb(33, 37, 43);")
        self.top_right.setFrameShape(QFrame.NoFrame)
        self.top_right.setFrameShadow(QFrame.Raised)
        self.top_layout.addWidget(self.top_right)

    def bottom_func(self, Form):
        if not Form.objectName():
            Form.setObjectName("Form")
        self.container_bottom = QFrame(Form)
        self.container_bottom.setObjectName("container_bottom")
        self.container_bottom.setGeometry(QRect(0, 0, 500, 10))
        self.container_bottom.setMinimumSize(QSize(0, 10))
        self.container_bottom.setMaximumSize(QSize(16777215, 10))
        self.container_bottom.setFrameShape(QFrame.NoFrame)
        self.container_bottom.setFrameShadow(QFrame.Raised)
        self.bottom_layout = QHBoxLayout(self.container_bottom)
        self.bottom_layout.setSpacing(0)
        self.bottom_layout.setObjectName("bottom_layout")
        self.bottom_layout.setContentsMargins(0, 0, 0, 0)
        self.bottom_left = QFrame(self.container_bottom)
        self.bottom_left.setObjectName("bottom_left")
        self.bottom_left.setMinimumSize(QSize(10, 10))
        self.bottom_left.setMaximumSize(QSize(10, 10))
        self.bottom_left.setCursor(QCursor(Qt.SizeBDiagCursor))
        self.bottom_left.setStyleSheet("background-color: rgb(33, 37, 43);")
        self.bottom_left.setFrameShape(QFrame.NoFrame)
        self.bottom_left.setFrameShadow(QFrame.Raised)
        self.bottom_layout.addWidget(self.bottom_left)
        self.bottom = QFrame(self.container_bottom)
        self.bottom.setObjectName("bottom")
        self.bottom.setCursor(QCursor(Qt.SizeVerCursor))
        self.bottom.setStyleSheet("background-color: rgb(85, 170, 0);")
        self.bottom.setFrameShape(QFrame.NoFrame)
        self.bottom.setFrameShadow(QFrame.Raised)
        self.bottom_layout.addWidget(self.bottom)
        self.bottom_right = QFrame(self.container_bottom)
        self.bottom_right.setObjectName("bottom_right")
        self.bottom_right.setMinimumSize(QSize(10, 10))
        self.bottom_right.setMaximumSize(QSize(10, 10))
        self.bottom_right.setCursor(QCursor(Qt.SizeFDiagCursor))
        self.bottom_right.setStyleSheet("background-color: rgb(33, 37, 43);")
        self.bottom_right.setFrameShape(QFrame.NoFrame)
        self.bottom_right.setFrameShadow(QFrame.Raised)
        self.bottom_layout.addWidget(self.bottom_right)

    def left_func(self, Form):
        if not Form.objectName():
            Form.setObjectName("Form")
        self.leftgrip = QFrame(Form)
        self.leftgrip.setObjectName("left")
        self.leftgrip.setGeometry(QRect(0, 10, 10, 480))
        self.leftgrip.setMinimumSize(QSize(10, 0))
        self.leftgrip.setCursor(QCursor(Qt.SizeHorCursor))
        self.leftgrip.setStyleSheet("background-color: rgb(255, 121, 198);")
        self.leftgrip.setFrameShape(QFrame.NoFrame)
        self.leftgrip.setFrameShadow(QFrame.Raised)

    def right_func(self, Form):
        if not Form.objectName():
            Form.setObjectName("Form")
        Form.resize(500, 500)
        self.rightgrip = QFrame(Form)
        self.rightgrip.setObjectName("right")
        self.rightgrip.setGeometry(QRect(0, 0, 10, 500))
        self.rightgrip.setMinimumSize(QSize(10, 0))
        self.rightgrip.setCursor(QCursor(Qt.SizeHorCursor))
        self.rightgrip.setStyleSheet("background-color: rgb(255, 0, 127);")
        self.rightgrip.setFrameShape(QFrame.NoFrame)
        self.rightgrip.setFrameShadow(QFrame.Raised)
