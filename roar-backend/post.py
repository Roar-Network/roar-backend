from .objects.robject import RObject
from .actor import Actor
from datetime import datetime
import Pyro5.server


@Pyro5.server.expose
class Post(RObject):
    def __init__(self, id:str, author:str, content:str, reply:str, published: datetime):
        super().__init__(id,"Post")
        self._author=author
        self._content=content
        self._published=published
        self._reply = reply
        self._likes=set()
        self._shared=set()
        self._replies=set()
        self._info={}
        self._info["likes"]=0
        self._info["shares"]=0
        self._info["reply"]=0
        _likes_soa=0
        _shared_soa=0
        _replies_soa=0
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
        return self._info
    
    def like(self, alias: str, notify_change: bool = True):
        self._likes.add(alias)
        if notify_change:
            self.change(self.id, "like", (alias, False)) 
    
        
    def unlike(self, alias: str, notify_change: bool = True):
        try: 
            self._likes.remove(alias)
            if notify_change:
                self.change(self.id, "unlike", (alias, False))
        except: 
            pass
        
    def add_shared(self, id_obj, notify_change: bool = True):
        self._shared.add(id_obj)
        if notify_change:
            self.change(self.id, "add_shared", (id_obj, False))

    def add_reply(self, id_obj, notify_change: bool = True):
        self._replies.add(id_obj)
        if notify_change:
            self.change(self.id, "add_reply", (id_obj, False))

    def remove_reply(self, id_obj, notify_change: bool = True):
        self._replies.remove(id_obj)
        if notify_change:
            self.change(self.id, "remove_reply", (id_obj, False))

    @property
    def likes_soa(self):
        return self._likes_soa
    
    @property
    def shared_soa(self):
        return self._shared_soa
    
    @property
    def replies_soa(self):
        return self._replies_soa
    
    @property
    def likes(self):
        return self._likes
    
    @property
    def shared(self):
        return self._shared
    
    @property
    def replies(self):
        return self._replies
    
