__all__ = [
    "ServiceProcessManager"
]

from typing import Union
from multiprocessing import Process, Queue

import psutil

from model.file import FileModel, DirModel
from model import public_types as ptype
from utils.logger import sysLogger
from . services import HttpService, FtpService

class ServiceProcessManager:

    def __init__(self, output_q: Queue) -> None:
        self._http_service = None
        self._ftp_service = None
        self._http_input_q = Queue()
        self._ftp_input_q = Queue()
        self._output_q = output_q

    def add_share(self, fileObj: Union[FileModel, DirModel]) -> bool:
        share_type = fileObj.shareType
        if share_type is ptype.ShareType.http:
            return self._add_http_share(fileObj)
        elif share_type is ptype.ShareType.ftp:
            self._add_http_share(fileObj)
            return self._add_ftp_share(fileObj)
        else:
            sysLogger.error(f"未知的共享类型参数: {share_type}, 共享失败！")
            return False

    def remove_share(self, uuid: str) -> bool:
        share_type = uuid[0]
        if share_type == "f":
            self._remove_http_share(uuid)
            return self._remove_ftp_share(uuid)
        elif share_type == "h":
            return self._remove_http_share(uuid)
        else:
            sysLogger.error(f"未知的共享类型参数: {share_type}, 共享失败！")
            return False

    def close_ftp(self) -> bool:
        if self._ftp_service is not None:
            self._kill_process(self._ftp_service.pid)

        return True

    def close_all(self) -> bool:
        self.close_ftp()
        if self._http_service is not None:
            self._kill_process(self._http_service.pid)

        return True

    def _add_http_share(self, fileObj: Union[FileModel, DirModel]) -> bool:
        if self._http_service is None:
            http_service = HttpService(self._http_input_q, self._output_q)
            self._http_service = Process(target=http_service.run)
            self._http_service.daemon = True
            self._http_service.start()

        self._http_input_q.put(("add", fileObj))
        return True

    def _add_ftp_share(self, fileObj: Union[FileModel, DirModel]) -> bool:
        if self._ftp_service is None:
            ftp_service = FtpService(self._ftp_input_q, self._output_q)
            self._ftp_service = Process(target=ftp_service.run)
            self._ftp_service.daemon = True
            self._ftp_service.start()

        self._ftp_input_q.put(("add", fileObj))
        return True

    def _remove_http_share(self, uuid: str) -> bool:
        self._http_input_q.put(("remove", uuid))
        return True

    def _remove_ftp_share(self, uuid: str) -> bool:
        self._ftp_input_q.put(("remove", uuid))
        return True

    @staticmethod
    def _kill_process(pid: int) -> None:
        try:
            process = psutil.Process(pid)
        except psutil.NoSuchProcess:
            return

        for child in process.children(recursive=True):
            child.kill()

        process.kill()