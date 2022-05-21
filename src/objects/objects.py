from abc import ABC,abstractmethod

class RObject(ABC):
    @abstractmethod
    def __init__(self,id:str,type:str) -> None:
        self._id=id
        self._type=type

    @property
    def id(self):
        return self._id

    @property
    def type(self):
        return self._type