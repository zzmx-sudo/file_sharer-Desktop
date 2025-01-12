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
from multiprocessing import Queue
from traceback import format_exc
from typing import Sequence, Dict, Any, List, Union, Tuple

import requests
import aiohttp
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.Qt import QApplication
from ftplib import FTP

from settings import settings
from utils.logger import sysLogger
from .public_types import DownloadStatus, HIT_LOG


class WatchResultThread(QThread):
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
            sysLogger.debug(f"监听到分享被浏览, 正在发射更新浏览次数事件, 分享的uuid: {file_uuid}")
            self.signal.emit(file_uuid)
            sysLogger.debug(f"发射更新浏览次数事件完成, 分享的uuid: {file_uuid}")


class LoadBrowseUrlThread(QThread):
    signal = pyqtSignal(dict)

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
        sysLogger.debug(f"正在加载分享链接[{self._browse_url}]")
        os.environ["NO_PROXY"] = "127.0.0.1"
        result = {}
        try:
            response = requests.get(self._browse_url, timeout=2)
        except:
            sysLogger.debug(f"连接服务异常, 正在发射显示分享链接数据事件")
            self.signal.emit(result)
            return

        try:
            result = json.loads(response.text)
        except json.JSONDecodeError:
            sysLogger.debug(f"服务器返回非法数据[{self._browse_url}]")
            pass

        if not self.run_flag:
            sysLogger.debug(f"加载分享链接任务停止成功[{self._browse_url}]")
            return
        sysLogger.debug(f"加载分享链接完成, 正在发射显示分享链接数据事件[{self._browse_url}]")
        self.signal.emit(result)
        sysLogger.debug(f"发射显示分享链接数据事件成功, 加载分享链接任务完成[{self._browse_url}]")


