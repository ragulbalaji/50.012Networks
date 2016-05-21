import sys
import time
from raw_packet import Connection
from multiprocessing import Process, Value

if len(sys.argv) < 3:
    print "Usage : optack.py dest_ip dest_port"
    sys.exit()


c = Connection(sys.argv[1], int(sys.argv[2]))


def pace(c, start_ack, mss, ack, window):
    """Reads the sequence number of the received packets,
    and ensures that we don't overrun the server"""
    last_received_seq = start_ack
    first_seq = start_ack
    while True:
        try:
            (r_seq, length) = c.read_packet()
            if r_seq == last_received_seq:
                ack.value = r_seq + length
                window.value /= 2
                if window.value < mss:
                    window.value = mss
            elif r_seq > last_received_seq:
                last_received_seq = r_seq
                #ack.value += window.value
            else:
                ack.value = last_received_seq
        except Connection.Closed:
            window.value = -1
            break


next_seq = c.initiate_connection()
start = time.time()
maxwindow = 30000
mss = 1460
window = Value('i', mss)
(start_ack, _) = c.read_packet()
ack = Value('i', start_ack)
start = time.time()
p = Process(target = pace, args=(c, start_ack, mss, ack, window))
print "time, acked"
p.start()
while True:
    if window.value < 0:
        break # we have finished
    cont = c.send_raw(seq_nbr = next_seq, ack_nbr=ack.value)
    now = time.time()
    print("%f, %d" % (now-start,(ack.value - start_ack) % (1 << 32)))
    ack.value += window.value
    if window.value < maxwindow:
        window.value += mss
    time.sleep(0.005)

p.join()