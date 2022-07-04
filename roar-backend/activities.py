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
        self._actor = actor
        self._obj = obj
        self._published = published
        self._to  = to
        self._replay=replay
        self._replies=[]

    @property
    def actor(self):
        return self._actor
    @property
    def obj(self):
        return self._obj
    @property
    def published(self):
        return self._published
    @property
    def to(self):
        return self._to
    @property
    def replay(self):
        return self._replay
    @property
    def replies(self):
        return self._replies


@Pyro5.server.expose
class DeleteActivity(Activity):
    def __init__(self, id: str, obj : str) -> None:
        super().__init__(id, 'DeleteActivity')
        self._obj=obj
    @property
    def obj(self):
        return self._obj

@Pyro5.server.expose
class FollowActivity(Activity):
    def __init__(self, id: str, actor:str) -> None:
        super().__init__(id, 'FollowActivity')
        self._actor=actor
    
    @property
    def actor(self):
        return self._actor

@Pyro5.server.expose
class UnfollowActivity(Activity):
    def __init__(self, id: str, actor:str) -> None:
        super().__init__(id, 'UnfollowActivity')
        self._actor=actor

    @property
    def actor(self):
        return self._actor

@Pyro5.server.expose
class LikeActivity(Activity):
    def __init__(self, id: str, actor:str, obj: str) -> None:
        super().__init__(id, 'LikeActivity')
        self._obj=obj
        self._actor=actor

    @property
    def actor(self):
        return self._actor

    @property
    def obj(self):
        return self._obj

class UnlikeActivity(Activity):
    def __init__(self, id: str, actor:str, obj: str) -> None:
        super().__init__(id, 'UnlikeActivity')
        self._obj=obj
        self._actor=actor

    @property
    def actor(self):
        return self._actor

    @property
    def obj(self):
        return self._obj

@Pyro5.server.expose
class ShareActivity(Activity):
    def __init__(self, id: str, obj_share: str) -> None:
        super().__init__(id, 'ShareActivity')
        self._obj_share = obj_share

    @property
    def obj(self):
        return self._obj_share