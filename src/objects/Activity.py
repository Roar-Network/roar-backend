from typing import List
from objects import RObject
from abc import ABC,abstractmethod
from actor import Actor

class Activity(RObject,ABC):
    @abstractmethod
    def __init__(self, id: str, type: str, actor : Actor, obj : RObject, to : List [str]) -> None:
        super().__init__(id, type)
        self.actor : Actor = actor
        self.obj : RObject = obj
        self.to : List = to