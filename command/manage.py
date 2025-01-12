__all__ = ["ServiceProcessManager"]

from typing import Union
from multiprocessing import Queue, Process

import psutil

from model.file import FileModel, DirModel
from model import public_types as ptype
from utils.logger import sysLogger
from .services import HttpService, FtpService


class ServiceProcessManager:
    def __init__(self, output_q: Queue):
        """
        共享服务进程管理器类初始化函数

        Args:
            output_q: 结果输出的进程队列
        """
        self._http_service = None
        self._ftp_service = None
        self._http_input_q = None
        self._ftp_input_q = None
        self._output_q = output_q

    def add_share(self, fileObj: Union[FileModel, DirModel]) -> bool:
        """
        添加分享文件或文件夹

        Args:
            fileObj: 待添加共享的文件或文件夹对象

        Returns:
            bool: 是否成功添加
        """
        sysLogger.debug(
            f"正在添加分享, 分享路径: {fileObj.targetPath}, 分享类型: {fileObj.shareType}"
        )
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
        """
        移除分享文件或文件夹

        Args:
            uuid: 待移除共享文件或文件夹的uuid

        Returns:
            bool: 是否成功移除
        """
        sysLogger.debug(f"正在移除分享, 分享的uuid: {uuid}")
        share_type = uuid[0]
        if share_type == "f":
            self._remove_http_share(uuid)
            return self._remove_ftp_share(uuid)
        elif share_type == "h":
            return self._remove_http_share(uuid)
        else:
            sysLogger.error(f"未知的共享类型参数: {share_type}, 共享失败！")
            return False

    def modify_settings(self, key: str, value: Union[bool, str]) -> bool:
        """
        同步更改配置项

        Args:
            key: 配置参数名
            value: 配置参数的值

        Returns:
            bool: 是否成功同步更改
        """
        sysLogger.debug(f"正在同步配置, 配置项名称: {key}, 配置项值: {value}")
        if self._http_input_q is not None:
            self._http_input_q.put(("settings", (key, value)))
        if self._ftp_input_q is not None:
            self._ftp_input_q.put(("settings", (key, value)))

        return True

    def close_ftp(self) -> bool:
        """
        关闭FTP共享服务

        Returns:
            bool: 是否成功关闭FTP共享服务
        """
        sysLogger.debug("[FTP] 正在关闭服务")
        if self._ftp_service is not None:
            self._kill_process(self._ftp_service.pid)

        self._ftp_service = None
        if self._ftp_input_q is not None:
            sysLogger.debug("[FTP] 正在关闭输入队列")
            self._ftp_input_q.close()
            self._ftp_input_q = None
            sysLogger.debug("[FTP] 关闭输入队列成功")
        return True

    def close_all(self) -> bool:
        """
        关闭所有共享服务, 包括HTTP服务和FTP服务

        Returns:
            bool: 是否成功关闭所有服务
        """
        sysLogger.debug("正在关闭所有分享服务")
        self.close_ftp()
        if self._http_service is not None:
            sysLogger.debug("[HTTP] 正在关闭服务")
            self._kill_process(self._http_service.pid)

        self._http_service = None
        if self._http_input_q is not None:
            sysLogger.debug("[HTTP] 正在关闭输入队列")
            self._http_input_q.close()
            self._http_input_q = None
            sysLogger.debug("[HTTP] 关闭输入队列成功")
        sysLogger.debug("关闭所有分享服务成功")
        return True

    def _add_http_share(self, fileObj: Union[FileModel, DirModel]) -> bool:
        sysLogger.debug(f"[HTTP] 开始添加分享, 分享路径: {fileObj.targetPath}")
        if self._http_input_q is None:
            sysLogger.debug("[HTTP] 开始初始化输入队列")
            self._http_input_q = Queue()
            sysLogger.debug("[HTTP] 初始化输入队列成功")
        if self._http_service is None:
            sysLogger.debug("[HTTP] 开始初始化服务")
            http_service = HttpService(self._http_input_q, self._output_q)
            self._http_service = Process(target=http_service.run)
            self._http_service.daemon = True
            self._http_service.start()

        sysLogger.debug("[HTTP] 开始添加分享")
        self._http_input_q.put(("add", fileObj))
        return True

    def _add_ftp_share(self, fileObj: Union[FileModel, DirModel]) -> bool:
        sysLogger.debug(f"[FTP] 开始添加分享, 分享路径: {fileObj.targetPath}")
        if self._ftp_input_q is None:
            sysLogger.debug("[FTP] 开始初始化输入队列")
            self._ftp_input_q = Queue()
            sysLogger.debug("[FTP] 初始化输入队列成功")
        if self._ftp_service is None:
            sysLogger.debug("[FTP] 开始初始化服务")
            ftp_service = FtpService(self._ftp_input_q, self._output_q)
            self._ftp_service = Process(target=ftp_service.run)
            self._ftp_service.daemon = True
            self._ftp_service.start()

        sysLogger.debug("[FTP] 开始追加分享")
        self._ftp_input_q.put(("add", fileObj))
        return True

    def _remove_http_share(self, uuid: str) -> bool:
        sysLogger.debug(f"[HTTP] 正在移除分享, 分享的uuid: {uuid}")
        self._http_input_q.put(("remove", uuid))
        return True

    def _remove_ftp_share(self, uuid: str) -> bool:
        sysLogger.debug(f"[FTP] 正在移除分享, 分享的uuid: {uuid}")
        self._ftp_input_q.put(("remove", uuid))
        return True

    @staticmethod
    def _kill_process(pid: int) -> None:
        sysLogger.debug(f"开始关闭进程: {pid}")
        try:
            process = psutil.Process(pid)
        except psutil.NoSuchProcess:
            sysLogger.debug("进程号没在运行")
            return

        for child in process.children(recursive=True):
            sysLogger.debug(f"正在关闭子进程: {child.pid}")
            child.kill()

        sysLogger.debug(f"正在关闭主进程: {pid}")
        process.kill()
        sysLogger.debug("进程关闭成功")
