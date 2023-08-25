__all__ = [
    "SharingModel"
]

from typing import Union

from .file import FileModel, DirModel

class SharingModel(dict):

    def __setitem__(self, key: str, value: Union[FileModel, DirModel]) -> None:

        super(SharingModel, self).__setitem__(key, value)

    def __delitem__(self, key: str) -> None:

        super(SharingModel, self).__delitem__(key)

    @property
    def length(self) -> int:

        return len(self)

    @property
    def isEmpty(self) -> bool:

        return not self