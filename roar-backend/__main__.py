from copy import copy
from xxlimited import new
import Pyro5.server as server
import Pyro5.client as client
from .dht.chord_node import ChordNode
from .dl.list_node import ListNode
from .dl.list_collection import ListCollection
import socket as sck
import scapy.all as scapy
import threading
import argparse
from typing import List, Set
from .activities import *
from .api import app
import uvicorn
from .actor import Actor
from schedule import every, run_pending

IP: str = sck.gethostbyname(sck.gethostname())

ACTORS: ChordNode = ChordNode(f"actors@{IP}:8002")
INBOXES: ChordNode = ChordNode(f"inboxes@{IP}:8002")
OUTBOXES: ChordNode = ChordNode(f"outboxes@{IP}:8002")
LIKEDS: ChordNode = ChordNode(f"likeds@{IP}:8002")
POSTS: ChordNode = ChordNode(f"posts@{IP}:8002")

NETWORK: List = []

@server.expose
@server.behavior(instance_mode="single")
class ServerAdmin:
    def __init__(self, daemon: server.Daemon):
        self._system_network: Set[str] = set(IP)
        daemon.register(self, "admin")

    @property
    def system_network(self) -> Set[str]:
        return self._system_network

    @system_network.setter
    def system_network(self, value: Set[str]):
        self._system_network = value

    def receive_system(self, system: Set[str]):
        sys_net = copy(system)
        self.system_network = self._system_network.union(sys_net)

    def add_chord_node(self, id: str) -> ChordNode:
        node = ChordNode(id)
        daemon.register(node, id.split("@")[0])
        return node

    def add_list_node(self, id: str) -> ListNode:
        node = ListNode(id)
        daemon.register(node, id.split("@")[0])
        return node

def scan(ip_address):
    arp_request = scapy.ARP(pdst=ip_address)
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_broadcast_request = broadcast/arp_request

    response = scapy.srp(arp_broadcast_request, timeout=1)[0]

    clients = []
    for item in response:
        clients.append(item[1].psrc)
    return clients

def check_chord_rings(node: ChordNode):
    name, ipport = node.id.split("@")
    ip, port = ipport.split(":")
    port = int(port)

    for item in NETWORK:
        try:
            with client.Proxy(f"PYRO:{name}@{item}:{port}") as rop:
                node.join(rop.id)
                break
        except Exception:
            continue

def check_lists():
    lists=['inboxes,outboxes','likeds']
    for ip in NETWORK:
        for i in lists:
            try:
                with client.Proxy(f"PYRO:{i}@{ip}:8002") as node:
                    for item in node.objects:
                        new_node=admin.add_list_node(f'{item.id}@{ip}:8002')
                        new_node.join(item)
            except:
                continue

def notify_system_network():
    def notify():   
        for ip in admin.system_network:
            try: 
                with Pyro5.client.Proxy(f"PYRO:admin@{ip}:8002") as admin_sys:
                    admin_sys.receive_system(admin.system_network)
            except: 
                continue
    every(0.05).seconds.do(notify)
    while True:
        run_pending()

def check_all_rings():
    check_lists()
    check_chord_rings(ACTORS)
    check_chord_rings(INBOXES)
    check_chord_rings(OUTBOXES)
    check_chord_rings(LIKEDS)
    check_chord_rings(POSTS)

    print('actors=',ACTORS.successor)
    print('inboxes=',INBOXES.successor)
    print('outboxes=',OUTBOXES.successor)
    print('likeds=',LIKEDS.successor)
    print('posts=',POSTS.successor)


parser = argparse.ArgumentParser(description="Start backend server of Roar.")
parser.add_argument('--ip', metavar='ip', type=str, nargs='+', default=[],
                help='a string representing all the known IP')
parser.add_argument("--subnet", metavar="subnet", type=str, help="a string representing the subnet off the server")

args = parser.parse_args()

daemon = server.Daemon("0.0.0.0", 8002)


NETWORK = scan(args.subnet) + args.ip

admin: ServerAdmin = ServerAdmin(daemon)
daemon.register(ACTORS, "actors")
daemon.register(INBOXES, "inboxes")
daemon.register(OUTBOXES, "outboxes")
daemon.register(LIKEDS, "likeds")
daemon.register(POSTS, "posts")
daemon.register(CreateActivity)
daemon.register(FollowActivity)
daemon.register(LikeActivity)
daemon.register(ShareActivity)
daemon.register(DeleteActivity)
daemon.register(UnfollowActivity)
daemon.register(Actor)
daemon.register(ListCollection)
threading.Thread(target=check_all_rings).start()
threading.Thread(target=notify_system_network).start()
uvicorn.run(app, host="0.0.0.0", port=32020)
daemon.requestLoop()
