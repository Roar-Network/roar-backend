from collections import deque
from typing import List,Deque,Tuple
from collection import Collection
from objects import RObject
import hashlib

class ListNode(RObject):
    def __init__(self,id:str) -> None:
        super().__init__(int(hashlib.sha1(id.encode('utf8')).hexdigest(),base=16),'ListNode')
        self.successor : ListNode = None
        self.predecessor : ListNode = None
        self._objects=deque()
        self._finger=[None for i in range(160)]
        self._successors=[]
        self.next=-1
        self.partOf:ListCollection=None
        self.top=0

    def __repr__(self) -> str:
        return 'ListNode ' + str(self.id)

    @property
    def finger(self):
        return self._finger

    @property
    def objects(self):
        return self._objects

    def closest_preceding_node(self,id:int)->'ListNode':
        if self.id > self.successor.id:
            return self.successor
        for i  in range(159,-1,-1):
            if self.finger[i].id > self.id and self.finger[i].id < id:
                return self.finger[i]
        return self

    def find_successor(self,id:int)->'ListNode':
        if id > self.id and id <= self.successor.id:
            return self.successor
        elif self.id > self.successor.id and (id > self.id or id <= self.successor.id):
            return self.successor
        else:
            aux=self.closest_preceding_node(id)
            return aux.find_successor(id)
    
    def join(self,other)->None:
        self.predecessor=None
        if isinstance(other,ListNode):
            self.successor=other.find_successor(self.id)
        elif isinstance(other,ListCollection):
            self.successor=other.first.find_successor(self.id)

    def notify(self,other:'ListNode')->None:
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

    def add(self, item:RObject):
        node=self.partOf.current
        node.objects.appendleft(item)
    
    def remove(self,k:int):
        total_objecs=len(self.objects)
        if k>=total_objecs:
            self.objects.clear()
            if k>total_objecs:
                if self.successor!=None:
                    self.successor.remove(k-total_objecs)
        else:
            while k!=0 and len(self.objects)!=0:
                self.objects.popleft()
            


class ListCollection(Collection):
    def __init__(self, id: str,servers:List[str]) -> None:
        super().__init__(id, "ListCollection")
        if len(servers)==0:
            raise Exception('Empty servers list')
        self.current:ListNode=None

        servers_list:List[ListNode]=[]
        
        for server in servers:
            node=ListNode(server)
            node.partOf=self
            node.top=20
            servers_list.append(node)

        servers_sorted_list:List[ListNode]=sorted(servers_list, key=lambda item : item.id)
        
        self.first=servers_sorted_list[0]
        self.last=servers_sorted_list[-1]

        for i in range(len(servers_sorted_list)-1):
            servers_sorted_list[i].successor=servers_sorted_list[i+1]

        for i in range(1,len(servers_sorted_list)):
            servers_sorted_list[i].predecessor=servers_sorted_list[i-1]

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

    def alocate(self):
        self.current=self.first

        actual_node=self.first
        while actual_node is not None:
            actual_node.top=2*actual_node.top
            actual_node=actual_node.successor
        
        actual_node=self.first
        losser_node=actual_node.successor

        while losser_node is not None:
            while len(actual_node.objects)<actual_node.top and losser_node is not None:
                if len(losser_node.objects)!=0:
                    obj=losser_node.objects.popleft()
                    actual_node.objects.append(obj)
                else:
                    losser_node=losser_node.successor
            actual_node=actual_node.successor
            self.current=actual_node

    def add(self, item):
        if self.current.top==len(self.current.objects):
            if self.current.successor is not None:
                self.current=self.succesor
            else:
                self.alocate()         
        self.current.add(item)
    
    def remove(self,k:int):
        self.first.remove(k)

    @property
    def items(self):
        actual_node=self.current
        while actual_node is not None:
            for item in actual_node.objects:
                yield item
            actual_node=actual_node.predecessor
