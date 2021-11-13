#!/usr/bin/python

from mininet.topo import Topo
from mininet.node import CPULimitedHost
from mininet.link import TCLink
from mininet.net import Mininet
from mininet.cli import CLI
from mininet.node import OVSController

from subprocess import Popen, PIPE
from time import sleep, time
from multiprocessing import Process
from argparse import ArgumentParser

class TopoStar(Topo):
  def __init__(self, n=2, cpu=None, bw_host=1, bw_net=1, delay='1000', maxq=None, diff=False):
    super(TopoStar, self ).__init__()
    for i in range(n): self.addHost( 'h%d' % (i+1), cpu=cpu )
    self.addSwitch('s0', fail_mode='open')
    self.addLink('h1', 's0', bw=bw_host, delay=delay)
    for i in range(1, n): self.addLink('h%d' % (i+1), 's0', bw=bw_net)

if __name__ == '__main__':
  topo = TopoStar(n=16)
  net = Mininet(topo=topo, host=CPULimitedHost, link=TCLink, autoPinCpus=True, controller=OVSController)
  net.start()
  net.pingAll()
  CLI(net)
  net.stop() 
