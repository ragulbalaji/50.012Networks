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

import time

class TopoStar(Topo):
  def __init__(self, n=2, cpu=None, bw_atkr=1, bw_recv=1, bw_net=1, delay='100', maxq=None, diff=False):
    super(TopoStar, self ).__init__()
    self.addSwitch('s0', fail_mode='open')
    self.addHost('atkr', cpu=cpu)
    self.addHost('recv', cpu=cpu)
    self.addLink('atkr', 's0', bw=bw_atkr, delay=delay)
    self.addLink('recv', 's0', bw=bw_recv, delay=delay)
    for i in range(n): self.addHost(f'h{i}', cpu=cpu)
    for i in range(n): self.addLink(f'h{i}', 's0', bw=bw_net, delay=delay)

def ControlExperiment(hosts=4, test_time=10):
  print("[Info] Starting Control Experiment")
  topo = TopoStar(n=hosts)
  net = Mininet(topo=topo, host=CPULimitedHost, link=TCLink, autoPinCpus=True, controller=OVSController)
  net.start()
  net.pingAll()
  
  # start tests
  savedir = f'./results/{time.strftime("%Y%b%d_%H%M")}'
  atkr = net.getNodeByName('atkr')
  # setup recv
  recv = net.getNodeByName('recv')
  recv.cmd(f'mkdir -p {savedir}')
  recv.cmd(f'iperf -s -p 5001 -w 16m -i 1 > {savedir}/iperf-recv.csv &')
  # setup others
  for i in range(hosts):
    hi = net.getNodeByName(f'h{i}')
    hi.cmd(f'iperf -c {recv.IP()} -p 5001 -i 1 -w 16m -N -Z {"reno"} -t {test_time + 10} -y C > {savedir}/iperf_h{i}.csv &')
  time.sleep(5) # delay start by 5 seconds
  atkr.cmd(f'iperf -c {recv.IP()} -p 5001 -i 1 -w 16m -N -Z {"reno"} -t {test_time} -y C > {savedir}/iperf_atkr.csv')
  time.sleep(5) # delay  end  by 5 seconds
  print("[Info] TEST ENDED, returning to CLI")
  # tests end

  CLI(net)
  net.stop()

if __name__ == '__main__':
  ControlExperiment()
