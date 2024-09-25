__all__ = [
    "FILE_LIST_URI",
    "DOWNLOAD_URI",
    "ShareType",
    "DownloadStatus",
    "ThemeColor",
    "ControlColorStruct",
    "ColorCardStruct",
]

from enum import Enum
from typing import Optional, Union
from collections import namedtuple

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


# theme color
class ThemeColor(str, Enum):
    Default = "Default"
    Red = "Red"
    Orange = "Orange"
    Yellow = "Yellow"
    Green = "Green"
    Cyan = "Cyan"
    Blue = "Blue"
    Purple = "Purple"

    @classmethod
    def dispatch(cls, color: Union[str, "ThemeColor"]) -> Optional["ThemeColor"]:
        if not isinstance(color, cls):
            if isinstance(color, str):
                for obj in cls:
                    if obj == color:
                        return obj
                return None
            else:
                return None

        return color


# control color struct
ControlColorStruct = namedtuple(
    "ControlColorStruct",
    [
        "DirName",
        "BaseColor",
        "LightColor",
        "DeepColor",
        "BaseBgColor",
        "LightBgColor",
        "DeepBgColor",
        "Deep2BgColor",
        "SpecialHovColor",
        "TextColor",
    ],
    defaults=[
        "Default",
        "64, 158, 255",
        "126, 199, 255",
        "42, 120, 255",
        "236, 236, 236",
        "247, 247, 247",
        "222, 222, 222",
        "200, 200, 200",
        "255, 255, 255",
        "0, 0, 0",
    ],
)


# color card struct - The elements is ControlColorStruct
def _namedtuple():
    struct = namedtuple(
        "ColorCardStruct",
        [x.value for x in ThemeColor],
        defaults=[None for _ in range(len(ThemeColor))],
    )

    def _dispatch(**kwargs):
        colorCardMap = {x.value: {} for x in ThemeColor}
        colorCardMap.update(kwargs)
        for theme_color, control_colors in colorCardMap.items():
            control_color_obj = ControlColorStruct(**control_colors)
            setattr(struct, theme_color, control_color_obj)
        return struct

    setattr(struct, "dispatch", _dispatch)
    return struct


ColorCardStruct = _namedtuple()
