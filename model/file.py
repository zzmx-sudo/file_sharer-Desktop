__all__ = [
    "FileModel",
    "DirModel"
]

import os
import random
from typing import Any, Union

from PyQt5.Qt import QPushButton

from model import public_types as ptype
from settings import settings
from utils import public_func
from utils.ui_function import UiFunction

class FileModel:

    def __init__(
        self,
        path: str,
        uuid: str,
        parent_uuid: Union[None, str] = None,
        pwd: Union[None, str] = None,
        port: Union[None, int] = None,
        ftp_base_path: Union[None, str] = None,
        **kwargs
    ) -> None:

        self._uuid = f"{parent_uuid}>{uuid}" if parent_uuid else uuid
        self._target_path = path.rstrip(os.sep) if path.endswith(os.sep) else path
        self._download_number = 0
        self._is_sharing = False
        self._row_index = None
        self._ftp_pwd = pwd
        self._ftp_port = port

        if self._uuid[0] == "h":
            self._share_type = ptype.ShareType.http
        else:
            self._share_type = ptype.ShareType.ftp

        if self._share_type is ptype.ShareType.ftp:
            self._ftp_base_path = ftp_base_path if ftp_base_path \
                else os.path.dirname(self._target_path)
            if self._ftp_port is None:
                self._ftp_port = self._generate_ftp_port()
            if self._ftp_pwd is None:
                self._ftp_pwd = public_func.generate_ftp_passwd()
        else:
            self._ftp_base_path = None

    def _generate_ftp_port(self):
        port = random.randint(10000, 65500)
        if not public_func.exists_port(port):
            return port
        else:
            return self._generate_ftp_port()

    @property
    def uuid(self) -> str:

        return self._uuid

    @property
    def isSharing(self) -> bool:

        return self._is_sharing

    @isSharing.setter
    def isSharing(self, newValue: bool) -> None:

        self._is_sharing = newValue

    @property
    def rowIndex(self) -> Union[None, int]:

        return self._row_index

    @rowIndex.setter
    def rowIndex(self, newValue: int) -> None:

        self._row_index = newValue

    @property
    def isDir(self) -> bool:

        return False

    @property
    def isExists(self) -> bool:

        return os.path.exists(self._target_path)

    @property
    def download_number(self) -> int:

        return self._download_number

    @download_number.setter
    def download_number(self, newValue: int) -> None:

        self._download_number = newValue

    @property
    def shareType(self) -> ptype.ShareType:

        return self._share_type

    @property
    def targetPath(self) -> str:

        return self._target_path

    @property
    def ftp_pwd(self) -> Union[None, str]:

        return self._ftp_pwd

    @property
    def ftp_port(self) -> Union[None, int]:

        return self._ftp_port

    @property
    def ftp_basePath(self) -> Union[None, str]:

        return self._ftp_base_path

    @property
    def ftp_cwd(self) -> str:

        result = os.path.dirname(self._target_path.replace(self._ftp_base_path, "", 1))
        if settings.IS_WINDOWS:
            result = result.replace("\\", "/")
        return result

    @property
    def browse_url(self) -> str:

        return f"http://{settings.LOCAL_HOST}:{settings.WSGI_PORT}{ptype.FILE_LIST_URI}/{self._uuid}"

    @property
    def download_url(self) -> str:

        return f"http://{settings.LOCAL_HOST}:{settings.WSGI_PORT}{ptype.DOWNLOAD_URI}/{self._uuid}"

    @property
    def file_name(self) -> str:

        return os.path.basename(self._target_path)

    async def to_dict_client(self) -> dict:

        return {
            "uuid": self._uuid,
            "downloadUrl": self.download_url,
            "fileName": self.file_name,
            "stareType": self._share_type.value,
            "isDir": self.isDir
        }

    async def to_ftp_data(self) -> dict:

        return {
            "uuid": self._uuid,
            "host": settings.LOCAL_HOST,
            "port": self._ftp_port,
            "user": "a",
            "passwd": self._ftp_pwd,
            "cwd": self.ftp_cwd,
            "filename": self.file_name
        }

    async def to_dict_server(self) -> dict:

        return {
            "uuid": self._uuid,
            "downloadUrl": self.download_url,
            "fileName": self.file_name,
            "stareType": self._share_type.value,
            "isDir": self.isDir,
            "browseUrl": self.browse_url,
            "targetPath": self._target_path,
            "ftpPwd": self._ftp_pwd,
            "ftpPort": self._ftp_port,
            "ftpBasePath": self._ftp_base_path
        }

    def to_dump_backup(self) -> dict:

        normal = {
            "path": self._target_path,
            "uuid": self._uuid,
            "parent_uuid": None,
            "share_type": self._share_type.value,
            "isDir": self.isDir
        }
        if self._share_type is ptype.ShareType.ftp:
            normal.update({
                "pwd": self._ftp_pwd,
                "port": self._ftp_port,
                "ftp_base_path": self._ftp_base_path
            })

        return normal

    def add_buttons(
        self,
        start_close_button: QPushButton,
        copy_browse_button: QPushButton,
        ui_function: UiFunction,
    ):
        pass

    def __eq__(self, other: str) -> bool:
        return other.rstrip(os.sep) == self._target_path

class DirChildrenModel(dict): pass

class DirModel(FileModel):

    def __init__(
        self,
        path: str,
        uuid: str,
        parent_uuid: Union[None, str] = None,
        pwd: Union[None, str] = None,
        port: Union[None, int] = None,
        ftp_base_path: Union[None, str] = None,
        **kwargs
    ) -> None:
        super(DirModel, self).__init__(path, uuid, parent_uuid, pwd, port, ftp_base_path, **kwargs)

        if self._share_type is ptype.ShareType.ftp:
            self._ftp_base_path = ftp_base_path if ftp_base_path else self._target_path
        else:
            self._ftp_base_path = None

        self._children = DirChildrenModel()
        self._setup_child()

    def _setup_child(self) -> None:

        for file_name in os.listdir(self._target_path):
            file_path = os.path.join(self._target_path, file_name)
            child_uuid = public_func.generate_uuid()
            fileModel = DirModel if os.path.isdir(file_path) else FileModel
            child = fileModel(
                file_path, child_uuid, self._uuid, self._ftp_pwd, self._ftp_port, self._ftp_base_path
            )

            self._children[child_uuid] = child

    def get(self, item: str) -> Any:

        return self._children.get(item)

    @property
    def isDir(self) -> bool:

        return True

    async def to_dict_client(self) -> dict:

        children = []
        for child_uuid, child in self._children.items():
            child_dict = {
                child_uuid: await child.to_dict_client()
            }
            children.append(child_dict)

        return {
            "uuid": self._uuid,
            "downloadUrl": self.download_url,
            "fileName": self.file_name,
            "stareType": self._share_type.value,
            "isDir": self.isDir,
            "children": children
        }

    async def to_dict_server(self) -> dict:

        children = []
        for child_uuid, child in self._children.items():
            child_dict = {
                child_uuid: await child.to_dict_server()
            }
            children.append(child_dict)

        return {
            "uuid": self._uuid,
            "downloadUrl": self.download_url,
            "fileName": self.file_name,
            "stareType": self._share_type.value,
            "isDir": self.isDir,
            "browseUrl": self.browse_url,
            "targetPath": self._target_path,
            "ftpPwd": self._ftp_pwd,
            "ftpPort": self._ftp_port,
            "ftpBasePath": self._ftp_base_path,
            "children": children
        }