import time
import json
import os
import asyncio
from multiprocessing import Queue

import requests
import aiohttp
from PyQt5.QtCore import QThread, pyqtSignal

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
        self._loop = asyncio.get_running_loop()
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
            base_path = os.path.basename(file_path)
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
        while self.run_flag:
            if self._file_list:
                downloading_list = self._append_up_to_five_files()
                self._loop.run_until_complete(self._main(downloading_list))
            else:
                time.sleep(3)

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
                ftp_param = self._get_ftp_param(download_list[0])
                for fileDict in download_list:
                    errmsg = self._download_file(ftp_param, fileDict)
                    downloadUrl = fileDict["downloadUrl"]
                    if errmsg:
                        self.signal.emit((downloadUrl, False, errmsg))
                    else:
                        self.signal.emit((downloadUrl, True, "下载成功"))
            else:
                time.sleep(3)

    def _download_file(self, ftp_param: dict, fileDict: dict) -> str:
        host = ftp_param.get("host")
        port = ftp_param.get("port")
        user = ftp_param.get("user")
        passwd = ftp_param.get("passwd")
        cwd = ftp_param.get("cwd")
        if not all([host, port, user, passwd, cwd]):
            return "对方系统异常"

        relativePath = fileDict["relativePath"]
        cwd = self._calc_cwd(cwd, relativePath)
        local_path = os.path.join(settings.DOWNLOAD_DIR, relativePath)
        base_path = os.path.dirname(local_path)


    def _get_ftp_param(self, fileDict: dict) -> dict:
        pass

    def _calc_cwd(self, cwd: str, relativePath: str) -> str:
        pass

    def append(self, fileList: list) -> None:

        self._file_list.append(fileList)