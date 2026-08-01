__all__ = [
    "WatchResultThread",
    "LoadBrowseUrlThread",
    "DownloadHttpFileThread",
    "DownloadFtpFileThread",
]

import time
import json
import os
import asyncio
import ssl
import logging
from multiprocessing import Queue
from traceback import format_exc
from typing import Dict, Any, List, Union, Tuple, Optional
from copy import deepcopy

import requests
import aiohttp
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.Qt import QApplication
from ftplib import FTP

from settings import settings
from utils.public_func import response_ret_code
from utils.response_code import RET
from .public_types import BrowseStatus, DownloadStatus, HIT_LOG
from .browse import BrowseFileDictModel, BrowseFileDataModel


class BaseThread(QThread):
    @property
    def sysLogger(self) -> logging.Logger:
        """
        sysLogger

        Returns:
            logging.Logger: logger.sysLogger
        """
        from utils.logger import sysLogger

        return sysLogger


class WatchResultThread(BaseThread):
    signal = pyqtSignal(str)

    def __init__(self, output_q: Queue):
        """
        监听浏览线程类初始化函数

        Args:
            output_q: 输出进程队列
        """
        super(WatchResultThread, self).__init__()
        self.run_flag = True
        self._output_q = output_q

    def run(self) -> None:
        """
        线程运行入口函数

        Returns:
            None
        """
        while self.run_flag:
            file_uuid = self._output_q.get()
            self.sysLogger.debug(f"监听到分享被浏览, 正在发射更新浏览次数事件, 分享的uuid: {file_uuid}")
            self.signal.emit(file_uuid)
            self.sysLogger.debug(f"发射更新浏览次数事件完成, 分享的uuid: {file_uuid}")


