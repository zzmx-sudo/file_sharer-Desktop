__all__ = [
    "HttpService"
]

import os
from typing import Union, Any
from multiprocessing import Queue

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.types import Scope

from ._base_service import BaseService
from model import public_types as ptype
from model.file import FileModel, DirModel
from settings import settings
from utils.logger import sharerLogger

class MyRequest:

    def __init__(self, scope: Scope) -> None:

        self._setup(scope)

    def _setup(self, scope: Scope) -> None:

        for key in ["client", "path"]:
            self.__dict__[key] = scope.get(key, "")
        for header_name, header_value in scope.get("headers"):
            if header_name == b"sec-ch-ua-platform":
                self.__dict__["client_platform"] = header_value.decode()
            elif header_name == b"X-Client":
                self.__dict__["is_client"] = True

    def __getitem__(self, item: str) -> Union[str, tuple[str, int]]:

        return self.__dict__.get(item, "")

class HttpService(BaseService):

    def __init__(self, input_q: Queue, output_q: Queue) -> None:
        super(HttpService, self).__init__(input_q, output_q)
        self._app = None

    def _add_share(self, uuid: str, fileObj: Union[FileModel, DirModel]) -> None:
        pass

    def _remove_share(self, uuid: str) -> None:
        pass

    def run(self) -> None:

        import uvicorn
        self._app = FastAPI()
        self.watch()
        self._setup()
        uvicorn.run(
            app=self._app,
            host=settings.LOCAL_HOST,
            port=settings.WSGI_PORT
        )

    def _setup(self) -> None:

        self._setup_middleware()
        self._setup_router()

    def _setup_middleware(self) -> None:

        async def is_download_ftp_without_client(
                shareType: ptype.ShareType, request: MyRequest
        ) -> bool:
            is_client = request["is_client"]
            if shareType is ptype.ShareType.ftp and not is_client:
                return True

            return False

        @self._app.middleware("http")
        async def check_file_exists(request: Request, cell_next):
            _request = MyRequest(request.scope)
            client_ip = _request["client"][0] if _request["client"] else "未知IP"
            uri, param = _request["path"].rsplit("/", 1)
            # client_platform = _request["client_platform"]
            if "%" in param:
                uuid_parent, uuid_child = param.split("%", 1)
                fileObj = self._sharing_dict.get(uuid_parent, {}).get(uuid_child, None)
            else:
                fileObj = self._sharing_dict.get(param, None)
            # 文件是否存在判断
            if fileObj is None or not os.path.exists(fileObj.targetPath):
                sharerLogger.warning("访问错误路径或文件/文件夹已不存在, 访问链接: %s, 用户IP: %s" % (
                    _request["path"], client_ip
                ))
                return JSONResponse({"errno": 404, "errmsg": "错误的路径或文件已不存在！"})
            # 浏览/下载记录写入日志
            if uri == "/file_list":
                sharerLogger.info("用户IP: %s, 用户访问了文件列表, 文件链接: %s" % (
                    client_ip, fileObj.targetPath,
                ))
            elif uri == "/download":
                # 用户下载时, 需进行是否为客户端判断
                if is_download_ftp_without_client(fileObj.shareType, _request):
                    sharerLogger.warning("用户使用非客户端无法下载FTP分享的文件/文件夹, 用户IP: %s" % client_ip)
                    return JSONResponse({"errno": 400, "errmsg": "ftp分享的文件/文件夹请使用客户端进行下载"})
                else:
                    sharerLogger.info("用户IP: %s, 用户下载了文件, 文件链接: %s" % (
                        client_ip, fileObj.targetPath
                    ))
                    self._output_q.put(param)

            response = await cell_next(request)
            return response

    def _setup_router(self) -> None:

        @self._app.get("%s/{uuid}" % ptype.FILE_LIST_URI)
        async def file_list(uuid: str) -> dict:

            return {"hello": uuid}

        @self._app.get("%s/{uuid}" % ptype.DOWNLOAD_URI)
        async def download(uuid: str) -> Any:

            return {"hello": uuid}