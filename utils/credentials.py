__all__ = ["Credentials"]

import hashlib
import base64
from typing import Union

from model.file import FileModel, DirModel
from utils.logger import sysLogger


class Credentials:
    @classmethod
    def encode(cls, secret_key: str, pwd: str) -> str:
        """
        生成凭据

        Args:
            secret_key: 凭据盐值
            pwd: 凭据密码

        Returns:
            str: 生成的凭据
        """
        iterations = 120000
        hash_name = "sha256"
        hash = hashlib.pbkdf2_hmac(
            hash_name, pwd.encode("utf-8"), secret_key.encode("utf-8"), iterations
        )
        b64_str = base64.b64encode(hash).decode("utf-8")
        sysLogger.debug("生成凭据成功")
        return f"pbkdf2_sha256${b64_str}"

    @classmethod
    def verification(cls, fileObj: Union[FileModel, DirModel], pwd: str) -> bool:
        """
        凭据验证

        Args:
            fileObj: 待验证凭据文件对象
            pwd: 输入的密码

        Returns:
            bool: 是否通过校验
        """
        if fileObj.secret_key == "" or fileObj.credentials == "":
            sysLogger.debug("该分享无需验证密码")
            return True

        new_hash = cls.encode(fileObj.secret_key, pwd)
        return new_hash == fileObj.credentials
