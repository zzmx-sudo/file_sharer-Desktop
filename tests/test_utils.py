"""Tests for utility-layer protocol and cryptography helpers."""

from pathlib import Path

from model.file import FileModel
from utils.credentials import Credentials
from utils.public_func import (
    generate_http_port,
    json_response,
    response_err_msg,
    response_ret_code,
)
from utils.response_code import RET


def test_credentials_hash_is_deterministic_and_password_sensitive(tmp_path: Path):
    target = tmp_path / "file.txt"
    target.write_text("data", encoding="utf-8")
    credentials = Credentials.encode("salt", "password")
    model = FileModel(target, "h-auth", secret_key="salt", credentials=credentials)

    assert credentials.startswith("pbkdf2_sha256$")
    assert Credentials.encode("salt", "password") == credentials
    assert Credentials.encode("salt", "other") != credentials
    assert model.credentials == credentials


def test_response_helpers_preserve_code_message_and_payload():
    payload = json_response(RET.OK, item="value")

    assert response_ret_code(payload) == RET.OK
    assert response_err_msg(payload) == "OK"
    assert payload["item"] == "value"


def test_generate_http_port_skips_occupied_ports(monkeypatch):
    occupied = {8080, 8081}
    monkeypatch.setattr("utils.public_func.exists_port", lambda port: port in occupied)

    assert generate_http_port(8080) == 8082
