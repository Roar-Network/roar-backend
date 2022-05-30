from objects import RObject
from listCollection import ListCollection
from typing import List
from chordRing import ChordRing

class Actor(RObject):
    def __init__(self, alias: str, user_name : str) -> None:
        super().__init__(alias, 'Actor')
        self._inbox : ListCollection = ListCollection(self.id + "/" + "inbox",[])
        self._outbox : ListCollection = ListCollection(self.id + "/" + "outbox",[])
        self._outbox_set : ChordRing = ChordRing(self.id + "/" + "outbox_set",[])
        self._following : ChordRing = ChordRing(self.id + "/" + "following",[])
        self._followers : ChordRing = ChordRing(self.id + "/" + "followers",[])
        self._liked : ChordRing = ChordRing(self.id + "/" + "followers",[])
        self._user_name : str = user_name

    @property
    def inbox(self):
        return self._inbox

    @property
    def outbox(self):
        return self._outbox

    @property
    def following(self):
        return self._following

    @property
    def followers(self):
        return self._followers
    
    @property
    def liked(self):
        return self._liked

    @property
    def user_name(self):
        return self._user_name