#!/usr/bin/env python2

import sys
import time
from raw_packet import Connection
from multiprocessing import Process, Value

mss = 1460
wscale = 4
ack_delay = 0.005

if len(sys.argv) < 4:
    print "Usage : optack.py dest_ip dest_port duration"
    sys.exit()
dest_ip = sys.argv[1]
port = int(sys.argv[2])
duration = int(sys.argv[3])

c = Connection(dest_ip, port)

def pace(c, start_ack, mss, ack, window):
    """Reads the sequence number of the received packets,
    and ensures that we don't overrun the server"""
    last_received_seq = start_ack
    first_seq = start_ack
    while True:
        try:
            (r_seq, length) = c.read_packet()
            if r_seq == last_received_seq:   # retransmission, so use slow start
                ack.value = r_seq + length
                window.value /= 2
                if window.value < mss:
                    window.value = mss
            elif r_seq > last_received_seq:
                last_received_seq = r_seq
                #ack.value += window.value
        except Connection.Closed:
            window.value = -1
            return

start = time.time()
window = Value('i', mss)
maxwindow = mss << wscale
next_seq = c.initiate_connection(window=mss, wscale=wscale)
(start_ack, _) = c.read_packet()

ack = Value('i', start_ack)
start = time.time()
p = Process(target = pace, args=(c, start_ack, mss, ack, window))
print("time, acked")
p.start()

while True:
    if window.value < 0:
        break # we have finished
    cont = c.send_raw(seq_nbr = next_seq, ack_nbr=ack.value)
    now = time.time()
    elapsed = now - start
    print("%f, %d" % (elapsed, (ack.value - start_ack) % (1 << 32)))
    if (elapsed > duration):
	sys.exit()
    ack.value += window.value
    if window.value < maxwindow:
        window.value += mss
    time.sleep(ack_delay)

p.join()
