__all__ = ["FILE_LIST_URI", "DOWNLOAD_URI", "ShareType"]

from enum import Enum

# URI
FILE_LIST_URI: str = "/file_list"
DOWNLOAD_URI: str = "/download"


# share type
class ShareType(str, Enum):
    http = "http"
    ftp = "ftp"


# download status
class DownloadStatus(int, Enum):
    DOING = 0
    PAUSE = 1
    SUCCESS = 2
    FAILED = 3