__all__ = [
    "BrowseFileDictModel"
]

from typing import TypeVar, Union

BrowseFileDictType = TypeVar("BrowseFileDictType", bound="BrowseFileDictModel")

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

    @classmethod
    def load(cls, data: dict) -> BrowseFileDictType:
        model = cls()

        return model