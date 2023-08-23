__all__ = [
    "logger"
]

import os
import logging
from typing import Callable

from settings import settings
from exceptions import NotImplException

class BaseLogger:

    def __init__(self) -> None:

        self._logger = None

    def __getattr__(self, item: str) -> Callable:
        if not self.configured:
            self.configure()

        return getattr(self._logger, item)

    def reload(self) -> None:

        self._logger = None

    def configure(self) -> None:

        if not os.path.isdir(self._log_path):
            os.makedirs(self._log_path)

        self._setup()
        self._logger = logging.getLogger(self.logger_name)

    def _setup(self) -> None:

        if settings.DEBUG:
            logger_level = "DEBUG"
        else:
            logger_level = "INFO"

        LOGGING = {
            "disable_existing_loggers": True,
            "formatter": {
                ""
            }
        }

    @property
    def configured(self) -> bool:

        return self._logger is not None

    @property
    def logger_name(self) -> str:

        raise NotImplException("实现logger对象的类必须有定义`logger_name`属性")

    @property
    def log_file(self) -> str:

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


sysLogger = SystemLogger()
sharerLogger = SharerLogger()