class LoadBrowseUrlThread(BaseThread):
    signal = pyqtSignal(tuple)

    def __init__(self, browse_url: str):
        """
        加载分享链接线程类初始化函数

        Args:
            browse_url: 分享链接
        """
        super(LoadBrowseUrlThread, self).__init__()
        self._browse_url = browse_url
        self.run_flag = True

    def run(self) -> None:
        """
        线程运行入口函数

        Returns:
            None
        """
        self.sysLogger.debug(f"正在加载分享链接[{self._browse_url}]")
        os.environ["NO_PROXY"] = "127.0.0.1"
        try:
            response = requests.get(self._browse_url, timeout=2)
        except:
            self.sysLogger.warning(f"连接服务异常, 正在发射显示分享链接数据事件")
            self.emit(BrowseStatus.ConnectErr, {})
            return

        try:
            result = json.loads(response.text)
        except json.JSONDecodeError:
            self.sysLogger.warning(f"服务器返回非法数据[{self._browse_url}]")
            self.emit(BrowseStatus.ServerErr, {})
            return

        empty_data = BrowseFileDictModel.load({})
        if not result or not isinstance(result, dict) or result.get("errno") is None:
            self.sysLogger.warning("分享服务器异常, 未能连接服务器或服务器返回非法数据")
            self.emit(BrowseStatus.ServerErr, empty_data)
        elif result.get("errno", 0) == RET.FILENOTFOUND:
            self.sysLogger.warning("来晚了, 分享的文件/文件夹已被删除")
            self.emit(BrowseStatus.NotFoundErr, empty_data)
        elif result.get("errno", 0) == RET.SEVERERR:
            self.sysLogger.warning("分享服务器存在异常")
            self.emit(BrowseStatus.ServerErr, empty_data)
        elif result.get("errno", 0) == RET.OK:
            data = result.get("data", {})
            if not self._verify_data(data):
                self.sysLogger.warning("分享服务器返回的数据格式存在非标")
                self.emit(BrowseStatus.ServerErr, empty_data)
            else:
                self.sysLogger.debug("加载访问数据成功")
                browse_data = self.process_filePath(data)
                self.emit(BrowseStatus.Succ, BrowseFileDictModel.load(browse_data))
        else:
            self.sysLogger.warning(f"发生未知错误, 返回的response: {result}")
            self.emit(BrowseStatus.ServerErr, empty_data)

    def process_filePath(self, fileDict: Dict[str, Any]) -> Dict[str, Any]:
        """
        给数据新增相对路径(相对最首层路径的父级路径)属性, 方便后续下载

        Args:
            fileDict: 后端返回的浏览数据

        Returns:
            Dict[str, Any]: 处理后的浏览数据
        """

        def _process_folder(fileDict: Dict[str, Any]):
            dir_name = fileDict["relativePath"]
            for id, child in enumerate(fileDict["children"]):
                child = next(iter(child.values()))
                relativePath = os.path.join(dir_name, child["fileName"])
                if child["isDir"]:
                    child.update({"relativePath": relativePath})
                    _process_folder(child)
                else:
                    child.update({"relativePath": relativePath})
                fileDict["children"][id] = child

        self.sysLogger.debug("正在遍历处理文件路径")
        new_fileDict = deepcopy(fileDict)
        new_fileDict.update({"relativePath": new_fileDict["fileName"]})
        if new_fileDict["isDir"]:
            _process_folder(new_fileDict)
        self.sysLogger.debug("处理文件路径完成")
        return new_fileDict

    def emit(self, status: BrowseStatus, data: Dict[str, Any]) -> None:
        """
        发射数据给回调函数

        Args:
            status: 访问状态
            data: 访问到的数据

        Returns:
            None
        """
        self.signal.emit((status, data))

    def _verify_data(self, data: Dict[str, Any], with_log: bool = True) -> bool:
        if with_log:
            self.sysLogger.debug("正在校验分享链接对应服务器返回数据的格式")
        if not data or not isinstance(data, dict):
            return False
        status = True
        isDir = data.get("isDir")
        if isDir is None:
            return False
        if isDir:
            other_full_keys = [
                "uuid",
                "downloadUrl",
                "fileName",
                "shareType",
                "children",
            ]
        else:
            other_full_keys = ["uuid", "downloadUrl", "fileName", "shareType"]
        if not all(key in data for key in other_full_keys):
            return False
        if isDir:
            for child in data["children"]:
                try:
                    if len(child) != 1:
                        return False
                    for file_dict in child.values():
                        status &= self._verify_data(file_dict, False)
                except AttributeError:
                    return False

        return status


