__all__ = ["SharingModel", "FuseSharingModel"]

import os
import json
from typing import Union, Optional

from .file import FileModel, DirModel
from .public_types import ShareType as shareType
from settings import settings
from utils.logger import sysLogger


class SharingModel(dict):
    def __setitem__(self, key: str, value: Union[FileModel, DirModel]) -> None:
        super(SharingModel, self).__setitem__(key, value)

    def __delitem__(self, key: str) -> None:
        super(SharingModel, self).__delitem__(key)

    @property
    def length(self) -> int:
        """
        分享的文件/文件夹个数

        Returns:
            int: 分享的文件/文件夹个数
        """
        return len(self)

    @property
    def isEmpty(self) -> bool:
        """
        分享是否为空

        Returns:
            bool: 分享是否为空
        """
        return not self


class FuseSharingModel(list):
    @property
    def length(self) -> int:
        """
        融合分享文件/文件夹个数

        Returns:
            int: 融合分享文件/文件夹个数
        """
        return len(self)

    def append(self, fileObj: Union[FileModel, DirModel]) -> None:
        """
        追加分享文件/文件夹对象

        Args:
            fileObj: 待追加的文件/文件夹对象

        Returns:
            None
        """
        super(FuseSharingModel, self).append(fileObj)
        fileObj.rowIndex = self.length - 1

    def remove(self, rowIndex: int) -> None:
        """
        移除分享文件/文件夹对象

        Args:
            rowIndex: 待移除文件/文件夹对象的行号

        Returns:
            None
        """
        super(FuseSharingModel, self).pop(rowIndex)
        for index in range(rowIndex, self.length):
            self[index].rowIndex -= 1

    def contains(self, target_path: str, share_type: shareType) -> Optional[int]:
        """
        目标分享文件/文件夹对象的行号

        Args:
            target_path: 文件/文件夹对象的路径
            share_type: 文件/文件夹对象的分享类型

        Returns:
            Optional[int]: 目标分享文件/文件夹对象的行号
        """
        for fileObj in self:
            if fileObj == target_path and fileObj.shareType is share_type:
                return fileObj.rowIndex

        return None

    def get_ftp_shared(self, target_path: str) -> Union[FileModel, DirModel, None]:
        """
        获取可复用FTP的文件/文件夹对象

        Args:
            target_path: 待分析文件/文件夹对象的路径

        Returns:
            Union[FileModel, DirModel, None]: 可复用FTP的文件/文件夹对象
        """
        basePath_file_params: dict = {}
        for fileObj in self:
            if fileObj.shareType is shareType.ftp:
                basePath_file_params[fileObj.ftp_basePath] = fileObj

        while os.path.dirname(target_path) != target_path:
            target_path = os.path.dirname(target_path)
            if target_path in basePath_file_params:
                return basePath_file_params[target_path]

        return None

    def dump(self) -> None:
        """
        转存

        Returns:
            None
        """
        backup_result: list = [fileObj.to_dump_backup() for fileObj in self]

        backup_file_path: str = os.path.join(
            settings.BASE_DIR, "file_sharing_backups.json"
        )
        with open(backup_file_path, "w", encoding="utf-8") as f:
            json.dump(
                backup_result, f, indent=4, separators=(",", ": "), ensure_ascii=False
            )

        sysLogger.info("保存历史分享记录成功")

    @classmethod
    def load(cls) -> "FuseSharingModel":
        """
        加载

        Returns:
            FuseSharingModel: 加载成融合分享对象
        """
        model = cls()
        backup_file_path: str = os.path.join(
            settings.BASE_DIR, "file_sharing_backups.json"
        )
        if not os.path.exists(backup_file_path):
            sysLogger.info("file_sharing_backups.json文件不存在, 跳过历史分享记录加载")
            return model

        with open(backup_file_path, encoding="utf-8") as f:
            try:
                backup_result = json.loads(f.read())
            except json.JSONDecodeError:
                sysLogger.error("加载历史分享记录失败, file_sharing_backups.json文件已损坏")
                return model

        path_share_params: list = []
        for file_dict in backup_result:
            targetPath = file_dict.get("path")
            if not targetPath or not os.path.exists(targetPath):
                continue
            # 路径整好看一点
            if settings.IS_WINDOWS:
                targetPath = targetPath.replace("/", "\\")
            else:
                targetPath = targetPath.replace("\\", "/")
            file_dict.update({"path": targetPath})
            path_share_param = (file_dict.get("path"), file_dict.get("share_type"))
            if path_share_param in path_share_params:
                continue
            path_share_params.append(path_share_param)
            isDir = file_dict.get("isDir")
            fileModel = FileModel if not isDir else DirModel
            try:
                fileObj = fileModel(**file_dict)
            except TypeError:
                sysLogger.error("加载历史分享记录失败, file_sharing_backups.json文件已损坏")
                return model
            except FileNotFoundError:
                continue

            model.append(fileObj)

        sysLogger.info("加载历史分享记录成功")
        return model
