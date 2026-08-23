"""Tests for remotely browsed directory data and path normalization."""

from pathlib import Path

import pytest

from exceptions import OperationException
from model.browse import BrowseFileDictModel
from model.qt_thread import LoadBrowseUrlThread
from utils.public_func import update_downloadUrl_with_hitLog


def test_browse_model_loads_deep_tree_with_files_and_directories_at_every_level():
    source = {
        "uuid": "root",
        "fileName": "shared",
        "shareType": "http",
        "downloadUrl": "http://localhost/download/root",
        "isDir": True,
        "children": [
            {
                "level-one": {
                    "uuid": "level-one",
                    "fileName": "level-one",
                    "shareType": "http",
                    "downloadUrl": "http://localhost/download/level-one",
                    "isDir": True,
                    "children": [
                        {
                            "level-one-file": {
                                "uuid": "level-one-file",
                                "fileName": "one.txt",
                                "shareType": "http",
                                "downloadUrl": "http://localhost/download/one.txt",
                                "isDir": False,
                                "children": [],
                            }
                        },
                        {
                            "level-two": {
                                "uuid": "level-two",
                                "fileName": "level-two",
                                "shareType": "http",
                                "downloadUrl": "http://localhost/download/level-two",
                                "isDir": True,
                                "children": [
                                    {
                                        "level-two-file": {
                                            "uuid": "level-two-file",
                                            "fileName": "two.txt",
                                            "shareType": "http",
                                            "downloadUrl": "http://localhost/download/two.txt",
                                            "isDir": False,
                                            "children": [],
                                        }
                                    },
                                    {
                                        "level-three": {
                                            "uuid": "level-three",
                                            "fileName": "level-three",
                                            "shareType": "http",
                                            "downloadUrl": "http://localhost/download/level-three",
                                            "isDir": True,
                                            "children": [
                                                {
                                                    "level-three-file": {
                                                        "uuid": "level-three-file",
                                                        "fileName": "three.txt",
                                                        "shareType": "http",
                                                        "downloadUrl": "http://localhost/download/three.txt",
                                                        "isDir": False,
                                                        "children": [],
                                                    }
                                                },
                                                {
                                                    "level-four": {
                                                        "uuid": "level-four",
                                                        "fileName": "level-four",
                                                        "shareType": "http",
                                                        "downloadUrl": "http://localhost/download/level-four",
                                                        "isDir": True,
                                                        "children": [],
                                                    }
                                                },
                                            ],
                                        }
                                    },
                                ],
                            }
                        },
                    ],
                }
            },
            {
                "root-file": {
                    "uuid": "root-file",
                    "fileName": "root.txt",
                    "shareType": "http",
                    "downloadUrl": "http://localhost/download/root.txt",
                    "isDir": False,
                    "children": [],
                }
            },
        ],
    }

    loader = LoadBrowseUrlThread("http://localhost/file_list/root")
    assert loader._verify_data(source) is True
    model = BrowseFileDictModel.load(loader.process_filePath(source))

    level_one = model.children[0]
    level_two = level_one.children[1]
    level_three = level_two.children[1]
    level_four = level_three.children[1]

    assert model.relativePath == Path("shared")
    assert level_one.relativePath == Path("shared/level-one")
    assert level_two.relativePath == Path("shared/level-one/level-two")
    assert level_three.relativePath == Path("shared/level-one/level-two/level-three")
    assert level_four.relativePath == Path(
        "shared/level-one/level-two/level-three/level-four"
    )
    assert level_one.children[0].isDir is False
    assert level_two.children[0].isDir is False
    assert level_three.children[0].isDir is False
    assert level_three.children[1].isDir is True
    assert level_three._prev is level_two


def test_browse_loader_rejects_malformed_wrapped_child_data():
    loader = LoadBrowseUrlThread("http://localhost/file_list/root")
    malformed = {
        "uuid": "root",
        "downloadUrl": "url",
        "fileName": "root",
        "shareType": "http",
        "isDir": True,
        "children": [{"one": {}, "two": {}}],
    }

    assert loader._verify_data(malformed) is False


def test_browse_model_marks_download_url_once():
    model = BrowseFileDictModel.load(
        {
            "uuid": "file",
            "fileName": "note.txt",
            "shareType": "http",
            "downloadUrl": "http://localhost/download/file",
            "relativePath": "note.txt",
            "isDir": False,
            "children": [],
        }
    )

    update_downloadUrl_with_hitLog(model)
    update_downloadUrl_with_hitLog(model)

    assert model.downloadUrl.endswith("?hit_log=true")
    assert model.downloadUrl.count("hit_log") == 1


def test_browse_model_rejects_read_only_property_assignment():
    model = BrowseFileDictModel.load({})

    with pytest.raises(OperationException):
        model.relativePath = Path("other")
