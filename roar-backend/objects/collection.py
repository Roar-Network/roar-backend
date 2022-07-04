from .robject import RObject
from abc import ABC,abstractmethod

class Collection(RObject,ABC):

    @abstractmethod
    def add(self):
        ...

    @abstractmethod
    def remove(self):
        ...