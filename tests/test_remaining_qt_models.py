"""Focused Qt-model tests for QR code, tray, and download-list behavior."""

from pathlib import Path
from types import SimpleNamespace

from PyQt5.QtWidgets import QMainWindow, QProgressBar, QPushButton, QTableWidget

from model.QRCode import QRCodeWindow
from model.browse import BrowseFileDictModel
from model.download import DownloadFileDictModel
from model.file import FileModel
from model.public_types import DownloadStatus
from model.tray_icon import TrayIcon


class _QrParent(QMainWindow):
    def __init__(self):
        super().__init__()
        self.changed = []

    def change_free_secret(self, file_obj):
        self.changed.append(file_obj.uuid)


class _TrayParent(QMainWindow):
    def __init__(self):
        super().__init__()
        self.calls = []

    def open_all_share(self):
        self.calls.append("open")

    def close_all_share(self):
        self.calls.append("close")


def test_qrcode_model_renders_and_resets_temporary_free_secret(
    qtbot, tmp_path: Path, monkeypatch
):
    target = tmp_path / "share.txt"
    target.write_text("share", encoding="utf-8")
    parent = _QrParent()
    window = QRCodeWindow(parent)
    qtbot.addWidget(parent)
    qtbot.addWidget(window)
    file_obj = FileModel(target, "qrcode-share")
    monkeypatch.setattr(
        FileModel, "mobile_browse_url", property(lambda _: "http://test/qrcode-share")
    )

    window.show_qrcode(file_obj)
    window.free_secret_button_clicked(file_obj)
    window.reset_free_secret()

    assert window.qrcode_label.pixmap() is not None
    assert file_obj.free_secret is False
    assert parent.changed == [file_obj.uuid]


def test_tray_actions_dispatch_to_main_window_and_toggle_visibility(qtbot):
    parent = _TrayParent()
    tray = TrayIcon(parent)
    qtbot.addWidget(parent)
    parent.show()

    tray.rich_share_action.trigger()
    tray.poor_share_action.trigger()
    tray.show_hide_action.trigger()
    qtbot.waitUntil(lambda: not parent.isVisible())

    assert parent.calls == ["open", "close"]
    assert tray.is_show_window is False


def test_download_list_model_updates_progress_widget(qtbot):
    file_obj = BrowseFileDictModel.load(
        {
            "uuid": "download",
            "fileName": "download.txt",
            "isDir": False,
            "relativePath": "download.txt",
        }
    )
    table = QTableWidget(1, 3)
    progress = QProgressBar()
    action = QPushButton("pause")
    table.setCellWidget(0, 1, progress)
    table.setCellWidget(0, 2, action)
    window = SimpleNamespace(
        ui=SimpleNamespace(downloadListTable=table),
        _ui_function=SimpleNamespace(),
    )
    downloads = DownloadFileDictModel(window)
    downloads.append(file_obj)

    downloads.update_download_status((file_obj, DownloadStatus.DOING, 42), table)

    assert downloads.length == 1
    assert downloads.is_empty() is False
    assert progress.value() == 42
