from collections import deque
from typing import List,Deque,Tuple
from collection import Collection
import Pyro5.server
import Pyro5.client
from RObjects import RObject

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