class BaseDownloadFileThread(BaseThread):
    signal = pyqtSignal(tuple)

    def __init__(self, fileDict: BrowseFileDictModel):
        """
        下载文件线程基类

        Args:
            fileDict: 待下载文件对象
        """
        super(BaseDownloadFileThread, self).__init__()
        self._file_maps: Dict[str, BrowseFileDataModel] = {}
        self._chunk_size = 1048576
        self.run_flag = True
        self._padding_fileUuids = []
        self.process_new_fileDict(fileDict)

    def run(self) -> None:
        """
        线程运行入口函数

        Returns:
            None
        """
        raise NotImplementedError("实现下载文件对象的线程类必须有定义`run`方法")

    def process_new_fileDict(self, fileDict: BrowseFileDictModel) -> None:
        """
        当添加新的下载文件对象时, 需进行的一系列操作

        Args:
            fileDict: 添加的待下载文件独享

        Returns:
            None
        """
        from utils.public_func import update_downloadUrl_with_hitLog

        file_count = 0

        def _process_folder(
            ori_uuid: str,
            fileDict: BrowseFileDictModel,
            download_list: List[BrowseFileDictModel],
        ):
            nonlocal file_count
            for child in fileDict.children:
                child.oriUuid = ori_uuid
                download_list.append(child)
                if not child.isDir:
                    file_count += 1
                else:
                    _process_folder(ori_uuid, child, download_list)

                QApplication.processEvents()

        file_copy = deepcopy(fileDict)
        uuid = fileDict.uuid
        update_downloadUrl_with_hitLog(file_copy)

        download_list = [file_copy]
        if file_copy.isDir:
            _process_folder(uuid, file_copy, download_list)
        else:
            file_count = 1
        self._file_maps[uuid] = BrowseFileDataModel(
            fileDict, download_list, file_count, 0
        )

    def append(self, fileDict: BrowseFileDictModel) -> None:
        """
        追加下载文件对象列表

        Args:
            fileDict: 待追加下载文件对象

        Returns:
            None
        """
        self.sysLogger.debug("追加下载列表")
        self.process_new_fileDict(fileDict)

    def remove(self, fileDict: BrowseFileDictModel) -> None:
        """
        移除下载文件对象

        Args:
            fileDict: 待移除的下载文件对象

        Returns:
            None
        """
        self.sysLogger.debug("移除下载")
        uuid = fileDict.uuid
        if uuid in self._file_maps:
            self._file_maps.pop(uuid)
        if uuid in self._padding_fileUuids:
            self._padding_fileUuids.remove(uuid)

    def pause(self, fileDict: BrowseFileDictModel) -> None:
        """
        暂停文件对象下载

        Args:
            fileDict: 待暂停下载的文件对象

        Returns:
            None
        """
        self.sysLogger.debug("暂停下载")
        uuid = fileDict.uuid
        if uuid in self._padding_fileUuids:
            return
        self._padding_fileUuids.append(uuid)
        self.signal.emit((fileDict, DownloadStatus.PAUSE, "暂停成功"))

    def resume(self, fileDict: BrowseFileDictModel) -> None:
        """
        恢复下载

        Args:
            fileDict: 待恢复下载的文件对象

        Returns:
            None
        """
        self.sysLogger.debug("重新下载")
        uuid = fileDict.uuid
        if uuid in self._padding_fileUuids:
            self._padding_fileUuids.remove(uuid)

    def is_padding(self, target_file: Union[str, BrowseFileDictModel]) -> bool:
        """
        当前下载对象是否是被暂停的

        Args:
            target_file: 当前下载对象/下载对象的ori_uuid

        Returns:
            bool: 下载对象是否是被暂停的
        """
        ori_uuid = (
            target_file.oriUuid
            if isinstance(target_file, BrowseFileDictModel)
            else target_file
        )
        return ori_uuid in self._padding_fileUuids or ori_uuid not in self._file_maps

    def is_single_file(self, download_file: BrowseFileDictModel) -> bool:
        """
        当前下载对象所在Map表是否为单文件

        Args:
            download_file: 当前下载对象

        Returns:
            bool: 是否为单文件
        """
        ori_uuid = download_file.oriUuid
        return not self._file_maps[ori_uuid].isDir

    def recover_download_file(self, download_file: BrowseFileDictModel) -> None:
        """
        当在下载中的文件发现自己需被暂停时, 将文件追加回downloadList, 用于继续下载

        Args:
            download_file: 下载中的文件对象

        Returns:
            None
        """
        self.sysLogger.debug(f"将文件追回下载列表, 文件: {download_file.relativePath}")
        ori_uuid = download_file.oriUuid
        if ori_uuid not in self._file_maps:
            self.sysLogger.warning(f"Map表已被删除, 无法追回下载, Map表: {ori_uuid}")
            return
        self._file_maps[ori_uuid].downloadList.append(download_file)
        self.sysLogger.debug(f"文件追回下载列表完成, 文件: {download_file.relativePath}")

    def emit_download_status(
        self,
        download_file: BrowseFileDictModel,
        status: DownloadStatus,
        msg: Union[str, float],
    ) -> None:
        """
        发射文件下载状态

        Args:
            download_file: 单个文件下载对象
            status: 下载状态
            msg: 状态附带的信息

        Returns:
            None
        """
        ori_uuid = download_file.oriUuid
        file_map = self._file_maps[ori_uuid]
        relativePath = file_map.nativeObj.relativePath
        if status is DownloadStatus.DOING:
            if file_map.isDir or self.is_padding(download_file):
                return
            self.sysLogger.debug(f"正在发射更新下载进度事件, 路径: {relativePath}, 进度: {msg}")
            self.signal.emit((file_map.nativeObj, status, int(msg)))
        elif status is DownloadStatus.PAUSE:
            self.sysLogger.debug(f"正在发射已暂停下载事件, 路径: {relativePath}")
            self.recover_download_file(download_file)
            self.signal.emit((file_map.nativeObj, status, msg))
            self.sysLogger.debug(f"发射已暂停下载事件完成, 路径: {relativePath}")
        elif status is DownloadStatus.FAILED:
            self.sysLogger.debug(f"正在发射下载失败事件, 路径: {relativePath}, 失败原因: {msg}")
            self.recover_download_file(download_file)
            self.signal.emit((file_map.nativeObj, status, msg))
            self.sysLogger.debug(f"发射下载失败事件完成, 路径: {relativePath}")
        else:
            file_map.increase()
            if file_map.allDone:
                self.sysLogger.debug(f"正在发射下载成功事件, 路径: {relativePath}")
                self.signal.emit((file_map.nativeObj, status, "下载完成"))
                self.sysLogger.debug(f"发射下载成功事件完成, 路径: {relativePath}")
                self._file_maps.pop(ori_uuid)
            elif file_map.isDir:
                self.sysLogger.debug(
                    f"正在发射更新下载进度事件, 路径： {relativePath}, 进度: {file_map.progress}"
                )
                self.signal.emit(
                    (file_map.nativeObj, DownloadStatus.DOING, file_map.progress)
                )
                self.sysLogger.debug(f"发射更新下载进度事件完成, 路径: {relativePath}")

    @property
    def hasNeedDownload(self) -> bool:
        """
        是否还有需要下载的文件

        Returns:
            bool: 是否还有需要下载的文件
        """
        return any(
            uuid not in self._padding_fileUuids and file_map.downloadList
            for uuid, file_map in self._file_maps.items()
        )


