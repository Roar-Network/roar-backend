from chordCollection import ChordRing,ChordNode

a=ChordRing('fsofiosdfiosdo',['fhsjkdfbisjdfbsi','daosfsduofsduofb','dfhsuofsduofbduo','sdfsdfgzdfsdfsfsffg'])

b=ChordNode('dadasdasdasdadasasadasasaa')

a.add(b)

print(a.search(b.id))