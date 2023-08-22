__all__ = [
    "SharingModel"
]

from _file import FileModel
from typing import List

class SharingModel(dict):

    def __getitem__(self, item: str) -> List[FileModel] or None:

        return self.get(item, None)

    def __setitem__(self, key: str, value: List[FileModel]) -> None:

        super(SharingModel, self).__setitem__(key, value)

    def __delitem__(self, key: str) -> None:

        super(SharingModel, self).__delitem__(key)

    @property
    def length(self) -> int:

        return len(self)

    @property
    def isEmpty(self) -> bool:

        return not self
