import Pyro5.server
import Pyro5.client
from collections import deque
from typing import List, Deque, Tuple
from ..objects.robject import RObject
from ..objects.collection import Collection

class ListCollection(Collection):
    def __init__(self, id: str,servers:List[str]) -> None:
        super().__init__(id, "ListCollection")
        if len(servers)<3:
            raise Exception('Insuficient servers')
        self.current:ListNode=None
        self._top=20

        servers_list:List[ListNode]=[]
        
        for server in servers:
            try:
                with Pyro5.client.Proxy('PYRO:'+'admin@'+server) as admin:
                    admin.listNode(id+'@'+server)
            except:
                print('Error creando nodos en el servidor')
            node=ListNode(server)
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

        for server in servers_list:
            try:
                with Pyro5.client.Proxy('PYRO:'+server.id) as node:
                    node.successor=server.successor.id
                    node.predecessor=server.predecessor.id
                    node.sucsuccessor=server.succesor.id
                    node.top=self._top
                    node.partOf=self.id
            except:
                print('Error asignando en la red')

        self.first=servers_list[0].id
        self.last=servers_list[-1].id
        
        self.current=self.first

    @property
    def first(self):             
        return self._first

    @first.setter
    def first(self, value):    
        self._first = value

    @property
    def last(self):             
        return self._last

    @last.setter
    def last(self, value):    
        self._last = value

    @property
    def top(self):             
        return self._top

    @last.setter
    def top(self, value):    
        self._top = value

    def allocate(self):
        self.top*=2
        actual_node = None
        losser_node = None
        try:
            with Pyro5.client.Proxy('PYRO:'+self.first) as node:
                node.top=self.top
                actual_node=node.successor
                losser_node = node.successor
        except:
            print('Error allocate first')

        self.current = self.first

        while actual_node != self.first:
            try:
                with Pyro5.client.Proxy('PYRO:'+actual_node) as node:
                    node.top*=2
                    actual_node=node.successor
            except:
                print('Error allocate node')
        
        actual_node=self.first

        while losser_node != self.first:
            try:
                actual_real_node = Pyro5.client.Proxy('PYRO:'+actual_node)
                losser_real_node = Pyro5.client.Proxy('Pyro'+losser_node)
            except:
                print('Error allocating')
            while len(actual_real_node.objects) < self.top:
                if len(losser_real_node.objects)!=0:
                    obj=losser_real_node.objects.popleft()
                    actual_real_node.objects.append(obj)
                else:
                    losser_node=losser_real_node.successor
                    losser_real_node._pyroRelease()
                    try:
                        losser_real_node = Pyro5.client.Proxy('Pyro'+losser_node)
                    except:
                        print('Error allocating')
            actual_node=actual_real_node.successor
            actual_real_node._pyroRelease()
            losser_real_node._pyroRelease()
            self.current=actual_node

    def add(self, item):
        try:
            with Pyro5.client.Proxy('PYRO:'+self.current) as current:
                if self.top <= len (current.objects):
                    if self.current != self.last:
                        self.current = current.id
                        self.add(item)
                    else:
                        self.allocate()
                        self.add(item)
                else:
                    current.add(item)
        except:
            print('Error asignando en la red')

    @property
    def items(self):
        actual_node=None
        try:
            with Pyro5.client.Proxy('PYRO:' + self.first) as node:
                for item in node.objects:
                    yield item
                actual_node=node.successor
        except:
            print('Error items')

        while actual_node != self.first:
            try:
                with Pyro5.client.Proxy('PYRO:' + actual_node) as node:
                    for item in node.objects:
                        yield item
                    actual_node = node.successor
            except:
                print('Error items')