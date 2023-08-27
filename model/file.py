import os
from typing import Any, Union

from model import public_types as ptype
from settings import settings
from utils.public_func import generate_uuid

class FileModel:

    def __init__(
            self, path: str, uuid: str, parent_uuid: Union[None, str] = None
    ) -> None:

        self._uuid = f"{parent_uuid}%{uuid}" if parent_uuid else uuid
        self._target_path = path
        self._download_number = 0
        if self._uuid[0] == "h":
            self._share_type = ptype.ShareType.http
        else:
            self._share_type = ptype.ShareType.ftp
        self._ftp_password = ""
        self._ftp_port = 10086

    @property
    def isDir(self) -> bool:

        return False

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
    def ftp_password(self) -> str:

        return self._ftp_password

    @ftp_password.setter
    def ftp_password(self, newValue: str) -> None:

        self._ftp_password = newValue

    @property
    def ftp_port(self) -> int:

        return self._ftp_port

    @ftp_port.setter
    def ftp_port(self, newValue: int) -> None:

        self._ftp_port = newValue

    @property
    def browse_url(self) -> str:

        return f"http://{settings.LOCAL_HOST}:{settings.WSGI_PORT}{ptype.FILE_LIST_URI}/{self._uuid}"

    @property
    def download_url(self) -> str:

        return f"http://{settings.LOCAL_HOST}:{settings.WSGI_PORT}{ptype.DOWNLOAD_URI}/{self._uuid}"

    @property
    def file_name(self) -> str:

        return os.path.basename(self._target_path)

    def to_dict(self) -> dict:

        return {
            "uuid": self._uuid,
            "download_url": self.download_url,
            "file_name": self.file_name,
            "stareType": self._share_type.value
        }

class DirModel(FileModel):

    def __init__(
            self, path: str, uuid: str, parent_uuid: Union[None, str] = None
    ) -> None:
        super(DirModel, self).__init__(path, uuid, parent_uuid)
        self._childs = {}
        self._setup_child()

    def _setup_child(self) -> None:

        for file_name in os.listdir(self._target_path):
            file_path = os.path.join(self._target_path, file_name)
            child_uuid = generate_uuid()
            if os.path.isdir(file_path):
                child = DirModel(file_path, child_uuid, self._uuid)
            else:
                child = FileModel(file_path, child_uuid, self._uuid)

            self._childs[child_uuid] = child

    def get(self, item: str) -> Any:

        return self._childs.get(item)

    @property
    def isDir(self) -> bool:

        return True

    def to_dict(self) -> dict:

        childs = []
        for child_uuid, child in self._childs.items():
            child_dict = {
                child_uuid: child.to_dict()
            }
            childs.append(child_dict)

        return {
            "uuid": self._uuid,
            "download_url": self.download_url,
            "file_name": self.file_name,
            "stareType": self._share_type.value,
            "childs": childs
        }