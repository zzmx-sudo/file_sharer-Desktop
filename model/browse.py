__all__ = ["BrowseFileDictModel"]

from typing import Dict, Any


class BrowseFileDictModel(dict):
    def __init__(self):
        """
        浏览目录文件集类初始化函数
        """
        super(BrowseFileDictModel, self).__init__()
        self._current_dict = self

    def prev(self) -> None:
        """
        上一级目录文件集

        Returns:
            None
        """
        self._current_dict = self._current_dict["prev"]

    def reload(self) -> None:
        """
        重制为主目录文件集

        Returns:
            None
        """
        self._current_dict = self

    @property
    def currentDict(self) -> Dict[str, Any]:
        """
        当前目录文件集

        Returns:
            Dict[str, Any]: 当前目录文件
        """
        return self._current_dict

    @currentDict.setter
    def currentDict(self, newVaule: Dict[str, Any]) -> None:
        """
        修改当前目录文件集

        Args:
            newVaule: 将要修改的目录文件集

        Returns:
            None
        """
        self._current_dict = newVaule

    @property
    def isRoot(self) -> bool:
        """
        当前是否为主目录文件集

        Returns:
            bool: 当前是否为主目录文件集
        """
        return self._current_dict == self

    @property
    def isDir(self) -> bool:
        """
        主目录是否为文件夹

        Returns:
            bool: 主目录是否为文件夹
        """
        return bool(self["isDir"])

    @classmethod
    def load(cls, data: Dict[str, Any]) -> "BrowseFileDictModel":
        """
        加载数据为目录集

        Args:
            data: 待加载的数据

        Returns:
            BrowseFileDictModel: 浏览目录文件集对象
        """
        model = cls()
        if not data:
            return model

        if data["isDir"]:
            data = cls._load_dict_recursive(data)

        for key, value in data.items():
            model[key] = value

        return model

    @classmethod
    def _load_dict_recursive(cls, data: dict) -> dict:
        children = data["children"]
        data["children"] = []
        for child in children:
            child = [x for x in child.values()][0]
            data["children"].append(child)
            if child["isDir"]:
                child["prev"] = data
                cls._load_dict_recursive(child)

        return data
