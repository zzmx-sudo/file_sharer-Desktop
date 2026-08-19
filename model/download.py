__all__ = ["DownloadFileDictModel"]

import logging
from typing import Tuple, Union

from PyQt5.Qt import QTableWidget, QApplication, QPushButton, QProgressBar

from .public_types import DownloadStatus
from .browse import BrowseFileDictModel
from main import MainWindow


class DownloadFileDictModel(list):
    def __init__(self, window: MainWindow):
        """
        下载文件集类初始化函数

        Args:
            window: 主程序窗口对象
        """
        super(DownloadFileDictModel, self).__init__()
        self._window = window
        self._download_progress_col = 1
        self._download_options_col = 2

    def update_download_status(
        self,
        status_tuple: Tuple[BrowseFileDictModel, DownloadStatus, Union[str, int]],
        tableWidget: QTableWidget,
    ) -> None:
        """
        更新下载状态

        Args:
            status_tuple: 欲更新的状态数据
            tableWidget: 显示下载记录的表格控件

        Returns:
            None
        """
        self.sysLogger.debug(
            f"更新下载状态, {status_tuple[0].relativePath}-{status_tuple[1]}"
        )
        if not isinstance(status_tuple, tuple) or len(status_tuple) != 3:
            self.sysLogger.error(f"获取的下载状态数据有误, 原始信息: {status_tuple}")
            return
        fileDict, status, msg = status_tuple
        if fileDict not in self:
            self.sysLogger.warning(
                f"未被存储的下载状态数据对象, 可能是重复下载的, 文件路径: {fileDict.relativePath}"
            )
            return

        index = self.index(fileDict)
        if index >= tableWidget.rowCount():
            self.sysLogger.error(f"程序存在BUG, 存储的下载URL数大于表格行数")
            return
        progressBar: QProgressBar = tableWidget.cellWidget(
            index, self._download_progress_col
        )
        pushButton: QPushButton = tableWidget.cellWidget(
            index, self._download_options_col
        )
        if status is DownloadStatus.DOING:
            progressBar.setFormat("下载进度: %p%")
            progressBar.setValue(msg)
        elif status is DownloadStatus.PAUSE:
            progressBar.setFormat("下载暂停")
            # 可能会有两次回调, 第二次忽略
            if self._options_is_button(index):
                button_str = self._window._ui_function._continue_button_str
                self._window._ui_function.progressBar_change_to_pause(progressBar)
                pushButton.clicked.disconnect()
                self._setup_options_widget(index, fileDict, button_str, tableWidget)
        elif status is DownloadStatus.SUCCESS:
            progressBar.setValue(100)
            progressBar.setFormat("下载完成")
            self._window._ui_function.pushButton_change_to_remove(pushButton)
            pushButton.clicked.connect(
                lambda: self._remove_download_item(fileDict, tableWidget)
            )
        else:
            progressBar.setFormat(f"下载失败({msg})")
            button_str = self._window._ui_function._reset_button_str
            self._window._ui_function.progressBar_change_to_failed(progressBar)
            pushButton.clicked.disconnect()
            self._setup_options_widget(index, fileDict, button_str, tableWidget)

    def remove_download_list(self, tableWidget: QTableWidget) -> None:
        """
        清空已完成下载记录

        Args:
            tableWidget: 显示下载记录的表格控件

        Returns:
            None
        """
        self.sysLogger.debug("清空已完成下载记录")
        row_index = 0
        ignore_urls = []
        for url in self:
            options = tableWidget.cellWidget(row_index, self._download_options_col)
            if isinstance(options, QPushButton) and options.text() == "移除该记录":
                tableWidget.removeRow(row_index)
            else:
                ignore_urls.append(url)
                row_index += 1

            QApplication.processEvents()

        self.clear()
        self.extend(ignore_urls)

    def is_empty(self) -> bool:
        """
        判断当前下载记录是否为空

        Returns:
            bool: 当前下载记录是否为空
        """
        return not self

    @property
    def length(self) -> int:
        """
        下载记录的个数

        Returns:
            int: 下载记录的个数
        """
        return len(self)

    @property
    def sysLogger(self) -> logging.Logger:
        """
        sysLogger

        Returns:
            logging.Logger: logger.sysLogger
        """
        from utils.logger import sysLogger

        return sysLogger

    def _options_is_button(self, index: int) -> bool:
        call_widget = self._window.ui.downloadListTable.cellWidget(
            index, self._download_options_col
        )

        return isinstance(call_widget, QPushButton)

    def _remove_download_item(
        self, fileDict: BrowseFileDictModel, tableWidget: QTableWidget
    ) -> None:
        self.sysLogger.debug(f"移除下载记录, {fileDict.fileName}")
        try:
            index = self.index(fileDict)
        except ValueError:
            return

        if index >= tableWidget.rowCount():
            return
        tableWidget.removeRow(index)
        self.pop(index)
        self._window.ui.removeDownloadsButton.setEnabled(not self.is_empty())

    def _setup_options_widget(
        self,
        index: int,
        fileDict: BrowseFileDictModel,
        reset_str: str,
        tableWidget: QTableWidget,
    ) -> None:
        self.sysLogger.debug("初始化操作按钮控件")
        widget = self._window._ui_function.pushButton_change_to_widget(reset_str)

        reset_button = widget.findChild(QPushButton, "restartButton")
        reset_button.clicked.connect(
            lambda: self._window._resume_download_file(fileDict)
        )

        remove_button = widget.findChild(QPushButton, "removeButton")
        remove_button.clicked.connect(
            lambda: self._window._remove_download_item(fileDict, tableWidget)
        )

        self._window.ui.downloadListTable.setCellWidget(
            index, self._download_options_col, widget
        )
