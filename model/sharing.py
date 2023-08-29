__all__ = [
    "SharingModel"
]

import os
import json
from typing import Union, TypeVar

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

        return len(self)

    @property
    def isEmpty(self) -> bool:

        return not self

FuseSharingType = TypeVar("FuseSharingType", bound="FuseSharingModel")

class FuseSharingModel(list):

    @property
    def length(self) -> int:

        return len(self)

    def append(self, fileObj: Union[FileModel, DirModel]) -> None:
        
        super(FuseSharingModel, self).append(fileObj)
        fileObj.rowNumber = self.length

    def remove(self, uuid: str) -> None:

        target_index: Union[None, int] = None
        for index,  fileObj in enumerate(self):
            if fileObj.uuid == uuid:
                super(FuseSharingModel, self).pop(index)
                target_index = index
                break

        if target_index is None:
            return

        for index in range(target_index, self.length):
            self[index].rowNumber -= 1

    def contains(self, target_path: str, share_type: shareType) -> Union[None, int]:
        for fileObj in self:
            if fileObj == target_path and fileObj.shareType is share_type:
                return fileObj.rowNumber

        return None

    def get_ftp_shared(self, target_path: str) -> Union[None, FileModel, DirModel]:

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

        backup_result: list = []
        backup_file_path: str = os.path.join(settings.BASE_DIR, "file_sharing_backups.json")

        for fileObj in self:
            backup_result.append(fileObj.to_dump_backup())

        with open(backup_file_path, "w") as f:
            json.dump(backup_result, f, indent=4, separators=(",", ": "), ensure_ascii=False)

        sysLogger.info("保存历史分享记录成功")

    @classmethod
    def load(cls) -> FuseSharingType:

        model = cls()
        backup_file_path: str = os.path.join(settings.BASE_DIR, "file_sharing_backups.json")
        if not os.path.exists(backup_file_path):
            sysLogger.info("file_sharing_backups.json文件不存在, 跳过历史分享记录加载")
            return model

        with open(backup_file_path) as f:
            try:
                backup_result = json.loads(f.read())
            except json.decoder.JSONDecodeError:
                sysLogger.error("加载历史分享记录失败, file_sharing_backups.json文件已损坏")
                return model

        for file_dict in backup_result:
            isDir = file_dict.get("isDir")
            fileModel = FileModel if not isDir else DirModel
            try:
                fileObj = fileModel(**file_dict)
            except TypeError:
                sysLogger.error("加载历史分享记录失败, file_sharing_backups.json文件已损坏")
                return model

            model.append(fileObj)

        sysLogger.info("加载历史分享记录成功")
        return model