from datetime import datetime
from typing import Dict, List
from .objects.robject import RObject
from abc import ABC,abstractmethod
import Pyro5.server

class Activity(RObject):
    ...

@Pyro5.server.expose
class CreateActivity(Activity):
    def __init__(self, id: str, actor: str, obj: str, published: datetime, to: List[str], replay: str) -> None:
        super().__init__(id, 'CreateActivity')
        self.actor = actor
        self.obj = obj
        self.published = published
        self.to  = to
        self.replay=replay
        self.replies=[]

@Pyro5.server.expose
class DeleteActivity(Activity):
    def __init__(self, id: str, obj : str) -> None:
        super().__init__(id, 'DeleteActivity')
        self.obj=obj

@Pyro5.server.expose
class FollowActivity(Activity):
    def __init__(self, id: str, actor:str) -> None:
        super().__init__(id, 'FollowActivity')
        self.actor=actor

@Pyro5.server.expose
class UnfollowActivity(Activity):
    def __init__(self, id: str, actor:str) -> None:
        super().__init__(id, 'UnfollowActivity')
        self.actor=actor

@Pyro5.server.expose
class LikeActivity(Activity):
    def __init__(self, id: str, actor:str, obj: str) -> None:
        super().__init__(id, 'LikeActivity')
        self.obj=obj
        self.actor=actor

class UnlikeActivity(Activity):
     def __init__(self, id: str, actor:str, obj: str) -> None:
        super().__init__(id, 'UnlikeActivity')
        self.obj=obj
        self.actor=actor

@Pyro5.server.expose
class ShareActivity(Activity):
    def __init__(self, id: str, obj_share: str) -> None:
        super().__init__(id, 'ShareActivity')
        self.obj_share = obj_share