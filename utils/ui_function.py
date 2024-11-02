__all__ = ["UiFunction"]

import webbrowser
from typing import Union, Optional

from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import QListView, QComboBox
from PyQt5.QtCore import QPropertyAnimation, QEasingCurve, Qt, QEvent, QPoint
from PyQt5.Qt import (
    QPushButton,
    QMessageBox,
    QTableWidgetItem,
    QWidget,
    QHBoxLayout,
    QApplication,
    QProgressBar,
    QPixmap,
)
from PyQt5.QtGui import QMouseEvent, QColor, QIcon
import pyperclip as clip

from main import MainWindow
from .custom_grips import CustomGrip
from model.file import FileModel, DirModel
from model.public_types import ShareType as shareType
from model.public_types import ThemeColor as themeColor
from model.public_types import ControlColorStruct as ControlColor
from model.browse import BrowseFileDictModel
from settings import settings


class UiFunction:
    def __init__(self, window: MainWindow) -> None:
        self._main_window = window
        self._elements = self._main_window.ui
        self._maximize_flag: bool = False
        self._dragPos: Union[QPoint, None] = None
        self._clicked_menu_name = ""
        self._is_sharing_str = "分享中"
        self._isNot_sharing_str = "已取消分享"
        self._pause_button_str = "暂停下载"
        self._continue_button_str = "继续下载"
        self._reset_button_str = "重新下载"
        self._share_number_col = 0
        self._share_type_col = 1
        self._share_targetPath_col = 2
        self._browse_number_col = 3
        self._share_status_col = 4
        self._share_options_col = 5
        self._download_fileName_col = 0
        self._download_progress_col = 1
        self._download_options_col = 2
        self._theme_color = settings.THEME_COLOR
        self._theme_opacity = settings.THEME_OPACITY

    def setup(self) -> None:
        # main window scale
        self._left_grip = CustomGrip(self._main_window, Qt.LeftEdge)
        self._right_grip = CustomGrip(self._main_window, Qt.RightEdge)
        self._top_grip = CustomGrip(self._main_window, Qt.TopEdge)
        self._bottom_grip = CustomGrip(self._main_window, Qt.BottomEdge)
        # main window event connect
        self._main_window.setWindowFlags(Qt.FramelessWindowHint)
        self._main_window.mousePressEvent = self._mousePressEvent
        self._main_window.resizeEvent = self._resize_grips
        # QCombox
        self._elements.shareTypeCombo.setView(QListView())
        self._elements.shareFileCombo.setView(QListView())
        self._comboBox_style_add_minHeight(
            self._elements.shareTypeCombo, self._elements.shareFileCombo
        )
        # elements event connect
        self._setup_event_connect()

    def _comboBox_style_add_minHeight(self, *comboBoxs: QComboBox) -> None:
        for comboBox in comboBoxs:
            ori_style = comboBox.styleSheet()
            comboBox.setStyleSheet(
                ori_style
                + """
                    QComboBox QAbstractItemView::item {
                        min-height: 20px;
                    }
                """
            )

    def _setup_event_connect(self) -> None:
        # window elements
        self._elements.minimizeButton.clicked.connect(
            lambda: self._main_window.showMinimized()
        )
        self._elements.maximizeRestoreButton.clicked.connect(
            lambda: self._maximize_restore()
        )
        self._elements.closeAppButton.clicked.connect(lambda: self._main_window.close())
        # left menu elements
        self._elements.homeButton.clicked.connect(self._menu_button_clicked)
        self._elements.serverButton.clicked.connect(self._menu_button_clicked)
        self._elements.clientButton.clicked.connect(self._menu_button_clicked)
        self._elements.downloadButton.clicked.connect(self._menu_button_clicked)
        self._elements.settingButton.clicked.connect(lambda: self._extra_setting())
        # extra elements
        self._elements.themeColorButtonGroup.buttonClicked.connect(
            lambda: self._change_theme_color()
        )
        self._elements.opacitySlider.valueChanged.connect(
            lambda v: self._change_theme_opacity(v)
        )
        self._elements.shareProjectButton.clicked.connect(
            lambda: self._save_share_msg()
        )
        self._elements.browseProjectButton.clicked.connect(
            lambda: self._open_project_code()
        )
        self._elements.closeSettingButton.clicked.connect(lambda: self._extra_setting())
        # content elements
        self._elements.contentTopBox.mouseDoubleClickEvent = (
            self._contentTopDpubleClicked
        )
        self._elements.contentTopBox.mouseMoveEvent = self._moveWindow
        self._setup_table_widget()
        self._elements.backupButton.setEnabled(False)
        self._elements.downloadDirButton.setEnabled(False)
        self._elements.removeDownloadsButton.setEnabled(False)

    def _maximize_restore(self) -> None:
        maximize_image = self._maximize_image(self._theme_color)
        restore_image = self._restore_image(self._theme_color)
        if not self._maximize_flag:
            self._main_window.showMaximized()
            self._maximize_flag = True
            self._elements.maximizeRestoreButton.setToolTip("缩放窗口")
            self._elements.maximizeRestoreButton.setStyleSheet(
                self._elements.maximizeRestoreButton.styleSheet().replace(
                    maximize_image, restore_image
                )
            )
        else:
            self._main_window.showNormal()
            self._maximize_flag = False
            self._elements.maximizeRestoreButton.setToolTip("窗口全屏")
            self._elements.maximizeRestoreButton.setStyleSheet(
                self._elements.maximizeRestoreButton.styleSheet().replace(
                    restore_image, maximize_image
                )
            )

    def _change_theme_color(self) -> None:
        check_radio = self._elements.themeColorButtonGroup.checkedButton()
        theme_color_str = check_radio.objectName()
        theme_color = themeColor.dispatch(theme_color_str)
        if theme_color is None:
            self.show_critical_messageBox(f"得到非预期的颜色主题: {theme_color_str}")
            return
        self._theme_color = theme_color
        self._elements.styleSheet.setStyleSheet(
            settings.style_sheet(theme_color, self._theme_opacity)
        )
        self._init_maximizeRestoreButton_style()

    def _change_theme_opacity(self, value: Optional[int] = None) -> None:
        theme_opacity = value or settings.THEME_OPACITY
        self._theme_opacity = theme_opacity
        self._elements.styleSheet.setStyleSheet(
            settings.style_sheet(self._theme_color, theme_opacity)
        )
        self._elements.opacityRateLabel.setText(f"{theme_opacity}%")

    def _init_maximizeRestoreButton_style(self):
        maximize_image = self._maximize_image(self._theme_color)
        restore_image = self._restore_image(self._theme_color)
        if not self._maximize_flag:
            self._elements.maximizeRestoreButton.setStyleSheet(maximize_image)
        else:
            self._elements.maximizeRestoreButton.setStyleSheet(restore_image)

    def _save_share_msg(self) -> None:
        msg = "我正在使用file-sharer分享/下载文件, 快一起来玩玩吧, 下载地址:https://zzmx.lanzoue.com/b01fiitgd, 密码:brjm"
        clip.copy(msg)

        self.show_info_messageBox("复制成功, 快发送给小伙伴吧^_^")

    def _open_project_code(self) -> None:
        webbrowser.open_new_tab("https://github.com/zzmx-sudo/file_sharer-Desktop")

    def _extra_setting(self) -> None:
        style = self._elements.settingButton.styleSheet()
        width = self._elements.extraBox.width()
        maxExtend = 200
        minExtend = 0

        if width == minExtend:
            widthExtended = maxExtend
            self._elements.settingButton.setStyleSheet(
                style + self.select_setting_style()
            )
        else:
            self._elements.settingButton.setStyleSheet(
                style.replace(self.select_setting_style(), "")
            )
            widthExtended = minExtend

        self._main_window.reset_settings()
        self.animation = QPropertyAnimation(self._elements.extraBox, b"minimumWidth")
        self.animation.setDuration(500)
        self.animation.setStartValue(width)
        self.animation.setEndValue(widthExtended)
        self.animation.setEasingCurve(QEasingCurve.InOutQuart)
        self.animation.start()

    def _setup_table_widget(self) -> None:
        self._elements.shareListTable.verticalHeader().setVisible(False)
        header = self._elements.shareListTable.horizontalHeader()
        header.setSectionResizeMode(self._share_number_col, QtWidgets.QHeaderView.Fixed)
        header.resizeSection(self._share_number_col, 40)
        header.setSectionResizeMode(self._share_type_col, QtWidgets.QHeaderView.Fixed)
        header.resizeSection(self._share_type_col, 80)
        header.setSectionResizeMode(
            self._browse_number_col, QtWidgets.QHeaderView.Fixed
        )
        header.resizeSection(self._browse_number_col, 80)
        header.setSectionResizeMode(self._share_status_col, QtWidgets.QHeaderView.Fixed)
        header.resizeSection(self._share_status_col, 120)
        header.setSectionResizeMode(
            self._share_targetPath_col, QtWidgets.QHeaderView.Stretch
        )
        header.setSectionResizeMode(
            self._share_options_col, QtWidgets.QHeaderView.Stretch
        )
        header.setSectionsClickable(False)
        self._elements.shareListTable.setRowCount(0)

        self._elements.fileListTable.verticalHeader().setVisible(False)
        self._elements.fileListTable.setRowCount(0)
        self._elements.fileListTable.horizontalHeader().setSectionsClickable(False)

        self._elements.downloadListTable.verticalHeader().setVisible(False)
        header = self._elements.downloadListTable.horizontalHeader()
        header.setSectionResizeMode(
            self._download_fileName_col, QtWidgets.QHeaderView.Stretch
        )
        header.setSectionResizeMode(
            self._download_progress_col, QtWidgets.QHeaderView.Stretch
        )
        header.resizeSection(self._download_options_col, 240)
        header.setSectionResizeMode(
            self._download_options_col, QtWidgets.QHeaderView.Fixed
        )
        header.setStretchLastSection(False)
        header.setSectionsClickable(False)
        self._elements.downloadListTable.setRowCount(0)

    def _mousePressEvent(self, event: QMouseEvent) -> None:
        self._dragPos = event.globalPos()

    def _contentTopDpubleClicked(self, event: QMouseEvent) -> None:
        if (
            event.type() == QEvent.MouseButtonDblClick
            and event.buttons() == Qt.LeftButton
        ):
            self._maximize_restore()

    def _moveWindow(self, event: QMouseEvent) -> None:
        if self._maximize_flag:
            self._maximize_restore()

        if event.buttons() == Qt.LeftButton:
            self._main_window.move(
                self._main_window.pos() + event.globalPos() - self._dragPos
            )
            self._dragPos = event.globalPos()
            event.accept()

    def _menu_button_clicked(self) -> None:
        button = self._main_window.sender()
        clicked_menu_name = button.objectName()

        if clicked_menu_name == "serverButton":
            stack_widget = self._elements.server
        elif clicked_menu_name == "clientButton":
            stack_widget = self._elements.client
        elif clicked_menu_name == "downloadButton":
            stack_widget = self._elements.download
        else:
            stack_widget = self._elements.home
        self._clicked_menu_name = clicked_menu_name

        self._elements.stackedWidget.setCurrentWidget(stack_widget)
        self._reset_menu_handler()
        button.setStyleSheet(self._select_menu(button.styleSheet()))

    def _select_menu(self, origin_style: str) -> str:
        newStyle = origin_style + self.select_menu_style()

        return newStyle

    def _deselect_menu(self, origin_style: str) -> str:
        newStyle = origin_style.replace(self.select_menu_style(), "")

        return newStyle

    def _select_menu_handler(self, menu_button_name: str) -> None:
        for button in self._elements.leftTopBox.findChildren(QPushButton):
            if button.objectName() == menu_button_name:
                button.setStyleSheet(self._select_menu(button.styleSheet()))
                break

    def _reset_menu_handler(self) -> None:
        for button in self._elements.leftTopBox.findChildren(QPushButton):
            if button.objectName() != self._clicked_menu_name:
                button.setStyleSheet(self._deselect_menu(button.styleSheet()))

    def _resize_grips(self, event: QMouseEvent) -> None:
        self._left_grip.setGeometry(0, 10, 10, self._main_window.height())
        self._right_grip.setGeometry(
            self._main_window.width() - 10, 10, 10, self._main_window.height()
        )
        self._top_grip.setGeometry(0, 0, self._main_window.width(), 10)
        self._bottom_grip.setGeometry(
            0, self._main_window.height() - 10, self._main_window.width(), 10
        )

    def _move_center(self) -> None:
        screen = QtWidgets.QDesktopWidget().screenGeometry()
        window = self._main_window.geometry()

        self._main_window.move(
            (screen.width() - window.width()) / 2,
            (screen.height() - window.height()) / 2,
        )

    def show_info_messageBox(
        self,
        msg: str,
        title: str = "消息提示",
        msg_color: str = "black",
        ok_button_text: str = "好的",
    ) -> None:
        info = QMessageBox(
            QMessageBox.Information, title, msg, parent=self._main_window
        )
        okButton = info.addButton(
            self._main_window.tr(ok_button_text), QMessageBox.YesRole
        )
        okButton.setCursor(QtGui.QCursor(Qt.PointingHandCursor))
        okButtonWidth = max(len(ok_button_text), 60)
        info.setWindowFlag(Qt.FramelessWindowHint)
        info.setStyleSheet(
            self.MessageBoxNormalStyle
            + f"""
            QLabel {{
                color: {msg_color}
            }}
            QMessageBox QPushButton {{
                border: 1px solid rgb({self.controlColor.BaseColor});
                color: rgb({self.controlColor.TextColor});
                width: {okButtonWidth}
            }}
            QMessageBox QPushButton:hover {{
                background-color: rgb({self.controlColor.SpecialHovColor});
            }}
        """
        )
        info.setIconPixmap(QPixmap(":/icons/images/icon/logo.png").scaled(50, 50))
        info.exec_()

    def show_question_messageBox(
        self,
        msg: str,
        title: str,
        yes_button_text: str = "取消",
        no_button_text: str = "确认",
    ) -> int:
        question = QMessageBox(
            QMessageBox.Question, title, msg, parent=self._main_window
        )
        question.setWindowFlag(Qt.FramelessWindowHint)
        yesButton = question.addButton(
            self._main_window.tr(yes_button_text), QMessageBox.YesRole
        )
        yesButton.setCursor(QtGui.QCursor(Qt.PointingHandCursor))
        yesButtonWidth = max(len(yes_button_text) * 15, 60)
        yesButton.setStyleSheet(
            f"""
            QPushButton {{
                color: rgb({self.controlColor.SpecialHovColor});
                background-color: rgb({self.controlColor.BaseColor});
                width: {yesButtonWidth}
            }}
            QPushButton:hover {{
                border: none;
                background-color: rgb({self.controlColor.DeepColor})
            }}
            QPushButton:pressed {{
                border: 2px solid rgb({self.controlColor.SpecialHovColor});
            }}
        """
        )
        noButton = question.addButton(
            self._main_window.tr(no_button_text), QMessageBox.NoRole
        )
        noButton.setCursor(QtGui.QCursor(Qt.PointingHandCursor))
        noButtonWidth = max(len(no_button_text) * 15, 60)
        noButton.setStyleSheet(
            f"""
            QPushButton {{
                border: none;
                color: rgb({self.controlColor.TextColor});
                background-color: rgb({self.controlColor.DeepBgColor});
                width: {noButtonWidth}
            }}
            QPushButton:hover {{
                border: none;
                background-color: rgb({self.controlColor.Deep2BgColor});
            }}
            QPushButton:pressed {{
                border: 2px solid rgb({self.controlColor.SpecialHovColor});
            }}
        """
        )
        question.setDefaultButton(noButton)
        question.setStyleSheet(
            self.MessageBoxNormalStyle
            + f"""
            QLabel {{
                color: rgb({self.controlColor.TextColor});;
            }}
            """
        )
        return question.exec_()

    def show_critical_messageBox(self, msg: str) -> None:
        full_msg = f"程序出现BUG, 你可以将复现方式和该弹框截图至项目GitHub提交Lssues, 原始错误信息:\n{msg}"
        critical = QMessageBox(
            QMessageBox.Critical, "程序出错", full_msg, parent=self._main_window
        )
        critical.setWindowFlag(Qt.FramelessWindowHint)
        okButton = critical.addButton(self._main_window.tr("好的"), QMessageBox.YesRole)
        okButton.setCursor(QtGui.QCursor(Qt.PointingHandCursor))
        critical.setStyleSheet(
            self.MessageBoxNormalStyle
            + f"""
            QLabel {{
                color: red;
            }}
            QMessageBox QPushButton {{
                border: 1px solid red;
                color: rgb({self.controlColor.TextColor});
            }}
            QMessageBox QPushButton:hover {{
                background-color: #ffffff;
            }}
            """
        )
        critical.exec_()

    def add_share_table_item(
        self: MainWindow, fileObj: Union[FileModel, DirModel]
    ) -> None:
        if self.ui.shareListTable.rowCount() <= self._sharing_list.length:
            self.ui.shareListTable.setRowCount(self.ui.shareListTable.rowCount() + 1)

        share_number = fileObj.rowIndex + 1
        share_number_item = QTableWidgetItem(str(share_number))
        share_number_item.setTextAlignment(Qt.AlignCenter)
        self.ui.shareListTable.setItem(
            fileObj.rowIndex, self._ui_function._share_number_col, share_number_item
        )
        share_type = "FTP" if fileObj.shareType is shareType.ftp else "HTTP"
        share_type_item = QTableWidgetItem(share_type)
        share_type_item.setTextAlignment(Qt.AlignCenter)
        self.ui.shareListTable.setItem(
            fileObj.rowIndex, self._ui_function._share_type_col, share_type_item
        )
        target_path_item = QTableWidgetItem(fileObj.targetPath)
        target_path_item.setTextAlignment(Qt.AlignCenter)
        self.ui.shareListTable.setItem(
            fileObj.rowIndex, self._ui_function._share_targetPath_col, target_path_item
        )
        browse_number_item = QTableWidgetItem("0")
        browse_number_item.setTextAlignment(Qt.AlignCenter)
        self.ui.shareListTable.setItem(
            fileObj.rowIndex, self._ui_function._browse_number_col, browse_number_item
        )

        open_close_button = QPushButton("")
        open_close_button.setObjectName("open_close")

        def _open_close_button_clicked(
            fileObj: Union[FileModel, DirModel], button: QPushButton
        ) -> None:
            if fileObj.isSharing:
                button_text = "打开共享"
                self.close_share(fileObj)
                fileObj.isSharing = False
                share_status_item = QTableWidgetItem(
                    self._ui_function._isNot_sharing_str
                )
                share_status_item.setTextAlignment(Qt.AlignCenter)
                self.ui.shareListTable.setItem(
                    fileObj.rowIndex,
                    self._ui_function._share_status_col,
                    share_status_item,
                )
            else:
                button_text = "取消共享"
                self.open_share(fileObj)
                fileObj.isSharing = True
                share_status_item = QTableWidgetItem(self._ui_function._is_sharing_str)
                share_status_item.setTextAlignment(Qt.AlignCenter)
                self.ui.shareListTable.setItem(
                    fileObj.rowIndex,
                    self._ui_function._share_status_col,
                    share_status_item,
                )
            button.setText(button_text)
            button.setStyleSheet(
                self._ui_function.open_close_button_style(fileObj.isSharing)
            )
            background, foreground = self._ui_function.status_item_back_foreground(
                fileObj.isSharing
            )
            share_status_item.setBackground(background)
            share_status_item.setForeground(foreground)

        fileObj.isSharing = not fileObj.isSharing
        _open_close_button_clicked(fileObj, open_close_button)
        open_close_button.clicked.connect(
            lambda: _open_close_button_clicked(fileObj, open_close_button)
        )

        copy_browse_button = QPushButton("复制分享链接")
        copy_browse_button.setObjectName("copy_browse")
        copy_browse_button.setStyleSheet(self._ui_function.copy_browse_button_style())

        def _copy_browse_button_clicked(fileObj: Union[FileModel, DirModel]) -> None:
            clip.copy(fileObj.browse_url)
            if not fileObj.isSharing:
                self._ui_function.show_info_messageBox(
                    "复制成功\n该分享已被取消,请打开分享后再发送给小伙伴哦~", msg_color="red"
                )
            else:
                self._ui_function.show_info_messageBox("复制成功,快去发送给小伙伴吧^_^")

        copy_browse_button.clicked.connect(lambda: _copy_browse_button_clicked(fileObj))

        remove_share_button = QPushButton("移除分享记录")
        remove_share_button.setObjectName("remove_share")
        remove_share_button.setStyleSheet(self._ui_function.remove_share_button_style())

        def _remove_share_button_clicked(fileObj: Union[FileModel, DirModel]) -> None:
            self.remove_share(fileObj)

        remove_share_button.clicked.connect(
            lambda: _remove_share_button_clicked(fileObj)
        )

        widget = QWidget()
        hLayout = QHBoxLayout()
        hLayout.addWidget(open_close_button)
        hLayout.addWidget(copy_browse_button)
        hLayout.addWidget(remove_share_button)
        hLayout.setContentsMargins(0, 1, 0, 1)
        hLayout.setSpacing(2)
        widget.setLayout(hLayout)
        self.ui.shareListTable.setCellWidget(
            fileObj.rowIndex, self._ui_function._share_options_col, widget
        )

    def save_theme(self, theme_color: themeColor):
        # The selected menu button changes color
        ori_menu_style = self.select_menu_style()
        new_menu_style = self.select_menu_style(theme_color)
        for button in self._elements.leftTopBox.findChildren(QPushButton):
            if button.objectName() == self._clicked_menu_name:
                button.setStyleSheet(
                    button.styleSheet().replace(ori_menu_style, new_menu_style)
                )
                break
        # The settingButton changes color
        ori_settingBt_style = self.select_setting_style()
        new_settingBt_style = self.select_setting_style(theme_color)
        self._elements.settingButton.setStyleSheet(
            self._elements.settingButton.styleSheet().replace(
                ori_settingBt_style, new_settingBt_style
            )
        )
        # The shareListTable Item changes color
        for row in range(self._elements.shareListTable.rowCount()):
            status_item = self._elements.shareListTable.item(
                row, self._share_status_col
            )
            is_sharing = status_item.text() == self._is_sharing_str
            background, foreground = self.status_item_back_foreground(
                is_sharing, theme_color
            )
            status_item.setBackground(background)
            status_item.setForeground(foreground)
            button_widget = self._elements.shareListTable.cellWidget(
                row, self._share_options_col
            )
            for button in button_widget.findChildren(QPushButton):
                if button.objectName() == "open_close":
                    button.setStyleSheet(
                        self.open_close_button_style(is_sharing, theme_color)
                    )
                elif button.objectName() == "copy_browse":
                    button.setStyleSheet(self.copy_browse_button_style(theme_color))
                else:
                    button.setStyleSheet(self.remove_share_button_style(theme_color))
            QApplication.processEvents()
        # The fileListTable Item changes color
        for row in range(self._elements.fileListTable.rowCount()):
            button = self._elements.fileListTable.cellWidget(row, 0)
            button.setStyleSheet(self.file_dir_button_style(theme_color))
            QApplication.processEvents()
        # The downloadListTable Item changes color
        for row in range(self._elements.downloadListTable.rowCount()):
            progressBar = self._elements.downloadListTable.cellWidget(
                row, self._download_progress_col
            )
            button_widget = self._elements.downloadListTable.cellWidget(
                row, self._download_options_col
            )
            # 正在下载或下载完成状态
            if isinstance(button_widget, QPushButton):
                progressBar.setStyleSheet(self.progressBar_init_style(theme_color))
                if button_widget.text() == self._pause_button_str:
                    button_widget.setStyleSheet(
                        self.download_pause_button_style(theme_color)
                    )
                else:
                    button_widget.setStyleSheet(
                        self.download_remove_button_style(theme_color)
                    )
                continue
            for button in button_widget.findChildren(QPushButton):
                if button.objectName() == "restartButton":
                    button.setStyleSheet(self.download_reset_button_style(theme_color))
                    # 下载失败状态
                    if button.text() == self._reset_button_str:
                        progressBar.setStyleSheet(
                            self.progressBar_failed_style(theme_color)
                        )
                    # 暂停下载状态
                    else:
                        progressBar.setStyleSheet(
                            self.progressBar_pause_style(theme_color)
                        )
                else:
                    button.setStyleSheet(self.download_remove_button_style(theme_color))
            QApplication.processEvents()

    def reset_theme(self):
        self._change_theme_color()
        self._change_theme_opacity()

    def remove_share_row(self: MainWindow, rowIndex: int) -> None:
        self.ui.shareListTable.removeRow(rowIndex)
        share_row_count = self.ui.shareListTable.rowCount()
        for row in range(rowIndex, share_row_count):
            self.ui.shareListTable.item(
                row, self._ui_function._share_number_col
            ).setText(str(row + 1))

    def show_error_browse(self: MainWindow) -> None:
        # TODO:单元格配置为CellWidget后,不能通过setItem设置为普通单元格,暂用以下方法解决,后续再寻找更合适方案
        self.ui.fileListTable.setRowCount(0)
        self.ui.fileListTable.setRowCount(1)
        table_item = QTableWidgetItem("加载失败,请输入正确的分享链接后再加载哦~")
        table_item.setForeground(QColor(255, 0, 0))
        self.ui.fileListTable.setItem(0, 0, table_item)

    def show_not_found_browse(self: MainWindow) -> None:
        self.ui.fileListTable.setRowCount(0)
        self.ui.fileListTable.setRowCount(1)
        table_item = QTableWidgetItem("目标的文件/文件夹不存在,请确认对方有开启分享后再加载哦~")
        table_item.setForeground(QColor(255, 0, 0))
        self.ui.fileListTable.setItem(0, 0, table_item)

    def show_server_error_browse(self: MainWindow) -> None:
        self.ui.fileListTable.setRowCount(0)
        self.ui.fileListTable.setRowCount(1)
        table_item = QTableWidgetItem("对方分享服务异常,请确认对方分享服务正常后再加载哦~")
        table_item.setForeground(QColor(154, 96, 2))
        self.ui.fileListTable.setItem(0, 0, table_item)

    def show_file_list(
        self: MainWindow, fileDict: Union[dict, BrowseFileDictModel]
    ) -> None:
        if not fileDict["isDir"]:
            self.ui.fileListTable.setRowCount(0)
            self.ui.fileListTable.setRowCount(1)
            file_button = self._UIClass.generate_file_button(self, fileDict)
            self.ui.fileListTable.setCellWidget(0, 0, file_button)
            self.ui.downloadDirButton.setEnabled(False)
        else:
            self._UIClass.set_dir_table(self, fileDict)
            self.ui.downloadDirButton.setEnabled(True)

    def generate_file_button(
        self: MainWindow, fileDict: Union[dict, BrowseFileDictModel]
    ) -> QPushButton:
        file_name = fileDict["fileName"]
        button = QPushButton(file_name)
        button.setStyleSheet(self._ui_function.file_dir_button_style())
        file_icon = QIcon()
        file_icon.addPixmap(
            QtGui.QPixmap(":/icons/images/icon/file.png"), QIcon.Normal, QIcon.Off
        )
        button.setIcon(file_icon)
        button.clicked.connect(lambda: self.create_download_record_and_start(fileDict))
        return button

    def set_dir_table(
        self: MainWindow, fileDict: Union[dict, BrowseFileDictModel]
    ) -> None:
        self.ui.fileListTable.setRowCount(0)
        children = fileDict.get("children")
        if not children:
            self.ui.fileListTable.setRowCount(1)
            table_item = QTableWidgetItem("该文件夹下空空如也~")
            table_item.setForeground(QColor(154, 96, 2))
            self.ui.fileListTable.setItem(0, 0, table_item)
            return
        else:
            self.ui.fileListTable.setRowCount(len(children))
            for index, childDict in enumerate(children):
                if childDict["isDir"]:
                    table_item = self._UIClass.generate_dir_button(self, childDict)
                else:
                    table_item = self._UIClass.generate_file_button(self, childDict)
                self.ui.fileListTable.setCellWidget(index, 0, table_item)

    def generate_dir_button(self: MainWindow, fileDict: dict) -> QPushButton:
        dir_name = fileDict["fileName"]
        button = QPushButton(dir_name)
        button.setStyleSheet(self._ui_function.file_dir_button_style())
        dir_icon = QIcon()
        dir_icon.addPixmap(
            QtGui.QPixmap(":/icons/images/icon/folder_new.png"), QIcon.Normal, QIcon.Off
        )
        button.setIcon(dir_icon)
        button.clicked.connect(lambda: self.enter_dir(fileDict))
        return button

    def add_download_table_item(self: MainWindow, fileList: list) -> None:
        if fileList[0]["isDir"]:
            table_fileList = fileList[1:]
        else:
            table_fileList = fileList

        row_count = self._download_data.length
        shareType = fileList[0]["stareType"]
        for fileObj in table_fileList:
            fileName = fileObj["relativePath"]
            try:
                index = self._download_data.index(fileObj)
            except ValueError:
                row_index = row_count
                row_count += 1
                self.ui.downloadListTable.setRowCount(row_count)
                fileName_item = QTableWidgetItem(fileName)
                fileName_item.setForeground(QColor(0, 0, 0))
                fileName_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                self.ui.downloadListTable.setItem(
                    row_index, self._ui_function._download_fileName_col, fileName_item
                )

                init_progressBar = self._ui_function.init_download_progressBar()
                self.ui.downloadListTable.setCellWidget(
                    row_index,
                    self._ui_function._download_progress_col,
                    init_progressBar,
                )
                self._download_data.append(fileObj)
            else:
                row_index = index
                self.ui.downloadListTable.item(
                    row_index, self._ui_function._download_fileName_col
                ).setText(fileName)

                progressBar = self.ui.downloadListTable.cellWidget(
                    row_index, self._ui_function._download_progress_col
                )
                self._ui_function.progressBar_change_to_normal(progressBar)

            init_pushButton = self._ui_function.init_download_pushButton(
                shareType, fileObj
            )
            self.ui.downloadListTable.setCellWidget(
                row_index, self._ui_function._download_options_col, init_pushButton
            )

            QApplication.processEvents()

    def init_download_pushButton(self, shareType: str, fileObj: dict) -> QPushButton:
        def _pause_download(shareType: str, fileObj: dict):
            if shareType == "http":
                if self._main_window._download_http_thread is None:
                    self.show_info_messageBox("暂停失败, 下载线程还未初始化, 请等待所有文件加入下载成功后再点击")
                    return
                self._main_window._download_http_thread.pause(fileObj)
            else:
                if self._main_window._download_ftp_thread is None:
                    self.show_info_messageBox("暂停失败, 下载线程还未初始化, 请等待所有文件加入下载成功后再点击")
                    return
                self._main_window._download_ftp_thread.pause(fileObj)

        pushButton = QPushButton(self._pause_button_str)
        pushButton.setStyleSheet(self.download_pause_button_style())
        pushButton.clicked.connect(lambda: _pause_download(shareType, fileObj))

        return pushButton

    def pushButton_change_to_remove(
        self, pushButton: QPushButton, buttonText: str = "移除该记录"
    ) -> None:
        pushButton.clicked.disconnect()
        pushButton.setText(buttonText)
        pushButton.setStyleSheet(self.download_remove_button_style())

    def pushButton_change_to_widget(self, restart_str: str = "重新下载") -> QWidget:
        restart_button = QPushButton(restart_str)
        restart_button.setObjectName("restartButton")
        restart_button.setStyleSheet(self.download_reset_button_style())

        remove_button = QPushButton("移除该记录")
        remove_button.setObjectName("removeButton")
        remove_button.setStyleSheet(self.download_remove_button_style())

        widget = QWidget()
        hLayout = QHBoxLayout()
        hLayout.addWidget(restart_button)
        hLayout.addWidget(remove_button)
        hLayout.setContentsMargins(0, 1, 0, 1)
        hLayout.setSpacing(2)
        widget.setLayout(hLayout)

        return widget

    def init_download_progressBar(self) -> QProgressBar:
        progressBar = QProgressBar()
        progressBar.setMaximum(100)
        progressBar.setMinimum(0)
        progressBar.setValue(0)
        progressBar.setFormat("等待下载中...")
        progressBar.setStyleSheet(self.progressBar_init_style())

        return progressBar

    def progressBar_change_to_pause(self, progressBar: QProgressBar) -> None:
        progressBar.setStyleSheet(self.progressBar_pause_style())

    def progressBar_change_to_failed(self, progressBar: QProgressBar) -> None:
        progressBar.setStyleSheet(self.progressBar_failed_style())

    def progressBar_change_to_normal(self, progressBar: QProgressBar) -> None:
        progressBar.setStyleSheet(self.progressBar_init_style())

    def select_menu_style(self, theme_color: Optional[themeColor] = None) -> str:
        """选中的menu按钮的样式"""
        theme_color = theme_color or settings.THEME_COLOR
        control_color = self._control_color(theme_color)
        return f"""
            border-left: 3px solid rgb({control_color.BaseColor});
            background-color: rgb({control_color.LightBgColor});
        """

    def select_setting_style(self, theme_color: Optional[themeColor] = None) -> str:
        """setting齿轮按钮选中时的样式"""
        theme_color = theme_color or settings.THEME_COLOR
        control_color = self._control_color(theme_color)
        return f"""
            border: 2px solid rgb({control_color.BaseColor});
            background-color: rgb({control_color.SpecialHovColor});
        """

    def open_close_button_style(
        self, is_sharing: bool, theme_color: Optional[themeColor] = None
    ) -> str:
        """打开/关闭分享按钮的样式"""
        theme_color = theme_color or settings.THEME_COLOR
        if is_sharing:
            return self._negative_button_style(theme_color)
        else:
            return self._positive_button_style(theme_color)

    def status_item_back_foreground(
        self, is_sharing: bool, theme_color: Optional[themeColor] = None
    ) -> [QColor, QColor]:
        """分享状态单元格的后背景色和前背景色"""
        theme_color = theme_color or settings.THEME_COLOR
        control_color = self._control_color(theme_color)
        if is_sharing:
            background = control_color.BaseColor
            foreground = control_color.SpecialHovColor
        else:
            background = control_color.DeepBgColor
            foreground = control_color.TextColor
        return QColor(*[int(x) for x in background.split(",")]), QColor(
            *[int(x) for x in foreground.split(",")]
        )

    def copy_browse_button_style(self, theme_color: Optional[themeColor] = None) -> str:
        """复制分享链接按钮的样式"""
        theme_color = theme_color or settings.THEME_COLOR
        return self._positive_button_style(theme_color)

    def remove_share_button_style(
        self, theme_color: Optional[themeColor] = None
    ) -> str:
        """移除分享按钮的样式"""
        theme_color = theme_color or settings.THEME_COLOR
        return self._negative_button_style(theme_color)

    def file_dir_button_style(self, theme_color: Optional[themeColor] = None) -> str:
        """客户端页加载的文件/文件夹按钮的样式"""
        theme_color = theme_color or settings.THEME_COLOR
        control_color = self._control_color(theme_color)
        return f"""
            QPushButton {{
                background-color: rgb({control_color.LightBgColor});
                color: rgb({control_color.TextColor});
                text-align: left;
                border: none;
                margin: 0;
                padding-left: 10px;
            }}
            QPushButton:hover {{border: 1px solid rgb({control_color.BaseColor});}}
            QPushButton:pressed {{border: 3px solid rgb({control_color.BaseColor});}}
        """

    def progressBar_init_style(self, theme_color: Optional[themeColor] = None) -> str:
        """下载进度初始化时的样式"""
        theme_color = theme_color or settings.THEME_COLOR
        control_color = self._control_color(theme_color)
        return f"""
            QProgressBar {{
                border: 2px solid rgb({control_color.BaseColor});
                border-radius: 5px;
                color: rgb({control_color.TextColor});
                background-color: rgb({control_color.LightBgColor});
                text-align: center;
            }}
            QProgressBar::chunk {{
                background: QLinearGradient(x1:0,y1:0,x2:2,y2:0,stop:0 rgb({control_color.DeepBgColor}),stop:1 rgb({control_color.BaseColor}));
            }}
        """

    def progressBar_pause_style(self, theme_color: Optional[themeColor] = None) -> str:
        """下载进度暂停时的样式"""
        theme_color = theme_color or settings.THEME_COLOR
        control_color = self._control_color(theme_color)
        return f"""
            QProgressBar {{
                border: 2px solid rgb({control_color.BaseColor});
                border-radius: 5px;
                color: rgb({control_color.TextColor});
                background-color: rgb({control_color.LightBgColor});
                text-align: center;
            }}
            QProgressBar::chunk {{
                background-color: rgb({control_color.DeepBgColor});
            }}
        """

    def progressBar_failed_style(self, theme_color: Optional[themeColor] = None) -> str:
        """下载进度失败时的样式"""
        theme_color = theme_color or settings.THEME_COLOR
        control_color = self._control_color(theme_color)
        return f"""
            QProgressBar {{
                border: 2px solid red;
                border-radius: 5px;
                color: rgb({control_color.TextColor});
                background-color: rgb({control_color.LightBgColor});
                text-align: center;
            }}
            QProgressBar::chunk {{
                background-color: red;
            }}
        """

    def download_pause_button_style(
        self, theme_color: Optional[themeColor] = None
    ) -> str:
        """暂停下载按钮的样式"""
        theme_color = theme_color or settings.THEME_COLOR
        return self._negative_button_style(theme_color)

    def download_remove_button_style(
        self, theme_color: Optional[themeColor] = None
    ) -> str:
        """移除下载记录按钮的样式"""
        theme_color = theme_color or settings.THEME_COLOR
        return self._negative_button_style(theme_color)

    def download_reset_button_style(
        self, theme_color: Optional[themeColor] = None
    ) -> str:
        """重新下载按钮的样式"""
        theme_color = theme_color or settings.THEME_COLOR
        return self._positive_button_style(theme_color)

    def _positive_button_style(self, theme_color: themeColor) -> str:
        """积极/正面的按钮样式"""
        control_color = self._control_color(theme_color)
        return f"""
            QPushButton {{
                text-align: center;
                background-color: rgb({control_color.BaseColor});
                color: rgb({control_color.SpecialHovColor});
                height: 28px;
                font: 14px;
                border-radius: 5%;
            }}
            QPushButton::hover {{
                background-color: rgb({control_color.DeepColor})
            }}
        """

    def _negative_button_style(self, theme_color: themeColor) -> str:
        """消极/负面的按钮样式"""
        control_color = self._control_color(theme_color)
        return f"""
            QPushButton {{
                text-align: center;
                background-color: rgb({control_color.DeepBgColor});
                color: rgb({control_color.TextColor});
                height: 28px;
                font: 14px;
                border-radius: 5%;
            }}
            QPushButton::hover {{
                background-color: rgb({control_color.Deep2BgColor})
            }}
        """

    def _maximize_image(self, theme_color: Optional[themeColor] = None):
        """放大按钮背景图片"""
        theme_color = theme_color or settings.THEME_COLOR
        dirName = self._control_color(theme_color).DirName

        return f"""
            background-image: url(:/icons/images/icon/{dirName}/maximize.png)
        """

    def _restore_image(self, theme_color: Optional[themeColor] = None):
        """缩小按钮背景图片"""
        theme_color = theme_color or settings.THEME_COLOR
        dirName = self._control_color(theme_color).DirName

        return f"""
            background-image: url(:/icons/images/icon/{dirName}/restore.png)
        """

    def _control_color(self, theme_color: themeColor) -> ControlColor:
        """控件颜色集"""
        return settings.controlColor(theme_color)

    @property
    def controlColor(self) -> ControlColor:
        """当前控件颜色集"""
        return self._control_color(self._theme_color)

    @property
    def MessageBoxNormalStyle(self) -> str:
        """弹框通用样式"""
        return f"""
            QMessageBox {{
                background-color: rgb({self.controlColor.BaseBgColor});
                border: 1px solid rgb({self.controlColor.BaseColor});
                border-radius: 10%;
            }}
            QLabel {{border: none; font-size: 14px;}}
            QMessageBox QPushButton {{width: 60px; height: 40px; border-radius: 10px;}}
        """