class DownloadHttpFileThread(QThread):
    signal = pyqtSignal(tuple)

    def __init__(self, fileList: Sequence[Dict[str, Any]]):
        """
        下载HTTP分享文件线程类初始化函数

        Args:
            fileList: 待下载文件对象列表
        """
        super(DownloadHttpFileThread, self).__init__()
        self._file_list = list(fileList)
        self._chunk_size = 1048576
        self.run_flag = True
        self._pause_fileObjs = []

    async def _download(
        self, session: aiohttp.ClientSession, fileObj: Dict[str, Any]
    ) -> None:
        relativePath = fileObj["relativePath"]
        if self._is_pause(fileObj):
            sysLogger.debug(f"下载暂停完成, 文件路径: {relativePath}")
            return
        url = fileObj["downloadUrl"]
        if HIT_LOG in url and fileObj.get("isDir"):
            sysLogger.debug(f"本次下载动作仅用于让服务器写下载记录, 路径: {relativePath}")
            await session.get(url)
            sysLogger.debug(f"让服务器写下载记录完成, 路径: {relativePath}")
            return
        file_path = os.path.abspath(os.path.join(settings.DOWNLOAD_DIR, relativePath))
        if os.path.exists(file_path):
            local_size = os.path.getsize(file_path)
            headers = {"Range": f"bytes={os.path.getsize(file_path)}-"}
            mode = "ab"
        else:
            local_size = 0
            headers = {}
            mode = "wb"
            base_path = os.path.dirname(file_path)
            if not os.path.isdir(base_path):
                os.makedirs(base_path)
        try:
            sysLogger.debug(f"开始下载文件, 路径: {relativePath}")
            async with session.get(url, headers=headers) as response:
                full_size = local_size + response.content_length
                if response.content_type == "application/json":
                    data = await response.json()
                    if data.get("errno", 200) == 404:
                        sysLogger.warning(f"文件分享后被删除, 文件路径: {relativePath}")
                        self.signal.emit((fileObj, DownloadStatus.FAILED, "文件分享后被删除"))
                        return
                    else:
                        sysLogger.warnint(
                            f"对方系统异常, 服务端返回的信息: {data.get('errmsg', '未知异常')}"
                        )
                        self.signal.emit((fileObj, DownloadStatus.FAILED, "对方系统异常"))
                        return
                elif response.content_type != "application/octet-stream":
                    sysLogger.warning(f"下载文件失败, 失败原因: 对方系统异常, 文件路径: {relativePath}")
                    self.signal.emit((fileObj, DownloadStatus.FAILED, "对方系统异常"))
                    return
                sysLogger.debug(f"正在写入本地, 路径: {relativePath}")
                with open(file_path, mode) as f:
                    if full_size == 0:
                        sysLogger.debug(f"文件大小为0, 正在发射更新下载状态为成功事件, 路径: {relativePath}")
                        self.signal.emit((fileObj, DownloadStatus.SUCCESS, "下载成功"))
                        sysLogger.debug(f"发射更新下载状态为成功事件完成, 路径: {relativePath}")
                        return
                    sysLogger.debug(f"正在发射更新下载进度事件, 路径: {relativePath}")
                    self.signal.emit(
                        (fileObj, DownloadStatus.DOING, local_size * 100 / full_size)
                    )
                    sysLogger.debug(f"发射更新下载进度事件完成, 路径: {relativePath}")
                    async for chunk in response.content.iter_chunked(self._chunk_size):
                        if self._is_pause(fileObj):
                            sysLogger.debug(
                                f"下载暂停完成, 正在发射更新下载状态为暂停事件, 路径: {relativePath}"
                            )
                            self.signal.emit((fileObj, DownloadStatus.PAUSE, "暂停成功"))
                            sysLogger.debug(f"发射更新下载状态为暂停事件完成, 路径: {relativePath}")
                            return
                        f.write(chunk)
                        local_size += chunk.__sizeof__()
                        sysLogger.debug(f"正在发射更新下载进度事件, 路径: {relativePath}")
                        self.signal.emit(
                            (
                                fileObj,
                                DownloadStatus.DOING,
                                local_size * 100 / full_size,
                            )
                        )
                        sysLogger.debug(f"发射更新下载进度事件完成, 路径: {relativePath}")
            sysLogger.debug(f"正在发射更新下载状态为成功事件, 路径: {relativePath}")
            self.signal.emit((fileObj, DownloadStatus.SUCCESS, "下载成功"))
            sysLogger.debug(f"发射更新下载状态为成功事件完成, 路径: {relativePath}")
        except aiohttp.ClientConnectorError:
            sysLogger.warning(f"下载文件失败, 失败原因: 连接目标网络失败, 文件路径: {relativePath}")
            self.signal.emit((fileObj, DownloadStatus.FAILED, "连接目标网络失败"))
        except aiohttp.ClientPayloadError:
            sysLogger.warning(f"下载文件失败, 失败原因: 与目标失去连接或该文件对方无权限, 文件路径: {relativePath}")
            self.signal.emit((fileObj, DownloadStatus.FAILED, "与目标失去连接或该文件对方无权限"))
        except aiohttp.client_exceptions.ServerDisconnectedError:
            sysLogger.warning(
                f"下载文件失败, 失败原因: 远程服务器关闭连接, 可能为本地存在该文件引起冲突, 请将其删除后再重新下载, 文件路径: {relativePath}"
            )
            self.signal.emit((fileObj, DownloadStatus.FAILED, "远程服务器关闭连接"))
        except Exception:
            sysLogger.error(
                f"下载文件失败, 文件路径: {relativePath}, 失败原因: 未知错误, 错误原始明细如下:\n{format_exc()}"
            )
            self.signal.emit((fileObj, DownloadStatus.FAILED, "未知错误"))

    async def _main(self, fileList: list) -> None:
        timeout = aiohttp.ClientTimeout(total=600)
        connector = aiohttp.TCPConnector(force_close=True)
        async with aiohttp.ClientSession(
            connector=connector, timeout=timeout
        ) as session:
            tasks = [asyncio.create_task(self._download(session, x)) for x in fileList]
            await asyncio.wait(tasks)

    def run(self) -> None:
        """
        线程运行入口函数

        Returns:
            None
        """
        sysLogger.debug("开始下载HTTP分享文件")
        os.environ["NO_PROXY"] = "127.0.0.1"
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        while self.run_flag:
            if self._file_list:
                downloading_list = self._append_up_to_five_files()
                loop.run_until_complete(self._main(downloading_list))
                QApplication.processEvents()
            else:
                time.sleep(3)

        loop.close()

    def _append_up_to_five_files(self) -> List[Dict[str, Any]]:
        sysLogger.debug("追加最多5个文件到下载列表")
        downloading_list = []
        while self._file_list:
            fileObj = self._file_list.pop(0)
            if fileObj not in self._pause_fileObjs:
                downloading_list.append(fileObj)
                if len(downloading_list) >= 5:
                    break
            else:
                self._pause_fileObjs.remove(fileObj)

        return downloading_list

    def append(self, fileList: Sequence[Dict[str, Any]]) -> None:
        """
        追加下载文件对象列表

        Args:
            fileList: 待追加文件对象列表

        Returns:
            None
        """
        sysLogger.debug("追加下载列表")
        self._file_list.extend(fileList)

    def pause(self, fileObj: Dict[str, Any]) -> None:
        """
        暂停下载文件对象

        Args:
            fileObj: 需暂停下载的文件对象

        Returns:
            None
        """
        sysLogger.debug("暂停下载")
        if fileObj in self._pause_fileObjs:
            return
        self._pause_fileObjs.append(fileObj)
        self.signal.emit((fileObj, DownloadStatus.PAUSE, "暂停成功"))

    def _is_pause(self, fileObj: Dict[str, Any]) -> bool:
        if fileObj in self._pause_fileObjs:
            self._pause_fileObjs.remove(fileObj)
            return True
        return False


