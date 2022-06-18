import Pyro5.server
import Pyro5.client
from collections import deque
from typing import List, Deque, Tuple
from ..objects.robject import RObject
from threading import Thread
import schedule
import time


@Pyro5.server.expose
class ListNode(RObject):
    def __init__(self,id:str) -> None:
        super().__init__(id,'ListNode')
        self._successor : str = None
        self._predecessor : str = None
        self._objects = deque()
        self._predecessor_objects = deque()
        self._sucsuccessor : str = None
        self._partOf : str = None
        self._top = 0
        self._stabilize_worker: Thread() = Thread(target=self.stabilize_worker)


    def stabilize_worker(self):
        def sw():
            self.check_successor()
            self.check_predecessor()
        schedule.every(1).minutes.do(sw)
        while True:
            schedule.run_pending()
            time.sleep(1)


    def __repr__(self) -> str:
        return 'ListNode ' + str(self.id)

    @property
    def objects(self):
        return self._objects

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
        self.predecessor = None
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
            Pyro5.client.Proxy(self.successor)._pyroRelease()
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
                        last.predecessor_objects=self.objects.copy()
                        try:
                            with Pyro5.client.Proxy('PYRO:'+last.successor) as successor:
                                last.objects = successor.predecessor_objects.copy()
                                successor.predecessor=last.id
                                last.sucsuccessor=successor.successor
                        except:
                            print('Error check_succesor sucsuccesor')
                    else:
                        actual_list.allocate()
            except:
                print('Error check_succesor last')
            
            try:
                with Pyro5.client.Proxy('PYRO:'+self.predecessor) as predecessor:
                    predecessor.sucsuccessor=self.successor
            except:
                print('Error check_succesor predecessor')

    def add(self, item:RObject):
        self.objects.appendleft(item)
        try:
            with Pyro5.client.Proxy('PYRO:'+self.successor) as successor:
                successor.predecessor_objects.appendleft(item)
        except:
            print('Error add successor')
