__all__ = ["BrowseFileDictModel", "BrowseFileDataModel"]

import logging
from typing import Dict, Any, List
from dataclasses import dataclass
from pathlib import Path

from exceptions import OperationException


class BrowseFileDictModel(dict):
    def __init__(self, _sentinel: bool = False):
        """
        浏览目录文件集类初始化函数
        """
        super(BrowseFileDictModel, self).__init__()
        self._current_dict = self
        if not _sentinel:
            self._prev = BrowseFileDictModel(True)
        else:
            self._prev = None

    def prev(self) -> None:
        """
        上一级目录文件集

        Returns:
            None
        """
        prev = self._current_dict._prev
        if prev is None or prev._prev is None:
            self.sysLogger.error("系统错误, 无上级路径的目录下触发了返回上一层")
            return
        self._current_dict = prev

    def reload(self) -> None:
        """
        重制为主目录文件集

        Returns:
            None
        """
        self._current_dict = self

    @property
    def currentDict(self) -> "BrowseFileDictModel":
        """
        当前目录文件集

        Returns:
            BrowseFileDictModel: 当前目录文件
        """
        return self._current_dict

    @currentDict.setter
    def currentDict(self, newValue: "BrowseFileDictModel") -> None:
        """
        修改当前目录文件集

        Args:
            newValue: 将要修改的目录文件集

        Returns:
            None
        """
        self._current_dict = newValue

    @property
    def isRoot(self) -> bool:
        """
        当前是否为主目录文件集

        Returns:
            bool: 当前是否为主目录文件集
        """
        return self._current_dict is self

    @isRoot.setter
    def isRoot(self, newValue: bool) -> None:
        raise OperationException("isRoot属性不可修改")

    @property
    def isDir(self) -> bool:
        """
        主目录是否为文件夹

        Returns:
            bool: 主目录是否为文件夹
        """
        return bool(self["isDir"])

    @isDir.setter
    def isDir(self, newValue: bool) -> None:
        raise OperationException("isDir属性不可修改")

    @property
    def children(self) -> List["BrowseFileDictModel"]:
        """
        子集文件列表, 当前若不是文件夹, 则返回空列表

        Returns:
            List["BrowseFileDictModel"]: 子集文件列表
        """
        return self["children"]

    @children.setter
    def children(self, newValue: List["BrowseFileDictModel"]) -> None:
        raise OperationException("children属性不可通过该方式修改")

    @property
    def fileName(self) -> str:
        """
        文件名称

        Returns:
            str: 文件名称
        """
        return self.get("fileName", "None")

    @fileName.setter
    def fileName(self, newValue: str) -> None:
        raise OperationException("fileName属性不可修改")

    @property
    def shareType(self) -> str:
        """
        文件的分享类型

        Returns:
            str: 文件的分享类型
        """
        return self["shareType"]

    @shareType.setter
    def shareType(self, newValue: str) -> None:
        raise OperationException("shareType属性不可修改")

    @property
    def downloadUrl(self) -> str:
        """
        下载链接

        Returns:
            str: 下载链接
        """
        return self["downloadUrl"]

    @downloadUrl.setter
    def downloadUrl(self, newValue: str) -> None:
        raise OperationException("downloadUrl不可通过该方式修改")

    @property
    def relativePath(self) -> Path:
        """
        相对主目录的路径

        Returns:
            Path: 相对主目录的路径
        """
        return Path(self["relativePath"])

    @relativePath.setter
    def relativePath(self, newValue: Path) -> None:
        raise OperationException("relativePath属性不可修改")

    @property
    def uuid(self) -> str:
        """
        uuid属性

        Returns:
            str: uuid属性
        """
        return self["uuid"]

    @uuid.setter
    def uuid(self, newValue: str) -> None:
        raise OperationException("uuid属性不可修改")

    @property
    def oriUuid(self) -> str:
        """
        作为下载源头的父级文件对象uuid属性, 未加入下载时为`NotFound`

        Returns:
            str: 下载源头的文件对象uuid属性
        """
        return self.get("oriUuid", "NotFound")

    @oriUuid.setter
    def oriUuid(self, newValue: str) -> None:
        """
        修改下载源头的文件对象uuid属性

        Args:
            newValue: 欲修改的uuid属性值

        Returns:
            None
        """
        self["oriUuid"] = newValue

    @property
    def sysLogger(self) -> logging.Logger:
        """
        sysLogger

        Returns:
            logging.Logger: logger.sysLogger
        """
        from utils.logger import sysLogger

        return sysLogger

    @classmethod
    def load(cls, data: Dict[str, Any], with_log: bool = True) -> "BrowseFileDictModel":
        """
        加载数据为目录集

        Args:
            data: 待加载的数据

        Returns:
            BrowseFileDictModel: 浏览目录文件集对象
        """
        model = cls()
        if with_log:
            model.sysLogger.debug("开始读取分享链接的数据")
        if not data:
            return model

        model.update(data)
        if data["isDir"]:
            child_list = cls._load_children(data)
            for child in child_list:
                child._prev = model
            model.update({"children": child_list})

        if with_log:
            model.sysLogger.debug("读取分享链接的数据完成")
        return model

    @classmethod
    def _load_children(cls, data: Dict[str, Any]) -> List["BrowseFileDictModel"]:
        child_list = [cls.load(child, False) for child in data["children"]]

        return child_list


@dataclass
class BrowseFileDataModel:
    """下载文件对象Map表"""

    __doc__ = """
    nativeObj: 原始下载文件对象
    downloadList: 拆分后的需下载的文件对象列表
    count: 该文件对象下文件个数
    """

    nativeObj: BrowseFileDictModel
    downloadList: List[BrowseFileDictModel]
    __file_count: int
    __finish_count: int = 0

    @property
    def isDir(self) -> bool:
        """
        当前下载文件对象是否为文件夹

        Returns:
            bool: 当前是否为文件夹
        """
        return self.nativeObj.isDir

    @property
    def progress(self) -> int:
        """
        当前下载对象的下载进度

        Returns:
            int: 下载进度
        """
        return int(self.__finish_count * 100 / self.__file_count)

    @property
    def allDone(self) -> bool:
        """
        所有文件是否均下载完成

        Returns:
            bool: 所有文件是否均下载完成
        """
        return not self.downloadList and self.__finish_count == self.__file_count

    def increase(self) -> None:
        """
        下载成功文件个数+1

        Returns:
            None
        """
        self.__finish_count += 1