class DownloadHttpFileThread(BaseDownloadFileThread):
    def run(self) -> None:
        """
        线程运行入口函数

        Returns:
            None
        """
        self.sysLogger.debug("开始下载HTTP分享文件")
        os.environ["NO_PROXY"] = "127.0.0.1"
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        while self.run_flag:
            if self.hasNeedDownload:
                download_list = self._append_up_to_five_files()
                loop.run_until_complete(self._main(download_list))
            else:
                time.sleep(3)

        loop.close()

    async def _main(self, file_list: List[BrowseFileDictModel]) -> None:
        timeout = aiohttp.ClientTimeout(total=600)
        connector = aiohttp.TCPConnector(force_close=True, limit=5)
        async with aiohttp.ClientSession(
            connector=connector, timeout=timeout
        ) as session:
            tasks = [asyncio.create_task(self._download(session, x)) for x in file_list]
            await asyncio.wait(tasks)

    async def _download(
        self, session: aiohttp.ClientSession, download_file: BrowseFileDictModel
    ) -> None:
        relativePath = download_file.relativePath
        file_path = os.path.abspath(os.path.join(settings.DOWNLOAD_DIR, relativePath))
        if self.is_padding(download_file):
            self.emit_download_status(download_file, DownloadStatus.PAUSE, "停止下载成功")
            return
        url = download_file.downloadUrl
        if download_file.isDir:
            os.makedirs(file_path, exist_ok=True)
            if HIT_LOG in url:
                self.sysLogger.debug(f"本次下载动作仅用于让服务器写下载记录, 路径: {relativePath}")
                await session.get(url)
                self.sysLogger.debug(f"让服务器写下载记录完成, 路径: {relativePath}")
            return

        if os.path.exists(file_path):
            local_size = os.path.getsize(file_path)
            headers = {"Range": f"bytes={os.path.getsize(file_path)}-"}
            mode = "ab"
        else:
            local_size = 0
            headers = {}
            mode = "wb"
            base_path = os.path.dirname(file_path)
            os.makedirs(base_path, exist_ok=True)
        try:
            self.sysLogger.debug(f"开始下载文件, 路径: {relativePath}")
            async with session.get(url, headers=headers) as response:
                full_size = local_size + response.content_length
                if response.content_type == "application/json":
                    data = await response.json()
                    if response_ret_code(data) == RET.FILENOTFOUND:
                        self.sysLogger.warning(f"文件分享后被删除, 文件路径: {relativePath}")
                    else:
                        self.sysLogger.warning(
                            f"对方系统异常, 服务端返回的信息: {data.get('errmsg', '未知异常')}"
                        )
                    if self.is_single_file(download_file):
                        self.emit_download_status(
                            download_file, DownloadStatus.FAILED, "文件被删除或分享异常"
                        )
                    return
                elif response.content_type != "application/octet-stream":
                    self.sysLogger.warning(
                        f"下载文件失败, 失败原因: 对方系统异常, 文件路径: {relativePath}"
                    )
                    self.emit_download_status(
                        download_file, DownloadStatus.FAILED, "对方系统异常"
                    )
                    return
                self.sysLogger.debug(f"正在写入本地, 路径: {relativePath}")
                with open(file_path, mode) as f:
                    if full_size == 0:
                        self.emit_download_status(
                            download_file, DownloadStatus.SUCCESS, "文件大小为0"
                        )
                        return
                    self.emit_download_status(
                        download_file,
                        DownloadStatus.DOING,
                        local_size * 100 / full_size,
                    )
                    async for chunk in response.content.iter_chunked(self._chunk_size):
                        if self.is_padding(download_file):
                            self.emit_download_status(
                                download_file, DownloadStatus.PAUSE, "停止下载成功"
                            )
                            return
                        f.write(chunk)
                        local_size += chunk.__sizeof__()
                        self.emit_download_status(
                            download_file,
                            DownloadStatus.DOING,
                            local_size * 100 / full_size,
                        )
            self.emit_download_status(download_file, DownloadStatus.SUCCESS, "下载成功")
        except aiohttp.ClientConnectorError:
            self.sysLogger.warning(f"下载文件失败, 失败原因: 连接目标网络失败, 文件路径: {relativePath}")
            self.emit_download_status(download_file, DownloadStatus.FAILED, "连接目标网络失败")
        except aiohttp.ClientPayloadError:
            self.sysLogger.warning(
                f"下载文件失败, 失败原因: 与目标失去连接或该文件对方无权限, 文件路径: {relativePath}"
            )
            self.emit_download_status(
                download_file, DownloadStatus.FAILED, "与目标失去连接或该文件对方无权限"
            )
        except aiohttp.client_exceptions.ServerDisconnectedError:
            self.sysLogger.warning(
                f"下载文件失败, 失败原因: 远程服务器关闭连接, 可能为本地存在该文件引起冲突, 请将其删除后再重新下载, 文件路径: {relativePath}"
            )
            self.emit_download_status(download_file, DownloadStatus.FAILED, "远程服务器关闭连接")
        except Exception:
            self.sysLogger.error(
                f"下载文件失败, 文件路径: {relativePath}, 失败原因: 未知错误, 错误原始明细如下:\n{format_exc()}"
            )
            self.emit_download_status(download_file, DownloadStatus.FAILED, "未知错误")

    def _append_up_to_five_files(self) -> List[BrowseFileDictModel]:
        self.sysLogger.debug("追加最多5个文件到下载列表")
        downloading_list = []
        """
        1. 先从每个文件对象中拿出最多一个文件去下载
        2. 若第1步不够5个文件, 则继续按序从文件对象中拿取文件, 直至拿满5个文件或拿完所有文件对象的文件
        """
        has_full = False
        while self.hasNeedDownload:
            if has_full:
                break
            for uuid, file_map in self._file_maps.items():
                if not self.hasNeedDownload:
                    break
                if uuid in self._padding_fileUuids or not file_map.downloadList:
                    continue
                downloading_list.append(file_map.downloadList.pop(0))
                if len(downloading_list) >= 5:
                    has_full = True
                    break

        return downloading_list


