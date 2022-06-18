from datetime import datetime
from typing import Dict, List
from .objects.robject import RObject
from abc import ABC,abstractmethod

class Activity(RObject,ABC):
    @abstractmethod
    def execute(self):
        ...

class CreateActivity(Activity):
    def __init__(self, id: str, actor: str, obj: str, published: datetime, to: List[str], replay: str) -> None:
        super().__init__(id, 'CreateActivity')
        self.actor = actor
        self.obj = obj
        self.published = published
        self.to  = to
        self.replay=replay
        self.replies=[]

class DeleteActivity(Activity):
    def __init__(self, id: str, obj : str) -> None:
        super().__init__(id, 'DeleteActivity')
        self.obj=obj

class FollowActivity(Activity):
    def __init__(self, id: str, actor:str) -> None:
        super().__init__(id, 'FollowActivity')
        self.actor=actor

class UnfollowActivity(Activity):
    def __init__(self, id: str, actor:str) -> None:
        super().__init__(id, 'UnfollowActivity')
        self.actor=actor


class LikeActivity(Activity):
    def __init__(self, id: str, actor:str, obj: str) -> None:
        super().__init__(id, 'LikeActivity')
        self.obj=obj
        self.actor=actor

class ShareActivity(Activity):
    def __init__(self, id: str, obj: str, obj_share: str) -> None:
        super().__init__(id, 'ShareActivity')
        self.obj = obj        
        self.obj_share = obj_share