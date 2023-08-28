import os
from typing import Any, Union, TypeVar

from model import public_types as ptype
from settings import settings
from utils.public_func import generate_uuid

FileType = TypeVar("FileType", bound="FileModel")

class FileModel:

    def __init__(
        self: FileType,
        path: str,
        uuid: str,
        parent_uuid: Union[None, str] = None,
        pwd: Union[None, str] = None,
        port: Union[None, int] = None,
        ftp_base_path: Union[None, str] = None
    ) -> None:

        self._uuid = f"{parent_uuid}>{uuid}" if parent_uuid else uuid
        self._target_path = path
        self._download_number = 0
        if self._uuid[0] == "h":
            self._share_type = ptype.ShareType.http
        else:
            self._share_type = ptype.ShareType.ftp
        self._ftp_pwd = pwd
        self._ftp_port = port
        self._ftp_base_path = ftp_base_path if ftp_base_path else ""

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
    def ftp_basePath(self) -> str:

        return self._ftp_base_path

    @ftp_basePath.setter
    def ftp_basePath(self, newValue: str) -> None:

        self._ftp_base_path = newValue

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

class DirChildrenModel(dict): pass

class DirModel(FileModel):

    def __init__(
        self: FileType,
        path: str,
        uuid: str,
        parent_uuid: Union[None, str] = None,
        pwd: Union[None, str] = None,
        port: Union[None, int] = None,
        ftp_base_path: Union[None, str] = None
    ) -> None:
        super(DirModel, self).__init__(path, uuid, parent_uuid, pwd, port, ftp_base_path)

        self._children = DirChildrenModel()
        self._setup_child()

    def _setup_child(self) -> None:

        for file_name in os.listdir(self._target_path):
            file_path = os.path.join(self._target_path, file_name)
            child_uuid = generate_uuid()
            if os.path.isdir(file_path):
                child = DirModel(
                    file_path, child_uuid, self._uuid, self._ftp_pwd, self._ftp_port,
                    self._ftp_base_path
                )
            else:
                child = FileModel(file_path, child_uuid, self._uuid, self._ftp_pwd, self._ftp_port)
                child.ftp_basePath = self._ftp_base_path

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