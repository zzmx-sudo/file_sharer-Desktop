from enum import Enum

# URI
FILE_LIST_URI = "/file_list"
DOWNLOAD_URI = "/download"

# share type
class ShareType(str, Enum):
    http = "http"
    ftp = "ftp"