class DownloadFtpFileThread(QThread):
    signal = pyqtSignal(tuple)

    def __init__(self, fileList: Sequence[Dict[str, Any]]):
        """
        下载FTP分享文件线程类初始化函数

        Args:
            fileList: 待下载文件对象列表
        """
        super(DownloadFtpFileThread, self).__init__()
        self._file_list = [fileList]
        self.run_flag = True
        self._chunk_size = 1048576
        self._pause_fileObjs = []

    def run(self) -> None:
        """
        线程运行入口函数

        Returns:
            None
        """
        sysLogger.debug("开始下载FTP分享文件")
        os.environ["NO_PROXY"] = "127.0.0.1"
        while self.run_flag:
            if self._file_list:
                download_list = self._file_list.pop(0)
                # 若下载单文件, 将该文件信息作为唯一元素存储在列表内
                # 若下载文件夹, 将文件夹信息存储在列表第一个元素, 仅用其获取FTP参数
                if len(download_list) == 1:
                    targetObj = download_list[0]
                else:
                    targetObj = download_list.pop(0)
                ftp_param = self._get_ftp_param(targetObj)
                ftp_status, ftp_client = self._generate_ftp_client(ftp_param)
                if not ftp_status:
                    sysLogger.warning(
                        f"文件/文件夹下载失败, 失败原因: {ftp_client}, 文件路径: {targetObj.get('relativePath', '未知路径')}"
                    )
                    for fileDict in download_list:
                        self.signal.emit((fileDict, DownloadStatus.FAILED, ftp_client))
                    continue

                for fileDict in download_list:
                    self._download_file(ftp_param["cwd"], ftp_client, fileDict)
                    QApplication.processEvents()
                ftp_client.close()
            else:
                time.sleep(3)

    def _generate_ftp_client(
        self, ftp_param: Dict[str, Union[str, int]]
    ) -> Tuple[bool, Union[str, FTP]]:
        sysLogger.debug("创建FTP连接")
        if not ftp_param:
            return (False, "获取FTP必要参数失败")
        host = ftp_param.get("host")
        port = ftp_param.get("port")
        user = ftp_param.get("user")
        passwd = ftp_param.get("passwd")
        if not all([host, port, user, passwd]):
            return (False, "对方系统异常")
        if "cwd" not in ftp_param:
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
        self, cwd: str, ftp_client: FTP, fileDict: Dict[str, Any]
    ) -> None:
        relativePath = fileDict["relativePath"]
        if self._is_pause(fileDict):
            sysLogger.debug(f"下载暂停完成, 文件路径: {relativePath}")
            return
        fileName = fileDict["fileName"]
        cwd = self._calc_cwd(cwd, relativePath)
        local_path = os.path.join(settings.DOWNLOAD_DIR, relativePath)
        if os.path.exists(local_path):
            local_size = os.path.getsize(local_path)
            mode = "ab"
        else:
            mode = "wb"
            local_size = 0
            base_path = os.path.dirname(local_path)
            if not os.path.isdir(base_path):
                os.makedirs(base_path)

        with open(local_path, mode) as r_f:
            ftp_client.sendcmd("TYPE I")
            try:
                ftp_client.cwd(cwd)
            except:
                sysLogger.warning(f"文件下载失败, 失败原因: 文件所在目录已不存在, 文件路径: {relativePath}")
                self.signal.emit((fileDict, DownloadStatus.FAILED, "文件所在目录已不存在"))
                return
            full_size = ftp_client.size(fileName)
            if full_size == 0:
                sysLogger.debug(f"文件大小为0, 正在发射更新下载状态为成功事件, 路径: {relativePath}")
                self.signal.emit((fileDict, DownloadStatus.SUCCESS, "下载成功"))
                sysLogger.debug(f"发射更新下载状态为成功事件完成, 路径: {relativePath}")
                return
            sysLogger.debug(f"正在发射更新下载进度事件, 路径: {relativePath}")
            self.signal.emit(
                (fileDict, DownloadStatus.DOING, local_size * 100 / full_size)
            )
            sysLogger.debug(f"发射更新下载进度事件完成, 路径: {relativePath}")
            ftp_client.sendcmd(f"REST {local_size}")
            with ftp_client.transfercmd(f"RETR {fileName}", None) as conn:
                while True:
                    if self._is_pause(fileDict):
                        sysLogger.debug(f"下载暂停完成, 正在发射更新下载状态为暂停事件, 路径: {relativePath}")
                        self.signal.emit((fileDict, DownloadStatus.PAUSE, "暂停成功"))
                        sysLogger.debug(f"发射更新下载状态为暂停事件完成, 路径: {relativePath}")
                        return
                    try:
                        data = conn.recv(self._chunk_size)
                    except Exception:
                        sysLogger.warning(
                            f"文件下载失败, 失败原因: 文件已找到,但下载中出现异常, 文件路径: {relativePath}"
                        )
                        self.signal.emit(
                            (fileDict, DownloadStatus.FAILED, "文件已找到,但下载中出现异常")
                        )
                    if not data:
                        break
                    r_f.write(data)
                    local_size += len(data)
                    sysLogger.debug(f"正在发射更新下载进度事件, 路径: {relativePath}")
                    self.signal.emit(
                        (fileDict, DownloadStatus.DOING, local_size * 100 / full_size)
                    )
                    sysLogger.debug(f"发射更新下载进度事件完成, 路径: {relativePath}")

                if isinstance(conn, ssl.SSLSocket):
                    conn.unwrap()
            ftp_client.voidresp()
            sysLogger.debug(f"正在发射更新下载状态为成功事件, 路径: {relativePath}")
            self.signal.emit((fileDict, DownloadStatus.SUCCESS, "下载成功"))
            sysLogger.debug(f"发射更新下载状态为成功事件完成, 路径: {relativePath}")

    def _get_ftp_param(self, fileDict: Dict[str, Any]) -> Dict[str, Union[str, int]]:
        sysLogger.debug("获取FTP必要参数")
        os.environ["NO_PROXY"] = "127.0.0.1"
        headers = {"X-Client": "file-sharer client"}
        try:
            response = requests.get(
                fileDict.get("downloadUrl"), headers=headers, timeout=2
            )
        except:
            sysLogger.warning("连接服务器失败, 获取FTP必要参数失败")
            return {}

        try:
            result = json.loads(response.text)
        except json.JSONDecodeError:
            sysLogger.warning("服务器返回非法数据")
            return {}

        if isinstance(result, dict):
            errno = result.get("errno", None)
            if errno == 200:
                sysLogger.debug("获取FTP必要参数完成")
                return result.get("data", {})
            else:
                sysLogger.debug(f"服务器返回数据异常, 异常代码: {errno}")
                return {}
        else:
            sysLogger.warning("服务器返回非标数据")
            return {}

    def _calc_cwd(self, cwd: str, relativePath: str) -> str:
        sysLogger.debug(f"正在计算文件cwd路径, 路径: {relativePath}")
        if "\\" not in relativePath and "/" not in relativePath:
            result = cwd
        else:
            if not cwd:
                step = "/" if not settings.IS_WINDOWS else "\\"
                relativePath = relativePath[relativePath.find(step) :]
            result = os.path.join(cwd, os.path.dirname(relativePath))

        result = result.replace("\\", "/")
        if not result.startswith("/"):
            result = "/" + result

        return result

    def append(self, fileList: Sequence[Dict[str, Any]]) -> None:
        """
        追加下载文件对象列表

        Args:
            fileList: 待追加文件对象列表

        Returns:
            None
        """
        sysLogger.debug("追加下载列表")
        self._file_list.append(fileList)

    def pause(self, fileObj: Dict[str, Any]) -> None:
        """
        暂停下载文件对象

        Args:
            fileObj: 需暂停下载的文件对象

        Returns:
            None
        """
        sysLogger.debug("暂停下载")
        if fileObj in self._pause_fileObjs:
            return
        self._pause_fileObjs.append(fileObj)
        self.signal.emit((fileObj, DownloadStatus.PAUSE, "暂停成功"))

    def _is_pause(self, fileObj: Dict[str, Any]) -> bool:
        if fileObj in self._pause_fileObjs:
            self._pause_fileObjs.remove(fileObj)
            return True
        return False
