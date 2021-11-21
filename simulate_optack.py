#!/usr/bin/env python
"""CS244 Spring'16 Project : Reproduce the Optimist-ACK attack. (Alexander Schaub, Trey Deitch)"""
from mininet.topo import Topo
from mininet.node import CPULimitedHost
from mininet.link import TCLink
from mininet.net import Mininet
import os
from subprocess import Popen, PIPE
from time import sleep, time
from multiprocessing import Process
from argparse import ArgumentParser

import time
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

    parser.add_argument('--nb_attackers',
                        type=int,
                        help="Number of servers to spawn and contact",
                        default=1)
    
    parser.add_argument('--nb_receivers', 
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

    def build(self, num_attacker, num_normal):
        # Single switch
        switch = self.addSwitch('s0')
        # Connect the server
        h0 = self.addHost('server0')
        self.addLink(h0, switch, 
            bw=100.0, delay="%fms" % args.delay, max_queue_size=1000)

        # Connect attackers
        for i in range(num_attacker):
            h = self.addHost('attacker%d' % i)
            self.addLink(h, switch,
                bw=1.5, delay="%fms" % args.delay, max_queue_size=1000)
            
        # Connect normal receivers
        for i in range(num_normal):
            h = self.addHost('receiver%d' % i)
            self.addLink(h, switch,
                bw=1.5, delay="%fms" % args.delay, max_queue_size=1000)
        return


def opt_ack(args):
    # Perform the Opt-ACK attack by creating the desired topology, spawning servers,  and launching the script
    topo = BBTopo(args.nb_attackers, args.nb_receivers)
    net = Mininet(topo=topo, host=CPULimitedHost, link=TCLink, autoStaticArp=True)
    net.start()
    
    server_addresses = ""
    h = net.get('server0')
    h.popen("python server/data_generator.py -p %d --duration %d --dir %s -i %s" % (PORT, args.time, args.dir, h.IP()), shell=True)
    server_addresses += "%s %d " % (h.IP(), PORT)
    
    
    if not os.path.exists("%s/receiver_output/"%(args.dir)):
        os.makedirs("%s/receiver_output/"%(args.dir))
    for i in range(args.nb_receivers):
        receiver = net.get('receiver%d' % i)
    # Suppress RST packets. Thank you very much, group-who-did-this-last-year !
        receiver.popen("iptables -t filter -I OUTPUT -p tcp --dport %d --tcp-flags RST RST -j DROP" % PORT)
        receiver.popen("python client/normal.py %d %d %s > %s/receiver_output/%d.txt" % (args.time, args.target_rate, server_addresses, args.dir, i), shell=True)
    #start client on h0
    if not os.path.exists("%s/attacker_output/"%(args.dir)):
        os.makedirs("%s/attacker_output/"%(args.dir))
    for i in range(args.nb_attackers-1):
        attacker = net.get('attacker%d' % i)
    # Suppress RST packets. Thank you very much, group-who-did-this-last-year !
        attacker.popen("iptables -t filter -I OUTPUT -p tcp --dport %d --tcp-flags RST RST -j DROP" % PORT)
        attacker.popen("python client/optack.py %d %d %s >  %s/attacker_output/%d.txt" % (args.time, args.target_rate, server_addresses,args.dir, i), shell=True)

    
    attacker = net.get('attacker%d' % (args.nb_attackers-1))
    # Suppress RST packets. Thank you very much, group-who-did-this-last-year !
    attacker.popen("iptables -t filter -I OUTPUT -p tcp --dport %d --tcp-flags RST RST -j DROP" % PORT)
    attacker.popen("python client/optack.py %d %d %s > %s/attacker_output/%d.txt" % (args.time, args.target_rate, server_addresses, args.dir, args.nb_attackers-1), shell=True).wait()
    sleep(5)
    # Correctly terminate
    net.stop()

if __name__ == "__main__":
    args = parse_args()
    opt_ack(args)
