import Pyro5.server
import Pyro5.client
import Pyro5.api
from collections import deque
from ..objects.robject import RObject
from threading import Thread
import schedule
from datetime import datetime

from ..activities import *
from ..post import Post

DICT_STR_TYPE={
    'CreateActivity':CreateActivity,
    'FollowActivity' : FollowActivity,
    'LikeActivity' : LikeActivity,
    'ShareActivity': ShareActivity,
    'DeleteActivity': DeleteActivity,
    'UnfollowActivity': UnfollowActivity,
    'UnlikeActivity': UnlikeActivity
}

DICT_STR_INS={
    'CreateActivity':CreateActivity("as","dasd","asds",datetime.now(),["sd"],"ert"),
    'FollowActivity' : FollowActivity("sjd","fdo"),
    'LikeActivity' : LikeActivity("eww","dqs","erui"),
    'ShareActivity': ShareActivity("hoh","bgjg"),
    'DeleteActivity': DeleteActivity("er","io"),
    'UnfollowActivity': UnfollowActivity("ds","dfsd"),
    'UnlikeActivity': UnlikeActivity("das","ds","sdfd")
}

SERIALIZER=Pyro5.api.SerializerBase()

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
        self._stabilize_worker.start()


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

    def get_dict(self,thing):
        class_dict=SERIALIZER.class_to_dict(thing)
        things_to_delete=['_change','__class__','_pyroId','_pyroDaemon']
        for i in things_to_delete:
            if i in class_dict:
                del class_dict[i]
        return class_dict
 
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
        self.partOf=other
        actual_list.last = self.id
        try :
            with Pyro5.client.Proxy('PYRO:'+self.successor) as nd:
                self.top = nd.top
                self.sucsuccessor = nd.succesor
        except:
            print('Error join succesor')
   
    def check_successor(self):
        if self.successor == self.id or self.successor is None or self.partOf is None:
            return
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
            
            if self.successor == actual_list.last:
                if self.successor==actual_list.current:
                    actual_list.current=self.id
                actual_list.last=self.id
                self.successor=actual_list.first
                try:
                    with Pyro5.client.Proxy('PYRO:'+self.successor) as nd:
                        while len(nd.predecessor_objects)>0:
                            thing=nd.predecessor_objects.pop()
                            class_dict = self.get_dict(thing)
                            self.left_copy(class_dict)
                except:
                    print("Error check_successor last")
                
                if len(self.objects)>self.top:
                    actual_list.allocate()
                return

            elif self.successor == actual_list.first:
                if self.successor == actual_list.current:
                    actual_list.current=self.id
                actual_list.first=self.id
                self.successor=self.sucsuccessor
                actual_list.last=self.predecessor
                if len(self.objects)==0:  
                    try:
                        with Pyro5.client.Proxy('PYRO:'+self.successor) as successor:
                            for i in successor.predecessor_objects:
                                class_dict = self.get_dict(i)
                                self.copy(class_dict)
                    except:
                        print('Error check_succesor first 1')
                else:
                    try:
                        with Pyro5.client.Proxy('PYRO:'+self.predecessor) as predecessor:
                            for i in self.objects:
                                class_dict = self.get_dict(i)
                                predecessor.left_copy(class_dict)
                        actual_list.allocate()
                    except:
                        print('Error check_successor first 2')
                return
            try:
                with Pyro5.client.Proxy('PYRO:'+actual_list.last) as last:
                    if len(last.objects) == 0:
                        if self.successor==actual_list.current:
                            actual_list.current=last.id
                        self.successor = last.id
                        last.successor=self.sucsuccessor
                        actual_list.last=last.predecessor
                        last.predecessor=self.id
                        for i in self.objects:
                            class_dict = self.get_dict(i)
                            last.predecessor_copy(class_dict)
                        try:
                            with Pyro5.client.Proxy('PYRO:'+last.successor) as successor:
                                for i in successor.predecessor_objects:
                                    class_dict = self.get_dict(i)
                                    last.copy(class_dict)
                                successor.predecessor=last.id
                                last.sucsuccessor=successor.successor
                        except:
                            print('Error check_succesor sucsuccesor')
                    else:
                        actual_list.allocate()
            except:
                print('Error check_successor last')
            
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
    
    def remove(self,id):
        for i in self.objects:
            if i.id==id:
                self._pyroDaemon.unregister(i)
                self.objects.remove(i)
        try:
            with Pyro5.client.Proxy(f"PYRO:{self.successor}") as successor:
                successor.remove_predecessor_objects(id)
        except:
            print('Error eliminando en sucesor')

    def remove_predecessor_objecs(self,id):
        for i in self.objects:
            if i.id==id:
                self.predecessor_objects.remove(i)

    def copy(self, class_dict):
        instance=DICT_STR_INS[class_dict['_type']]()

        for k in class_dict:
            setattr(instance,k,class_dict[k])
        self.objects.append(instance)

        self._pyroDaemon.register(instance)
        self.change += self.change_data_sucessor

    def predecessor_copy(self,class_dict):
        instance=DICT_STR_INS[class_dict['_type']]()

        for k in class_dict:
            setattr(instance,k,class_dict[k])
        self.predecessor_objects.append(instance)

    def left_copy(self, class_dict):
        instance=DICT_STR_INS[class_dict['_type']]()

        for k in class_dict:
            setattr(instance,k,class_dict[k])
        self.objects.appendleft(instance)

        self._pyroDaemon.register(instance)
        self.change += self.change_data_sucessor