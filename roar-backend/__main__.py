import Pyro5.server as server
import Pyro5.client as client
from .dht.chord_node import ChordNode
from .dl.list_node import ListNode
import socket as sck
import scapy.all as scapy
import threading
import argparse
from typing import List

IP: str = sck.gethostbyname(sck.gethostname())

ACTORS: ChordNode = ChordNode(f"actors@{IP}:8002")
INBOXES: ChordNode = ChordNode(f"inboxes@{IP}:8002")
OUTBOXES: ChordNode = ChordNode(f"outboxes@{IP}:8002")
LIKEDS: ChordNode = ChordNode(f"likeds@{IP}:8002")
POSTS: ChordNode = ChordNode(f"likeds@{IP}:8002")

NETWORK: List = []

@server.expose
@server.behavior(instance_mode="single")
class ServerAdmin:
    def __init__(self, daemon: server.Daemon):
        daemon.register(self, "admin")

    def add_chord_node(self, id: str) -> None:
        node = ChordNode(id)
        daemon.register(node, id.split("@")[0])

    def add_list_node(self, id: str) -> None:
        node = ListNode(id)
        daemon.register(node, id.split("@")[0])

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

def check_all_rings():
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


#if __name__ == "__main__":
parser = argparse.ArgumentParser(description="Start backend server of Roar.")
parser.add_argument('--ip', metavar='ip', type=str, nargs='+', default=[],
                help='a string representing all the known IP')
parser.add_argument("--subnet", metavar="subnet", type=str, help="a string representing the subnet off the server")

args = parser.parse_args()

daemon = server.Daemon("0.0.0.0", 8001)


NETWORK = scan(args.subnet) + args.ip

admin = ServerAdmin(daemon)
daemon.register(ACTORS, "actors")
daemon.register(INBOXES, "inboxes")
daemon.register(OUTBOXES, "outboxes")
daemon.register(LIKEDS, "likeds")
daemon.register(POSTS, "posts")
threading.Thread(target=check_all_rings).start()
daemon.requestLoop()

