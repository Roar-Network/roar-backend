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
        self.info={}
        self.info["likes"]=0
        self.info["shares"]=0
        self.info["reply"]=0
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
    
    def like(self,alias:str):
        self.l_ikes[alias]=alias    
        self.likes+=1
        
    def unlike(self,alias:str):
        self.l.remove(alias)
        self.likes-=1
        
    