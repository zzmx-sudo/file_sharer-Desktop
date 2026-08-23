"""Regression tests for shared-file domain objects."""

import asyncio
from pathlib import Path

from model.file import FileModel
from model.public_types import ShareType
from settings import settings


def test_http_directory_model_exposes_pathlib_paths_and_children(tmp_path: Path):
    shared_dir = tmp_path / "shared"
    shared_dir.mkdir()
    child_file = shared_dir / "readme.txt"
    child_file.write_text("hello", encoding="utf-8")

    model = FileModel(shared_dir, "h-share")

    assert model.targetPath == shared_dir
    assert model.isDir is True
    assert model.isExists is True
    assert model.shareType is ShareType.http
    assert model.ftp_basePath is None
    assert len(model._children) == 1
    assert next(iter(model._children.values())).targetPath == child_file


def test_file_model_serializes_paths_at_external_boundaries(
    tmp_path: Path, monkeypatch
):
    shared_file = tmp_path / "document.txt"
    shared_file.write_text("payload", encoding="utf-8")
    monkeypatch.setattr(settings, "LOCAL_HOST", "127.0.0.1")
    monkeypatch.setattr(settings, "WSGI_PORT", 8080, raising=False)
    model = FileModel(shared_file, "h-file")

    backup = model.to_dump_backup()
    mobile_data = asyncio.run(model.to_dict_mobile())
    server_data = asyncio.run(model.to_dict_server())

    assert backup["path"] == str(shared_file)
    assert mobile_data["targetPath"] == str(shared_file)
    assert server_data["targetPath"] == str(shared_file)
    assert model.file_name == "document.txt"
    assert model.file_size == len("payload")


def test_ftp_file_uses_parent_directory_as_default_ftp_root(
    tmp_path: Path, monkeypatch
):
    shared_file = tmp_path / "archive.zip"
    shared_file.write_bytes(b"zip")
    monkeypatch.setattr(FileModel, "_generate_ftp_port", lambda self: 21001)

    model = FileModel(shared_file, "f-file", pwd="secret")

    assert model.shareType is ShareType.ftp
    assert model.ftp_port == 21001
    assert model.ftp_basePath == tmp_path
