import time
import json
from multiprocessing import Queue

import requests
import aiohttp
from PyQt5.QtCore import QThread, pyqtSignal

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