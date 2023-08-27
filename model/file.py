import os

from model import public_types as ptype
from settings import settings

class FileModel:

    def __init__(self, uuid: str, path: str) -> None:

        self._uuid = uuid
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

    @property
    def isDir(self) -> bool:

        return True