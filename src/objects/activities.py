from datetime import datetime
from typing import Dict, List
from collection import Collection
from RObjects import RObject,ActivityObject
from abc import ABC,abstractmethod
from actor import Actor

class Activity(RObject,ABC):
    @abstractmethod
    def execute(self):
        ...

class CreateActiity(Activity):
    def __init__(self, id: str, actor: Actor, obj: ActivityObject, published: datetime, to: List[str]) -> None:
        super().__init__(id, 'CreateActivity')
        self.actor = actor
        self.obj = obj
        self.published = published
        self.to  = to

class UpdateActiity(Activity):
    def __init__(self, id: str, obj : ActivityObject, updates : Dict) -> None:
        super().__init__(id, 'UpdateActivity')
        self.obj=obj
        self.updates=updates

class DeleteActivity(Activity):
    def __init__(self, id: str, obj : ActivityObject) -> None:
        super().__init__(id, 'DeleteActivity')
        self.obj=obj

class FollowActivity(Activity):
    def __init__(self, id: str, actor:Actor) -> None:
        super().__init__(id, 'FollowActivity')
        self.actor=actor

class AddActivity(Activity):
    def __init__(self, id: str, obj: RObject, target : Collection) -> None:
        super().__init__(id, 'AddActivity')
        self.obj=obj
        self.target=target

class Remove(Activity):
    def __init__(self, id: str, obj: RObject, target : Collection) -> None:
        super().__init__(id, 'RemoveActivity')
        self.obj=obj
        self.target=target

class LikeActivity(Activity):
    def __init__(self, id: str, obj: RObject) -> None:
        super().__init__(id, 'LikeActivity')
        self.obj=obj

class BlockActivity(Activity):
    def __init__(self, id: str, actor: Actor) -> None:
        super().__init__(id, 'BlockActivity')
        self.actor = actor

class UndoActivity(Activity):
    def __init__(self, id: str, activity: Activity) -> None:
        super().__init__(id, 'UndoActivity')
        self.activity=activity

class ShareActivity(Activity):
    def __init__(self, id: str, obj: ActivityObject) -> None:
        super().__init__(id, 'ShareActiity')
        self.obj = obj        