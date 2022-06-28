from .objects.robject import RObject
from .actor import Actor
from datetime import datetime

class Post(RObject):
    def __init__(self, id:str, author:str, content:str, reply:str, published: datetime):
        super().__init__(id,"Post")
        self._author=author
        self._content=content
        self._published=published
        self._reply = reply
        self._likes={}
        self._shared=[]
        self._replies=[]
        self._info={}
        self._info["likes"]=0
        self._info["shares"]=0
        self._info["reply"]=0
        cat_label=-1

    @property
    def author(self):
        return self._author

    @property
    def content(self):
        return self._content

    @property
    def reply(self):
        return self._reply

    @property
    def published(self):
        return self._published
    
    @property
    def info(self):
        return self._info}
    
    def like(self,alias:str):
        self._likes[alias]=alias    
        self.likes+=1
        
    def unlike(self,alias:str):
        self._likes.remove(alias)
        self.likes-=1
        
    