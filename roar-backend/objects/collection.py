from .robject import RObject
from abc import ABC,abstractmethod

class Collection(RObject,ABC):

    @property
    def items(self):
        ...

    @abstractmethod
    def add(self):
        ...