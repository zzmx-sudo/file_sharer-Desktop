__all__ = ["HttpService"]

import os
import re
from typing import Union, Any, AsyncGenerator, Dict
from multiprocessing import Queue
from urllib.parse import quote
from email.utils import formatdate

import aiofiles
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, StreamingResponse, Response
from fastapi.staticfiles import StaticFiles
from starlette.types import Scope

from ._base_service import BaseService
from model import public_types as ptype
from model.file import FileModel, DirModel
from settings import settings
from utils.logger import sharerLogger, sysLogger


class MyRequest:
    def __init__(self, scope: Scope):
        self._setup(scope)

    def _setup(self, scope: Scope) -> None:
        for key in ["client", "path"]:
            self.__dict__[key] = scope.get(key, "")
        for header_name, header_value in scope.get("headers"):
            if header_name == b"x-client":
                self.__dict__["is_client"] = "True"
                break
            # elif header_name == b"sec-ch-ua-platform":
            #     self.__dict__["client_platform"] = header_value.decode()

    def __getitem__(self, item: str) -> Union[str, tuple]:
        return self.__dict__.get(item, "")


class HttpService(BaseService):
    def __init__(self, input_q: Queue, output_q: Queue):
        """
        HTTP共享服务类初始化函数

        Args:
            input_q: 输入的进程队列
            output_q: 输出的进程队列
        """
        super(HttpService, self).__init__(input_q, output_q)
        self._service_name = "HTTP"
        self._app = None

    def _add_share(self, fileObj: Union[FileModel, DirModel]) -> None:
        """
        添加共享文件或文件夹

        Args:
            fileObj: 待添加共享的文件或文件夹对象

        Returns:
            None
        """
        self._sysLogger_debug(f"开始添加分享, 分享路径: {fileObj.targetPath}")
        self._sharing_dict.update({fileObj.uuid: fileObj})
        self._sysLogger_debug(f"添加分享完成, 分享路径: {fileObj.targetPath}")

    def _remove_share(self, uuid: str) -> None:
        """
        移除共享文件或文件夹

        Args:
            uuid: 待移除共享文件或文件夹的uuid

        Returns:
            None
        """
        self._sysLogger_debug(f"开始移除分享, 分享的uuid: {uuid}")
        if uuid in self._sharing_dict:
            del self._sharing_dict[uuid]
        self._sysLogger_debug(f"移除分享完成, 分享的uuid: {uuid}")

    def _change_free_secret(self, uuid: str, value: bool) -> None:
        """
        修改文件/文件夹对象的免密状态

        Args:
            uuid: 待修改文件/文件夹对象的uuid
            value: 待修改的免密状态

        Returns:
            None
        """
        self._sysLogger_debug(f"开始修改免密状态, 分享的uuid: {uuid}, 新的免密状态: {value}")
        if uuid not in self._sharing_dict:
            sysLogger.error(f"系统错误, 接收到修改免密状态任务, 但该文件/文件夹并未分享, 文件uuid: {uuid}")
            return

        self._sharing_dict[uuid].free_secret = value
        self._sysLogger_debug(f"修改免密状态完成, 分享的uuid: {uuid}")

    def run(self) -> None:
        """
        HTTP服务进程运行入口函数

        Returns:
            None
        """
        self.watch()
        super(HttpService, self).run()

        import uvicorn

        self._sysLogger_debug("初始化FastAPI")
        self._app = FastAPI()
        self._setup()
        self._sysLogger_debug("开启服务")
        uvicorn.run(
            app=self._app, host=settings.LOCAL_HOST, port=settings.init_wsgi_port()
        )
        self._sysLogger_debug("开启HTTP服务失败")

    def _setup(self) -> None:
        """
        初始化HTTP服务配置, 意在初始化中间件和路由

        Returns:
            None
        """
        self._sysLogger_debug("初始化路由")
        self._setup_middleware()
        self._setup_router()

    def _setup_middleware(self) -> None:
        """
        初始化中间件

        Returns:
            None
        """

        async def generate_fileObj_recursive(
            uuid: str, parentObj: Union[None, DirModel] = None
        ) -> Union[FileModel, DirModel, None]:
            if parentObj is None:
                try:
                    parent_uuid, other_uuid = uuid.split(">", 1)
                except ValueError:
                    return self._sharing_dict.get(uuid)

                parentObj = self._sharing_dict.get(parent_uuid)
                if parentObj is None or not parentObj.isDir:
                    return None
                return await generate_fileObj_recursive(other_uuid, parentObj)

            try:
                parent_uuid, other_uuid = uuid.split(">", 1)
            except ValueError:
                return parentObj.get(uuid)
            parentObj = parentObj.get(parent_uuid)
            if parentObj is None or not parentObj.isDir:
                return None
            return await generate_fileObj_recursive(other_uuid, parentObj)

        async def is_download_ftp_without_client(
            shareType: ptype.ShareType, request: MyRequest
        ) -> bool:
            is_client = request["is_client"]
            if shareType is ptype.ShareType.ftp and not is_client:
                return True

            return False

        @self._app.middleware("http")
        async def complete_middleware(request: Request, cell_next) -> Response:
            """
            该中间件目前完成以下功能:
            1. 无效/非法路由返回错误链接提示
            2. 访问/下载的文件/文件夹是否有效校验
            3. 访问/下载日志写入
            4. 是否下载文件夹
            5. 是否用非客户端下载FTP服务文件/文件夹
            6. 文件/文件夹对象往后传递给视图

            Args:
                request: request对象
                cell_next: 后续中间件/视图回调函数

            Returns:
                Response: response对象
            """
            _request = MyRequest(request.scope)
            client_ip = _request["client"][0] if _request["client"] else "未知IP"
            uri, param = _request["path"].rsplit("/", 1)
            # client_platform = _request["client_platform"]
            fileObj = await generate_fileObj_recursive(param)
            # 文件是否存在判断
            if fileObj is None or not fileObj.isExists:
                sharerLogger.warning(
                    f"访问错误路径或文件/文件夹已不存在, 访问链接: {_request['path']}, 用户IP: {client_ip}"
                )
                return JSONResponse({"errno": 404, "errmsg": "错误的路径或文件已不存在！"})
            # 浏览/下载记录写入日志
            if uri == ptype.FILE_LIST_URI:
                sharerLogger.info(
                    f"用户IP: {client_ip}, 用户访问了文件列表, 文件链接: {fileObj.targetPath}"
                )
                self._output_q.put(param)
            elif uri == ptype.DOWNLOAD_URI:
                params = request.query_params
                hit_log = params.get(ptype.HIT_LOG, "false")
                if fileObj.shareType is ptype.ShareType.http:
                    # 下载的若为HTTP分享的文件夹, 需进行是否含hit_log标志校验
                    if fileObj.isDir and hit_log != "true":
                        sharerLogger.warning(f"用户使用非客户端无法直接下载分享的文件夹, 用户IP: {client_ip}")
                        return JSONResponse(
                            {"errno": 400, "errmsg": "无法直接下载文件夹, 请使用客户端进行下载！"}
                        )
                    elif fileObj.isDir and hit_log == "true":
                        sharerLogger.info(
                            f"用户IP: {client_ip}, 用户下载了文件夹, 文件夹路径: {fileObj.targetPath}"
                        )
                        return JSONResponse({"errno": 200, "errmsg": ""})
                    elif hit_log == "true":
                        sharerLogger.info(
                            f"用户IP: {client_ip}, 用户下载了文件, 文件路径: {fileObj.targetPath}"
                        )
                else:
                    file_type = "文件夹" if fileObj.isDir else "文件"
                    # 下载的若为FTP分享文件, 需进行是否为客户端判断
                    if await is_download_ftp_without_client(
                        fileObj.shareType, _request
                    ):
                        sharerLogger.warning(
                            f"用户使用非客户端无法下载FTP分享的文件/文件夹, 用户IP: {client_ip}"
                        )
                        return JSONResponse(
                            {"errno": 400, "errmsg": "ftp分享的文件/文件夹请使用客户端进行下载！"}
                        )
                    if hit_log == "true":
                        sharerLogger.info(
                            f"用户IP: {client_ip}, 用户下载了{file_type}, {file_type}路径: {fileObj.targetPath}"
                        )
            # else:
            #     return JSONResponse({"errno": 404, "errmsg": "访问的链接不存在！"})

            request.scope["fileObj"] = fileObj
            response = await cell_next(request)
            return response

    def _setup_router(self) -> None:
        """
        初始化路由

        Returns:
            None
        """

        ### root app
        @self._app.get("%s/{uuid}" % ptype.FILE_LIST_URI)
        async def file_list(uuid: str, request: Request) -> Dict[str, Any]:
            fileObj = request.scope.get("fileObj")
            fileObj: Union[None, FileModel, DirModel]
            if not fileObj:
                sysLogger.error(
                    "发生了错误, 获取不到用户访问的文件/文件夹对象, "
                    "请用uuid对比`file_sharing_backups.json`文件, "
                    f"查看分享的文件/文件夹状态, uuid: {uuid}"
                )
                return {"errno": 500, "errmsg": "系统发生错误, 文件/文件夹对象没有被正确传递"}

            data = await fileObj.to_dict_client()
            return {"errno": 200, "errmsg": "", "data": data}

        @self._app.get("%s/{uuid}" % ptype.DOWNLOAD_URI, response_model=None)
        async def download(
            uuid: str, request: Request
        ) -> Union[Dict[str, Any], StreamingResponse]:
            fileObj = request.scope.get("fileObj")
            fileObj: Union[None, FileModel, DirModel]
            if not fileObj:
                sysLogger.error(
                    "发生了错误, 获取不到用户访问的文件/文件夹对象, "
                    "请用uuid对比`file_sharing_backups.json`文件, "
                    f"查看分享的文件/文件夹状态, uuid: {uuid}"
                )
                return {"errno": 500, "errmsg": "系统发生错误, 文件/文件夹对象没有被正确传递"}

            if fileObj.shareType is ptype.ShareType.http:
                return await self.generate_file_stream_response(request, fileObj)
            elif fileObj.shareType is ptype.ShareType.ftp:
                ftp_data = await fileObj.to_ftp_data()
                return {"errno": 200, "errmsg": "", "data": ftp_data}
            else:
                sysLogger.error(f"未被预判的分享类型: {fileObj.shareType.value}, 系统发生错误")
                return {"errno": 500, "errmsg": "下载文件/文件夹失败"}

        ### mobile app
        mobile = FastAPI()

        @mobile.get("%s/{uuid}" % ptype.FILE_LIST_URI)
        async def file_list_mobile(uuid: str, request: Request) -> Dict[str, Any]:
            fileObj = request.scope.get("fileObj")
            fileObj: Union[None, FileModel, DirModel]
            if not fileObj:
                sysLogger.error(
                    "发生了错误, 获取不到用户访问的文件/文件夹对象, "
                    "请用uuid对比`file_sharing_backups.json`文件, "
                    f"查看分享的文件/文件夹状态, uuid: {uuid}"
                )
                return {"errno": 500, "errmsg": "系统发生错误, 文件/文件夹对象没有被正确传递"}

            data = await fileObj.to_dict_mobile()
            return {"errno": 200, "errmsg": "", "data": data}

        # mount app
        self._app.mount(ptype.MOBILE_PREFIX, mobile)
        static_path = os.path.join(
            os.path.dirname(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            ),
            "static",
            "mobile_frontend",
        )
        self._app.mount(
            ptype.STATIC_PREFIX, StaticFiles(directory=static_path), name="static"
        )

    @staticmethod
    async def generate_file_stream_response(
        request: Request, fileObj: FileModel
    ) -> StreamingResponse:
        async def file_generator(
            file_path: str, offset: int, chunk_size: int
        ) -> AsyncGenerator:
            async with aiofiles.open(file_path, "rb") as f:
                await f.seek(offset, os.SEEK_SET)
                while True:
                    chunk = await f.read(chunk_size)
                    if chunk:
                        yield chunk
                    else:
                        break

        stat_result = os.stat(fileObj.targetPath)
        st_size = stat_result.st_size
        range_str = request.headers.get("range", "")
        range_match = re.match(r"bytes=(\d+)-", range_str) or re.match(
            r"bytes=(\d+)-(\d+)", range_str
        )
        if range_match:
            start = int(range_match.group(1))
            end = (
                int(range_match.group(2)) if range_match.lastindex == 2 else st_size - 1
            )
        else:
            start = 0
            end = st_size - 1
        file_name = quote(fileObj.file_name)
        content_length = st_size - start
        content_type = "application/octet-stream"
        return StreamingResponse(
            file_generator(fileObj.targetPath, start, 1048576),
            media_type=content_type,
            headers={
                "content-disposition": f"attachment; filename={file_name}",
                "accept-ranges": "bytes",
                "connection": "keep-alive",
                "content-length": str(content_length),
                "content-range": f"{start}-{end}/{st_size}",
                "last-modified": formatdate(stat_result.st_mtime, usegmt=True),
            },
            status_code=206 if start > 0 else 200,
        )
