from ..objects.robject import RObject
import hashlib
import Pyro5.server
import Pyro5.client
from threading import Thread
import schedule
import time
from copy import deepcopy

@Pyro5.server.expose
class ChordNode(RObject):
    def __init__(self,id:str) -> None:
        super().__init__(id,'chordNode')
        self._key = int(hashlib.sha1(id.encode('utf8')).hexdigest(),base=16)
        self._successor : str = None
        self._predecessor : str = None
        self._objects={}
        self._predecessor_objects={}
        self._finger=[id for i in range(160)]
        self._sucsuccessor : str = None
        self._next=-1
        self._partOf : str = None
        self._stabilize_worker: Thread() = Thread(target=self.stabilize_worker)
        
        self._stabilize_worker.start()
    

    def stabilize_worker(self):
        def sw():
            self.check_successor()
            self.check_predecessor()
            self.stabilize()
            self.fix_fingers()
        schedule.every(20).seconds.do(sw)
        while True:
            schedule.run_pending()
            time.sleep(1)


    def __repr__(self) -> str:
        return 'chordNode ' + str(self.id)

    @property
    def finger(self):
        return self._finger

    @property
    def objects(self):
        return self._objects

    @property
    def predecessor_objects(self):
        return self._predecessor_objects

    @property
    def key(self):
        return self._key

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
    def next(self):             
        return self._next

    @next.setter
    def next(self, value):    
        self._next = value


    def closest_preceding_node(self,key:int)->str:
       
        if self.key > int(hashlib.sha1(self.successor.encode('utf8')).hexdigest(),base=16):
            return self.successor
        for i in range(159,-1,-1):
            aux_key=int(hashlib.sha1(self.finger[i].encode('utf8')).hexdigest(),base=16)
            if aux_key > self.key and aux_key < key:
                return self.finger[i]
        return self.id
        

    def find_successor(self,key:int)->str:
        if self.successor is None:
            return self.id
        if key > self.key and key <= int(hashlib.sha1(self.successor.encode('utf8')).hexdigest(),base=16):
            return self.successor
        elif self.key > int(hashlib.sha1(self.successor.encode('utf8')).hexdigest(),base=16) and (key > self.key or key <= int(hashlib.sha1(self.successor.encode('utf8')).hexdigest(),base=16)):
            return self.successor
        else:
            aux_id = self.closest_preceding_node(key)
            try:
                with Pyro5.client.Proxy('PYRO:' + aux_id) as aux:
                    return aux.find_successor(key)
            except:
                print('Error find successor')
    
    def join(self, other:str)->None:
        self.predecessor=None
        self.objects.clear()
        self.predecessor_objects.clear()

        try:
            with Pyro5.client.Proxy('PYRO:' + other) as other_node:
                self.successor = other_node.find_successor(self.key)
                self.partOf=other_node.partOf
            with Pyro5.client.Proxy('PYRO:' + self.successor) as successor:
                if successor.successor is None:
                    successor.successor=self.id
                    successor.sucsuccessor=successor.id
                self.sucsuccessor=successor.successor
        except Exception as e:
            print(e)
            print('Error join 1')

        self.fix_fingers()

        if self.partOf is not None:
            try:
                with Pyro5.client.Proxy('PYRO:' + self.partOf) as partOf:
                    if self.key < int(hashlib.sha1(partOf.first.encode('utf8')).hexdigest(),base=16):
                        partOf.first=self.id
            except:
                print('Error join')


    def notify(self,other:str)->None:
        other_node = None

        try:
            other_node = Pyro5.client.Proxy('PYRO:' + other)
        except:
            print('Error notify other error')
        
        # print('self_key=',self.key)
        # print('other_node_key=', other_node.key)
        # if self.predecessor is not None:
        #     print('predecessor_key=', int(hashlib.sha1(self.predecessor.encode('utf8')).hexdigest(),base=16))
        # else:
        #     print('None')
        
        if self.predecessor is not None:
            predecessor_key=int(hashlib.sha1(self.predecessor.encode('utf8')).hexdigest(),base=16)

        if self.predecessor is None or (other_node.key > predecessor_key and (other_node.key < self.key or self.key < predecessor_key)):
            self.predecessor = other
            for k in self.objects:
                if k < other_node.key:
                    other_node.objects[k]=self.objects[k]
                    del self.objects[k]
            self._predecessor_objects = other_node.objects.copy()

        other_node._pyroRelease()
    
    def stabilize(self)->None:
        try :
            with Pyro5.client.Proxy('PYRO:'+self.successor) as successor:
                if successor.predecessor is not None:
                    x=int(hashlib.sha1(successor.predecessor.encode('utf8')).hexdigest(),base=16)
                    if x > self.key and (x  < successor.key or self.key > successor.key):
                        self.successor=successor.predecessor
                successor.notify(self.id)
        except Exception as e:
            print(e)

    def fix_fingers(self):
        print(self.next)
        self.next+=1
        if self.next==160:
            self.next=0
        self.finger[self.next]=self.find_successor(self.key + 2**self.next)

    def check_predecessor(self):
        print('predecessor=',self.predecessor)
        try:
            Pyro5.client.Proxy('PYRO:' + self.predecessor)._pyroRelease()
        except:
            self.predecessor = None
            for item in self.predecessor_objects:
                self.objects[item]=self.predecessor_objects[item]

    def check_successor(self):
        print('successor=',self.successor)
        try:
            Pyro5.client.Proxy('PYRO:' + self.successor)._pyroRelease()
        except:

            if self.sucsuccessor == self.id:
                self.successor=None
                self.sucsuccessor=None

            else:

                self.successor=self.sucsuccessor
                
                try:
                    with Pyro5.client.Proxy('PYRO:'+self.successor) as successor:
                        self.sucsuccessor=successor.successor
                except:
                    print('Error check_succesor succesor')
                
                try:
                    with Pyro5.client.Proxy('PYRO:'+self.predecessor) as predecessor:
                        predecessor.sucsuccessor=self.successor
                except:
                    print('Error check_succesor predecessor')


    def search(self,id)->RObject:
        key=int(hashlib.sha1(id.encode('utf8')).hexdigest(),base=16)
        node=self.find_successor(key)
        try :
            with Pyro5.client.Proxy('PYRO:'+node) as nd:
                if id in nd.objects:
                    return node.objects[id]
                else:
                    return None
        except:
            print('Error search')
        

    def add(self, item:RObject):
        key=int(hashlib.sha1(item.id.encode('utf8')).hexdigest(),base=16)
        node=self.find_successor(key)

        try :
            with Pyro5.client.Proxy('PYRO:'+node) as nd:
                
                nd.objects[id]=deepcopy(item)

                try:
                    with Pyro5.client.Proxy('PYRO:'+nd.successor) as successor:
                        successor.add_predecessor_objects(item)
                except:
                    print('Error add successor')
        except:
            print('Error add')

    def add_predecessor_objects(self, item: RObject):
        self.predecessor_objects[item.id]=deepcopy(item)
    
    def remove(self,id):
        key=int(hashlib.sha1(id.encode('utf8')).hexdigest(),base=16)
        node=self.find_successor(key)
        try :
            with Pyro5.client.Proxy('PYRO:'+node) as nd:
                del nd.objects[id]

                try:
                    with Pyro5.client.Proxy('PYRO:'+nd.successor) as successor:
                        del successor.predecessor_objects[id]
                except:
                    print('Error del successor')   
        except:
            print('Error del')

        return True
