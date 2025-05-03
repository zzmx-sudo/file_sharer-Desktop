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
from typing import Dict, Any, Callable, Tuple, Optional

import toml
from PyQt5.Qt import QApplication, QWidget
from PyQt5.QtGui import QGuiApplication
from model import public_types as ptype
from .response_code import RET, MSG_MAP


def get_system() -> str:
    """
    获取系统类型

    Returns:
        str: 系统类型
    """
    return platform.system()


def generate_uuid() -> str:
    """
    生成uuid

    Returns:
        str: 生成的uuid
    """
    return str(uuid.uuid1()).replace("-", "")


def generate_timestamp() -> int:
    """
    获取毫秒

    Returns:
        int: 毫秒
    """
    return int(time.time() * 1000)


def get_local_ip() -> str:
    """
    获取本地可通讯IP地址

    Returns:
        str: 本地可通讯IP地址
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except:
        try:
            ip = socket.gethostbyname(socket.gethostname())
        except:
            return ""
    finally:
        s.close()

    return ip


def generate_ftp_passwd() -> str:
    """
    生成FTP密码

    Returns:
        str: FTP密码
    """
    base_str = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"

    return "".join(random.sample(base_str, 5))


def generate_secret_key() -> str:
    """
    获取随机盐值

    Returns:
        str: 生成的盐值
    """
    base_str = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"

    return "".join(random.sample(base_str, 12))


def exists_port(port: int) -> bool:
    """
    判断端口是否被占用

    Args:
        port: 被判断端口号

    Returns:
        bool: 是否被占用
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.2)
        sock.connect((get_local_ip(), port))
        sock.close()
        return True
    except:
        return False


def generate_http_port(start_port: int) -> int:
    """
    生成HTTP可用端口

    Args:
        start_port: 起始端口

    Returns:
        int: HTTP可用端口
    """
    if start_port <= 1024:
        start_port = 8080

    if exists_port(start_port):
        start_port += 1
        return generate_http_port(start_port)
    else:
        return start_port


def generate_project_path() -> str:
    """
    生成项目主目录路径

    Returns:
        str: 项目主目录路径
    """
    if getattr(sys, "frozen", False):
        # MacOS的静态文件均放在Resources路径下
        if get_system() == "Darwin":
            return os.path.join(
                os.path.dirname(os.path.dirname(sys.executable)), "Resources"
            )
        else:
            return os.path.dirname(sys.executable)
    else:
        # MacOS下子进程为Resources/lib/python3.*/..., 需剔除到Resources
        curr_path = os.path.abspath(__file__)
        if "Resources" in curr_path:
            return f"{curr_path.split('Resources')[0]}Resources"
        else:
            return os.path.dirname(os.path.dirname(curr_path))


def get_config_from_toml(is_customize: bool = True) -> Dict[str, Any]:
    """
    配置文件转字典

    Args:
        is_customize: 是否为用户配置

    Returns:
        Dict[str, Any]: 转成的字典
    """
    project_path = generate_project_path()
    tool_config = {}
    if is_customize:
        settings_file = os.path.join(project_path, "customize.toml")
        if not os.path.exists(settings_file):
            settings_file = os.path.join(project_path, "pyproject.toml")
    else:
        settings_file = os.path.join(project_path, "pyproject.toml")
    if not os.path.exists(settings_file):
        return tool_config

    try:
        tool_config = toml.load(settings_file)
    except Exception:
        pass

    return tool_config


def generate_product_version() -> str:
    """
    生成项目版本号

    Returns:
        str: 项目版本号
    """
    tool_config = get_config_from_toml(False)

    return tool_config.get("file-sharer", {}).get("version", "0.1.0")


def generate_color_card_map() -> Dict[str, str]:
    """
    生成配置的颜色表(色卡)

    Returns:
        Dict[str, str]: 配置的颜色表
    """
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


def window_reservation_when_box_destroyed(show_box: Callable) -> Callable:
    """
    在弹框前/后分别配置最后窗口关闭时程序不退出和最后窗口关闭时程序退出,
    来修复主窗口隐藏时弹框关闭导致程序退出的BUG

    Args:
        show_box: 弹框执行函数

    Returns:
        Callable: 装饰后的弹框执行函数
    """

    def _inner(*args, **kwargs) -> Any:
        # 在QMessageBox弹出前配置最后窗口关闭程序不退出, 以修复当主窗口隐藏时关闭弹框后程序退出的BUG
        QApplication.setQuitOnLastWindowClosed(False)
        result = show_box(*args, **kwargs)
        # QMessageBox结束后配置最后窗口关闭程序退出, 以修复无法关闭程序的BUG
        QApplication.setQuitOnLastWindowClosed(True)
        return result

    return _inner


def update_downloadUrl_with_hitLog(fileDict: Dict[str, Any]) -> None:
    """
    更新download_url, 以便告知服务端存储下载记录日志

    Args:
        fileDict: 需下载的文件/文件夹对象

    Returns:
        None
    """
    if ptype.HIT_LOG not in fileDict["downloadUrl"]:
        new_download_url = f"{fileDict['downloadUrl']}?{ptype.HIT_LOG}=true"
        fileDict.update({"downloadUrl": new_download_url})


def get_screen_resolution(window: QWidget) -> Tuple[int, int]:
    """
    获取当前屏幕分辨率

    Args:
        window: Qt界面对象

    Returns:
        Tuple[int, int]: 当前屏幕的分辨率 [宽, 高]
    """
    screen = QGuiApplication.screenAt(window.pos()).geometry()

    return screen.width(), screen.height()


def resize_window(
    window: QWidget, min_size: Tuple[int, int], screen_resolution: Tuple[int, int]
) -> None:
    """
    根据Qt界面要求最小大小和当前屏幕分辨率, 重置Qt界面大小

    Args:
        window: Qt界面对象
        min_size: Qt界面要求的最小大小
        screen_resolution: 当前屏幕分辨率

    Returns:
        None
    """
    min_width, min_height = min_size
    screen_width, screen_height = screen_resolution
    width_scale, height_scale = int(1920 / min_width) + 1, int(1080 / min_height) + 1
    if screen_width <= 1920:
        width = min_width
    else:
        width = screen_width // width_scale

    if screen_height <= 1080:
        height = min_height
    else:
        height = screen_height // height_scale

    window.resize(width, height)


def json_response(
    ret: RET.__class__, special_msg: Optional[str] = None, **datas
) -> Dict[str, Any]:
    """
    生成JsonResponse

    Args:
        ret: 返回的errno, 类型为RET类属性
        special_msg: 返回的特殊消息, 为None时根据ret从MSG_MAP获取
        **datas: 其他返回数据

    Returns:
        Dict[str, Any]: 生成的JsonResponse
    """
    special_msg = special_msg or MSG_MAP[ret]

    return {"errno": ret, "errmsg": special_msg, **datas}


def response_ret_code(data: Dict[str, Any]) -> int:
    """
    从后端返回数据中提取errno

    Args:
        data: 后端返回的数据

    Returns:
        int: 后端返回数据中的errno
    """
    return data.get("errno", 10086)


def response_err_msg(data: Dict[str, Any]) -> str:
    """
    从后端返回数据中提取errmsg

    Args:
        data: 后端返回的数据

    Returns:
        str: 后端返回数据中的errno
    """
    return data.get("errmsg", "未知消息")
