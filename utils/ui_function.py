__all__ = [
    "UiFunction"
]

import webbrowser
from typing import Union

from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import (
    QPropertyAnimation, QEasingCurve, Qt, QEvent, QPoint
)
from PyQt5.Qt import (
    QPushButton, QMessageBox, QTableWidgetItem, QWidget, QHBoxLayout
)
from PyQt5.QtGui import QMouseEvent, QColor, QIcon
import pyperclip as clip

from main import MainWindow
from . custom_grips import CustomGrip
from model.file import FileModel, DirModel
from model.public_types import ShareType as shareType
from model.browse import BrowseFileDictModel

class UiFunction:

    def __init__(self, window: MainWindow) -> None:

        self._main_window = window
        self._elements = self._main_window.ui
        # self._elements = self._main_window
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
        self._file_dir_button_style = """
        QPushButton {background-color: rgb(247, 247, 247); color: rgb(0, 0, 0); 
                    text-align: left; border: none; margin: 0; padding-left: 10px;}
        QPushButton:hover {border: 1px solid #409eff;}
        QPushButton:pressed {border: 3px solid #409eff;}
        """
        self._share_number_col = 0
        self._share_type_col = 1
        self._share_targetPath_col = 2
        self._browse_number_col = 3
        self._share_status_col = 4
        self._share_options_col = 5

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
        # elements event connect
        self._setup_event_connect()

    def _setup_event_connect(self) -> None:
        # window elements
        self._elements.minimizeButton.clicked.connect(lambda: self._main_window.showMinimized())
        self._elements.maximizeRestoreButton.clicked.connect(lambda : self._maximize_restore())
        self._elements.closeAppButton.clicked.connect(lambda: self._main_window.close())
        # left menu elements
        self._elements.homeButton.clicked.connect(self._menu_button_clicked)
        self._elements.serverButton.clicked.connect(self._menu_button_clicked)
        self._elements.clientButton.clicked.connect(self._menu_button_clicked)
        self._elements.downloadButton.clicked.connect(self._menu_button_clicked)
        self._elements.settingButton.clicked.connect(lambda: self._extra_setting())
        # extra elements
        self._elements.shareProjectButton.clicked.connect(lambda : self._save_share_msg())
        self._elements.browseProjectButton.clicked.connect(lambda: self._open_project_code())
        self._elements.closeSettingButton.clicked.connect(lambda : self._extra_setting())
        # content elements
        self._elements.contentTopBox.mouseDoubleClickEvent = self._contentTopDpubleClicked
        self._elements.contentTopBox.mouseMoveEvent = self._moveWindow
        self._setup_table_widget()
        self._elements.backupButton.setEnabled(False)
        self._elements.downloadDirButton.setEnabled(False)

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

    def _save_share_msg(self) -> None:
        msg = "我正在使用file-sharer分享/下载文件, 快一起来玩玩吧, 下载地址: https://github.com/zzmx-sudo/file_sharer-LAN"
        clip.copy(msg)

        self.show_info_messageBox("复制成功, 快发送给小伙伴吧^_^")

    def _open_project_code(self) -> None:

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

    def _setup_table_widget(self):
        self._elements.shareListTable.verticalHeader().setVisible(False)
        header = self._elements.shareListTable.horizontalHeader()
        header.setSectionResizeMode(self._share_number_col, QtWidgets.QHeaderView.Fixed)
        header.resizeSection(self._share_number_col, 40)
        header.setSectionResizeMode(self._share_type_col, QtWidgets.QHeaderView.Fixed)
        header.resizeSection(self._share_type_col, 80)
        header.setSectionResizeMode(self._browse_number_col, QtWidgets.QHeaderView.Fixed)
        header.resizeSection(self._browse_number_col, 80)
        header.setSectionResizeMode(self._share_status_col, QtWidgets.QHeaderView.Fixed)
        header.resizeSection(self._share_status_col, 120)
        header.setSectionResizeMode(self._share_targetPath_col, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(self._share_options_col, QtWidgets.QHeaderView.Stretch)
        self._elements.shareListTable.setRowCount(0)

        self._elements.fileListTable.setRowCount(0)

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

    def show_info_messageBox(
            self,
            msg: str,
            title: str = "消息提示",
            msg_color: str = "black",
            ok_button_text: str = "好的"
    ) -> None:
        info = QMessageBox(
            QMessageBox.Information,
            title, msg,
            parent=self._main_window
        )
        okButton = info.addButton(self._main_window.tr(ok_button_text), QMessageBox.YesRole)
        okButton.setCursor(QtGui.QCursor(Qt.PointingHandCursor))
        okButtonWidth = max(len(ok_button_text), 60)
        info.setWindowFlag(Qt.FramelessWindowHint)
        info.setStyleSheet(self._messageBox_normal_style + f"""
            QLabel {{
                color: {msg_color}
            }}
            QMessageBox QPushButton {{
                border: 1px solid #409eff;
                width: {okButtonWidth}
            }}
            QMessageBox QPushButton:hover {{
                background-color: #ffffff;
            }}
        """)
        info.exec_()

    def show_question_messageBox(
            self,
            msg: str,
            title: str,
            yes_button_text: str = "确认",
            no_button_text: str = "取消"
    ):
        question = QMessageBox(
            QMessageBox.Question,
            title, msg,
            parent=self._main_window
        )
        question.setWindowFlag(Qt.FramelessWindowHint)
        yesButton = question.addButton(self._main_window.tr(yes_button_text), QMessageBox.YesRole)
        yesButton.setCursor(QtGui.QCursor(Qt.PointingHandCursor))
        yesButtonWidth = max(len(yes_button_text) * 15, 60)
        yesButton.setStyleSheet(f"""
            QPushButton {{
                color: #ffffff;
                background-color: #409eff;
                width: {yesButtonWidth}
            }}
            QPushButton:hover {{
                border: 1px solid rgb(61, 13, 134);
            }}
            QPushButton:pressed {{
                border: 3px solid rgb(61, 13, 134);
            }}
        """)
        noButton = question.addButton(self._main_window.tr(no_button_text), QMessageBox.NoRole)
        noButton.setCursor(QtGui.QCursor(Qt.PointingHandCursor))
        noButtonWidth = max(len(no_button_text) * 15, 60)
        noButton.setStyleSheet(f"""
            QPushButton {{
                color: rgb(0, 0, 0);
                background-color: rgb(222, 222, 222);
                width: {noButtonWidth}
            }}
            QPushButton:hover {{
                border: 1px solid rgb(61, 13, 134);
            }}
            QPushButton:pressed {{
                border: 3px solid rgb(61, 13, 134);
            }}
        """)
        question.setDefaultButton(noButton)
        question.setStyleSheet(self._messageBox_normal_style)
        return question.exec_()

    def add_share_table_item(self: MainWindow, fileObj: Union[FileModel, DirModel]) -> None:
        if self.ui.shareListTable.rowCount() <= self._sharing_list.length:
            self.ui.shareListTable.setRowCount(self.ui.shareListTable.rowCount() + 1)

        share_number = fileObj.rowIndex + 1
        share_number_item = QTableWidgetItem(str(share_number))
        share_number_item.setTextAlignment(Qt.AlignCenter)
        self.ui.shareListTable.setItem(fileObj.rowIndex, self._ui_function._share_number_col, share_number_item)
        share_type = "FTP" if fileObj.shareType is shareType.ftp else "HTTP"
        share_type_item = QTableWidgetItem(share_type)
        share_type_item.setTextAlignment(Qt.AlignCenter)
        self.ui.shareListTable.setItem(fileObj.rowIndex, self._ui_function._share_type_col, share_type_item)
        target_path_item = QTableWidgetItem(fileObj.targetPath)
        target_path_item.setTextAlignment(Qt.AlignCenter)
        self.ui.shareListTable.setItem(fileObj.rowIndex, self._ui_function._share_targetPath_col, target_path_item)
        browse_number_item = QTableWidgetItem("0")
        browse_number_item.setTextAlignment(Qt.AlignCenter)
        self.ui.shareListTable.setItem(fileObj.rowIndex, self._ui_function._browse_number_col, browse_number_item)

        open_close_button = QPushButton("")
        def _open_close_button_clicked(fileObj: Union[FileModel, DirModel], button: QPushButton) -> None:
            if fileObj.isSharing:
                background_color = "rgb(126, 199, 255)"
                color = "#ffffff"
                hover_background = "#409eff"
                button_text = "打开共享"
                self.close_share(fileObj)
                fileObj.isSharing = False
                share_status_item = QTableWidgetItem("已取消分享")
                share_status_item.setTextAlignment(Qt.AlignCenter)
                share_status_item.setBackground(QColor(200, 200, 200))
                share_status_item.setForeground(QColor(0, 0, 0))
                self.ui.shareListTable.setItem(fileObj.rowIndex, self._ui_function._share_status_col, share_status_item)
            else:
                background_color = "rgb(200, 200, 200)"
                color = "rgb(0, 0, 0)"
                hover_background = "rgb(100, 100, 100)"
                button_text = "取消共享"
                self.open_share(fileObj)
                fileObj.isSharing = True
                share_status_item = QTableWidgetItem("分享中")
                share_status_item.setTextAlignment(Qt.AlignCenter)
                share_status_item.setBackground(QColor("#409eff"))
                share_status_item.setForeground(QColor("#ffffff"))
                self.ui.shareListTable.setItem(fileObj.rowIndex, self._ui_function._share_status_col, share_status_item)
            button.setText(button_text)
            button.setStyleSheet(f"""
                QPushButton {{
                    text-align: center;
                    background-color: {background_color};
                    color: {color};
                    height: 28px;
                    font: 14px;
                    border-radius: 5%;
                }}

                QPushButton:hover {{
                    background-color: {hover_background}
                }}
            """)
        fileObj.isSharing = not fileObj.isSharing
        _open_close_button_clicked(fileObj, open_close_button)
        open_close_button.clicked.connect(lambda : _open_close_button_clicked(fileObj, open_close_button))

        copy_browse_button = QPushButton("复制分享链接")
        copy_browse_button.setStyleSheet("""
            QPushButton {
                text-align: center;
                background-color: rgb(126, 199, 255);
                color: #ffffff;
                height: 28px;
                font: 14px;
                border-radius: 5%;
            }
            
            QPushButton:hover {
                background-color: #409eff
            }
        """)
        def _copy_browse_button_clicked(fileObj: Union[FileModel, DirModel]) -> None:
            clip.copy(fileObj.browse_url)
            if not fileObj.isSharing:
                self._ui_function.show_info_messageBox(
                    "复制成功\n该分享已被取消,请打开分享后再发送给小伙伴哦~", msg_color="red"
                )
            else:
                self._ui_function.show_info_messageBox("复制成功,快去发送给小伙伴吧^_^")
        copy_browse_button.clicked.connect(lambda : _copy_browse_button_clicked(fileObj))

        remove_share_button = QPushButton("移除分享记录")
        remove_share_button.setStyleSheet("""
            QPushButton {
                text-align: center;
                background-color: rgb(200, 200, 200);
                color: rgb(0, 0, 0);
                height: 28px;
                font: 14px;
                border-radius: 5%;
            }

            QPushButton:hover {
                background-color: rgb(100, 100, 100)
            }
        """)
        def _remove_share_button_clicked(fileObj: Union[FileModel, DirModel]) -> None:
            self.remove_share(fileObj)
        remove_share_button.clicked.connect(lambda: _remove_share_button_clicked(fileObj))

        widget = QWidget()
        hLayout = QHBoxLayout()
        hLayout.addWidget(open_close_button)
        hLayout.addWidget(copy_browse_button)
        hLayout.addWidget(remove_share_button)
        hLayout.setContentsMargins(0,1,0,1)
        hLayout.setSpacing(2)
        widget.setLayout(hLayout)
        self.ui.shareListTable.setCellWidget(fileObj.rowIndex, self._ui_function._share_options_col, widget)

    def remove_share_row(self: MainWindow, rowIndex: int) -> None:
        self.ui.shareListTable.removeRow(rowIndex)
        share_row_count = self.ui.shareListTable.rowCount()
        for row in range(rowIndex, share_row_count):
            self.ui.shareListTable.item(row, self._ui_function._share_number_col).setText(str(row + 1))

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

    def show_file_list(self: MainWindow, fileDict: Union[dict, BrowseFileDictModel]) -> None:
        if not fileDict["isDir"]:
            self.ui.fileListTable.setRowCount(0)
            self.ui.fileListTable.setRowCount(1)
            file_button = self._UIClass.generate_file_button(self, fileDict)
            self.ui.fileListTable.setCellWidget(0, 0, file_button)
            self.ui.downloadDirButton.setEnabled(False)
        else:
            self._UIClass.set_dir_table(self, fileDict)
            self.ui.downloadDirButton.setEnabled(True)

    def generate_file_button(self: MainWindow, fileDict: Union[dict, BrowseFileDictModel]) -> QPushButton:
        file_name = fileDict["fileName"]
        button = QPushButton(file_name)
        button.setStyleSheet(self._ui_function._file_dir_button_style)
        file_icon = QIcon()
        file_icon.addPixmap(QtGui.QPixmap(":/icons/images/icon/file.png"), QIcon.Normal, QIcon.Off)
        button.setIcon(file_icon)
        button.clicked.connect(lambda: self.create_download_record_and_start(fileDict))
        return button

    def set_dir_table(self: MainWindow, fileDict: Union[dict, BrowseFileDictModel]) -> None:
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
                self.ui.fileListTable.setCellWidget(index, 0 ,table_item)

    def generate_dir_button(self: MainWindow, fileDict: dict) -> QPushButton:
        dir_name = fileDict["fileName"]
        button = QPushButton(dir_name)
        button.setStyleSheet(self._ui_function._file_dir_button_style)
        dir_icon = QIcon()
        dir_icon.addPixmap(QtGui.QPixmap(":/icons/images/icon/folder.png"), QIcon.Normal, QIcon.Off)
        button.setIcon(dir_icon)
        button.clicked.connect(lambda : self.enter_dir(fileDict))
        return button