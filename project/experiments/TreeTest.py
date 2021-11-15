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
    def __init__(self, n=10, cpu=None, bw_atkr=10, bw_recv=10, bw_net=10, delay='100', maxq=None, diff=False):
        """

            receiver + 2 normal
                |
            switch
                |
            --------------
            |            |
attacker + 2 normal      4 normal

        :param n:
        :param cpu:
        :param bw_atkr:
        :param bw_recv:
        :param bw_net:
        :param delay:
        :param maxq:
        :param diff:
        """
        super(TopoTree, self).__init__()


        # receiver node
        self.addSwitch('s0', fail_mode='open')
        self.addHost('recv', cpu=cpu)
        self.addLink('recv', 's0', bw=bw_recv, delay=delay)
        for i in range(0, (n//3)-1, 1):
            self.addHost("h%s" % i, cpu=cpu)
            self.addLink("h%s" % i, 's0', bw=bw_net, delay=delay)
            # TODO: change print to log
            print("added normal host %s", i)

        # attacker node
        self.addSwitch('s1', fail_mode='open')
        self.addHost('atkr', cpu=cpu)
        self.addLink('atkr', 's1', bw=bw_atkr, delay=delay)
        for i in range((n//3)-1, 2*((n//3)-1), 1):
            self.addHost("h%s" % i, cpu=cpu)
            self.addLink("h%s" % i, 's1', bw=bw_net, delay=delay)
            print("added normal host %s", i)

        # normal node - 4 hosts
        self.addSwitch('s2', fail_mode='open')
        self.addLink('norm', 's2', bw=bw_atkr, delay=delay)
        for i in range(2*((n//3)-1), n-2, 1):
            self.addHost("h%s" % i, cpu=cpu)
            self.addLink("h%s" % i, 's2', bw=bw_net, delay=delay)
            print("added normal host %s", i)

        for i in range(n):
            # self.addHost(f'h{i}', cpu=cpu)
            self.addHost("h%s" % i, cpu=cpu)
        for i in range(n):
            # self.addLink(f'h{i}', 's0', bw=bw_net, delay=delay)
            self.addLink("h%s" % i, 's0', bw=bw_net, delay=delay)


def ControlExperiment(expname="EXP_%s" % time.time(), hosts=8, test_time=10, transport_alg='-Z reno'):
    # xpname=f'EXP_{time.time()}'
    topo = TopoTree(n=hosts)
    net = Mininet(topo=topo, host=CPULimitedHost, link=TCLink, autoPinCpus=True, controller=OVSController)
    net.start()
    net.pingAll()

    print("[Info] Starting Control Experiment")
    # start tests
    savedir = './results/{0}/{1}'.format(expname, transport_alg.replace(" ", "_"))
    atkr = net.getNodeByName('atkr')
    # setup recv
    recv = net.getNodeByName('recv')
    recv.cmd('mkdir -p {0}'.format(savedir))
    recv.cmd('iperf -s -p 5001 -w 16m -i 1 -N {0} > {1}/iperf-recv.csv &'.format(transport_alg, savedir))
    # the other 2 recv hosts - hardcoded, change later
    for i in range(0, 2):
        hi = net.getNodeByName("h%s" % i)
        hi.cmd('iperf -s -p 5001 -w 16m -i 1 -N {0} > {1}/iperf-recv.csv &'.format(transport_alg, savedir))

    # setup others
    for i in range(2, hosts):
        hi = net.getNodeByName("h%s" % i)
        hi.cmd('iperf -c {0} -p 5001 -i 1 -w 16m -b 1M -N {1} -t {2} -y C > {3}/iperf_h{4}.csv &'
               .format(recv.IP(), transport_alg, test_time + 10, savedir, i))
    time.sleep(5)  # delay start by 5 seconds
    attacker_parallel_connections = 2
    atkr.cmd('iperf -c {0} -p 5001 -i 1 -w 256m -b 128M -N {1} -t {2} -y C > {3}/iperf_atkr.csv'
             .format(recv.IP(), transport_alg, test_time, savedir))
    time.sleep(5)  # delay end by 5 seconds
    print("[Info] Test Ended")
    # tests end

    # CLI(net) # comment out when running main test
    net.stop()


if __name__ == '__main__':
    ExperimentName = time.strftime("%Y%b%d_%H%M%S")
    TransportAlgos = ['-Z reno', '-Z cubic', '-u']
    for algo in TransportAlgos:
        print('[Test] Running {0} with {1} algo...'.format(ExperimentName, algo))
        ControlExperiment(expname=ExperimentName, transport_alg=algo)
    os.system('zip ./results/{0}.zip -r ./results/{1}/'.format(ExperimentName, ExperimentName))
    os.system('rm -rf ./results/{}'.format(ExperimentName))  # remove small files so git doesnt get angry
