from objects import RObject
from abc import ABC,abstractmethod

class Collection(RObject,ABC):
    @abstractmethod
    def __init__(self, id: str, type: str) -> None:
        super().__init__(id, type)
        self.first
        self.last
        self.total_items:int

    @property
    def items(self):
        ...

    @abstractmethod
    def add(self):
        ...

    @abstractmethod
    def remove(self):
        ...