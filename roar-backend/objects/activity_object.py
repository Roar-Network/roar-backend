from .robject import RObject
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List


class ActivityObject(RObject,ABC):
    @abstractmethod
    def __init__(self, id: str, type: str, attributedTo , published : datetime, to : List[str]) -> None:
        super().__init__(id, type)
        self.attributedTo = attributedTo
        self.published = published
        self.to = to