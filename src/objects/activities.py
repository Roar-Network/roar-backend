from datetime import datetime
from typing import Dict, List
from RObjects import RObject
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

# class UpdateActivity(Activity):
#     def __init__(self, id: str, obj : str, updates : Dict) -> None:
#         super().__init__(id, 'UpdateActivity')
#         self.obj=obj
#         self.updates=updates

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

# class AddActivity(Activity):
#     def __init__(self, id: str, obj: RObject, target : Collection) -> None:
#         super().__init__(id, 'AddActivity')
#         self.obj=obj
#         self.target=target

# class Remove(Activity):
#     def __init__(self, id: str, obj: RObject, target : Collection) -> None:
#         super().__init__(id, 'RemoveActivity')
#         self.obj=obj
#         self.target=target

class LikeActivity(Activity):
    def __init__(self, id: str, actor:str, obj: str) -> None:
        super().__init__(id, 'LikeActivity')
        self.obj=obj
        self.actor=actor

# class BlockActivity(Activity):
#     def __init__(self, id: str, actor: Actor) -> None:
#         super().__init__(id, 'BlockActivity')
#         self.actor = actor

# class UndoActivity(Activity):
#     def __init__(self, id: str, activity: Activity) -> None:
#         super().__init__(id, 'UndoActivity')
#         self.activity=activity

class ShareActivity(Activity):
    def __init__(self, id: str, obj: str, obj_share: str) -> None:
        super().__init__(id, 'ShareActivity')
        self.obj = obj        
        self.obj_share = obj_share