__all__ = ["Credentials"]

import hashlib
import base64
from typing import Union

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

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
        pwd = cls.__decrypt(fileObj.secret_key, pwd)
        new_hash = cls.encode(fileObj.secret_key, pwd)
        return new_hash == fileObj.credentials

    @staticmethod
    def __decrypt(salt: str, ciphertext: str) -> str:
        """
        对密码解密

        Args:
            salt: 密钥的盐值
            ciphertext: 密文

        Returns:
            str: 解密后的结果
        """
        iv_b64, encrypted_data_b64 = ciphertext.split("|")
        salt = salt.encode("utf-8")
        iv = base64.b64decode(iv_b64)
        encrypted_data = base64.b64decode(encrypted_data_b64)

        # 使用盐值和密钥生成解密密钥
        backend = default_backend()
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,  # 密钥长度
            salt=salt,
            iterations=100000,  # 迭代次数
            backend=backend,
        )
        derived_key = kdf.derive("secret_key".encode())

        # 创建解密器
        cipher = Cipher(algorithms.AES(derived_key), modes.CBC(iv), backend=backend)
        decryptor = cipher.decryptor()

        # 解密数据
        padded_plaintext = decryptor.update(encrypted_data) + decryptor.finalize()

        # 去除填充
        unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
        plaintext = unpadder.update(padded_plaintext) + unpadder.finalize()

        return plaintext.decode()
