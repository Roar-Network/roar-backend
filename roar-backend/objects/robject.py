from abc import ABC,abstractmethod
from datetime import datetime
from typing import List
import Pyro5.server

class RObject(ABC):
    @abstractmethod
    def __init__(self,id:str,type:str) -> None:
        self._id=id
        self._type=type
        self._likes={}

    @Pyro5.server.expose
    @property
    def id(self):
        return self._id

    @Pyro5.server.expose
    @property
    def type(self):
        return self._type

    @property
    def likes(self):
        return self.likes
