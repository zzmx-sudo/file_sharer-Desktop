__all__ = [
    "ServiceProcessManager"
]

from typing import Union

from multiprocessing import Process, Queue

from model.file import FileModel, DirModel
from utils.logger import sysLogger
from .services import HttpService, FtpService

class ServiceProcessManager:

    def __init__(self) -> None:
        self._http_service = None
        self._ftp_service = None
        self._http_input_q = Queue()
        self._ftp_input_q = Queue()
        self._output_q = Queue()

    def add_share(self, uuid: str, fileObj: Union[FileModel, DirModel]) -> bool:
        share_type = uuid[0]
        if share_type == "h":
            return self._add_http_share(uuid, fileObj)
        elif share_type == "f":
            return self._add_ftp_share(uuid, fileObj)
        else:
            sysLogger.error(f"未知的共享类型参数: {share_type}, 共享失败！")
            return False

    def remove_share(self) -> bool:
        pass

    def close_ftp(self) -> bool:
        pass

    def close_all(self) -> bool:
        pass

    def _add_http_share(self, uuid: str, finleObj: Union[FileModel, DirModel]) -> bool:
        pass

    def _add_ftp_share(self, uuid: str, fileObj: Union[FileModel, DirModel]) -> bool:
        pass

    def _add_browse_link(self, uuid: str, fileObj: Union[FileModel, DirModel]) -> bool:
        pass

    def _remove_browse_link(self, uuid: str, fileObj: Union[FileModel, DirModel]) -> bool:
        pass