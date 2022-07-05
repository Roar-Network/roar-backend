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
        self._likes_soa=0
        self._shared_soa=0
        self._replies_soa=0
        self._cat_label=-1

    @property
    def cat_label(self):
        return self._cat_label

    @cat_label.setter
    def cat_label(self, value):
        self._cat_label=value
        
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

    @property
    def likes_soa(self):
        return self._likes_soa

    @likes_soa.setter
    def likes_soa(self,value):
        self._likes_soa=value
    
    @property
    def shared_soa(self):
        return self._shared_soa

    @shared_soa.setter
    def shared_soa(self,value):
        self._shared_soa=value
    
    @property
    def replies_soa(self):
        return self._replies_soa
    
    @replies_soa.setter
    def replies_soa(self,value):
        self._replies_soa=value

    @property
    def likes(self):
        return self._likes
    
    @property
    def shared(self):
        return self._shared
    
    @property
    def replies(self):
        return self._replies
    
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