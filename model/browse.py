__all__ = [
    "BrowseFileDictModel"
]

from typing import Union

class BrowseFileDictModel(dict):
    
    def __init__(self):
        super(BrowseFileDictModel, self).__init__()
        self._current_dict = self

    def prev(self) -> None:

        self._current_dict = self._current_dict["prev"]

    @property
    def currentDict(self) -> dict[str: Union[str, list, dict]]:

        return self._current_dict

    @currentDict.setter
    def currentDict(self, newVaule: dict):

        self._current_list = newVaule

    @property
    def isRoot(self) -> bool:

        return self._current_dict == self

    @classmethod
    def load(cls, data: dict) -> "BrowseFileDictModel":
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
        for child in data["children"]:
            child = [x for x in child.values()][0]
            if child["isDir"]:
                child["prev"] = data
                cls._load_dict_recursive(child)

        return data
