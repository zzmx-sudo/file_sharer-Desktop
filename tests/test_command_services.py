"""Unit tests for service dispatch, share state, and stream responses."""

import asyncio
from pathlib import Path
from queue import Queue

from command.manage import ServiceProcessManager
from command.services.ftp_service import FtpService
from command.services.http_service import HttpService, MyRequest
from model.file import FileModel
from model.public_types import ShareType


class _Request:
    def __init__(self, range_header=""):
        self.headers = {"range": range_header}


def test_service_manager_routes_http_and_ftp_operations(tmp_path: Path, monkeypatch):
    manager = ServiceProcessManager(Queue())
    http_file = tmp_path / "http.txt"
    ftp_file = tmp_path / "ftp.txt"
    http_file.write_text("http", encoding="utf-8")
    ftp_file.write_text("ftp", encoding="utf-8")
    http_model = FileModel(http_file, "h-http")
    ftp_model = FileModel(ftp_file, "f-ftp", pwd="secret", port=21001)
    calls = []
    monkeypatch.setattr(
        manager,
        "_add_http_share",
        lambda item: calls.append(("http", item.uuid)) or True,
    )
    monkeypatch.setattr(
        manager, "_add_ftp_share", lambda item: calls.append(("ftp", item.uuid)) or True
    )
    monkeypatch.setattr(
        manager,
        "_remove_http_share",
        lambda uuid: calls.append(("remove-http", uuid)) or True,
    )
    monkeypatch.setattr(
        manager,
        "_remove_ftp_share",
        lambda uuid: calls.append(("remove-ftp", uuid)) or True,
    )

    assert manager.add_share(http_model) is True
    assert manager.add_share(ftp_model) is True
    assert manager.remove_share(http_model.uuid) is True
    assert manager.remove_share(ftp_model.uuid) is True
    assert calls == [
        ("http", "h-http"),
        ("http", "f-ftp"),
        ("ftp", "f-ftp"),
        ("remove-http", "h-http"),
        ("remove-http", "f-ftp"),
        ("remove-ftp", "f-ftp"),
    ]


def test_http_service_changes_share_state_without_network(tmp_path: Path):
    target = tmp_path / "shared.txt"
    target.write_text("content", encoding="utf-8")
    service = HttpService(Queue(), Queue())
    model = FileModel(target, "h-state")

    service._add_share(model)
    service._change_free_secret(model.uuid, True)
    service._remove_share(model.uuid)

    assert model.free_secret is True
    assert model.uuid not in service._sharing_dict


def test_ftp_service_reuses_server_without_opening_socket(tmp_path: Path, monkeypatch):
    target = tmp_path / "shared.txt"
    target.write_text("content", encoding="utf-8")
    service = FtpService(Queue(), Queue())
    model = FileModel(target, "f-state", pwd="secret", port=21001)
    started = []

    class FakeServer:
        address = ("127.0.0.1", 21001)

    def start_server(item):
        started.append(item.uuid)
        service._uuid_ftpServer_params[item.uuid] = FakeServer()

    monkeypatch.setattr(service, "_start_new_server", start_server)

    service._add_share(model)
    service._add_share(model)

    assert started == [model.uuid]
    assert service._sharing_dict[model.uuid] is model
    assert model.shareType is ShareType.ftp


def test_http_stream_response_uses_end_exclusive_range_header(tmp_path: Path):
    target = tmp_path / "payload.bin"
    target.write_bytes(b"abcdef")
    model = FileModel(target, "h-stream")

    response = asyncio.run(
        HttpService.generate_file_stream_response(_Request("bytes=2-4"), model)
    )

    async def read_body():
        return b"".join([chunk async for chunk in response.body_iterator])

    # The existing stream generator treats the end value as exclusive.
    assert asyncio.run(read_body()) == b"cd"
    assert response.status_code == 206
    assert response.headers["content-range"] == "2-4/6"


def test_my_request_identifies_client_header():
    request = MyRequest(
        {
            "client": ("127.0.0.1", 1234),
            "path": "/file",
            "headers": [(b"x-client", b"desktop")],
        }
    )

    assert request["client"] == ("127.0.0.1", 1234)
    assert request["path"] == "/file"
    assert request["is_client"] == "True"
