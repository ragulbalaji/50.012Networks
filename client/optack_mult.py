#!/usr/bin/env python2
"""Optimist ACK script for multiple clients"""

import sys
import time
from raw_packet import Connection
from multiprocessing import Process, Value

mss = 1460
wscale = 4
client_bw = 1544000.


if len(sys.argv) < 5 or len(sys.argv) % 2 != 1:
    print("Usage : optack_mult.py duration target_rate dest_ip dest_port [dest_ip dest_port [...]] ")
    sys.exit()
duration = int(sys.argv[1]) + 1    
target_rate = int(sys.argv[2])

connections = []
for i in range(3, len(sys.argv), 2):
    try:
        dest_ip = sys.argv[i]
        port = int(sys.argv[i+1])
        if port < 0 or port > 65536:
            raise ValueError
        c = Connection(dest_ip, port)
        print('Connecting to %s:%d' % (dest_ip, port))
        connections.append(c)
    except ValueError:
        print("Not a valid IP / port pair : (%s, %s)" % (sys.argv[i], sys.argv[i+1]) )

cur_rate = target_rate / 20.
min_wait = 1.2*8*40./1544000.

def pace(connections, duration, start_ack, mss, overrun_ack):
    """Reads the sequence number of the received packets,
    and ensures that we don't overrun the server"""
    last_received_seq = [x for x in start_ack]
    first_seq = [x for x in start_ack]
    start = time.time()
    while True:
        for (i, c) in enumerate(connections):
            try:
                (r_seq, length) = c.read_packet()
                if r_seq <= last_received_seq[i]:   # retransmission, so use slow start
                    overrun_ack[i].value = last_received_seq[i]
                elif r_seq > last_received_seq[i]:
                    last_received_seq[i] = r_seq
                now = time.time()
                elapsed = now - start
                if (elapsed > duration):
                    sys.exit()
            except Connection.Closed:
                # Not much we can do...
                return

nbr_connections = len(connections)
start = time.time()
maxwindow = 15000 << wscale

start = time.time()
# Start the experiment

# Contact each server in turn
seq = [c.initiate_connection(window=mss, wscale=wscale) for c in connections]
ack = [c.read_packet()[0] for c in connections]
# Save the starting acks for logging purposes
start_ack = [x for x in ack]
# One window per server
window = [mss for _ in range(nbr_connections)]

# Allow the pace thread to selectively indicate an overrun
overrun_ack = [Value('i', -1) for _ in range(nbr_connections)]

p = Process(target = pace, args=(connections, duration, start_ack, mss, overrun_ack))
print("time, acked")
p.start()
while True:
    round_start = time.time()
    elapsed = round_start - start
    if elapsed > duration:
        for (i, c) in enumerate(connections):
            c.send_raw(seq[i]+1, ack_nbr=ack[i], rst=1)
        sys.exit()

    for (i, c) in enumerate(connections):
        # Check for an overrun
        if overrun_ack[i].value > 0:
            # yes, we have an overrun
            print "Overrun"
            ack[i] = overrun_ack[i].value
            overrun_ack[i].value = -1
            window[i] /= 2
            if window[i] < mss:
                window[i] = mss
        c.send_raw(seq_nbr = seq[i], ack_nbr=ack[i])
        now = time.time()
        elapsed = now - start
        print("#%d : %f, %d, (%d)" % (i, elapsed, (ack[i] - start_ack[i]) % (1 << 32), ack[i]))

        ack[i] += window[i]
        if window[i] < maxwindow:
            window[i] += mss
        time.sleep(min_wait) # don't clog the egress link !
    
    round_delay = time.time() - round_start
    wait = max((window[i]/cur_rate) - round_delay, 0.)
    time.sleep(wait)

    # The rate is identical for everyone
    if cur_rate < target_rate:
        cur_rate += target_rate/100.

p.join()
