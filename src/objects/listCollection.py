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
        self._predecessor_objects=deque()
        self.sucsuccessor : ListNode = None
        self.partOf : ListCollection = None
        self.top=0
        self.predecessor_is_current = False

    def __repr__(self) -> str:
        return 'ListNode ' + str(self.id)

    @property
    def finger(self):
        return self._finger

    @property
    def objects(self):
        return self._objects

    @property
    def predecessor_objects(self):
        return self._predecessor_objects
    
    def join(self,other) -> None:
        self.predecessor=None
        self.objects.clear()
        if isinstance(other,ListNode):
            other=other.partOf
        self.successor=other.first
        self.predecessor=other.last
        other.last=self
        self.top=self.successor.top
        self.sucsuccessor=self.successor.successor
   
    '''
    Falta implementar
    n.check predecessor()
        if (predecessor has failed)
            predecessor = nil;

    n.check succesor()
        if (successor has failed)
            successor = sucsucessor
            sucsuccessor=successor.successor
            predecessor.sucsuccessor=successor

            aplicar la idea de poner el ultimo nodo para llenar el hueco

            si tiene elementos hacer crecer la lista
    
    hacerse cargo de los items del nodo caido

    si el caido era el current ahora yo soy el current

    '''

    def add(self, item:RObject):
        self.objects.appendleft(item)
        self.successor.predecessor_objects.appendleft(item)
    
    def remove(self,k:int):
        total_objecs=len(self.objects)
        if k>=total_objecs:
            self.objects.clear()
            if k>total_objecs:
                if self != self.partOf.last:
                    self.successor.remove(k-total_objecs)
        else:
            while k!=0 and len(self.objects)!=0:
                self.objects.pop()
            


class ListCollection(Collection):
    def __init__(self, id: str,servers:List[str]) -> None:
        super().__init__(id, "ListCollection")
        if len(servers)<3:
            raise Exception('Insuficient servers')
        self.current:ListNode=None

        servers_list:List[ListNode]=[]
        
        for server in servers:
            #if server not has failed
            node=ListNode(server)
            node.partOf=self
            node.top=20
            servers_list.append(node)
        
        self.first=servers_list[0]
        self.last=servers_list[-1]

        for i in range(len(servers_list)-1):
            servers_list[i].successor=servers_list[i+1]

        for i in range(1,len(servers_list)):
            servers_list[i].predecessor=servers_list[i-1]

        self.first.predecessor=self.last
        self.last.successor=self.first

        for server in servers_list:
            server.sucsuccessor=server.successor.successor

    def alocate(self):
        self.first.top=2*self.first.top

        self.current=self.first

        actual_node=self.first.successor
        while actual_node != self.first:
            actual_node.top=2*actual_node.top
            actual_node=actual_node.successor
        
        actual_node=self.first
        losser_node=actual_node.successor

        while losser_node is not self.first:
            while len(actual_node.objects)<actual_node.top and losser_node is not None:
                if len(losser_node.objects)!=0:
                    obj=losser_node.objects.popleft()
                    actual_node.objects.append(obj)
                else:
                    losser_node=losser_node.successor
            actual_node=actual_node.successor
            self.current=actual_node

    def add(self, item):
        if self.current.top<=len(self.current.objects):
            if self.current != self.last:
                self.current=self.succesor
            else:
                self.alocate()         
        self.current.add(item)
    
    def remove(self,k:int):
        self.first.remove(k)

    @property
    def items(self):
        for item in self.current.objects:
            yield item
        actual_node=self.current.predecessor
        while actual_node != self.last:
            for item in actual_node.objects:
                yield item
            actual_node=actual_node.predecessor
