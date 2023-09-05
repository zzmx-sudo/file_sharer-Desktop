__all__ = [
    "UiFunction"
]

from PyQt5.QtCore import QPropertyAnimation, QEasingCurve, Qt

from main import MainWindow

class UiFunction:

    def __init__(self, window: MainWindow) -> None:

        self._winodw = window
        self._ui = self._winodw.ui
        self._maximize_flag = False

    def setup(self) -> None:
        self._winodw.setWindowFlags(Qt.FramelessWindowHint)
        # event connect
        self._setup_event_connect()

    def _setup_event_connect(self) -> None:
        self._ui.minimizeButton.clicked.connect(lambda: self._winodw.showMinimized())
        self._ui.maximizeRestoreButton.clicked.connect(lambda : self._maximize_restore())
        self._ui.settingButton.clicked.connect(lambda : self._extra_setting())
        self._ui.closeSettingButton.clicked.connect(lambda : self._extra_setting())
        self._ui.closeAppButton.clicked.connect(lambda : self._winodw.close())

    def _maximize_restore(self) -> None:
        maximize_image = "background-image: url(:/icons/images/icon/maximize.png);"
        restore_image = "background-image: url(:/icons/images/icon/restore.png);"
        if not self._maximize_flag:
            self._winodw.showMaximized()
            self._maximize_flag = True
            self._ui.maximizeRestoreButton.setToolTip("缩放窗口")
            self._ui.maximizeRestoreButton.setStyleSheet(
                self._ui.maximizeRestoreButton.styleSheet().replace(maximize_image, restore_image)
            )
        else:
            self._winodw.showNormal()
            self._maximize_flag = False
            self._ui.maximizeRestoreButton.setToolTip("窗口全屏")
            self._ui.maximizeRestoreButton.setStyleSheet(
                self._ui.maximizeRestoreButton.styleSheet().replace(restore_image, maximize_image)
            )

    def _extra_setting(self) -> None:
        select_style = "border: 2px solid #409eff;"
        style = self._ui.settingButton.styleSheet()
        width = self._ui.extraBox.width()
        maxExtend = 200
        minExtend = 0

        if width == minExtend:
            widthExtended = maxExtend
            self._ui.settingButton.setStyleSheet(style + select_style)
        else:
            self._ui.settingButton.setStyleSheet(style.replace(select_style, ""))
            widthExtended = minExtend

        animation = QPropertyAnimation(self._ui.extraBox, b"maximumWidth")
        animation.setDuration(500)
        animation.setStartValue(width)
        animation.setEndValue(widthExtended)
        animation.setEasingCurve(QEasingCurve.InOutQuart)
        animation.start()