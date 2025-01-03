__all__ = ["logger"]

import os
import logging
import logging.config
from logging import LogRecord
from typing import Callable

from settings import settings
from exceptions import NotImplException


class BaseLogger:
    def __init__(self):
        """
        logger基类初始化函数
        """
        self._logger = None

    def __getattr__(self, item: str) -> Callable:
        if not self.configured:
            self.configure()

        base_func = getattr(self._logger, item)
        self.__dict__[item] = base_func
        return base_func

    def reload(self) -> None:
        """
        重制logger对象

        Returns:
            None
        """
        # 一定要先clear(),否则无限递归
        self.__dict__.clear()
        self._logger = None

    def configure(self) -> None:
        """
        配置logger对象

        Returns:
            None
        """
        if not os.path.isdir(settings.LOGS_PATH):
            os.makedirs(settings.LOGS_PATH)

        self._setup()
        self._logger = logging.getLogger(self.logger_name)

    def _setup(self) -> None:
        LOGGING = {
            "version": 1,
            "disable_existing_loggers": True,
            "formatters": {
                "debug": {
                    "format": "[%(asctime)s] [%(filename)s:%(lineno)d] [%(module)s:%(funcName)s] [%(levelname)s]- %(message)s"
                },
                "prod": {"format": "[%(asctime)s] [%(levelname)s]- %(message)s"},
            },
            "filters": {
                "require_debug_true": {"()": "utils.logger.RequireDebugTrue"},
                "require_debug_false": {"()": "utils.logger.RequireDebugFalse"},
                "system_log_enable": {"()": "utils.logger.SystemLogEnable"},
                "sharer_log_enable": {"()": "utils.logger.SharerLogEnable"},
            },
            "handlers": {
                "console": {
                    "level": "DEBUG",
                    "filters": ["require_debug_true"],
                    "class": "logging.StreamHandler",
                    "formatter": "debug",
                },
                "system.file": {
                    "level": "INFO",
                    "filters": ["require_debug_false", "system_log_enable"],
                    "class": "logging.handlers.RotatingFileHandler",
                    "maxBytes": 1024 * 1024 * 10,
                    "backupCount": 10,
                    "encoding": "utf-8",
                    "formatter": "prod",
                    "filename": os.path.join(settings.LOGS_PATH, self.log_file),
                },
                "sharer.file": {
                    "level": "INFO",
                    "filters": ["require_debug_false", "sharer_log_enable"],
                    "class": "logging.handlers.RotatingFileHandler",
                    "maxBytes": 1024 * 1024 * 10,
                    "backupCount": 10,
                    "encoding": "utf-8",
                    "formatter": "prod",
                    "filename": os.path.join(settings.LOGS_PATH, self.log_file),
                },
            },
            "loggers": {
                "system": {
                    "handlers": ["console", "system.file"],
                    "level": "DEBUG",
                    "propagate": False,
                },
                "sharer": {
                    "handlers": ["console", "sharer.file"],
                    "level": "DEBUG",
                    "propagate": False,
                },
            },
        }

        logging.config.dictConfig(LOGGING)

    @property
    def configured(self) -> bool:
        """
        判断是否有配置

        Returns:
            bool: 是否有配置
        """
        return self._logger is not None

    @property
    def logger_name(self) -> str:
        """
        logger名称, 需子类定义

        Returns:
            str: logger名称
        """
        raise NotImplException("实现logger对象的类必须有定义`logger_name`属性")

    @property
    def log_file(self) -> str:
        """
        logger文件名, 需子类定义

        Returns:
            str: logger文件名
        """
        raise NotImplException("实现logger对象的类必须有定义`log_file`属性")


class SystemLogger(BaseLogger):
    @property
    def logger_name(self) -> str:
        return "system"

    @property
    def log_file(self) -> str:
        return "system.log"


class SharerLogger(BaseLogger):
    @property
    def logger_name(self) -> str:
        return "sharer"

    @property
    def log_file(self) -> str:
        return "sharer.log"


class RequireDebugTrue(logging.Filter):
    def filter(self, record: LogRecord) -> bool:
        return settings.DEBUG


class RequireDebugFalse(logging.Filter):
    def filter(self, record: LogRecord) -> bool:
        return not settings.DEBUG


class SystemLogEnable(logging.Filter):
    def filter(self, record: LogRecord) -> bool:
        return settings.SAVE_SYSTEM_LOG


class SharerLogEnable(logging.Filter):
    def filter(self, record: LogRecord) -> bool:
        return settings.SAVE_SHARER_LOG


sysLogger = SystemLogger()
sharerLogger = SharerLogger()
