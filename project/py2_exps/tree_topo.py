##
# Mininet code to compare 4 different TCP congestion control algorithms.
#

import argparse
import csv
import subprocess
from datetime import datetime
from time import mktime, sleep
import os, time

#import matplotlib

#matplotlib.use("Agg")  # Force matplotlib to not use any Xwindows backend.
#import matplotlib.pyplot as plt
# from mininet.link import TCLink
from mininet.log import info, lg, setLogLevel
from mininet.net import Mininet
from mininet.topo import Topo
from mininet.util import dumpNodeConnections, quietRun
from mininet.node import CPULimitedHost, OVSController
from mininet.link import TCLink


# Globals
##########
# time (sec), cwnd (MSS)
tcpprobe_csv_header = [
    "time",
    "src_addr_port",
    "dst_addr_port",
    "bytes",
    "next_seq",
    "unacknowledged",
    "cwnd",
    "slow_start",
    "swnd",
    "smoothedRTT",
    "rwnd",
]
# time (YYYYMMDDHHMMSS), interval (S.S-S.S), bps (bps)
iperf_csv_header = [
    "time",
    "src_addr",
    "src_port",
    "dst_addr",
    "dst_port",
    "other",
    "interval",
    "B_sent",
    "bps",
]


class SimpleTreeTopo(Topo):
    """Simple tree topology.

    3 switches, 4 hosts

           s1
           |
        --------
        |      |
        s2     s3
        |      |
    -------  -------
    |     |  |      |
    h1    h2 h3    h4


    """

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
            delay="0ms",
            max_queue_size=(21 * delay * 20) / 100,
            use_htb=True,
        )  # access router intf tc params
        # TODO: remove queue size from hosts and try.
        hi_params = dict(
            bw=960,
            delay="0ms",
            max_queue_size=80 * delay,
            use_htb=True,
        )  # host interface tc params

        # Create routers s1 to s5
        s1 = self.addSwitch("s1")
        s2 = self.addSwitch("s2")
        s3 = self.addSwitch("s3")

        # connect Layer 0 switch to Layer 1 switches
        self.addLink(s1, s2, cls=TCLink, **ar_params)
        self.addLink(s1, s3, cls=TCLink, **ar_params)

        depth = 2
        fanout = 4

        # connect Layer 1 switches to Layer 2 hosts
        h1 = self.addHost("h1")
        h2 = self.addHost("h2")
        h3 = self.addHost("h3")
        h4 = self.addHost("h4")

        # Link the hosts to router
        self.addLink(s2, h1, cls=TCLink, **hi_params)
        self.addLink(s2, h2, cls=TCLink, **hi_params)

        self.addLink(s3, h3, cls=TCLink, **hi_params)
        self.addLink(s3, h4, cls=TCLink, **hi_params)


class TreeTopo(Topo):
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
            delay="0ms",
            max_queue_size=(21 * delay * 20) / 100,
            use_htb=True,
        )  # access router intf tc params
        # TODO: remove queue size from hosts and try.
        hi_params = dict(
            bw=960,
            delay="0ms",
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


def ControlExperiment(expname="EXP_%s" % time.time(), hosts=8, test_time=10, transport_alg='-Z reno'):
    # xpname=f'EXP_{time.time()}'
    topo = SimpleTreeTopo()
    net = Mininet(topo=topo, host=CPULimitedHost, link=TCLink, autoPinCpus=True,
                  controller=OVSController)
    net.start()
    net.pingAll()

    print("[Info] Starting Control Experiment")
    # start tests
    savedir = './results/{0}/{1}'.format(expname, transport_alg.replace(" ", "_"))
    print(savedir)
    os.system("mkdir -p {}".format(savedir))

    for i in range(1, 2):
        hi = net.getNodeByName("h%s" % i)
        hi.cmd('iperf -s -p 5001 -w 16m -i 1 -N {0} > {1}/iperf-recv.csv &'.format(transport_alg, savedir))

    # setup others
    for i in range(2, 4):
        hi = net.getNodeByName("h%s" % i)
        hi.cmd('iperf -c {0} -p 5001 -i 1 -w 16m -N {1} -t {2} -y C > {3}/iperf_h{4}.csv &'
               .format(hi.IP(), transport_alg, test_time + 10, savedir, i))
    time.sleep(5)  # delay start by 5 seconds
    for i in range(4, 5):
        hi = net.getNodeByName("h%s" % i)
        hi.cmd('iperf -c {0} -p 5001 -i 1 -w 16m -N {1} -t {2} -y C > {3}/iperf_h{4}.csv &'
               .format(hi.IP(), transport_alg, test_time + 10, savedir, i))

    time.sleep(5)  # delay end by 5 seconds
    print("[Info] Test Ended")
    # tests end

    # CLI(net) # comment out when running main test
    net.stop()


if __name__ == '__main__':
    ExperimentName = time.strftime("%Y%b%d_%H%M%S")
    TransportAlgos = ['-Z reno', '-Z cubic', '-u']
    print(ExperimentName)
    for algo in TransportAlgos:
        print('[Test] Running {0} with {1} algo...'.format(ExperimentName, algo))
        ControlExperiment(expname=ExperimentName, transport_alg=algo)
    # os.system('zip ./results/{0}.zip -r ./results/{1}/'.format(ExperimentName, ExperimentName))
    # os.system('rm -rf ./results/{}'.format(ExperimentName))  # remove small files so git doesnt get angry


