import os
import sys
from multiprocessing import Queue
from typing import Union

from PyQt5.QtWidgets import (
    QMainWindow, QFileDialog, QLineEdit, QCheckBox, QWidget
)
from PyQt5.Qt import QApplication, QMessageBox
from PyQt5 import QtGui
from PyQt5.uic import loadUi

from static.ui.main_ui import Ui_MainWindow
from settings import settings
from utils.logger import sysLogger, sharerLogger
from command.manage import ServiceProcessManager
from model.sharing import FuseSharingModel
from model.file import FileModel, DirModel
from model.public_types import ShareType as shareType
from utils.public_func import generate_uuid

class MainWindow(QMainWindow):

    def __init__(self) -> None:
        super(MainWindow, self).__init__()

        # load ui
        # self.ui = Ui_MainWindow()
        # self.ui.setupUi(self)
        ui_path = os.path.join(settings.BASE_DIR, "static", "ui", "main.ui")
        self.ui = loadUi(ui_path)

        # setup ui_function
        from utils.ui_function import UiFunction
        # self._ui_function = UiFunction(self)
        self._ui_function = UiFunction(self.ui)
        self._ui_function.setup()

        # env load
        self._load_settings()
        self._load_sharing_backups()

        # process manage and start watch output thread
        self._create_manager_and_watch_output()

        # event connect
        self._setup_event_connect()

        # show window
        # self.show()
        self.ui.closeEvent = self.closeEvent
        self.ui.show()

    def _load_settings(self) -> None:
        settings.load()
        self._cancel_settings()

    def _load_sharing_backups(self) -> None:
        self._sharing_list = FuseSharingModel.load()
        for fileObj in self._sharing_list:
            self._add_share_table_item(fileObj)

    def _create_manager_and_watch_output(self) -> None:
        self._output_q = Queue()
        self._service_process = ServiceProcessManager(self._output_q)

    def _setup_event_connect(self) -> None:
        # settings elements
        self.ui.logPathButton.clicked.connect(lambda : self._open_folder(self.ui.logPathEdit))
        self.ui.downloadPathButton.clicked.connect(lambda : self._open_folder(self.ui.downloadPathEdit))
        self.ui.saveSettingButton.clicked.connect(lambda : self._save_settings())
        self.ui.cancelSettingButton.clicked.connect(lambda : self._cancel_settings())
        # server elements
        self.ui.sharePathButton.clicked.connect(lambda : self._open_folder(self.ui.sharePathEdit))
        self.ui.sharePathButton.clicked.connect(lambda : self._update_file_combo())
        self.ui.createShareButton.clicked.connect(lambda : self._create_share())

    def _save_settings(self) -> None:
        logs_path: str = self.ui.logPathEdit.text()
        download_path: str = self.ui.downloadPathEdit.text()
        if not logs_path or not download_path:
            self._ui_function.show_info_messageBox("保存设置错误,日志路径或下载路径不可为空！", msg_color="red")
            return
        if not os.path.isdir(logs_path):
            self._ui_function.show_info_messageBox(
                "保存设置错误,日志路径不存在！\n建议用按钮打开资源管理器选择路径", msg_color="red"
            )
            return
        if not os.path.isdir(download_path):
            self._ui_function.show_info_messageBox(
                "保存设置错误,下载路径不存在！\n建议用按钮打开资源管理器选择路径", msg_color="red"
            )
            return

        save_system_log: bool = self.ui.saveSystemCheck.isChecked()
        if save_system_log != settings.SAVE_SYSTEM_LOG:
            settings.SAVE_SYSTEM_LOG = save_system_log
            self._process.modify_settings("SAVE_SYSTEM_LOG", save_system_log)
        save_share_log: bool = self.ui.saveShareCheck.isChecked()
        if save_share_log != settings.SAVE_SHARER_LOG:
            settings.SAVE_SHARER_LOG = save_share_log
            self._process.modify_settings("SAVE_SHARER_LOG", save_share_log)
        if settings.LOGS_PATH != logs_path:
            settings.LOGS_PATH = logs_path
            self._process.modify_settings("LOGS_PATH", logs_path)
            sysLogger.reload()
            sharerLogger.reload()
        settings.DOWNLOAD_DIR = download_path
        settings.dump()
        self._ui_function.show_info_messageBox("保存配置成功")

    def _cancel_settings(self) -> None:
        self.ui.saveSystemCheck.setChecked(settings.SAVE_SYSTEM_LOG)
        self.ui.saveShareCheck.setChecked(settings.SAVE_SHARER_LOG)
        self.ui.logPathEdit.setText(settings.LOGS_PATH)
        self.ui.downloadPathEdit.setText(settings.DOWNLOAD_DIR)

    def _update_file_combo(self) -> None:
        share_path: str = self.ui.sharePathEdit.text()
        if not os.path.isdir(share_path):
            return
        self.ui.shareFileCombo.clear()
        fileList: list = os.listdir(share_path)
        for item in fileList:
            self.ui.shareFileCombo.addItem(item)

    def _create_share(self) -> None:
        base_path: str = self.ui.sharePathEdit.text()
        if not os.path.isdir(base_path):
            self._ui_function.show_info_messageBox(
                "分享的路径不存在！\n建议用按钮打开资源管理器选择路径", msg_color="red"
            )
            return
        target_path: str = os.path.join(base_path, self.ui.shareFileCombo.currentText())
        if not os.path.exists(target_path):
            self._ui_function.show_info_messageBox(
                "分享的路径不存在！\n请确认后再新建", msg_color="red"
            )
            return
        share_type: Union[str, shareType] = self.ui.shareTypeCombo.currentText()
        share_type = shareType.ftp if share_type == "FTP" else shareType.http
        shared_row_number: Union[None, int] = self._sharing_list.contains(target_path, share_type)
        if shared_row_number is not None:
            self._ui_function.show_info_messageBox(
                f"该路径已被分享过, 他在分享记录的第 [{shared_row_number + 1}] 行",
                msg_color="red"
            )
            return
        uuid: str = f"{share_type.value[0]}{generate_uuid()}"
        fileModel = DirModel if os.path.isdir(target_path) else FileModel
        if share_type is shareType.ftp:
            shared_fileObj = self._sharing_list.get_ftp_shared(target_path)
        else:
            shared_fileObj = None
        if shared_fileObj is None:
            fileObj = fileModel(target_path, uuid)
        else:
            fileObj = fileModel(
                target_path, uuid, pwd=shared_fileObj.ftp_pwd,
                port=shared_fileObj.ftp_pwd, ftp_base_path=shared_fileObj.ftp_basePath
            )
        self._sharing_list.append(fileObj)
        self._add_share_table_item(fileObj, True)
        self._service_process.add_share(fileObj)

    def _remove_share(self, rowIndex: int) -> None:
        if rowIndex < 0 or rowIndex >= self._sharing_list.length:
            sysLogger.error(f"移除分享记录异常,行号溢出,欲移除的行号:{rowIndex+1},总行数:{self._sharing_list.length}")
            return
        fileObj = self._sharing_list[rowIndex]
        if fileObj.isSharing:
            self._ui_function.show_info_messageBox(
                "该分享未关闭,请先关闭分享后再移除哦～", msg_color="red"
            )
            return
        self._sharing_list.remove(rowIndex)
        self._service_process.remove_share(fileObj)
        del fileObj
        self._remove_share_table_item(rowIndex)

    def _open_folder(self, lineEdit: QLineEdit) -> None:
        folder_path = QFileDialog.getExistingDirectory(self, "选择文件夹", "./")
        if folder_path:
            lineEdit.setText(folder_path)

    def _add_share_table_item(
        self,
        fileObj: Union[FileModel, DirModel],
        isSharing: bool = False
    ) -> None:
        fileObj.isSharing = isSharing
        self._ui_function.add_share_table_item(fileObj)

    def _remove_share_table_item(self, rowIndex: int) -> None:
        self._ui_function.remove_share_table_item(rowIndex)

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        result = self._ui_function.show_question_messageBox("是否退出？", "您正在退出程序，请确认是否退出？")
        if result == 0:
            self._service_process.close_all()
            event.accept()
        else:
            event.ignore()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())