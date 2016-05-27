#!/usr/bin/env python
"""CS244 Spring'16 Project : Reproduce the Optimist-ACK attack. (Alexander Schaub, Trey Deitch)"""
from mininet.topo import Topo
from mininet.node import CPULimitedHost
from mininet.link import TCLink
from mininet.net import Mininet

from subprocess import Popen, PIPE
from time import sleep, time
from multiprocessing import Process
from argparse import ArgumentParser


import sys
import os
import math

PORT = 8080
def parse_args():
    parser = ArgumentParser(description="Optimist-ACK simulation")
    #parser.add_argument('--bw-client', '-b',
    #                    type=float,
    #                    help="Bandwidth of client link (Mb/s)",
    #                    default=1.544)

    parser.add_argument('--bw-server', '-B',
                        type=float,
                        help="Bandwidth of servers (Mb/s)",
                        default=100.)

    parser.add_argument('--delay',
                        type=float,
                        help="Link propagation delay (ms)",
                        default=10.)

    parser.add_argument('--dir', '-d',
                        help="Directory to store outputs",
                        required=True)

    parser.add_argument('--time', '-t',
                        help="Duration (sec) to run the experiment",
                        type=int,
                        default=45)

    parser.add_argument('--nb_servers', '-n',
                        type=int,
                        help="Number of servers to spawn and contact",
                        default=1)

    parser.add_argument('--target_rate', '-r',
                        type=float,
                        help="Target bandwidth for the client to sustain (Mb/s)",
                        default=72.)

    # Expt parameters
    args = parser.parse_args()
    # Convert the target rate from Mb/s to B/s
    args.target_rate *= (1000000. / 8.)

    return args

class BBTopo(Topo):
    "Star topology : one router, one client, n servers"

    def build(self, n=1):
        # Single switch
        switch = self.addSwitch('s0')
        # Connect the client
        h0 = self.addHost('h0')
        self.addLink(h0, switch, 
            bw=1.544, delay="%fms" % args.delay, max_queue_size=1000)

        # Connect n servers
        for i in range(1, n+1):
            h = self.addHost('h%d' % i)
            self.addLink(h, switch,
                bw=args.bw_server, delay="%fms" % args.delay, max_queue_size=1000)
        return


def opt_ack(args):
    # Perform the Opt-ACK attack by creating the desired topology, spawning servers,  and launching the script
    topo = BBTopo(n=args.nb_servers)
    net = Mininet(topo=topo, host=CPULimitedHost, link=TCLink, autoStaticArp=True)
    net.start()

    server_addresses = ""
    for i in range(1, args.nb_servers+1):
        h = net.get('h%d' % i)
        h.popen("python server/data_generator.py -p %d --duration %d --dir %s -i %s" % (PORT, args.time, args.dir, h.IP()), shell=True)
        server_addresses += "%s %d " % (h.IP(), PORT)

    #start client on h0
    h0 = net.get('h0')
    # Suppress RST packets. Thank you very much, group-who-did-this-last-year !
    h0.popen("iptables -t filter -I OUTPUT -p tcp --dport %d --tcp-flags RST RST -j DROP" % PORT)
    h0.popen("python client/optack.py %d %d %s > /dev/null 2> /dev/null" % (args.time, args.target_rate, server_addresses), shell=True).wait()

    # Correctly terminate
    net.stop()

if __name__ == "__main__":
    args = parse_args()
    opt_ack(args)
