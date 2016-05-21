import sys
import time
from raw_packet import Connection

if len(sys.argv) < 3:
    print "Usage : optack.py dest_ip dest_port"
    sys.exit()


c = Connection(sys.argv[1], int(sys.argv[2]))


next_seq = c.initiate_connection()
start = time.time()
first_seq = -1
maxwindow = 20000
mss = 1460
window = mss
(seq, length) = c.read_packet()
first_seq = seq
last_received_seq = seq
start = time.time()
print "time, acked"
while True:
    cont = c.send_raw(seq_nbr = next_seq, ack_nbr=seq)
    now = time.time()
    print("%f, %d" % (now-start,(seq - first_seq)))
    if window < maxwindow:
        window += mss
    try:
        (r_seq, length) = c.read_packet()
        print(r_seq - first_seq)
        if r_seq == last_received_seq:
            seq = r_seq + length
            window /= 2
        elif r_seq > last_received_seq:
            last_received_seq = r_seq
            seq += window
        else:
            seq = last_received_seq
    except Connection.Closed:
        break
