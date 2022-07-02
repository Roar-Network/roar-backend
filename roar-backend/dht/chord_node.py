from copy import deepcopy
from ..objects.robject import RObject
import hashlib
import Pyro5.server
import Pyro5.client
from threading import Thread
import schedule
from ..dl.list_collection import ListCollection
from ..actor import Actor
from ..post import Post
from copy import deepcopy
from typing import Tuple

DICT_STR_TYPE = {
    'ListCollection': ListCollection,
    'Actor': Actor,
    'Post': Post
}


@Pyro5.server.expose
class ChordNode(RObject):
    def __init__(self, id: str) -> None:
        super().__init__(id, 'chordNode')
        self._key = int(hashlib.sha1(id.encode('utf8')).hexdigest(), base=16)
        self._predecessor: str = None
        self._objects = {}
        self._predecessor_objects = {}
        self._finger = [id]*160
        self._next = -1
        self._partOf: str = None
        self._stabilize_worker: Thread() = Thread(target=self.stabilize_worker)
        self._sucsuccessor = self.id
        self._stabilize_worker.start()

    def stabilize_worker(self):
        def sw():
            self.check_successor()
            self.check_predecessor()
            self.stabilize()
            self.fix_fingers()
        schedule.every(0.05).seconds.do(sw)
        while True:
            schedule.run_pending()

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
        return self._finger[0]

    @successor.setter
    def successor(self, value):
        self._finger[0] = value

    @property
    def predecessor(self):
        return self._predecessor

    @predecessor.setter
    def predecessor(self, value):
        self._predecessor = value

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

    @property
    def sucsuccessor(self):
        return self._sucsuccessor

    @sucsuccessor.setter
    def sucsuccessor(self, value):
        self._sucsuccessor = value

    def change_data_sucessor(self, id_obj: str, field: str, value: Tuple) -> None:
        # if sucessor is yourself, don't change anything
        if self.successor == self.id:
            return
        # else change data in successor
        try:
            with Pyro5.client.Proxy('PYRO:' + self.successor) as successor:
                successor.change_data(id_obj, field, value)
        except:
            print('Error change_data_sucessor')

    def change_data(self, id_obj: str, field: str, args: Tuple) -> None:
        if id_obj in self.predecessor_objects:
            self.predecessor_objects[id_obj].__dict__[field](*args)

    def between(self, x, y, z):
        if y <= z:
            return x > y and x < z
        else:
            return x > y or x < z

    def closest_preceding_node(self, key: int) -> str:
        for i in range(159, -1, -1):
            aux_key = int(hashlib.sha1(
                self.finger[i].encode('utf8')).hexdigest(), base=16)
            if self.between(self.key, key, aux_key):
                return self.finger[i]
        return self.finger[159]

    def find_successor(self, key: int) -> str:
        if self.successor == self.id:
            return self.id
        elif key > self.key and key <= int(hashlib.sha1(self.successor.encode('utf8')).hexdigest(), base=16):
            return self.successor
        elif self.key > int(hashlib.sha1(self.successor.encode('utf8')).hexdigest(), base=16) and (key > self.key or key <= int(hashlib.sha1(self.successor.encode('utf8')).hexdigest(), base=16)):
            return self.successor
        else:
            aux_id = self.closest_preceding_node(key)
            try:
                with Pyro5.client.Proxy('PYRO:' + aux_id) as aux:
                    return aux.find_successor(key)
            except:
                # print(aux_id)
                print('Successor not found')

    def join(self, other: str) -> None:
        self.predecessor = None
        self.objects.clear()
        self.predecessor_objects.clear()

        try:
            with Pyro5.client.Proxy('PYRO:' + other) as other_node:
                self.successor = other_node.find_successor(self.key)
                self.partOf = other_node.partOf
        except:
            print('Invalid node for join')

        # if self.partOf is not None:
        #     try:
        #         with Pyro5.client.Proxy('PYRO:' + self.partOf) as partOf:
        #             if self.key < int(hashlib.sha1(partOf.first.encode('utf8')).hexdigest(),base=16):
        #                 partOf.first=self.id
        #     except:
        #         print('Error join')

    def notify(self, other: str) -> None:
        other_node = None

        try:
            other_node = Pyro5.client.Proxy('PYRO:' + other)
            other_node.id
        except:
            print('Error notify other error')
            return

        if self.predecessor is not None:
            predecessor_key = int(hashlib.sha1(
                self.predecessor.encode('utf8')).hexdigest(), base=16)

        if self.predecessor is None or self.between(other_node.key, predecessor_key, self.key):
            self.predecessor = other
            for k in self.objects:
                key = int(hashlib.sha1(k.encode('utf8')).hexdigest(), base=16)
                if self.between(key, self.key, other_node.key):
                    # unsuscribe event
                    self.objects[k] -= self.change_data_sucessor
                    other_node.copy(self.objects[k])
                    self._pyroDaemon.unregister(self.objects[k])
                    del self.objects[k]
            self._predecessor_objects = other_node.objects.copy()

        other_node._pyroRelease()

    def stabilize(self) -> None:
        if self.successor == self.id:
            if self.predecessor is not None:
                self.successor = self.predecessor
            return
        try:
            with Pyro5.client.Proxy('PYRO:'+self.successor) as successor:
                if successor.predecessor is not None:
                    x = int(hashlib.sha1(successor.predecessor.encode(
                        'utf8')).hexdigest(), base=16)
                    if self.between(x, self.key, successor.key):
                        self.successor = successor.predecessor
                successor.notify(self.id)
        except:
            print('Error stabilize')
            self.check_successor()

    def fix_fingers(self):
        self.next += 1
        if self.next == 160:
            self.next = 0
        self.finger[self.next] = self.find_successor(
            (self.key+2**self.next) % 2**160)

    def check_predecessor(self):
        if self.predecessor is None:
            return
        try:
            node = Pyro5.client.Proxy('PYRO:' + self.predecessor)
            node.id
            node._pyroRelease()
        except:
            self.predecessor = None
            for item in self.predecessor_objects:
                self.objects[item] = self.predecessor_objects[item]

    def check_successor(self):
        if self.successor == self.id:
            return
        try:
            with Pyro5.client.Proxy('PYRO:' + self.successor) as successor:
                self.sucsuccessor = successor.successor
        except:

            try:
                with Pyro5.client.Proxy('PYRO:' + self.sucsuccessor) as sucsuccessor:
                    self.successor = self.sucsuccessor
                    self.sucsuccessor = sucsuccessor.successor
            except:
                for i in self.finger:
                    try:
                        with Pyro5.client.Proxy('PYRO:' + i) as node:
                            self.successor = node.id
                        break
                    except:
                        pass

    def search(self, id) -> RObject:

        key = int(hashlib.sha1(id.encode('utf8')).hexdigest(), base=16)
        print(f"Search succesor node of {key} in {self.id}")
        node = self.find_successor(key)
        print(f"Got node {node}")
        if node is None:
            raise Exception("Error search")
        elif node == self.id:
            return self.objects[id] if id in self.objects else None
        try:
            with Pyro5.client.Proxy('PYRO:'+node) as nd:
                return nd.objects[id] if id in nd.objects else None
        except:
            print('Error search')

    def add_item(self, type_class, args):
        type_instance = DICT_STR_TYPE[type_class]
        item = type_instance(*args)
        self.objects[item.id] = item
        # suscribe to the event of change
        item.change += self.change_data_sucessor
        try:
            self._pyroDaemon.register(item)
        except Exception as e:
            print(str(e))

    def add(self, type_class, args):
        key = int(hashlib.sha1(args[0].encode('utf8')).hexdigest(), base=16)
        node = self.find_successor(key)
        if node is None:
            raise Exception("Error add")
        try:
            with Pyro5.client.Proxy('PYRO:'+node) as nd:
                nd.add_item(type_class, args)
                try:
                    with Pyro5.client.Proxy('PYRO:'+nd.successor) as successor:
                        successor.add_predecessor_objects(type_class, args)
                except:
                    print('Error add successor')
        except:
            print('Error add')

    def add_predecessor_objects(self, type_class, args):
        type_instance = DICT_STR_TYPE[type_class]
        item = type_instance(*args)
        self.predecessor_objects[item.id] = item

    def remove(self, id):
        key = int(hashlib.sha1(id.encode('utf8')).hexdigest(), base=16)
        node = self.find_successor(key)
        if node is None:
            raise Exception("Error remove")
        try:
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

    def copy(self, item):
        self.objects[item.id] = deepcopy(item)
        self._pyroDaemon.register(item)
        self.change += self.change_data_sucessor
