from abc import ABC,abstractmethod

from chordRing import ChordRing

class RObject(ABC):
    @abstractmethod
    def __init__(self,id:str,type:str) -> None:
        self._id=id
        self._type=type
        self._likes=ChordRing(self.id+"/"+"likes",[])

    @property
    def id(self):
        return self._id

    @property
    def type(self):
        return self._type