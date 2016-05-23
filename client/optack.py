#!/usr/bin/env python2

import sys
import time
from raw_packet import Connection
from multiprocessing import Process, Value

mss = 1460
wscale = 4

if len(sys.argv) < 4:
    print "Usage : optack.py dest_ip dest_port duration"
    sys.exit()
dest_ip = sys.argv[1]
port = int(sys.argv[2])
duration = int(sys.argv[3]) + 1
target_rate = 9000000.
cur_rate = target_rate / 20.
min_wait = 1.2*8*40./1544000.
c = Connection(dest_ip, port)

def pace(c, duration, start_ack, mss, overrun_ack, window):
    """Reads the sequence number of the received packets,
    and ensures that we don't overrun the server"""
    last_received_seq = start_ack
    first_seq = start_ack
    start = time.time()
    while True:
        try:
            (r_seq, length) = c.read_packet()
            #print("Received new : %d" % (r_seq))
            #print("Window size : %d" % window.value)
            if r_seq <= last_received_seq:   # retransmission, so use slow start
                overrun_ack.value = last_received_seq
                #print("Overrun, received out of order : %d" % (r_seq))
                window.value /= 2
                if window.value < mss:
                    window.value = mss

            elif r_seq > last_received_seq:
                last_received_seq = r_seq
            now = time.time()
            elapsed = now - start
            if (elapsed > duration):
                sys.exit()
        except Connection.Closed:
            window.value = -1
            return

start = time.time()
window = Value('i', mss)
maxwindow = 15000 << wscale
next_seq = c.initiate_connection(window=mss, wscale=wscale)
(start_ack, _) = c.read_packet()

ack = start_ack
overrun_ack = Value('i', -1)
start = time.time()
p = Process(target = pace, args=(c, duration, start_ack, mss, overrun_ack, window))
print("time, acked")
p.start()
while True:
    if window.value < 0:
        break # we have finished
    # Verify if we have an overrun situation
    if overrun_ack.value > 0:
        # yes, we do
        print "Overrun"
        ack = overrun_ack.value
        overrun_ack.value = -1
    cont = c.send_raw(seq_nbr = next_seq, ack_nbr=ack)
    #cont = c.send_raw(seq_nbr = next_seq, ack_nbr=ack)
    #print("Ack sent: %s" % ack)
    now = time.time()
    elapsed = now - start
    print("%f, %d, (%d)" % (elapsed, (ack - start_ack) % (1 << 32), ack))
    if elapsed > duration:
        c.send_raw(next_seq+1, ack_nbr=ack, rst=1)
        sys.exit()
    ack += window.value
    if window.value < maxwindow:
        window.value += mss
    wait = max(window.value/cur_rate, min_wait)
    time.sleep(wait)
    if cur_rate < target_rate:
        cur_rate += target_rate/100.

p.join()
