from mininet.topo import Topo
from mininet.node import CPULimitedHost
from mininet.link import TCLink
from mininet.net import Mininet
from mininet.cli import CLI
from mininet.node import OVSController

# from subprocess import Popen, PIPE
# from multiprocessing import Process
# from argparse import ArgumentParser

import time
import os

class TopoTree(Topo):
    def __init__(self, n=4, cpu=None, bw_atkr=1000, bw_recv=500, bw_net=100, delay='100', maxq=None, diff=False):
        super(TopoTree, self ).__init__()

        s1 = self.addSwitch("s1", fail_mode='open')
        s2 = self.addSwitch("s2", fail_mode='open')
        s3 = self.addSwitch("s3", fail_mode='open')
        s4 = self.addSwitch("s4", fail_mode='open')
        s5 = self.addSwitch("s5", fail_mode='open')

        self.addLink(s1, s2, bw=bw_atkr, delay=delay)
        self.addLink(s1, s3, bw=bw_net, delay=delay)
        self.addLink(s1, s4, bw=bw_net, delay=delay)
        self.addLink(s1, s5, bw=bw_recv, delay=delay)

        self.addHost('atkr', cpu=cpu)
        self.addHost('recv', cpu=cpu)
        self.addLink('atkr', 's2', bw=bw_atkr, delay=delay)
        self.addLink('recv', 's5', bw=bw_recv, delay=delay)

        self.addHost("h0", cpu=cpu)
        self.addHost("h1", cpu=cpu)

        self.addLink('h0', 's3', bw=bw_net, delay=delay)
        self.addLink('h1', 's4', bw=bw_net, delay=delay)


def ControlExperiment(expname='EXP_{i}'.format(i=time.time()), hosts=4, test_time=10, transport_alg='-Z reno'):
    topo = TopoTree(n=hosts)
    net = Mininet(topo=topo, host=CPULimitedHost, link=TCLink, autoPinCpus=True, controller=OVSController)
    net.start()
    net.pingAll()

    print("[Info] Starting Control Experiment")
    # start tests
    savedir = './results/{expname}/{h}'.format(expname=expname, h=transport_alg.replace(" ","_"))

    # setup recv
    recv = net.getNodeByName('recv')
    recv.cmd('mkdir -p {savedir}'.format(savedir=savedir))
    recv.cmd('iperf -s -p 5001 -w 16m -i 1 -N {transport_alg} > {savedir}/iperf-recv.csv &'.format(transport_alg=transport_alg, savedir=savedir))
    
    # setup others
    for i in range(0, 2):
        hi = net.getNodeByName('h{i}'.format(i=i))
        hi.cmd('iperf -c {j} -p 5001 -i 1 -w 16m -N {transport_alg} -t {a} -y C > {savedir}/iperf_h{i}.csv &'
        .format(j=recv.IP(), transport_alg=transport_alg, a=test_time + 10,savedir = savedir, i=i))
    # time.sleep(5) # delay start by 5 seconds

    atkr = net.getNodeByName('atkr')
    atkr.cmd('iperf -c {a} -p 5001 -i 1 -w 16m -N {transport_alg} -t {test_time} -y C > {savedir}/iperf_atkr.csv'
        .format(a=recv.IP(), transport_alg=transport_alg, test_time=test_time, savedir=savedir))
    # time.sleep(5) # delay  end  by 5 seconds
    print("[Info] Test Ended")
    # tests end

    # CLI(net) # comment out when running main test
    net.stop()


if __name__ == '__main__':
    ExperimentName = time.strftime("%Y%b%d_%H%M%S")
    TransportAlgos = ['-Z reno', '-Z cubic', '-u']
    for algo in TransportAlgos:
        print('[Test] Running {ExperimentName} with {algo} CCalgo...'.format(ExperimentName=ExperimentName, algo=algo))
        ControlExperiment(expname=ExperimentName, transport_alg=algo)
    os.system('zip ./results/{ExperimentName}.zip -r ./results/{ExperimentName}/'.format(ExperimentName=ExperimentName))
    os.system('rm -rf ./results/{ExperimentName}'.format(ExperimentName=ExperimentName)) # remove small files so git doesnt get angry
