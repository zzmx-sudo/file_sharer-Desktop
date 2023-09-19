__all__ = [
    "WatchResultThread",
    "LoadBrowseUrlThread",
    "DownloadHttpFileThread",
    "DownloadFtpFileThread"
]

import time
import json
import os
import asyncio
from multiprocessing import Queue
from typing import Union

import requests
import aiohttp
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.Qt import QApplication
from ftplib import FTP

from settings import settings
from utils.logger import sysLogger

class WatchResultThread(QThread):
    signal = pyqtSignal(str)

    def __init__(self, output_q: Queue) -> None:
        super(WatchResultThread, self).__init__()
        self.run_flag = True
        self._output_q = output_q

    def run(self) -> None:
        while self.run_flag:
            if not self._output_q.empty():
                file_uuid = self._output_q.get()
                self.signal.emit(file_uuid)
            else:
                time.sleep(2)

class LoadBrowseUrlThread(QThread):
    signal = pyqtSignal(dict)

    def __init__(self, browse_url: str) -> None:
        super(LoadBrowseUrlThread, self).__init__()
        self._browse_url = browse_url
        self.run_flag = True

    def run(self) -> None:
        os.environ["NO_PROXY"] = "127.0.0.1"
        result = {}
        try:
            response = requests.get(self._browse_url, timeout=2)
        except:
            self.signal.emit(result)
            return

        try:
            result = json.loads(response.text)
        except json.JSONDecodeError:
            pass

        if not self.run_flag:
            return
        self.signal.emit(result)

class DownloadHttpFileThread(QThread):
    signal = pyqtSignal(tuple)

    def __init__(self, fileList: list) -> None:
        super(DownloadHttpFileThread, self).__init__()
        self._file_list = fileList
        self._chunk_size = 1048576
        self.run_flag = True

    async def _download(
            self,
            session: aiohttp.ClientSession,
            url: str,
            file_path: str
    ) -> None:
        file_path = os.path.abspath(file_path)
        if os.path.exists(file_path):
            headers = {"Range": f"bytes={os.path.getsize(file_path)}-"}
            mode = "ab"
        else:
            headers = {}
            mode = "wb"
            base_path = os.path.dirname(file_path)
            if not os.path.isdir(base_path):
                os.makedirs(base_path)
        try:
            async with session.get(url, headers=headers) as response:
                if response.content_type != "application/octet-stream":
                    self.signal.emit((url, False, "对方系统异常"))
                    return
                with open(file_path, mode) as f:
                    async for chunk in response.content.iter_chunked(self._chunk_size):
                        f.write(chunk)
            self.signal.emit((url, True, "下载成功"))
        except aiohttp.ClientConnectorError:
            self.signal.emit((url, False, "连接目标网络失败"))
        except aiohttp.ClientPayloadError:
            self.signal.emit((url, False, "下载失败,与目标失去连接"))
        except Exception as e:
            self.signal.emit((url, False, "未知错误"))
            sysLogger.error("下载发生未知错误, 错误原始明细: %s" % str(e))

    async def _main(self, fileList: list) -> None:
        async with aiohttp.ClientSession() as session:
            tasks = [
                asyncio.create_task(
                    self._download(session, x["downloadUrl"],
                                  os.path.join(settings.DOWNLOAD_DIR, x["relativePath"]))
                ) for x in fileList
            ]
            await asyncio.wait(tasks)

    def run(self) -> None:
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

    def _append_up_to_five_files(self) -> list:
        downloading_list = []
        while self._file_list:
            downloading_list.append(self._file_list.pop(0))
            if len(downloading_list) >= 5:
                break

        return downloading_list

    def append(self, fileList: list) -> None:
        self._file_list.extend(fileList)

class DownloadFtpFileThread(QThread):
    signal = pyqtSignal(tuple)

    def __init__(self, fileList: list) -> None:
        super(DownloadFtpFileThread, self).__init__()
        self._file_list = [fileList]
        self.run_flag = True

    def run(self) -> None:
        os.environ["NO_PROXY"] = "127.0.0.1"
        while self.run_flag:
            if self._file_list:
                download_list = self._file_list.pop(0)
                # 若下载单文件, 将该文件信息作为唯一元素存储在列表内
                # 若下载文件夹, 将文件夹信息存储在列表第一个元素, 仅用其获取FTP参数
                if len(download_list) == 1:
                    ftp_param = self._get_ftp_param(download_list[0])
                else:
                    ftp_param = self._get_ftp_param(download_list.pop(0))
                ftp_status, ftp_client = self._generate_ftp_client(ftp_param)
                if not ftp_status:
                    for fileDict in download_list:
                        downloadUrl = fileDict["downloadUrl"]
                        self.signal.emit((downloadUrl, False, ftp_client))
                    continue

                for fileDict in download_list:
                    errmsg = self._download_file(ftp_param["cwd"], ftp_client, fileDict)
                    downloadUrl = fileDict["downloadUrl"]
                    if errmsg:
                        self.signal.emit((downloadUrl, False, errmsg))
                    else:
                        self.signal.emit((downloadUrl, True, "下载成功"))
                    QApplication.processEvents()
                ftp_client.close()
            else:
                time.sleep(3)

    def _generate_ftp_client(self, ftp_param: dict) -> tuple[bool, Union[str, FTP]]:
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

    def _download_file(self, cwd: str, ftp_client: FTP, fileDict: dict) -> str:
        relativePath = fileDict["relativePath"]
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
                return "文件所在目录已不存在"
            ftp_client.sendcmd(f"REST {local_size}")
            try:
                ftp_client.retrbinary(f"RETR {fileName}", r_f.write)
            except:
                return "文件已找到,但下载中出现异常"
            else:
                return ""

    def _get_ftp_param(self, fileDict: dict) -> dict:
        os.environ["NO_PROXY"] = "127.0.0.1"
        headers = {"X-Client": "file-sharer client"}
        try:
            response = requests.get(fileDict.get("downloadUrl"), headers=headers, timeout=2)
        except:
            return {}

        try:
            result = json.loads(response.text)
        except json.JSONDecodeError:
            return {}

        if isinstance(result, dict):
            if result.get("errno", "") == 200:
                return result.get("data", {})
            else:
                return {}
        else:
            return {}

    def _calc_cwd(self, cwd: str, relativePath: str) -> str:
        if "\\" not in relativePath and "/" not in relativePath:
            result =  cwd
        else:
            if not cwd:
                step = "/" if not settings.IS_WINDOWS else "\\"
                relativePath = relativePath[relativePath.find(step):]
            result = os.path.join(cwd, os.path.dirname(relativePath))

        result = result.replace("\\", "/")
        if not result.startswith("/"):
            result = "/" + result

        return result

    def append(self, fileList: list) -> None:

        self._file_list.append(fileList)