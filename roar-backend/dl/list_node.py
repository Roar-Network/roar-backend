from copy import deepcopy
import Pyro5.server
import Pyro5.client
from collections import deque
from ..objects.robject import RObject
from threading import Thread
import schedule

from ..activities import *
from ..post import Post

DICT_STR_TYPE={
    'CreateActivity':CreateActivity,
    'FollowActivity' : FollowActivity,
    'LikeActivity' : LikeActivity,
    'ShareActivity': ShareActivity,
    'DeleteActivity': DeleteActivity,
    'UnfollowActivity': UnfollowActivity,
    'Post' : Post
}

@Pyro5.server.expose
class ListNode(RObject):
    def __init__(self,id:str) -> None:
        super().__init__(id,'ListNode')
        self._successor : str = id
        self._predecessor : str = id
        self._objects = deque()
        self._objects_ids = set()
        self._predecessor_objects = deque()
        self._sucsuccessor : str = id
        self._partOf : str = None
        self._top = 0
        self._stabilize_worker: Thread() = Thread(target=self.stabilize_worker)


    def stabilize_worker(self):
        schedule.every(0.05).seconds.do(self.check_successor)
        while True:
            schedule.run_pending()


    def __repr__(self) -> str:
        return 'ListNode ' + str(self.id)

    @property
    def objects(self):
        return self._objects

    @property
    def objects_ids(self):
        return self._objects_ids

    @property
    def predecessor_objects(self):
        return self._predecessor_objects

    @property
    def successor(self):             
        return self._successor

    @successor.setter
    def successor(self, value):    
        self._successor = value

    @property
    def predecessor(self):             
        return self._predecessor

    @predecessor.setter
    def predecessor(self, value):    
        self._predecessor = value

    @property
    def sucsuccessor(self):             
        return self._sucsuccessor

    @sucsuccessor.setter
    def sucsuccessor(self, value):    
        self._sucsuccessor = value

    @property
    def partOf(self):             
        return self._partOf

    @partOf.setter
    def partOf(self, value):    
        self._partOf = value

    @property
    def top(self):             
        return self._top

    @top.setter
    def top(self, value):    
        self._top = value
 
    def join(self,other:str) -> None:
        self.objects.clear()
        self.predecessor_objects.clear()

        list_type=other.split('/')[1]
        server=self.id.split('@')[1]
        actual_list = None

        if list_type == 'inbox':
            try :
                with Pyro5.client.Proxy('PYRO:'+'inboxes@'+server) as nd:
                    actual_list=nd.search(other)
            except:
                print('Error join inbox')

        elif list_type == 'outbox':
            try :
                with Pyro5.client.Proxy('PYRO:'+'outboxes@'+server) as nd:
                    actual_list=nd.search(other)
            except:
                print('Error join outbox')
        
        else:
            try :
                with Pyro5.client.Proxy('PYRO:'+'likeds@'+server) as nd:
                    actual_list=nd.search(other)
            except:
                print('Error join liked')

        self.successor=actual_list.first
        self.predecessor=actual_list.last
        self.partof=other
        actual_list.last = self.id
        try :
            with Pyro5.client.Proxy('PYRO:'+self.successor) as nd:
                self.top = nd.top
                self.sucsuccessor = nd.succesor
        except:
            print('Error join succesor')
   
    def check_successor(self):
        try:
            with Pyro5.client.Proxy('PYRO:' + self.successor) as successor:
                self.sucsuccessor=successor.successor
        except:

            list_type=self.partOf.split('/')[1]
            server=self.id.split('@')[1]
            actual_list = None

            if list_type == 'inbox':
                try :
                    with Pyro5.client.Proxy('PYRO:'+'inboxes@'+server) as nd:
                        actual_list=nd.search(self.partOf)
                except:
                    print('Error check_successor inbox')

            elif list_type == 'outbox':
                try :
                    with Pyro5.client.Proxy('PYRO:'+'outboxes@'+server) as nd:
                        actual_list=nd.search(self.partOf)
                except:
                    print('Error check_successor outbox')
            
            elif list_type == 'liked':
                try :
                    with Pyro5.client.Proxy('PYRO:'+'likeds@'+server) as nd:
                        actual_list=nd.search(self.partOf)
                except:
                    print('Error check_successor liked')
            
            try:
                if self.successor == actual_list.first:
                    actual_list.first=self.sucsuccessor
                with Pyro5.client.Proxy('PYRO:'+actual_list.last) as last:
                    if len(last.objects) == 0:
                        self.successor = last.id
                        last.successor=self.sucsuccessor
                        actual_list.last=last.predecessor
                        last.predecessor=self.id
                        last.predecessor_objects=deepcopy(self.objects)
                        try:
                            with Pyro5.client.Proxy('PYRO:'+last.successor) as successor:
                                last.objects = deepcopy(successor.predecessor_objects)
                                successor.predecessor=last.id
                                last.sucsuccessor=successor.successor
                        except:
                            print('Error check_succesor sucsuccesor')
                    else:
                        actual_list.allocate()
            except:
                print('Error check_succesor last')
            
    def add(self, type_class, args):

        type_instance=DICT_STR_TYPE[type_class]
        item=type_instance(*args)
        self.objects.appendleft(item)
        self.objects_ids.add(item.id)
        try:
            self._pyroDaemon.register(item)
        except Exception as e:
            print(str(e))

        try:
            with Pyro5.client.Proxy('PYRO:'+self.successor) as successor:
                successor.add_predecessor_objects(type_class,args)
        except:
            print('Error add successor')
            self.check_successor()

    def add_predecessor_objects(self,type_class,args):
        type_instance=DICT_STR_TYPE[type_class]
        item=type_instance(*args)
        self.predecessor_objects.appendleft(item)
