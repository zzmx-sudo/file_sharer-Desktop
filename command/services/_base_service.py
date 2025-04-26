__all__ = ["BaseService"]

from typing import Union, Dict
from threading import Thread
from multiprocessing import Queue

from model.sharing import SharingModel
from model.file import FileModel, DirModel
from exceptions import NotImplException, OperationException
from settings import settings
from utils.logger import sysLogger, sharerLogger


class BaseService:
    def __init__(self, input_q: Queue, output_q: Queue):
        """
        共享服务类初始化函数

        Args:
            input_q: 输入的进程队列
            output_q: 输出的进程队列
        """
        self._sharing_dict: Dict[str, Union[FileModel, DirModel]] = SharingModel()
        self._input_q = input_q
        self._output_q = output_q
        self._watch_thread = None
        self._service_name = ""

    def watch(self) -> None:
        """
        共享服务的监听函数

        Returns:
            None
        """
        self._sysLogger_debug("开启监听线程")
        self._watch_thread = Thread(target=self._watch)
        self._watch_thread.setDaemon(True)
        self._watch_thread.start()
        self._sysLogger_debug("监听线程开启成功")

    def _watch(self) -> None:
        while True:
            command_type, command_msg = self._input_q.get()
            if command_type == "add":
                self._sysLogger_debug(f"接到添加分享任务, 分享路径: {command_msg.targetPath}")
                self._add_share(command_msg)
            elif command_type == "remove":
                self._sysLogger_debug(f"接到移除分享任务, 分享的uuid: {command_msg}")
                self._remove_share(command_msg)
            elif command_type == "settings":
                self._sysLogger_debug(f"接到同步配置任务, 配置参数: {command_msg}")
                self._modify_settings(*command_msg)
            elif command_type == "free-secret":
                self._sysLogger_debug(f"接到修改免密状态任务, 配置参数: {command_msg}")
                self._change_free_secret(*command_msg)

    def _add_share(self, fileObj: Union[FileModel, DirModel]) -> None:
        """
        添加共享文件或文件夹, 具体实现在各共享服务子类中

        Args:
            fileObj: 待添加共享的文件或文件夹对象

        Returns:
            None
        """
        raise NotImplException("实现service对象的类必须有定义`_add_share`方法")

    def _remove_share(self, uuid: str) -> None:
        """
        移除共享文件或文件夹, 具体实现在各共享服务子类中

        Args:
            uuid: 待移除共享文件或文件夹的uuid

        Returns:
            None
        """
        raise NotImplException("实现service对象的类必须有定义`_remove_share`方法")

    def _modify_settings(self, *args) -> None:
        """
        同步更改配置项

        Args:
            *args: 待同步的配置项

        Returns:
            None
        """
        self._sysLogger_debug("开始同步配置项")
        if len(args) != 2:
            sysLogger.error(
                f"[{self._service_name}] 同步配置任务参数个数不合法, 参数个数需为2, 得到的任务参数个数: {len(args)}"
            )
            return
        setattr(settings, args[0], args[1])
        if args[0] == "LOGS_PATH":
            sysLogger.reload()
            sharerLogger.reload()
        self._sysLogger_debug("同步配置完成")

    def _change_free_secret(self, uuid: str, value: bool) -> None:
        """
        修改文件/文件夹对象的免密状态

        Args:
            uuid: 待修改文件/文件夹对象的uuid
            value: 待修改的免密状态

        Returns:
            None
        """
        raise NotImplException("实现service对象的类必须有定义`_change_free_secret`方法")

    def _sysLogger_debug(self, msg) -> None:
        """
        添加系统debug日志

        Args:
            msg: 要添加的日志内容
        """
        sysLogger.debug(f"[{self._service_name}] {msg}")

    def run(self) -> None:
        """
        进程运行入口函数, 基类中仅实现关闭控制台输出, 其他功能实现在各共享服务子类中

        Returns:
            None
        """
        if not settings.DEBUG:
            import sys, os

            sys.stdout = open(os.devnull, "w")
            sys.stderr = open(os.devnull, "w")

        if self._watch_thread is None:
            raise OperationException("在service运行前必须先开启watch线程")
