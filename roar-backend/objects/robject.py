from abc import ABC,abstractmethod
from datetime import datetime
from typing import List, Any
import Pyro5.server
from pyEventHook import Event


class RObject(ABC):
    @abstractmethod
    def __init__(self,id:str,type:str) -> None:
        self._id=id
        self._type=type
        self._likes={}
        self._change: Event = Event()

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

    @Pyro5.server.expose
    @property
    def change(self):
        return self._change

    @Pyro5.server.expose
    @change.setter
    def change(self,value):
        self._change=value