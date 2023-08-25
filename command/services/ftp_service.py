__all__ = [
    "FtpService"
]

from typing import Union

from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer

from ._base_service import BaseService
from model.file import FileModel, DirModel

class FtpService(BaseService):

    def _add_share(self, uuid: str, fileObj: Union[FileModel, DirModel]) -> None:

        pass

    def _remove_share(self, uuid: str) -> None:

        pass

    def run(self) -> None:

        pass