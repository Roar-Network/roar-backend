from .objects.robject import RObject
from typing import List
import Pyro5.client
import Pyro5.server
import socket as sck

@Pyro5.server.expose
class Actor(RObject):
    def __init__(self, alias: str, user_name : str, hashed_password, a1:str, a2:str) -> None:
        super().__init__(alias, 'Actor')
        self._inbox : str = f'{alias}/inbox'
        self._outbox : str = f'{alias}/outbox'
        self._following  = set()
        self._followers = set()
        self._liked : str = f'{alias}/liked'
        self._user_name : str = user_name
        self._hashed_password : str = hashed_password
        self._most_liked=[None]*10
        self._following_soa=0
        self._followers_soa=0
        self._likes_soa=0
        self._posts_soa=0
        self._shared_soa=0
        self.a1=a1
        self.a2=a2
        self.preferences=[]

        if alias == 'me':
            return

        IP: str = sck.gethostbyname(sck.gethostname())

        direction_list = []

        try:
            with Pyro5.client.Proxy('PYRO:admin@'+IP+':8002') as admin:
                direction_list=[item + ':8002' for item in admin.system_network]
        except Exception as e:
            print("Error actor admin" + str(e))

        try:
            with Pyro5.client.Proxy('PYRO:inboxes@'+IP+':8002') as node:
                node.add('ListCollection',(f'{alias}/inbox',direction_list))
        except Exception as e:
            print('Error creando inbox' + str(e))

        try:
            with Pyro5.client.Proxy('PYRO:outboxes@'+IP+':8002') as node:
                node.add('ListCollection',(f'{alias}/outbox',direction_list))
        except Exception as e:
            print('Error creando outbox' + str(e))

    @property
    def following_soa(self):
        return self._following_soa

    @following_soa.setter
    def following_soa(self, value: int):
        self._following_soa = value

    @property
    def followers_soa(self):
        return self._followers_soa

    @followers_soa.setter
    def followers_soa(self, value: int):
        self._followers_soa = value

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
    def alias(self):
        return self.id
    
    @property
    def forgot_password(self,value,a1,a2):
        if self.a1==a1 and self.a2==a2:
            self._hashed_password=value
            return True
        
        else:
            return False
            

    def add_followers(self, id_obj: str, notify_change: bool = True) -> None:
        self.followers.add(id_obj)
        if notify_change:
            self.change(self.alias, "add_followers", (id_obj, False))

    def remove_followers(self, id_obj: str, notify_change: bool = True) -> None:
        self.followers.remove(id_obj)
        if notify_change:
            self.change(self.alias, "remove_followers", (id_obj, False))

    def add_followings(self, id_obj: str, notify_change: bool = True) -> None:
        self.following.add(id_obj)
        if notify_change:
            self.change(self.alias, "add_followings", (id_obj, False))

    def remove_followings(self, id_obj: str, notify_change: bool = True) -> None:
        self.following.remove(id_obj)
        if notify_change:
            self.change(self.alias, "remove_followings", (id_obj, False))
        
    @property
    def likes_soa(self):
        return self._likes_soa
    
    @likes_soa.setter
    def likes_soa(self, value):
        self._likes_soa = value

    @property
    def shared_soa(self):
        return self._shared_soa
    
    @shared_soa.setter
    def shared_soa(self, value):
        self._shared_soa = value
        

    @property
    def posts_soa(self):
        return self._posts_soa

    @posts_soa.setter
    def posts_soa(self, value):
        self._posts_soa = value

