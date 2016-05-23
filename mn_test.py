#!/usr/bin/python

from mininet.topo import Topo
from mininet.node import CPULimitedHost
from mininet.link import TCLink
from mininet.net import Mininet
from mininet.log import lg, info
from mininet.util import dumpNodeConnections
from mininet.cli import CLI

from subprocess import Popen, PIPE
from time import sleep, time
from multiprocessing import Process
from argparse import ArgumentParser

#from monitor import monitor_qlen
import termcolor as T

import sys
import os
import math

PORT = 8080
DURATION = 60

args = {
	"delay": 20.,
	"max_queue_size":100,
	"bw_host":100.,
	"bw_net":1.0
}

class BBTopo(Topo):
    "Simple topology for experiment."

    def build(self, n=2):

        # Here I have created a switch.  If you change its name, its
        # interface names will change from s0-eth1 to newname-eth1.
        switch = self.addSwitch('s0')

        # TODO: create two hosts
        h1 = self.addHost('h1')
        h2 = self.addHost('h2')

        # TODO: Add links with appropriate characteristics
        self.addLink(h1, switch, 
            bw=100., delay="10ms", max_queue_size=1000)
        self.addLink(h2, switch,
            bw=1.544, delay="10ms", max_queue_size=1000)
        return

topo = BBTopo()
net = Mininet(topo=topo, host=CPULimitedHost, link=TCLink)
net.start()
h1 = net.get('h1')
h2 = net.get('h2')

#start server on h1
h1.popen("python http/data_generator.py -p %d --duration %d --dir . -i %s > a.txt 2> c.txt" % (PORT, DURATION, h1.IP()), shell=True)

#start client on h2
h2.popen("python client/optack.py %s %d %d > b.txt 2> d.txt" % (h1.IP(), PORT, DURATION), shell=True).wait()
