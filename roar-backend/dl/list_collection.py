import Pyro5.server
import Pyro5.client
from typing import List
from ..objects.collection import Collection
from .list_node import ListNode
import Pyro5.server
import time
from threading import Thread
import schedule

@Pyro5.server.expose
class ListCollection(Collection):
    def __init__(self, id: str,servers:List[str]) -> None:
        super().__init__(id, "ListCollection")
   
        if len(servers)==0:
            raise Exception('Insuficient servers')

        self._current=None
        self._top=64
        
        servers_list:List[ListNode]=[]
        

        for server in servers:
            try:
                with Pyro5.client.Proxy('PYRO:'+'admin@'+server) as admin:
                    admin.add_list_node(id+'@'+server)
            except Exception as e:
                print('Error creando nodos en el servidor')
                print(str(e))
            node=ListNode(id+'@'+server)
            servers_list.append(node)

        self._first=servers_list[0]
        self._last=servers_list[-1]

        for i in range(len(servers_list)-1):
            servers_list[i].successor=servers_list[i+1]

        for i in range(1,len(servers_list)):
            servers_list[i].predecessor=servers_list[i-1]


        self._first.predecessor=self._last
        self._last.successor=self._first


        for server in servers_list:
            server.sucsuccessor=server.successor.successor

        for server in servers_list:
            try:
                with Pyro5.client.Proxy('PYRO:'+server.id) as node:
                    node.successor=server.successor.id
                    node.predecessor=server.predecessor.id
                    node.sucsuccessor=server.successor.id
                    node.top=self._top
                    node.partOf=self.id
            except Exception as e:
                print(str(e))

        self._first=servers_list[0].id
        self._last=servers_list[-1].id
        
        self._current=self._first

    @property
    def first(self):       
        if isinstance(self._first, ListNode):
            return self._first.id      
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
    def current(self):             
        return self._current

    @current.setter
    def current(self, value):    
        self.current = value

    @property
    def top(self):             
        return self._top

    @top.setter
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
            time.sleep(1)
            self.allocate()
            return

        self.current = self.first

        while actual_node != self.first:
            try:
                with Pyro5.client.Proxy('PYRO:'+actual_node) as node:
                    node.top*=2
                    actual_node=node.successor
            except:
                print('Error allocate node')
                time.sleep(1)
                self.allocate()
                return
        
        actual_node=self.first

        while losser_node != self.first:
            try:
                actual_real_node = Pyro5.client.Proxy('PYRO:'+actual_node)
                actual_real_node.id
                losser_real_node = Pyro5.client.Proxy('PYRO:'+losser_node)
                losser_real_node.id
            except:
                print('Error allocating')
                time.sleep(1)
                self.allocate()
                return
            while len(actual_real_node.objects) < self.top:
                if len(losser_real_node.objects)!=0:
                    obj=losser_real_node.objects.popleft()
                    losser_real_node._pyroDaemon.unregister(obj)
                    class_dict=losser_real_node.get_dict(obj)
                    actual_node.copy(class_dict)
                    actual_node._pyroDaemon.register(obj)
                else:
                    losser_node=losser_real_node.successor
                    losser_real_node._pyroRelease()
                    try:
                        losser_real_node = Pyro5.client.Proxy('Pyro'+losser_node)
                        losser_real_node.id
                    except:
                        print('Error allocating')
                        time.sleep(1)
                        self.allocate()
                        return
            actual_node=actual_real_node.successor
            actual_real_node._pyroRelease()
            losser_real_node._pyroRelease()
            self.current=actual_node

    def add(self, type_class, args):
        try:
            with Pyro5.client.Proxy('PYRO:'+self.current) as current:
                if len (current.objects) >= self.top:
                    if self.current != self.last:
                        self.current = current.successor
                        self.add(type_class, args)
                    else:
                        self.allocate()
                        self.add(type_class, args)
                else:
                    current.add(type_class, args)
        except Exception as e:
            print(str(e))

    def remove(self, id):
        actual_node=None
        try:
            with Pyro5.client.Proxy('PYRO:' + self.current) as node:
                if id in node.objects_ids:
                    node.remove(id)
                    return
                actual_node = node.predecessor
        except:
            print('Error remove')

        while actual_node != self.last:
            try:
                with Pyro5.client.Proxy('PYRO:' + actual_node) as node:
                    if id in node.objects_ids:
                        node.remove(id)
                        return
                actual_node = node.predecessor
            except:
                print('Error items remove')

    def items(self,activity_type:List[str]):
        actual_node=self.current

        # filtered_items = []

        while actual_node != self.first:
            try:
                with Pyro5.client.Proxy('PYRO:' + actual_node) as node:
                    for item in node.objects:
                        if item.type in activity_type:
                            # filtered_items.append(item.obj)
                            yield item.obj
                    actual_node = node.predecessor
            except Exception as e:
                print(f'Error items {e}')

        
        try:
            with Pyro5.client.Proxy('PYRO:' + self.first) as node:
                for item in node.objects:
                    if item.type in activity_type:
                        # print("item=",item.id)
                        # filtered_items.append(item.obj)
                        yield item.obj
                        # print("list=",filtered_items)
        except Exception as e:
            print(str(e))
        # return filtered_items