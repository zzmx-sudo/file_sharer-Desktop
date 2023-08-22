__all__ = [
    "OperationException"
]

class BaseException(Exception):

    def __init__(self, msg: str) -> None:

        self._msg = msg

    def __str__(self) -> str:

        return self._msg

class OperationException(BaseException):

    def __init__(self, msg: str) -> None:

        self._msg = f"无效的操作, {msg}!"

