"""Download model tests for recursive work queues and Qt status signals."""

from pathlib import Path

from model.browse import BrowseFileDictModel
from model.public_types import DownloadStatus
from model.qt_thread import DownloadHttpFileThread, LoadBrowseUrlThread


def _deep_download_tree() -> BrowseFileDictModel:
    payload = {
        "uuid": "root",
        "fileName": "root",
        "shareType": "http",
        "downloadUrl": "http://localhost/download/root",
        "isDir": True,
        "children": [
            {
                "directory": {
                    "uuid": "directory",
                    "fileName": "directory",
                    "shareType": "http",
                    "downloadUrl": "http://localhost/download/directory",
                    "isDir": True,
                    "children": [
                        {
                            "file": {
                                "uuid": "file",
                                "fileName": "file.txt",
                                "shareType": "http",
                                "downloadUrl": "http://localhost/download/file",
                                "isDir": False,
                                "children": [],
                            }
                        }
                    ],
                }
            }
        ],
    }
    return BrowseFileDictModel.load(
        LoadBrowseUrlThread("http://localhost").process_filePath(payload)
    )


def test_download_thread_flattens_deep_tree_and_marks_hit_log(qapp):
    root = _deep_download_tree()
    thread = DownloadHttpFileThread(root)
    file_map = thread._file_maps[root.uuid]

    assert [item.relativePath for item in file_map.downloadList] == [
        Path("root"),
        Path("root/directory"),
        Path("root/directory/file.txt"),
    ]
    assert file_map.downloadList[0].downloadUrl.endswith("?hit_log=true")
    assert file_map.progress == 0


def test_download_pause_resume_emits_status_and_updates_queue(qtbot):
    root = _deep_download_tree()
    thread = DownloadHttpFileThread(root)

    with qtbot.waitSignal(thread.signal, timeout=1000) as blocker:
        thread.pause(root)

    assert blocker.args[0][0] is root
    assert blocker.args[0][1] is DownloadStatus.PAUSE
    assert thread.is_padding(root) is True

    root_copy = thread._file_maps[root.uuid].downloadList[0]
    thread.resume(root_copy)
    assert thread.is_padding(root_copy) is False
