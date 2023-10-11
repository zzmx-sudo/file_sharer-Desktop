__all__ = ["DownloadFileDictModel"]

from PyQt5.Qt import QTableWidget, QApplication, QPushButton, QProgressBar

from utils.logger import sysLogger
from model.public_types import DownloadStatus
from main import MainWindow


class DownloadFileDictModel(list):
    def __init__(self, window: MainWindow):
        super(DownloadFileDictModel, self).__init__()
        self._window = window
        self._download_progress_col = 1
        self._download_options_col = 2

    def update_download_status(
        self, status_tuple: tuple, tableWidget: QTableWidget
    ) -> None:
        if not isinstance(status_tuple, tuple) or len(status_tuple) != 3:
            sysLogger.error(f"获取的下载状态数据有误, 原始信息: {status_tuple}")
            return
        url, status, msg = status_tuple
        if url not in self:
            sysLogger.warning(
                f"未被存储的下载状态数据对象, 可能是重复下载的, url: {url}, 原始信息: {status_tuple}"
            )
            return

        index = self.index(url)
        if index >= tableWidget.rowCount():
            sysLogger.error(f"程序存在BUG, 存储的下载URL数大于表格行数")
            return
        progressBar: QProgressBar = tableWidget.cellWidget(
            index, self._download_progress_col
        )
        pushButton: QPushButton = tableWidget.cellWidget(
            index, self._download_options_col
        )
        if status is DownloadStatus.DOING:
            progressBar.setValue(msg)
        elif status is DownloadStatus.PAUSE:
            self._window._ui_function.progressBar_change_to_pause(progressBar)
            print("暂停成功, ", url)
            pushButton.clicked.disconnect()
            widget = self._window._ui_function.pushButton_change_to_widget("继续下载")
            # TODO: 给两个按钮绑定事件
            tableWidget.setCellWidget(index, self._download_options_col, widget)
        elif status is DownloadStatus.SUCCESS:
            progressBar.setValue(100)
            self._window._ui_function.pushButton_change_to_remove(pushButton)
            pushButton.clicked.connect(
                lambda: self._remove_download_item(url, tableWidget)
            )
        else:
            pushButton.clicked.disconnect()
            widget = self._window._ui_function.pushButton_change_to_widget()
            # TODO: 给两个按钮绑定事件
            tableWidget.setCellWidget(index, self._download_options_col, widget)

    def remove_download_list(self, tableWidget: QTableWidget) -> None:
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

    def _remove_download_item(self, url: str, tableWidget: QTableWidget) -> None:
        try:
            index = self.index(url)
        except ValueError:
            return

        if index >= tableWidget.rowCount():
            return
        tableWidget.removeRow(index)
        self.pop(index)
        self._window.ui.removeDownloadsButton.setEnabled(not self.is_empty())

    def is_empty(self) -> bool:
        return not self

    @property
    def length(self) -> int:
        return len(self)
