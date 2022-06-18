from collections import deque
from typing import Deque, List, Tuple
from ..objects.robject import RObject
import hashlib
from ..objects.collection import Collection
import Pyro5.server
import Pyro5.client
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