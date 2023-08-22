import os

class FileModel:

    def __init__(self, path):

        self._target_path = path
        self._download_number = 0

    @property
    def isDir(self):

        return

    @property
    def download_number(self):

        return self