from collections import deque
from copy import deepcopy
from typing import Deque, List, Tuple
from RObjects import RObject
import hashlib
from collection import Collection
import Pyro5.server
import Pyro5.client

@Pyro5.server.expose
class ChordNode(RObject):
    def __init__(self,id:str) -> None:
        super().__init__(id,'chordNode')
        self._key = int(hashlib.sha1(id.encode('utf8')).hexdigest(),base=16)
        self._successor : str = None
        self._predecessor : str = None
        self._objects={}
        self._predecessor_objects={}
        self._finger=[None for i in range(160)]
        self._sucsuccessor : str = None
        self._next=-1
        self._partOf : str = None

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

    @partOf.setter
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
            return self
        if key > self.key and key <= int(hashlib.sha1(self.successor.encode('utf8')).hexdigest(),base=16):
            return self.successor
        elif self.key > int(hashlib.sha1(self.successor.encode('utf8')).hexdigest(),base=16) and (key > self.key or key <= int(hashlib.sha1(self.successor.encode('utf8')).hexdigest(),base=16)):
            return self.successor
        else:
            aux = self.closest_preceding_node(key)
            return aux.find_successor(key)
    
    def join(self, other:str)->None:
        print(other + " in join! ")
        self.predecessor=None
        self.objects.clear()
        self.predecessor_objects.clear()

        try:
            with Pyro5.client.Proxy('PYRO:' + other) as other_node:
                self.successor = other_node.find_successor(self.key)
                print(self.successor)
                self.sucsuccessor=self.successor.successor
                self.partOf=other_node.partOf
        except Exception as e:
            print(e)
            print('Error join 1')

        if self.partOf is not None:
            try:
                with Pyro5.client.Proxy('PYRO:' + self.partOf) as partOf:
                    if self.key < int(hashlib.sha1(partOf.first.encode('utf8')).hexdigest(),base=16):
                        partOf.first=self.id
            except:
                print('Error join')

        print(f"finish join! {self.successor}")

    def notify(self,other:str)->None:
        other_node = None

        try:
            other_node = Pyro5.client.Proxy('PYRO:' + other)
        except:
            print('Error notify other error')
        
        if self.predecessor is None or other_node.key > int(hashlib.sha1(self.predecessor.encode('utf8')).hexdigest(),base=16) and other_node.key < self.key:
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
                x=int(hashlib.sha1(successor.predecessor.encode('utf8')).hexdigest(),base=16)
                if x > self.key and x  < successor.key:
                    self.successor=successor.predecessor
                successor.notify(self.id)
        except:
            print('Error stabilize')

    def fix_fingers(self):
        self.next+=1
        if self.next==160:
            self.next=0
        self.finger[self.next]=self.find_successor(self.key + 2**self.next)

    def check_predecessor(self):
        try:
            Pyro5.client.Proxy(self.predecessor)._pyroRelease()
        except:
            self.predecessor = None
            for item in self.predecessor_objects:
                self.objects[item]=self.predecessor_objects[item]

    def check_successor(self):
        try:
            Pyro5.client.Proxy(self.successor)._pyroRelease()
        except:

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
                if key in nd.objects:
                    return node.objects[key]
                else:
                    return None
        except:
            print('Error search')
        

    def add(self, item:RObject):
        key=int(hashlib.sha1(item.id.encode('utf8')).hexdigest(),base=16)
        node=self.find_successor(key)
        registed = False

        try :
            with Pyro5.client.Proxy('PYRO:'+node) as nd:
                if key in nd.objects:
                    registed = True
                
                nd.objects[key]=deepcopy(item)

                try:
                    with Pyro5.client.Proxy('PYRO:'+nd.successor) as successor:
                        successor.predecessor_objects[key]=deepcopy(item)
                except:
                    print('Error add successor')
        except:
            print('Error add')      
       
        return registed
    
    def remove(self,id):
        key=int(hashlib.sha1(id.encode('utf8')).hexdigest(),base=16)
        node=self.find_successor(key)
        try :
            with Pyro5.client.Proxy('PYRO:'+node) as nd:
                del nd.objects[id]

                try:
                    with Pyro5.client.Proxy('PYRO:'+nd.successor) as successor:
                        del successor.predecessor_objects[key]
                except:
                    print('Error del successor')   
        except:
            print('Error del')

        return True

