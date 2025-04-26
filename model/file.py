__all__ = ["FileModel", "DirModel"]

import os
import random
from typing import Any, Union, Dict, Optional

from model import public_types as ptype
from settings import settings
from utils import public_func


class FileModel:
    def __init__(
        self,
        path: str,
        uuid: str,
        parent_uuid: Optional[str] = None,
        pwd: Optional[str] = None,
        port: Optional[int] = None,
        ftp_base_path: Optional[str] = None,
        secret_key: Optional[str] = None,
        credentials: Optional[str] = None,
        **kwargs,
    ):
        """
        文件模型类初始化函数

        Args:
            path: 文件所在路径
            uuid: 文件uuid
            parent_uuid: 父级文件夹的uuid, 若无父级则为None, 默认为None
            pwd: FTP服务的密码, 若不是FTP共享则为None, 默认为None
            port: FTP服务的端口, 若不是FTP共享则为None, 默认为None
            ftp_base_path: FTP服务的根路径, 若不是FTP共享则为None, 默认为None
            secret_key: 文件分享的盐值, 用于密码校验, 默认无校验
            credentials: 文件分享的凭据, 用于密码校验, 默认无校验
            **kwargs: 其他关键字参数
        """
        self._uuid = f"{parent_uuid}>{uuid}" if parent_uuid else uuid
        self._target_path = path.rstrip(os.sep) if path.endswith(os.sep) else path
        self._browse_number = 0
        self._is_sharing = False
        self._row_index = None
        self._ftp_pwd = pwd
        self._ftp_port = port
        self._secret_key = secret_key
        self._credentials = credentials
        self._free_secret = False

        if self._uuid[0] == "h":
            self._share_type = ptype.ShareType.http
        else:
            self._share_type = ptype.ShareType.ftp

        if self._share_type is ptype.ShareType.ftp:
            self._ftp_base_path = (
                ftp_base_path if ftp_base_path else os.path.dirname(self._target_path)
            )
            if self._ftp_port is None:
                self._ftp_port = self._generate_ftp_port()
            if self._ftp_pwd is None:
                self._ftp_pwd = public_func.generate_ftp_passwd()
        else:
            self._ftp_base_path = None

    def _generate_ftp_port(self) -> int:
        """
        生成FTP服务端口

        Returns:
            int: FTP服务器端口
        """
        port = random.randint(10000, 65500)
        if not public_func.exists_port(port):
            return port
        else:
            return self._generate_ftp_port()

    @property
    def uuid(self) -> str:
        """
        文件对象的uuid

        Returns:
            str: 文件对象的uuid
        """
        return self._uuid

    @property
    def isSharing(self) -> bool:
        """
        文件对象是否被在分享中

        Returns:
            bool: 文件对象是否在分享中
        """
        return self._is_sharing

    @isSharing.setter
    def isSharing(self, newValue: bool) -> None:
        """
        修改文件对象分享状态

        Args:
            newValue: 将要修改的分享状态

        Returns:
            None
        """
        self._is_sharing = newValue

    @property
    def rowIndex(self) -> Union[None, int]:
        """
        文件对象在分享列表控件的行号

        Returns:
            Union[None, int]: 在分享列表控件的行号
        """
        return self._row_index

    @rowIndex.setter
    def rowIndex(self, newValue: int) -> None:
        """
        修改文件对象在分享列表控件的行号

        Args:
            newValue: 将要修改的行号

        Returns:
            None
        """
        self._row_index = newValue

    @property
    def isDir(self) -> bool:
        """
        文件对象是否为文件夹

        Returns:
            bool: 文件对象是否为文件夹
        """
        return False

    @property
    def isExists(self) -> bool:
        """
        文件对象的路径是否存在

        Returns:
            bool: 文件对象的路径是否存在
        """
        return os.path.exists(self._target_path)

    @property
    def browse_number(self) -> int:
        """
        文件对象被浏览次数

        Returns:
            int: 文件对象被浏览次数
        """
        return self._browse_number

    @browse_number.setter
    def browse_number(self, newValue: int) -> None:
        """
        修改文件对象被浏览次数

        Args:
            newValue: 将要修改的浏览次数

        Returns:
            None
        """
        self._browse_number = newValue

    @property
    def shareType(self) -> ptype.ShareType:
        """
        文件对象分享的类型

        Returns:
            ptype.ShareType: 文件对象分享的类型
        """
        return self._share_type

    @property
    def targetPath(self) -> str:
        """
        文件对象的路径

        Returns:
            str: 文件对象的路径
        """
        return self._target_path

    @property
    def ftp_pwd(self) -> Union[None, str]:
        """
        FTP服务的密码

        Returns:
            Union[None, str]: FTP服务的密码
        """
        return self._ftp_pwd

    @property
    def ftp_port(self) -> Union[None, int]:
        """
        FTP服务的端口

        Returns:
            Union[None, int]: FTP服务的端口
        """
        return self._ftp_port

    @property
    def ftp_basePath(self) -> Union[None, str]:
        """
        FTP服务的根路径

        Returns:
            Union[None, str]: FTP服务的根路径
        """
        return self._ftp_base_path

    @property
    def ftp_cwd(self) -> str:
        """
        文件对象对于FTP服务根目录的相对路径

        Returns:
            str: 文件对象对于FTP服务根目录的相对路径
        """
        result = os.path.dirname(self._target_path.replace(self._ftp_base_path, "", 1))
        if settings.IS_WINDOWS:
            result = result.replace("\\", "/")
        return result

    @property
    def browse_url(self) -> str:
        """
        文件对象浏览的url

        Returns:
            str: 文件对象浏览的url
        """
        return f"http://{settings.LOCAL_HOST}:{settings.WSGI_PORT}{ptype.FILE_LIST_URI}/{self._uuid}"

    @property
    def mobile_browse_url(self) -> str:
        """
        移动设备(浏览器)浏览时文件对象的浏览url

        Returns:
            str: 手机浏览时文件对象的浏览url
        """
        return f"http://{settings.LOCAL_HOST}:{settings.WSGI_PORT}{ptype.MOBILE_PREFIX}{ptype.QRCODE_URL}/{self._uuid}"

    @property
    def download_url(self) -> str:
        """
        文件对象下载的url

        Returns:
            str: 文件对象下载的url
        """
        return f"http://{settings.LOCAL_HOST}:{settings.WSGI_PORT}{ptype.DOWNLOAD_URI}/{self._uuid}"

    @property
    def browse_download_url(self) -> str:
        """
        移动设备(浏览器)浏览时文件对象的下载url

        Returns:
            str: 手机浏览时文件对象的下载url
        """
        return f"http://{settings.LOCAL_HOST}:{settings.WSGI_PORT}{ptype.MOBILE_PREFIX}{ptype.DOWNLOAD_URI}/{self._uuid}"

    @property
    def file_name(self) -> str:
        """
        文件对象的文件名

        Returns:
            str: 文件对象的文件名
        """
        return os.path.basename(self._target_path)

    @property
    def file_size(self) -> int:
        """
        文件对象的文件大小

        Returns:
            int: 文件对象的文件大小
        """
        return os.path.getsize(self._target_path)

    @property
    def secret_key(self) -> str:
        """
        盐值

        Returns:
            str: 盐值
        """
        return self._secret_key or ""

    @property
    def credentials(self) -> str:
        """
        凭据

        Returns:
            str: 凭据
        """
        return self._credentials or ""

    @property
    def free_secret(self) -> bool:
        """
        临时免密属性

        Returns:
            bool: 是否临时免密
        """
        return self._free_secret

    @free_secret.setter
    def free_secret(self, newValue: bool) -> None:
        """
        修改临时免密属性

        Args:
            newValue: 需修改临时免密属性的新值

        Returns:
            None
        """
        self._free_secret = bool(newValue)

    async def to_dict_client(self) -> Dict[str, Union[str, bool]]:
        """
        给客户端的格式化数据

        Returns:
            Dict[str, Union[str, bool]]: 给客户端的格式化数据
        """
        return {
            "uuid": self._uuid,
            "downloadUrl": self.download_url,
            "fileName": self.file_name,
            "stareType": self._share_type.value,
            "isDir": self.isDir,
        }

    async def to_dict_mobile(self) -> Dict[str, Union[str, bool]]:
        """
        移动设备(浏览器)浏览的格式化数据

        Returns:
            Dict[str, Union[str, bool]]: 给移动设备(浏览器)浏览的格式化数据
        """
        return {
            "uuid": self._uuid,
            "downloadUrl": self.browse_download_url,
            "fileName": self.file_name,
            "isDir": self.isDir,
            "targetPath": self.targetPath,
        }

    async def to_ftp_data(self) -> Dict[str, Union[str, int]]:
        """
        FTP各项数据

        Returns:
            Dict[str, Union[str, int]]: FTP的各项数据
        """
        return {
            "uuid": self._uuid,
            "host": settings.LOCAL_HOST,
            "port": self._ftp_port,
            "user": "a",
            "passwd": self._ftp_pwd,
            "cwd": self.ftp_cwd,
            "filename": self.file_name,
        }

    async def to_dict_server(self) -> Dict[str, Union[str, int, bool]]:
        """
        给服务端的格式化数据

        Returns:
            Dict[str, Union[str, int, bool]]: 给服务端的格式化数据
        """
        return {
            "uuid": self._uuid,
            "downloadUrl": self.download_url,
            "fileName": self.file_name,
            "stareType": self._share_type.value,
            "isDir": self.isDir,
            "browseUrl": self.browse_url,
            "targetPath": self._target_path,
            "ftpPwd": self._ftp_pwd,
            "ftpPort": self._ftp_port,
            "ftpBasePath": self._ftp_base_path,
            "browseNumber": self._browse_number,
        }

    def to_dump_backup(self) -> Dict[str, Union[str, bool, int, None]]:
        """
        转存的格式化数据

        Returns:
            Dict[str, Union[str, bool, int, None]]: 转存的格式化数据
        """
        normal = {
            "path": self._target_path,
            "uuid": self._uuid,
            "parent_uuid": None,
            "share_type": self._share_type.value,
            "isDir": self.isDir,
            "secret_key": self.secret_key,
            "credentials": self.credentials,
        }
        if self._share_type is ptype.ShareType.ftp:
            normal.update(
                {
                    "pwd": self._ftp_pwd,
                    "port": self._ftp_port,
                    "ftp_base_path": self._ftp_base_path,
                }
            )

        return normal

    def __eq__(self, other: str) -> bool:
        return other.rstrip(os.sep) == self._target_path


