from .objects.robject import RObject
from typing import List
import Pyro5.client
import Pyro5.server
import json
from .dl.list_collection import ListCollection

@Pyro5.server.expose
class Actor(RObject):
    def __init__(self, alias: str, user_name : str, hashed_password, a1:str, a2:str) -> None:
        super().__init__(alias, 'Actor')
        self._inbox : str = f'{alias}/inbox'
        self._outbox : str = f'{alias}/outbox'
        self._following  = {}
        self._followers = {}
        self._liked : str = f'{alias}/liked'
        self._user_name : str = user_name
        self._hashed_password : str = hashed_password
        self._most_liked=[None]*10
        self.following_soa=0
        self.followers_soa=0
        self.likes_soa=0
        self.posts_soa=0
        self.a1=a1
        self.a2=a2

        with json.load('servers.json') as servers:
            connect_server = servers[0]
            try:
                with Pyro5.client.Proxy('PYRO:inboxes@'+connect_server+':8002') as node:
                    node.add(ListCollection(f'{alias}/inbox',servers))
            except:
                print('Error creando inbox')

            try:
                with Pyro5.client.Proxy('PYRO:outboxes@'+connect_server+':8002') as node:
                    node.add(ListCollection(f'{alias}/outbox',servers))
            except:
                print('Error creando outbox')

            try:
                with Pyro5.client.Proxy('PYRO:likeds@'+connect_server+':8002') as node:
                    node.add(ListCollection(f'{alias}/liked',servers))
            except:
                print('Error creando liked')

        
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

    @property
    def hashed_password(self):
        return self._hashed_password

    @hashed_password.setter
    def hashed_password(self,value):
        self._hashed_password = value

    @property
    def most_liked(self):
        return self._most_liked
    
    @property
    def forgot_password(self,value,a1,a2):
        if self.a1==a1 and self.a2==a2:
            self._hashed_password=value
            return True
        
        else:
            return False
            