@Pyro5.server.expose
class ChordRing(Collection):
    def __init__(self, id: str,servers:List[str]) -> None:
        super().__init__(id, 'ChordRing')
        
        if len(servers)==0:
            raise Exception('Empty servers list')

        servers_list:List[ChordNode]=[]
        
        for server in servers:
            try:
                with Pyro5.client.Proxy('PYRO:'+'admin@'+server) as admin:
                    admin.addChordNode(id+'@'+server)
            except:
                print('Error creando nodos en el servidor')
            node=ChordNode(id+'@'+server)
            servers_list.append(node)

        servers_sorted_list:List[ChordNode]=sorted(servers_list, key=lambda item : item.id)
        
        self._first=servers_sorted_list[0]
        self._last=servers_sorted_list[-1]

        for i in range(len(servers_sorted_list)-1):
            servers_sorted_list[i].successor=servers_sorted_list[i+1]

        for i in range(1,len(servers_sorted_list)):
            servers_sorted_list[i].predecessor=servers_sorted_list[i-1]

        self._first.predecessor=self._last
        self._last.successor=self._first

        for server in servers_sorted_list:
            server.sucsuccessor=server.successor.successor

        q:Deque[Tuple[int,int]]=deque()

        index=0

        for i in range(160):
            q.append((index,i))

        actual_node=self._first.successor
        tup_set=set()
        while len(q)!=0 or index!=len(servers_sorted_list)-1:

            if len(q)==0:
                actual_node=actual_node.successor
                index+=1
                for i in range(160):
                    q.append((index,i))
                tup_set.clear()

            tup=q.popleft()
            
            if tup in tup_set:
                actual_node=actual_node.successor
                index+=1
                for i in range(160):
                    q.append((index,i))
                tup_set.clear()

            actual_id=servers_sorted_list[tup[0]].id
            actual_value=actual_id + 2**tup[1]

            if actual_value > self.last.id:
                servers_sorted_list[tup[0]].finger[tup[1]]=self._first
            elif actual_value<=actual_node.id:
                servers_sorted_list[tup[0]].finger[tup[1]]=actual_node
            else:
                q.append(tup)
                tup_set.add(tup)
        
        for server in servers_sorted_list:
            try:
                with Pyro5.client.Proxy('PYRO:'+server.id) as node:
                    node.successor=server.successor.id
                    node.predecessor=server.predecessor.id
                    node.sucsuccessor=server.succesor.id
                    node.partOf=self.id
                    for i in range(len(server.finger)):
                        node.finger[i]=server.finger[i].id
            except:
                print('Error asignando en la red')

        self._first=servers_sorted_list[0].id
        self._last=servers_sorted_list[-1].id

    @property
    def first(self):             
        return self._first

    @first.setter
    def next(self, value):    
        self._first = value

    @property
    def last(self):             
        return self._last

    @first.setter
    def last(self, value):    
        self._last = value

    def search(self,id):
        try:
            with Pyro5.client.Proxy('PYRO:' + self.first) as node:
                return node.search(id)
        except:
            print('Error join')

    def add(self, item):
        try:
            with Pyro5.client.Proxy('PYRO:' + self.first) as node:
                node.add(item)
        except:
            print('Error add')
        
    def remove(self,id):
        try:
            with Pyro5.client.Proxy('PYRO:' + self.first) as node:
                node.add(id)
        except:
            print('Error remove')

    @property
    def items(self):
        actual_node=None
        try:
            with Pyro5.client.Proxy('PYRO:' + self.first) as node:
                for item in node.objects.values():
                    yield item
                actual_node=node.successor
        except:
            print('Error items')

        while actual_node != self.first:
            try:
                with Pyro5.client.Proxy('PYRO:' + actual_node) as node:
                    for item in node.objects.values():
                        yield item
                    actual_node = node.successor
            except:
                print('Error items')