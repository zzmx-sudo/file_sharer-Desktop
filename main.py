import os
import sys
from multiprocessing import Queue
from typing import Union

from PyQt5.QtWidgets import QMainWindow, QFileDialog, QLineEdit, QCheckBox
from PyQt5.Qt import QApplication
from PyQt5.uic import loadUi

from static.ui.main_ui import Ui_MainWindow
from settings import settings
from utils.logger import sysLogger, sharerLogger
from command.manage import ServiceProcessManager
from model.sharing import FuseSharingModel
from model.file import FileModel, DirModel

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
        self.ui.show()

    def _load_settings(self) -> None:
        settings.load()
        self._cancel_settings()

    def _load_sharing_backups(self) -> None:
        self.ui.shareListTable.setRowCount(0)
        self._sharing_list = FuseSharingModel.load()
        for fileObj in self._sharing_list:
            self._add_share_table_item(fileObj)

    def _create_manager_and_watch_output(self) -> None:
        self._output_q = Queue()
        self._process = ServiceProcessManager(self._output_q)

    def _setup_event_connect(self) -> None:
        # settings elements
        self.ui.logPathButton.clicked.connect(lambda : self._open_folder(self.ui.logPathEdit))
        self.ui.downloadPathButton.clicked.connect(lambda : self._open_folder(self.ui.downloadPathEdit))
        self.ui.saveSettingButton.clicked.connect(lambda : self._save_settings())
        self.ui.cancelSettingButton.clicked.connect(lambda : self._cancel_settings())
        # server elements
        self.ui.sharePathButton.clicked.connect(lambda : self._open_folder(self.ui.sharePathEdit))
        self.ui.createShareButton.clicked.connect(lambda : self._create_share())

    def _save_settings(self) -> None:
        logs_path = self.ui.logPathEdit.text()
        download_path = self.ui.downloadPathEdit.text()
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

        save_system_log = self.ui.saveSystemCheck.isChecked()
        if save_system_log != settings.SAVE_SYSTEM_LOG:
            settings.SAVE_SYSTEM_LOG = save_system_log
            self._process.modify_settings("SAVE_SYSTEM_LOG", save_system_log)
        save_share_log = self.ui.saveShareCheck.isChecked()
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

    def _create_share(self) -> None:
        pass

    def _open_folder(self, lineEdit: QLineEdit) -> None:
        folder_path = QFileDialog.getExistingDirectory(self, "选择文件夹", "./")
        if folder_path:
            lineEdit.setText(folder_path)

    def _add_share_table_item(self, filObj: Union[FileModel, DirModel], isSharing: bool = False) -> None:
        pass

    def _remove_share_table_item(self, table_number: int) -> None:
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())