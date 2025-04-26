__all__ = ["HttpService"]

import os
import re
from typing import Union, Any, AsyncGenerator, Dict
from multiprocessing import Queue
from urllib.parse import quote
from email.utils import formatdate
from pydantic import BaseModel

import aiofiles
from fastapi import FastAPI, Request, Depends, UploadFile, File, Form
from fastapi.responses import (
    JSONResponse,
    StreamingResponse,
    Response,
    HTMLResponse,
    FileResponse,
)
from fastapi.staticfiles import StaticFiles
from starlette.types import Scope

from ._base_service import BaseService
from model import public_types as ptype
from model.file import FileModel, DirModel
from settings import settings
from utils.logger import sharerLogger, sysLogger
from utils.credentials import Credentials


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


class AuthParam(BaseModel):
    secret_key: str
    ciphertext: str


class HttpService(BaseService):
    STATIC_PATH = os.path.join(settings.BASE_DIR, "static", "mobile_frontend")

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
            if param == "favicon.ico":
                return FileResponse(os.path.join(self.STATIC_PATH, "favicon.ico"))
            if uri.startswith("/static"):
                return await cell_next(request)
            # client_platform = _request["client_platform"]
            fileObj = await generate_fileObj_recursive(param)
            # 文件是否存在判断
            if fileObj is None or not fileObj.isExists:
                sharerLogger.warning(
                    f"访问错误路径或文件/文件夹已不存在, 访问链接: {_request['path']}, 用户IP: {client_ip}"
                )
                return JSONResponse({"errno": 404, "errmsg": "错误的路径或文件已不存在！"})
            # 浏览/下载记录写入日志
            if ptype.FILE_LIST_URI in uri:
                sharerLogger.info(
                    f"用户IP: {client_ip}, 用户访问了文件列表, 文件链接: {fileObj.targetPath}"
                )
                self._output_q.put(param)
            elif ptype.DOWNLOAD_URI in uri:
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
        FOR_BIDDEN_RESPONSE = {"errno": 400, "errmsg": "For Bidden!"}

        def REQUIRE_PWD_RESPONSE(secret_key):
            return {
                "errno": 401,
                "errmsg": "Password verification is required",
                "secret_key": secret_key,
            }

        async def no_need_credentials(fileObj: Union[FileModel, DirModel]) -> bool:
            """
            是否需要校验凭据

            Args:
                fileObj: 待确认的文件/文件夹对象

            Returns:
                bool: 是否需要校验凭据
            """
            return (
                not fileObj.secret_key or not fileObj.credentials or fileObj.free_secret
            )

        async def verify_credentials(
            fileObj: Union[FileModel, DirModel], pwd: str
        ) -> bool:
            """
            凭据校验

            Args:
                fileObj: 待校验的文件/文件夹对象
                pwd: 待校验的密码

            Returns:
                bool: 校验的结果
            """
            return Credentials.verification(fileObj, pwd)

        async def with_credentials(
            uuid: str, request: Request, auth_param: AuthParam
        ) -> Dict[str, Union[int, str, FileModel, DirModel]]:
            fileObj = request.scope.get("fileObj")
            fileObj: Union[None, FileModel, DirModel]
            if not fileObj:
                sysLogger.error(
                    "发生了错误, 获取不到用户访问的文件/文件夹对象, "
                    "请用uuid对比`file_sharing_backups.json`文件, "
                    f"查看分享的文件/文件夹状态, uuid: {uuid}"
                )
                return {"errno": 500, "errmsg": "系统发生错误, 文件/文件夹对象没有被正确传递"}
            if fileObj.shareType is ptype.ShareType.ftp:
                return FOR_BIDDEN_RESPONSE
            if await no_need_credentials(fileObj):
                return {
                    "errno": 200,
                    "errmsg": "no need credentials",
                    "fileObj": fileObj,
                }
            if auth_param.secret_key != fileObj.secret_key:
                return FOR_BIDDEN_RESPONSE
            if await verify_credentials(fileObj, auth_param.ciphertext):
                return {
                    "errno": 200,
                    "errmsg": "credentials verification passed",
                    "fileObj": fileObj,
                }

            return REQUIRE_PWD_RESPONSE(fileObj.secret_key)

        async def with_credentials_form(
            uuid: str,
            request: Request,
            secret_key: str = Form(...),
            ciphertext: str = Form(...),
        ) -> Dict[str, Union[int, str, FileModel, DirModel]]:
            fileObj = request.scope.get("fileObj")
            fileObj: Union[None, FileModel, DirModel]
            if not fileObj:
                sysLogger.error(
                    "发生了错误, 获取不到用户访问的文件/文件夹对象, "
                    "请用uuid对比`file_sharing_backups.json`文件, "
                    f"查看分享的文件/文件夹状态, uuid: {uuid}"
                )
                return {"errno": 500, "errmsg": "系统发生错误, 文件/文件夹对象没有被正确传递"}
            if fileObj.shareType is ptype.ShareType.ftp:
                return FOR_BIDDEN_RESPONSE
            if await no_need_credentials(fileObj):
                return {
                    "errno": 200,
                    "errmsg": "no need credentials",
                    "fileObj": fileObj,
                }
            if secret_key != fileObj.secret_key:
                return FOR_BIDDEN_RESPONSE
            if await verify_credentials(fileObj, ciphertext):
                return {
                    "errno": 200,
                    "errmsg": "credentials verification passed",
                    "fileObj": fileObj,
                }

            return REQUIRE_PWD_RESPONSE(fileObj.secret_key)

        @mobile.get("%s/{uuid}" % ptype.QRCODE_URL)
        async def get_mobile_start(uuid: str) -> HTMLResponse:
            index_html = os.path.join(self.STATIC_PATH, "index.html")
            with open(index_html) as f:
                contend = f.read()
            replace_content = contend.replace(
                "{{ BASE_URL }}",
                f"http://{settings.LOCAL_HOST}:{settings.WSGI_PORT}{ptype.MOBILE_PREFIX}",
            )
            replace_content = replace_content.replace("{{ UUID }}", uuid)
            return HTMLResponse(replace_content)

        @mobile.get("%s/{uuid}" % ptype.FILE_LIST_URI)
        async def get_list_mobile(uuid: str, request: Request) -> Dict[str, Any]:
            fileObj = request.scope.get("fileObj")
            fileObj: Union[None, FileModel, DirModel]
            if not fileObj:
                sysLogger.error(
                    "发生了错误, 获取不到用户访问的文件/文件夹对象, "
                    "请用uuid对比`file_sharing_backups.json`文件, "
                    f"查看分享的文件/文件夹状态, uuid: {uuid}"
                )
                return {"errno": 500, "errmsg": "系统发生错误, 文件/文件夹对象没有被正确传递"}
            if fileObj.shareType is ptype.ShareType.ftp:
                return FOR_BIDDEN_RESPONSE
            if await no_need_credentials(fileObj):
                data = await fileObj.to_dict_mobile()
                return {"errno": 200, "errmsg": "", "data": data}

            return REQUIRE_PWD_RESPONSE(fileObj.secret_key)

        @mobile.post("%s/{uuid}" % ptype.FILE_LIST_URI)
        async def post_list_mobile(
            verify_result: Dict[str, Any] = Depends(with_credentials),
        ) -> Dict[str, Any]:
            if verify_result.get("errno", 400) != 200:
                return verify_result

            fileObj = verify_result.get("fileObj")
            data = await fileObj.to_dict_mobile()
            return {"errno": 200, "errmsg": "", "data": data}

        @mobile.get("%s/{uuid}" % ptype.FILE_SIZE_URI)
        async def get_file_size(uuid: str, request: Request) -> Dict[str, Any]:
            fileObj = request.scope.get("fileObj")
            fileObj: Union[None, FileModel, DirModel]
            if not fileObj:
                sysLogger.error(
                    "发生了错误, 获取不到用户访问的文件/文件夹对象, "
                    "请用uuid对比`file_sharing_backups.json`文件, "
                    f"查看分享的文件/文件夹状态, uuid: {uuid}"
                )
                return {"errno": 500, "errmsg": "系统发生错误, 文件/文件夹对象没有被正确传递"}
            if fileObj.shareType is ptype.ShareType.ftp:
                return FOR_BIDDEN_RESPONSE

            if fileObj.isDir:
                return {"errno": 300, "errmsg": "Can not get size for folder"}
            if not fileObj.isExists:
                return {"errno": 404, "errmsg": "The File is not exists"}

            return {"errno": 200, "errmsg": "", "fileSize": fileObj.file_size}

        @mobile.post("%s/{uuid}" % ptype.DOWNLOAD_URI, response_model=None)
        async def download_mobile(
            request: Request, verify_result: Dict[str, Any] = Depends(with_credentials)
        ) -> Union[Dict[str, Any], StreamingResponse]:
            if verify_result.get("errno", 400) != 200:
                return verify_result
            fileObj = verify_result.get("fileObj")

            return await self.generate_file_stream_response(request, fileObj)

        @mobile.post("%s/{uuid}" % ptype.UPLOAD_URI)
        async def upload_mobile(
            request: Request,
            file: UploadFile = File(...),
            file_name: str = Form(...),
            chunk_id: int = Form(...),
            curr_path: str = Form(...),
            verify_result: Dict[str, Any] = Depends(with_credentials_form),
        ) -> Dict[str, Any]:
            if verify_result.get("errno", 400) != 200:
                return verify_result
            if not os.path.isdir(curr_path):
                return {
                    "errno": 400,
                    "errmsg": "Cannot upload files to non folder locations",
                }
            merge_file_name = os.path.join(curr_path, file_name)
            chunk_file_name = os.path.join(curr_path, f"{file_name}_{chunk_id}.part")
            if os.path.exists(merge_file_name) or os.path.exists(chunk_file_name):
                return {
                    "errno": 400,
                    "errmsg": "The file with the same name already exists!",
                }

            with open(chunk_file_name, "wb") as f:
                f.write(await file.read())

            if request.query_params.get(ptype.HIT_LOG, "false"):
                client_ip = request.get("client", ["未知IP"])[0]
                sysLogger.info(
                    f"用户IP： {client_ip}, 用户正在上传文件: {file_name}, 上传路径: {curr_path}"
                )

            return {
                "errno": 200,
                "errmsg": "Upload chunk succed",
                "data": {"fileName": file_name, "chunkId": chunk_id},
            }

        @mobile.post("%s/{uuid}" % ptype.UPLOAD_MERGE_URI)
        async def upload_merge_mobile(
            file_name: str = Form(...),
            chunk_count: int = Form(...),
            curr_path: str = Form(...),
            verify_result: Dict[str, Any] = Depends(with_credentials_form),
        ) -> Dict[str, Any]:
            if verify_result.get("errno", 400) != 200:
                return verify_result

            if not os.path.isdir(curr_path):
                return {
                    "errno": 400,
                    "errmsg": "Cannot upload files to non folder locations",
                }

            for i in range(chunk_count):
                chunk_file_name = os.path.join(curr_path, f"{file_name}_{i}.part")
                if not os.path.exists(chunk_file_name):
                    return {"errno": 400, "errmsg": f"There is chunk loss: {i}"}

            merge_file_name = os.path.join(curr_path, file_name)
            with open(merge_file_name, "wb") as merge_f:
                for i in range(chunk_count):
                    chunk_file_name = os.path.join(curr_path, f"{file_name}_{i}.part")
                    with open(chunk_file_name, "rb") as chunk_f:
                        merge_f.write(chunk_f.read())
                    os.remove(chunk_file_name)

            return {
                "errno": 200,
                "errmsg": "Merge chunks succed",
                "data": {"fileName": file_name, "chunkCount": chunk_count},
            }

        @mobile.post("%s/{uuid}" % ptype.UPLOAD_REMOVE_URI)
        async def upload_remove_mobile(
            file_name: str = Form(...),
            curr_path: str = Form(...),
            verify_result: Dict[str, Any] = Depends(with_credentials_form),
        ) -> Dict[str, Any]:
            if verify_result.get("errno", 400) != 200:
                return verify_result
            if not os.path.isdir(curr_path):
                return {
                    "errno": 400,
                    "errmsg": "The curr_path is not a folder.",
                }
            rm_count = 0
            for curr_file in os.listdir(curr_path):
                curr_file_path = os.path.join(curr_path, curr_file)
                if os.path.isdir(curr_file_path):
                    continue
                if re.match(f"{file_name}_\d+\.part", curr_file):
                    os.remove(os.path.join(curr_path, curr_file))
                    rm_count += 1

            return {
                "errno": 200,
                "errmsg": "Remove all chunk file succ",
                "data": {"fileName": file_name, "removeCount": rm_count},
            }

        # mount app
        self._app.mount(ptype.MOBILE_PREFIX, mobile)
        self._app.mount(
            ptype.STATIC_PREFIX, StaticFiles(directory=self.STATIC_PATH), name="static"
        )

    @staticmethod
    async def generate_file_stream_response(
        request: Request, fileObj: FileModel
    ) -> StreamingResponse:
        async def file_generator(
            file_path: str, offset: int, end: int, chunk_size: int
        ) -> AsyncGenerator:
            async with aiofiles.open(file_path, "rb") as f:
                await f.seek(offset, os.SEEK_SET)
                remaining_bytes = end - offset
                while remaining_bytes > 0:
                    chunk_size_ = min(chunk_size, remaining_bytes)
                    chunk = await f.read(chunk_size_)
                    if not chunk:
                        break
                    yield chunk
                    remaining_bytes -= chunk_size_

        stat_result = os.stat(fileObj.targetPath)
        st_size = stat_result.st_size
        range_str = request.headers.get("range", "")
        range_match = re.match(r"bytes=(\d+)-(\d+)", range_str) or re.match(
            r"bytes=(\d+)-", range_str
        )
        if range_match:
            start = int(range_match.group(1))
            end = int(range_match.group(2)) if range_match.lastindex == 2 else st_size
        else:
            start = 0
            end = st_size
        file_name = quote(fileObj.file_name)
        content_length = end - start
        content_type = "application/octet-stream"
        return StreamingResponse(
            file_generator(fileObj.targetPath, start, end, 1048576),
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
