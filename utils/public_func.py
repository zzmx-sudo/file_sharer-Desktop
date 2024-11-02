__all__ = [
    "get_system",
    "generate_uuid",
    "generate_timestamp",
    "get_local_ip",
    "generate_ftp_passwd",
    "exists_port",
    "generate_http_port",
    "generate_project_path",
    "get_config_from_toml",
    "generate_product_version",
]

import time
import socket
import random
import os
import sys
import platform
import uuid
import json

import toml


def get_system() -> str:
    return platform.system()


def generate_uuid() -> str:
    return str(uuid.uuid1()).replace("-", "")


def generate_timestamp() -> int:
    return int(time.time() * 1000)


def get_local_ip() -> str:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except:
        ip = socket.gethostbyname(socket.gethostname())
    finally:
        s.close()

    return ip


def generate_ftp_passwd() -> str:
    base_str = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"

    return "".join(random.sample(base_str, 5))


def exists_port(port: int) -> bool:
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.2)
        sock.connect((get_local_ip(), port))
        sock.close()
        return True
    except:
        return False


def generate_http_port(start_port: int) -> int:
    if start_port <= 1024:
        start_port = 8080

    if exists_port(start_port):
        start_port += 1
        return generate_http_port(start_port)
    else:
        return start_port


def generate_project_path() -> str:
    if getattr(sys, "frozen", False):
        # MacOS的静态文件均放在Resources路径下
        if get_system() == "Darwin":
            return os.path.join(
                os.path.dirname(os.path.dirname(sys.executable)), "Resources"
            )
        else:
            return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_config_from_toml() -> dict:
    project_path = generate_project_path()
    tool_config = {}
    settings_file = os.path.join(project_path, "pyproject.toml")
    if not os.path.exists(settings_file):
        return tool_config

    try:
        tool_config = toml.load(settings_file)
    except Exception:
        pass

    return tool_config


def generate_product_version() -> str:
    tool_config = get_config_from_toml()

    return tool_config.get("file-sharer", {}).get("version", "0.1.0")


def generate_color_card_map() -> dict:
    project_path = generate_project_path()
    color_card_json_path = os.path.join(
        project_path, "static", "themes", "color_card.json"
    )
    if not os.path.exists(color_card_json_path):
        color_card_json_path = os.path.join(project_path, "color_card.json")
    if not os.path.exists(color_card_json_path):
        return {}

    with open(color_card_json_path, encoding="utf-8") as f:
        try:
            return json.load(f)
        except:
            return {}
