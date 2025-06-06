__all__ = ["settings"]

import os
import importlib
from typing import Any, Optional

import toml
from PyQt5.Qt import QWidget

from exceptions import OperationException
from settings import _base
from utils.public_func import (
    generate_http_port,
    get_config_from_toml,
    generate_color_card_map,
    get_screen_resolution,
)
from model.public_types import (
    ThemeColor as themeColor,
    ColorCardStruct,
    ControlColorStruct,
)

empty = object()


class configurable(object):
    pass


class FuseSettings:
    _wrapper = empty

    def __init__(self, mode: str):
        """
        融合配置类初始化函数

        Args:
            mode: 配置模式
        """
        self.__mode = mode

    def _setup(self) -> None:
        _wrapper = configurable()
        if self.__mode == "develop":
            _wrapper.SETTINGS_MODE = "settings.development"
        elif self.__mode == "prod":
            _wrapper.SETTINGS_MODE = "settings.production"
        else:
            raise OperationException(f"不被允许的环境模式参数: {self.__mode}")

        for setting in dir(_base):
            if setting.isupper():
                setattr(_wrapper, setting, getattr(_base, setting))
        self._wrapper = _wrapper

        mod = importlib.import_module(self.SETTINGS_MODE)
        lock_settings = [
            "BASE_DIR",
            "SYSTEM",
            "IS_WINDOWS",
            "LOCAL_HOST",
            "CURR_RESOLUTION",
        ]

        for setting in dir(mod):
            if setting.isupper():
                if setting in lock_settings:
                    raise OperationException(f"不可修改的参数: {setting}")
                elif setting == "LOGS_PATH":
                    self._check_logs_path(getattr(mod, setting))

                setattr(self._wrapper, setting, getattr(mod, setting))

    def __getattr__(self, item: str) -> Any:
        if self._wrapper is empty:
            self._setup()
            self._load()
        val = getattr(self._wrapper, item)
        self.__dict__[item] = val

        return val

    def __setattr__(self, key: str, value: Any) -> None:
        if key == "_wrapper":
            self.__dict__.clear()
        elif key == "LOGS_PATH":
            self._check_logs_path(value)
            self.__dict__.pop(key, None)
        else:
            self.__dict__.pop(key, None)

        super(FuseSettings, self).__setattr__(key, value)

    def __delattr__(self, item: str) -> None:
        super(FuseSettings, self).__delattr__(item)
        self.__dict__.pop(item, None)

    def __repr__(self) -> str:
        if self._wrapper is empty:
            return "<FuseSettings [Unevaluated]>"
        else:
            return f"<FuseSettings Custom fetch to {self.SETTINGS_MODE}>"

    @staticmethod
    def _check_logs_path(logs_path: str) -> None:
        if not os.path.isdir(logs_path):
            raise OperationException(f"配置的日志文件夹路径不存在, LOGS_PATH: {logs_path}")

    def _load(self) -> None:
        from utils.logger import sysLogger

        sysLogger.debug("开始读取配置")
        tool_config = get_config_from_toml()
        if not tool_config:
            return

        settings_config = tool_config.get("file-sharer")
        if not settings_config or not isinstance(settings_config, dict):
            return

        self._wrapper.SAVE_SYSTEM_LOG = settings_config.get("saveSystemLog", True)
        self._wrapper.SAVE_SHARER_LOG = settings_config.get("saveShareLog", True)
        logsPath = settings_config.get("logsPath")
        if logsPath and os.path.isdir(logsPath):
            self._wrapper.LOGS_PATH = logsPath
        downloadPath = settings_config.get("downloadPath")
        if downloadPath and os.path.isdir(downloadPath):
            self._wrapper.DOWNLOAD_DIR = downloadPath
        theme_color = themeColor.dispatch(settings_config.get("theme_color", "Default"))
        self._wrapper.THEME_COLOR = theme_color or self.THEME_COLOR
        theme_opacity = settings_config.get("theme_opacity", 99)
        self._wrapper.THEME_OPACITY = (
            theme_opacity if isinstance(theme_opacity, int) else 99
        )
        color_card_map = generate_color_card_map()
        self._wrapper.COLOR_CARD = ColorCardStruct.dispatch(**color_card_map)
        sysLogger.debug("读取配置完成")

    def _available_http_port(self) -> None:
        http_port = self._wrapper.__dict__.get("WSGI_PORT", 8080)
        available_http_port = generate_http_port(http_port)

        self._wrapper.WSGI_PORT = available_http_port

    def dump(self) -> None:
        """
        转存

        Returns:
            None
        """
        from utils.logger import sysLogger

        sysLogger.debug("开始写入配置")
        settings_file = os.path.join(self.BASE_DIR, "customize.toml")
        try:
            tool_config = toml.load(settings_file)
        except Exception:
            tool_config = {}

        tool_config.update(
            {
                "file-sharer": {
                    "saveSystemLog": self.SAVE_SYSTEM_LOG,
                    "saveShareLog": self.SAVE_SHARER_LOG,
                    "logsPath": self.LOGS_PATH,
                    "downloadPath": self.DOWNLOAD_DIR,
                    "theme_color": self.THEME_COLOR.name,
                    "theme_opacity": self.THEME_OPACITY,
                }
            }
        )
        with open(settings_file, "w", encoding="utf-8") as f:
            toml.dump(tool_config, f)
        sysLogger.debug("写入配置完成")

    def style_sheet(
        self,
        theme_color: Optional[themeColor] = None,
        theme_opacity: Optional[int] = None,
    ) -> str:
        """
        主程序窗口全局样式表

        Args:
            theme_color: 主题颜色
            theme_opacity: 透明度

        Returns:
            str: 主程序窗口全局样式表
        """
        theme_color = theme_color or self.THEME_COLOR
        theme_opacity = theme_opacity or self.THEME_OPACITY
        control_color = getattr(self.COLOR_CARD, theme_color.value)
        control_color_map = control_color._asdict()
        control_color_map.update({"ThemeOpacity": theme_opacity / 100})
        return self.BASIC_QSS % (control_color_map)

    def resize_window(self, *windows: QWidget) -> None:
        """

        Args:
            *windows: 各Qt界面对象

        Returns:
            None
        """
        self.CURR_RESOLUTION = get_screen_resolution(windows[0])

        for window in windows:
            window.resize()

    def controlColor(
        self, theme_color: Optional[themeColor] = None
    ) -> ControlColorStruct:
        """
        主题样式对象

        Args:
            theme_color: 主题颜色

        Returns:
            ControlColorStruct: 主题样式对象
        """
        theme_color = theme_color or self.THEME_COLOR
        return getattr(self.COLOR_CARD, theme_color.value)

    @property
    def initStyle(self) -> str:
        """
        初始化主程序窗口全局样式表

        Returns:
            str: 初始化主程序窗口全局样式表
        """
        return self.style_sheet()

    def init_wsgi_port(self) -> int:
        """
        获取有效WSGI端口

        Returns:
            int: 可用的WSGI端口
        """
        if self._wrapper is empty:
            self._setup()
            self._load()
        self._available_http_port()

        return self._wrapper.WSGI_PORT


settings = FuseSettings("prod")