class DirChildrenModel(dict):
    pass


class DirModel(FileModel):
    def __init__(
        self,
        path: str,
        uuid: str,
        parent_uuid: Optional[str] = None,
        pwd: Optional[str] = None,
        port: Optional[int] = None,
        ftp_base_path: Optional[str] = None,
        secret_key: Optional[str] = None,
        credentials: Optional[str] = None,
        **kwargs,
    ):
        """
        文件夹模型类初始化函数

        Args:
            path: 文件夹所在路径
            uuid: 文件夹uuid
            parent_uuid: 父级文件夹的uuid, 若无父级则为None, 默认为None
            pwd: FTP服务的密码, 若不是FTP共享则为None, 默认为None
            port: FTP服务的端口, 若不是FTP共享则为None, 默认为None
            ftp_base_path: FTP服务的根路径, 若不是FTP共享则为None, 默认为None
            secret_key: 文件分享的盐值, 用于密码校验, 默认无校验
            credentials: 文件分享的凭据, 用于密码校验, 默认无校验
            **kwargs: 其他关键字参数
        """
        super(DirModel, self).__init__(
            path,
            uuid,
            parent_uuid,
            pwd,
            port,
            ftp_base_path,
            secret_key,
            credentials,
            **kwargs,
        )

        if self._share_type is ptype.ShareType.ftp:
            self._ftp_base_path = ftp_base_path if ftp_base_path else self._target_path
        else:
            self._ftp_base_path = None

        self._children: Dict[str, Union[FileModel, DirModel]] = DirChildrenModel()
        self._setup_child()

    def _setup_child(self) -> None:
        """
        初始化下级文件/文件夹

        Returns:
            None
        """
        for file_name in os.listdir(self._target_path):
            file_path = os.path.join(self._target_path, file_name)
            child_uuid = public_func.generate_uuid()
            fileModel = DirModel if os.path.isdir(file_path) else FileModel
            child = fileModel(
                file_path,
                child_uuid,
                self._uuid,
                self._ftp_pwd,
                self._ftp_port,
                self._ftp_base_path,
            )

            self._children[child_uuid] = child

    def get(self, item: str) -> Union[FileModel, "DirModel"]:
        """
        获取子级文件/文件夹对象

        Args:
            item: 子级文件/文件夹对象对应的key(uuid)

        Returns:
            Union[FileModel, "DirModel"]: 目标文件/文件夹对象
        """
        return self._children.get(item)

    @property
    def isDir(self) -> bool:
        """
        文件对象是否为文件夹

        Returns:
            bool: 文件对象是否为文件夹
        """
        return True

    @property
    def free_secret(self) -> bool:
        """
        临时免密属性

        Returns:
            bool: 是否临时免密
        """
        return self._free_secret

    @free_secret.setter
    def free_secret(self, newValue: bool) -> None:
        """
        修改临时免密属性

        Args:
            newValue: 需修改临时免密属性的新值

        Returns:
            None
        """
        self._free_secret = bool(newValue)
        for child in self._children.values():
            child.free_secret = newValue

    async def to_dict_client(self) -> Dict[str, Any]:
        """
        给客户端的格式化数据

        Returns:
            Dict[str, Any]: 给客户端的格式化数据
        """
        children = []
        for child_uuid, child in self._children.items():
            child_dict = {child_uuid: await child.to_dict_client()}
            children.append(child_dict)

        return {
            "uuid": self._uuid,
            "downloadUrl": self.download_url,
            "fileName": self.file_name,
            "stareType": self._share_type.value,
            "isDir": self.isDir,
            "children": children,
        }

    async def to_dict_mobile(self) -> Dict[str, Any]:
        """
        移动设备(浏览器)浏览的格式化数据

        Returns:
            Dict[str, Any]: 给移动设备(浏览器)浏览的格式化数据
        """
        children = []
        for child_uuid, child in self._children.items():
            children.append(await child.to_dict_mobile())

        return {
            "uuid": self._uuid,
            "downloadUrl": self.browse_download_url,
            "fileName": self.file_name,
            "isDir": self.isDir,
            "targetPath": self.targetPath,
            "children": children,
        }

    async def to_dict_server(self) -> Dict[str, Any]:
        """
        给服务端的格式化数据

        Returns:
            Dict[str, Any]: 给服务端的格式化数据
        """
        children = []
        for child_uuid, child in self._children.items():
            child_dict = {child_uuid: await child.to_dict_server()}
            children.append(child_dict)

        return {
            "uuid": self._uuid,
            "downloadUrl": self.download_url,
            "fileName": self.file_name,
            "stareType": self._share_type.value,
            "isDir": self.isDir,
            "browseUrl": self.browse_url,
            "targetPath": self._target_path,
            "ftpPwd": self._ftp_pwd,
            "ftpPort": self._ftp_port,
            "ftpBasePath": self._ftp_base_path,
            "children": children,
        }
