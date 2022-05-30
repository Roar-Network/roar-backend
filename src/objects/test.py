from chordRing import ChordRing,ChordNode
from listCollection import ListCollection,ListNode

a=ChordRing('fsofiosdfiosdo',['fhsjkdfbisjdfbsi','daosfsduofsduofb','dfhsuofsduofbduo','sdfsdfgzdfsdfsfsffg'])

b=ChordNode('dadasdasdasdadasasadasasaa')

A=ListCollection('adadas',['dadadasdas','dadasdasdas'])

a.add(b)

print(a.search(b.id))