class DownloadFtpFileThread(BaseDownloadFileThread):
    def run(self) -> None:
        """
        线程运行入口函数

        Returns:
            None
        """
        self.sysLogger.debug("开始下载FTP分享文件")
        os.environ["NO_PROXY"] = "127.0.0.1"
        while self.run_flag:
            if self.hasNeedDownload:
                file_map = self._gen_one_file_map()
                if file_map is None:
                    continue
                download_list = file_map.downloadList
                targetObj = download_list[0]
                ftp_param = self._get_ftp_param(targetObj)
                ftp_status, ftp_client = self._generate_ftp_client(ftp_param)
                if not ftp_status:
                    self.sysLogger.warning(
                        f"文件/文件夹下载失败, 失败原因: {ftp_client}, 文件路径: {targetObj.get('relativePath', '未知路径')}"
                    )
                    self.emit_download_status(
                        targetObj, DownloadStatus.FAILED, ftp_client
                    )
                    continue

                while download_list:
                    download_file = download_list.pop(0)
                    if download_file.isDir:
                        relativePath = download_file.relativePath
                        folder_path = os.path.abspath(
                            os.path.join(settings.DOWNLOAD_DIR, relativePath)
                        )
                        os.makedirs(folder_path, exist_ok=True)
                        continue

                    if self.is_padding(download_file):
                        self.emit_download_status(
                            download_file, DownloadStatus.PAUSE, "停止下载成功"
                        )
                        break
                    self._download_file(ftp_client, download_file)
                ftp_client.close()
            else:
                time.sleep(3)

    def _generate_ftp_client(
        self, ftp_param: Dict[str, Union[str, int]]
    ) -> Tuple[bool, Union[str, FTP]]:
        self.sysLogger.debug("创建FTP连接")
        if not ftp_param:
            return (False, "获取FTP必要参数失败")
        host = ftp_param.get("host")
        port = ftp_param.get("port")
        user = ftp_param.get("user")
        passwd = ftp_param.get("passwd")
        if not all([host, port, user, passwd]):
            return (False, "对方系统异常")
        ftp = FTP()
        try:
            ftp.connect(host, port)
        except:
            return (False, "FTP服务连失败, 请确认对方FTP服务有开启")

        try:
            ftp.login(user, passwd)
        except:
            return (False, "FTP登录失败, 请确认对方服务状态")
        else:
            ftp.encoding = "utf-8"
            return (True, ftp)

    def _download_file(
        self, ftp_client: FTP, download_file: BrowseFileDictModel
    ) -> None:
        relativePath = download_file.relativePath
        if self.is_padding(download_file):
            self.emit_download_status(download_file, DownloadStatus.PAUSE, "停止下载成功")
            return
        fileName = download_file.fileName
        cwd = self._calc_cwd(relativePath)
        local_path = os.path.join(settings.DOWNLOAD_DIR, relativePath)
        if os.path.exists(local_path):
            local_size = os.path.getsize(local_path)
            mode = "ab"
        else:
            mode = "wb"
            local_size = 0
            base_path = os.path.dirname(local_path)
            os.makedirs(base_path, exist_ok=True)

        with open(local_path, mode) as r_f:
            ftp_client.sendcmd("TYPE I")
            try:
                ftp_client.cwd(cwd)
            except:
                self.sysLogger.warning(
                    f"文件下载失败, 失败原因: 文件所在目录已不存在, 文件路径: {relativePath}"
                )
                if self.is_single_file(download_file):
                    self.emit_download_status(
                        download_file, DownloadStatus.FAILED, "文件所在目录已不存在"
                    )
                return
            full_size = ftp_client.size(fileName)
            if full_size == 0:
                self.emit_download_status(
                    download_file, DownloadStatus.SUCCESS, "文件大小为0"
                )
                return
            self.emit_download_status(
                download_file, DownloadStatus.DOING, local_size * 100 / full_size
            )
            ftp_client.sendcmd(f"REST {local_size}")
            with ftp_client.transfercmd(f"RETR {fileName}", None) as conn:
                while True:
                    if self.is_padding(download_file):
                        self.emit_download_status(
                            download_file, DownloadStatus.PAUSE, "停止下载成功"
                        )
                        return
                    try:
                        data = conn.recv(self._chunk_size)
                    except Exception:
                        self.sysLogger.warning(
                            f"文件下载失败, 失败原因: 文件已找到,但下载中出现异常, 文件路径: {relativePath}"
                        )
                        self.emit_download_status(
                            download_file, DownloadStatus.FAILED, "下载异常"
                        )
                        return
                    if not data:
                        break
                    r_f.write(data)
                    local_size += len(data)
                    self.emit_download_status(
                        download_file,
                        DownloadStatus.DOING,
                        local_size * 100 / full_size,
                    )

                if isinstance(conn, ssl.SSLSocket):
                    conn.unwrap()
            ftp_client.voidresp()
            self.emit_download_status(download_file, DownloadStatus.SUCCESS, "下载成功")

    def _get_ftp_param(
        self, download_file: BrowseFileDictModel
    ) -> Dict[str, Union[str, int]]:
        self.sysLogger.debug("获取FTP必要参数")
        os.environ["NO_PROXY"] = "127.0.0.1"
        headers = {"X-Client": "file-sharer client"}
        try:
            response = requests.get(
                download_file.downloadUrl, headers=headers, timeout=2
            )
        except:
            self.sysLogger.warning("连接服务器失败, 获取FTP必要参数失败")
            return {}

        try:
            result = json.loads(response.text)
        except json.JSONDecodeError:
            self.sysLogger.warning("服务器返回非法数据")
            return {}

        if isinstance(result, dict):
            errno = response_ret_code(result)
            if errno == RET.OK:
                self.sysLogger.debug("获取FTP必要参数完成")
                return result.get("data", {})
            else:
                self.sysLogger.debug(f"服务器返回数据异常, 异常代码: {errno}")
                return {}
        else:
            self.sysLogger.warning("服务器返回非标数据")
            return {}

    def _calc_cwd(self, relativePath: str) -> str:
        """
        从文件相对路径计算出文件所在的FTP cwd路径
            e.g. a/b/c/d.txt, FTP分享路径为a, 结果: /b/c

        Args:
            relativePath: 文件的相对路径

        Returns:
            str: 文件所在的FTP cwd路径
        """
        self.sysLogger.debug(f"正在计算文件cwd路径, 路径: {relativePath}")
        dir_name = os.path.dirname(relativePath)
        # FTP的cwd路径用'/'区分层级, 因此需将当前系统的路径分层符替换成'/'
        dir_name = dir_name.replace(os.sep, "/")
        result = "/"
        if "/" in dir_name:
            result = dir_name[dir_name.find("/") :]
        self.sysLogger.debug(f"cwd路径计算完成, 文件路径: {relativePath}, 结果: {result}")

        return result

    def _gen_one_file_map(self) -> Optional[BrowseFileDataModel]:
        self.sysLogger.debug("拿取一个待下载列表")

        return next(
            (
                file_map
                for uuid, file_map in self._file_maps.items()
                if file_map.downloadList and uuid not in self._padding_fileUuids
            ),
            None,
        )
