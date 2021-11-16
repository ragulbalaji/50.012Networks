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

# time (sec), cwnd (MSS)
tcpprobe_csv_header = ['time', 'src_addr_port', 'dst_addr_port', 'bytes', 'next_seq', 'unacknowledged', 'cwnd',
                       'slow_start', 'swnd', 'smoothedRTT', 'rwnd']
# time (YYYYMMDDHHMMSS), interval (S.S-S.S), bps (bps)
iperf_csv_header = ['time', 'src_addr', 'src_port', 'dst_addr' ,'dst_port', 'other', 'interval', 'B_sent', 'bps']

class TreeTopo(Topo):
    def __init__(self, n=10, cpu=None, bw_infra = 1000, bw_atkr=800, bw_recv=500, bw_net=100, delay='100', maxq=None, diff=False):
        """
        1 attacker client + 1 server + 8 normal client

        see topo: {LINK TO COME}

        """
        
        super(TreeTopo, self ).__init__()

        # well
        s0 = self.addSwitch("s0", fail_mode='open')            
        s1 = self.addSwitch("s1", fail_mode='open')
        s2 = self.addSwitch("s2", fail_mode='open')
        s3 = self.addSwitch("s3", fail_mode='open')
        s4 = self.addSwitch("s4", fail_mode='open')
        s5 = self.addSwitch("s5", fail_mode='open')
        s6 = self.addSwitch("s6", fail_mode='open')
        s7 = self.addSwitch("s7", fail_mode='open')
        s8 = self.addSwitch("s8", fail_mode='open')
        s9 = self.addSwitch("s9", fail_mode='open')
        s10 = self.addSwitch("s10", fail_mode='open')

        self.addLink(s0, s1, bw=bw_infra, delay=delay)
        self.addLink(s0, s2, bw=bw_infra, delay=delay)
        self.addLink(s0, s3, bw=bw_infra, delay=delay)
        self.addLink(s0, s4, bw=bw_infra, delay=delay)
        self.addLink(s0, s5, bw=bw_infra, delay=delay)
        self.addLink(s0, s6, bw=bw_infra, delay=delay)
        self.addLink(s0, s7, bw=bw_infra, delay=delay)
        self.addLink(s0, s8, bw=bw_infra, delay=delay)
        self.addLink(s0, s9, bw=bw_infra, delay=delay)
        self.addLink(s0, s10, bw=bw_infra, delay=delay)

        # h1 is attacher, h10 is server that is listening for data
        for i in range(0, n):
            self.addHost("h{}".format(i+1), cpu=cpu)

        self.addLink("h1", "s1", bw=bw_atkr, delay=delay)
        self.addLink("h10", "s10", bw=bw_recv, delay=delay)
        # h2 - h9 are normal hosts
        for i in range(1, n-1):
            self.addLink("h{}".format(i+1), "s{}".format(i+1), bw=bw_net, delay=delay)


class _TreeTopo(Topo):
    def build(self, delay=2):
        """Create the topology by overriding the class parent's method.

        :param  delay   One way propagation delay, delay = RTT / 2. Default is 2ms.
        """
        # The bandwidth (bw) is in Mbps, delay in milliseconds and queue size is in packets
        br_params = dict(
            bw=984,
            delay="{0}ms".format(delay),
            max_queue_size=82 * delay,
            use_htb=True,
        )  # backbone router interface tc params
        ar_params = dict(
            bw=252,
            delay="{0}ms".format(delay),
            max_queue_size=(21 * delay * 20) / 100,
            use_htb=True,
        )  # access router intf tc params
        # TODO: remove queue size from hosts and try.
        hi_params = dict(
            bw=960,
            delay="{0}ms".format(delay),
            max_queue_size=80 * delay,
            use_htb=True,
        )  # host interface tc params

        # Create routers s1 to s5
        s1 = self.addSwitch("s1")
        s2 = self.addSwitch("s2")
        s3 = self.addSwitch("s3")
        s4 = self.addSwitch("s4")
        s5 = self.addSwitch("s5")

        # connect Layer 0 switch to Layer 1 switches
        self.addLink(s1, s2, cls=TCLink, **ar_params)
        self.addLink(s1, s3, cls=TCLink, **ar_params)
        self.addLink(s1, s4, cls=TCLink, **ar_params)
        self.addLink(s1, s5, cls=TCLink, **ar_params)

        depth = 2
        fanout = 4

        # connect Layer 1 switches to Layer 2 hosts
        hosts = {}
        for i in range(fanout ** depth):
            hostname = "h{}".format(i+1)
            hosts[hostname] = self.addHost(hostname)

        # Link the hosts to router
        for i in range(1, 5):
            hostname = "h{}".format(i)
            self.addLink(s2, hosts[hostname], cls=TCLink, **hi_params)

        for i in range(5, 9):
            hostname = "h{}".format(i)
            self.addLink(s3, hosts[hostname], cls=TCLink, **hi_params)

        for i in range(9, 13):
            hostname = "h{}".format(i)
            self.addLink(s4, hosts[hostname], cls=TCLink, **hi_params)

        for i in range(13, 17):
            hostname = "h{}".format(i)
            self.addLink(s5, hosts[hostname], cls=TCLink, **hi_params)


def ControlExperiment(expname='EXP_{i}'.format(i=time.time()), hosts=10, test_time=10, transport_alg='-Z reno'):
    n = hosts
    topo = TreeTopo(n=hosts)
    net = Mininet(topo=topo, host=CPULimitedHost, link=TCLink, autoPinCpus=True, controller=OVSController)
    net.start()
    net.pingAll()

    print("[Info] Starting Control Experiment")
    # start tests
    savedir = './results/{expname}/{h}'.format(expname=expname, h=transport_alg.replace(" ","_"))

    # setup recv
    recv = net.getNodeByName("h{}".format(n))
    recv.cmd('mkdir -p {savedir}'.format(savedir=savedir))
    recv.cmd('iperf -s -p 5001 -w 16m -i 1 -N {transport_alg} > {savedir}/iperf-recv.csv &'
        .format(transport_alg=transport_alg, savedir=savedir))
    
    # setup others
    for i in range(1, n-1):
        hi = net.getNodeByName('h{i}'.format(i=i+1))
        hi.cmd('iperf -c {j} -p 5001 -i 1 -w 16m -N {transport_alg} -t {a} -y C > {savedir}/iperf_h{i}.csv &'
            .format(j=recv.IP(), transport_alg=transport_alg, a=test_time + 10,savedir = savedir, i=i))

    atkr = net.getNodeByName("h1")
    atkr.cmd('iperf -c {a} -p 5001 -i 1 -w 16m -N {transport_alg} -t {test_time} -y C > {savedir}/iperf_atkr.csv'
        .format(a=recv.IP(), transport_alg=transport_alg, test_time=test_time, savedir=savedir))

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