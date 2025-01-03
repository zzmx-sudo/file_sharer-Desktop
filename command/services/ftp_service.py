__all__ = ["FtpService"]

import sys
import time
from typing import Union
from multiprocessing import Queue
from threading import Thread

from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer

from ._base_service import BaseService
from model.file import FileModel, DirModel
from settings import settings


class UuidServerMode(dict):
    pass


class FtpService(BaseService):
    def __init__(self, input_q: Queue, output_q: Queue):
        """
        FTP共享服务类初始化函数

        Args:
            input_q: 输入的进程队列
            output_q: 输出的进程队列
        """
        super(FtpService, self).__init__(input_q, output_q)
        self._uuid_ftpServer_params = UuidServerMode()

    def _add_share(self, fileObj: Union[FileModel, DirModel]) -> None:
        """
        添加共享文件或文件夹

        Args:
            fileObj: 待添加共享的文件或文件夹对象

        Returns:
            None
        """
        self._sharing_dict.update({fileObj.uuid: fileObj})
        need_start_new_server: bool = True
        for ftpServer in self._uuid_ftpServer_params.values():
            if ftpServer.address[1] == fileObj.ftp_port:
                need_start_new_server = False
                break

        if need_start_new_server:
            self._start_new_server(fileObj)

    def _remove_share(self, uuid: str) -> None:
        """
        移除共享文件或文件夹

        Args:
            uuid: 待移除共享文件或文件夹的uuid

        Returns:
            None
        """
        if uuid in self._sharing_dict:
            del self._sharing_dict[uuid]

        ftpServer = self._uuid_ftpServer_params.get(uuid)
        if ftpServer is None:
            return

        need_close_server = True
        for fileObj in self._sharing_dict.values():
            if fileObj.ftp_port == ftpServer.address[1]:
                need_close_server = False
                self._uuid_ftpServer_params[fileObj.uuid] = ftpServer
                break

        if need_close_server:
            self._uuid_ftpServer_params[uuid].close_when_done()
        del self._uuid_ftpServer_params[uuid]

    def _start_new_server(self, fileObj: Union[FileModel, DirModel]) -> None:
        host: str = settings.LOCAL_HOST
        port: int = fileObj.ftp_port
        passwd: str = fileObj.ftp_pwd

        authorizer = DummyAuthorizer()
        authorizer.add_user("a", passwd, fileObj.ftp_basePath, perm="elr")
        handler = FTPHandler
        handler.authorizer = authorizer
        address: tuple = (host, port)

        server = FTPServer(address, handler)
        t = Thread(target=server.serve_forever)
        t.setDaemon(True)
        t.start()

        self._uuid_ftpServer_params[fileObj.uuid] = server

    def run(self) -> None:
        """
        FTP服务进程运行入口函数

        Returns:
            None
        """
        self.watch()
        super(FtpService, self).run()

        while True:
            try:
                time.sleep(1000)
            except KeyboardInterrupt:
                sys.exit(0)
