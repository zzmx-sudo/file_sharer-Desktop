__all__ = [
    "logger"
]

from settings import settings


class BaseLogger:

    def __init__(self) -> None:

        pass

    def info(self) -> None:

        pass

    def reload(self) -> None:

        print(settings.LOGS_PATH)


logger = BaseLogger()