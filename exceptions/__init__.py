__all__ = [
    "OperationException",
    "NotImplException"
]

class BaseException(Exception):

    def __init__(self, msg: str) -> None:

        self._msg = msg

    def __str__(self) -> str:

        return self._msg

class OperationException(BaseException):

    def __init__(self, msg: str) -> None:

        self._msg = f"无效的操作, {msg}!"

class NotImplException(BaseException):

    def __init__(self, msg: str) -> None:

        self._msg = f"未实现错误, {msg}!"

class UnknowParamException(BaseException):

    def __init__(self, msg: str) -> None:

        self._msg = f"未知的参数, {msg}!"