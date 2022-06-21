from .objects.robject import RObject
from .actor import Actor
from datetime import datetime

class Post(RObject):
    def __init__(self, id:str, author:str, content:str, replay:str, published: datetime):
        super().__init__(id,"Post")
        self._author=author
        self._content=content
        self._published=published
        self._replay = replay
        self._likes={}
        cat_label=-1

    @property
    def author(self):
        return self._author

    @property
    def content(self):
        return self._content

    @property
    def replay(self):
        return self._replay

    @property
    def published(self):
        return self._published
    
    def like(self,alias:str):
        self.l_ikes[alias]=alias    