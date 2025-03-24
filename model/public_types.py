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
UPLOAD_URI: str = "/upload"
HIT_LOG: str = "hit_log"
MOBILE_PREFIX: str = "/mobile"
STATIC_PREFIX: str = "/static"


# share type
class ShareType(str, Enum):
    """
    分享类型枚举类
    """

    http = "http"
    ftp = "ftp"


# download status
class DownloadStatus(int, Enum):
    """
    下载状态枚举类
    """

    DOING = 0
    PAUSE = 1
    SUCCESS = 2
    FAILED = 3


# verify status
class VerifyStatus(int, Enum):
    """
    校验状态枚举类
    """

    INFO = 0
    WARN = 1
    FATAL = 2
    DONE = 3


# theme color
class ThemeColor(str, Enum):
    """
    主题(颜色)枚举类
    """

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
        """
        主题枚举值分配

        Args:
            color: 待分配的颜色值

        Returns:
            Optional["ThemeColor"]: 主题枚举值或None(传入不合法参数时)
        """
        if not isinstance(color, cls):
            try:
                return cls(color)
            except:
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
def _namedtuple() -> "ColorCardStruct":
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
