from collections import deque
from typing import Deque, List, Tuple
from objects import RObject
import hashlib
from collection import Collection

class ChordNode(RObject):
    def __init__(self,id:str) -> None:
        super().__init__(int(hashlib.sha1(id.encode('utf8')).hexdigest(),base=16),'chordNode')
        self.successor : ChordNode = None
        self.predecessor : ChordNode = None
        self._objects={}
        self._finger=[None for i in range(160)]
        self._successors=[]
        self.next=-1
        self.partOf:ChordRing=None

    def __repr__(self) -> str:
        return 'chordNode ' + str(self.id)

    @property
    def finger(self):
        return self._finger

    @property
    def objects(self):
        return self._objects

    def closest_preceding_node(self,id:int)->'ChordNode':
        if self.id > self.successor.id:
            return self.successor
        for i  in range(159,-1,-1):
            if self.finger[i].id > self.id and self.finger[i].id < id:
                return self.finger[i]
        return self

    def find_successor(self,id:int)->'ChordNode':
        if id > self.id and id <= self.successor.id:
            return self.successor
        elif self.id > self.successor.id and (id > self.id or id <= self.successor.id):
            return self.successor
        else:
            aux=self.closest_preceding_node(id)
            return aux.find_successor(id)
    
    def join(self,other)->None:
        self.predecessor=None
        if isinstance(other,ChordNode):
            self.successor=other.find_successor(self.id)
        elif isinstance(other,ChordRing):
            self.successor=other.first.find_successor(self.id)

    def notify(self,other:'ChordNode')->None:
        if self.predecessor is None or other.id > self.predecessor.id and other.id <self.id:
            self.predecessor=other
    
    def stabilize(self)->None:
        x=self.successor.predecessor
        if x.id > self.id and x.id < self.successor.id:
            self.successor=x
        self.successor.notify(self)

    def fix_fingers(self):
        self.next+=1
        if self.next==160:
            self.next=0
        self.finger[self.next]=self.find_successor(self.id + 2**self.next)

    '''
    Falta implementar
    n.check predecessor()
        if (predecessor has failed)
            predecessor = nil;
    '''

    def search(self,id)->RObject:
        node=self.find_successor(id)
        return node.objects[id]

    def add(self, item:RObject):
        node=self.find_successor(item.id)
        if item.id not in node.objects:
            self.partOf.total_items+=1
        node.objects[item.id]=item
    
    def remove(self,id):
        node=self.find_successor(id)
        del node.objects[id]
        self.partOf.total_items-=1

class ChordRing(Collection):
    def __init__(self, id: str,servers:List[str]) -> None:
        super().__init__(id, 'ChordRing')
        
        if len(servers)==0:
            raise Exception('Empty servers list')

        servers_list:List[ChordNode]=[]
        
        for server in servers:
            node=ChordNode(server)
            node.partOf=self
            servers_list.append(node)

        servers_sorted_list:List[ChordNode]=sorted(servers_list, key=lambda item : item.id)
        
        self.first=servers_sorted_list[0]
        self.last=servers_sorted_list[-1]

        for i in range(len(servers_sorted_list)-1):
            servers_sorted_list[i].successor=servers_sorted_list[i+1]

        for i in range(1,len(servers_sorted_list)):
            servers_sorted_list[i].predecessor=servers_sorted_list[i-1]

        self.first.predecessor=self.last
        self.last.successor=self.first

        q:Deque[Tuple[int,int]]=deque()

        index=0

        for i in range(160):
            q.append((index,i))

        actual_node=self.first.successor
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
                servers_sorted_list[tup[0]].finger[tup[1]]=self.first
            elif actual_value<=actual_node.id:
                servers_sorted_list[tup[0]].finger[tup[1]]=actual_node
            else:
                q.append(tup)
                tup_set.add(tup)

    def search(self,id):
        return self.first.search(id)

    def add(self, item):
        self.first.add(item)
    
    def remove(self,id):
        self.first.remove(id)

    @property
    def items(self):
        for item in self.first.objects.values():
            yield item
        actual_node=self.first.successor
        while actual_node!=self.first:
            for item in actual_node.objects.values():
                yield item
            actual_node=actual_node.successor