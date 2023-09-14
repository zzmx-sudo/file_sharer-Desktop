__all__ = [
    "DownloadFileDictModel"
]

class DownloadFileDictModel(dict):

    def __init__(self):
        super(DownloadFileDictModel, self).__init__()

    def update_download_status(self, url: str) -> None:
        pass
    