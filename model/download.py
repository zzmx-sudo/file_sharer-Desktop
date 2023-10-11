__all__ = ["DownloadFileDictModel"]

from utils.logger import sysLogger
from PyQt5.Qt import QTableWidgetItem, QColor, QTableWidget, QApplication

from model.public_types import DownloadStatus


class DownloadFileDictModel(list):
    def __init__(self):
        super(DownloadFileDictModel, self).__init__()

    def update_download_status(self, status_tuple: tuple) -> None:
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


        item: QTableWidgetItem = self[url]
        item.setText(msg)
        if status:
            item.setForeground(QColor("green"))
        else:
            item.setForeground(QColor("red"))

    def remove_download_list(self, tableWidget: QTableWidget) -> None:
        row_index = 0
        need_remove_urls = []
        for url, item in self.items():
            if item.text() != "下载中...":
                tableWidget.removeRow(row_index)
                need_remove_urls.append(url)
            else:
                row_index += 1

            QApplication.processEvents()

        for need_remove_url in need_remove_urls:
            del self[need_remove_url]

    def is_empty(self) -> bool:
        return not self

    @property
    def length(self) -> int:
        return len(self)
