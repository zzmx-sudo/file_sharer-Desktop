import os

class FileModel:

    def __init__(self, path: str) -> None:

        self._target_path = path
        self._download_number = 0

    @property
    def isDir(self) -> bool:

        return True

    @property
    def download_number(self) -> int:

        return self._download_number