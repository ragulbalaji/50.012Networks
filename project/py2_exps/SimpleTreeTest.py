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
    def __init__(self, n=16, cpu=None, 
        bw_infra=1000, bw_atkr=800, bw_recv=500, bw_net=100, delay='100', maxq=None, diff=False):
        """
        1 attacker client + 1 server + 8 normal client

        see topo here: https://drive.google.com/file/d/1noPCEP8JwEg37yzA0JoBRk9u4TXJXHhx/view?usp=sharing
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
        s11 = self.addSwitch("s11", fail_mode='open')
        s12 = self.addSwitch("s12", fail_mode='open')
        s13 = self.addSwitch("s13", fail_mode='open')
        s14 = self.addSwitch("s14", fail_mode='open')
        s15 = self.addSwitch("s15", fail_mode='open')
        s16 = self.addSwitch("s16", fail_mode='open')

        s01 = self.addSwitch("s01", fail_mode='open')
        s02 = self.addSwitch("s02", fail_mode='open') 
        s03 = self.addSwitch("s03", fail_mode='open') 
        s04 = self.addSwitch("s04", fail_mode='open')      

        self.addLink(s0, s01, bw=bw_infra, delay=delay)  
        self.addLink(s0, s02, bw=bw_infra, delay=delay)  
        self.addLink(s0, s03, bw=bw_infra, delay=delay)  
        self.addLink(s0, s04, bw=bw_infra, delay=delay)  

        self.addLink(s01, s1, bw=bw_infra, delay=delay)
        self.addLink(s01, s2, bw=bw_infra, delay=delay)
        self.addLink(s01, s3, bw=bw_infra, delay=delay)
        self.addLink(s01, s4, bw=bw_infra, delay=delay)

        self.addLink(s02, s5, bw=bw_infra, delay=delay)
        self.addLink(s02, s6, bw=bw_infra, delay=delay)
        self.addLink(s02, s7, bw=bw_infra, delay=delay)
        self.addLink(s02, s8, bw=bw_infra, delay=delay)

        self.addLink(s03, s9, bw=bw_infra, delay=delay)
        self.addLink(s03, s10, bw=bw_infra, delay=delay)
        self.addLink(s03, s11, bw=bw_infra, delay=delay)
        self.addLink(s03, s12, bw=bw_infra, delay=delay)

        self.addLink(s04, s13, bw=bw_infra, delay=delay)
        self.addLink(s04, s14, bw=bw_infra, delay=delay)
        self.addLink(s04, s15, bw=bw_infra, delay=delay)
        self.addLink(s04, s16, bw=bw_infra, delay=delay)

        # h1 is attacker, h10 is server that is listening for data
        for i in range(0, n):
            self.addHost("h{}".format(i+1), cpu=cpu)

        self.addLink("h1", "s1", bw=bw_atkr, delay=delay)
        self.addLink("h16", "s16", bw=bw_recv, delay=delay)

        # h2 - h9 are normal hosts, the rest of the hosts are idle
        for i in range(1, n-1):
            self.addLink("h{}".format(i+1), "s{}".format(i+1), bw=bw_net, delay=delay)


class TopoStar(Topo):
    def __init__(self, n=8, cpu=None, bw_infra=1000, bw_atkr=10, bw_recv=10, bw_net=10, delay='100', maxq=None, diff=False):
        super(TopoStar, self ).__init__()

        self.addSwitch('s0', fail_mode='open')
        self.addSwitch('s98', fail_mode='open')
        self.addSwitch('s99', fail_mode='open')

        self.addHost('atkr', cpu=cpu)
        self.addHost('recv', cpu=cpu)
        
        self.addLink('atkr', 's98', bw=bw_atkr, delay=delay)
        self.addLink('recv', 's99', bw=bw_recv, delay=delay)
        self.addLink('s0', 's98', bw=bw_infra, delay=delay)
        self.addLink('s0', 's99', bw=bw_infra, delay=delay)

        for i in range(1, n): 
            self.addHost('h{i}'.format(i=i), cpu=cpu)
            self.addSwitch('s{i}'.format(i=i), fail_mode='open')
            self.addLink('h{i}'.format(i=i), 's{i}'.format(i=i), bw=bw_net, delay=delay)
            self.addLink('s0', 's{i}'.format(i=i), bw=bw_net, delay=delay)


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


def ControlExperiment(expname='EXP_{i}'.format(i=time.time()), hosts=16, test_time=10, transport_alg='-Z reno',
    bw_infra=1000, bw_atkr=800, bw_recv=500, bw_net=100):
    n = hosts
    topo = TopoStar(n=n, bw_infra=bw_infra, bw_atkr=bw_atkr, bw_recv=bw_recv, bw_net=bw_net)
    net = Mininet(topo=topo, host=CPULimitedHost, link=TCLink, autoPinCpus=True, controller=OVSController)
    net.start()
    net.pingAll()

    print("[Info] Starting Control Experiment")
    # start tests
    savedir = './results/{expname}_{h}'.format(expname=expname, h=transport_alg.replace(" ","_"))

    # setup recv
    recv = net.getNodeByName('recv')
    recv.cmd('mkdir -p {savedir}'.format(savedir=savedir))
    recv.cmd('iperf -s -p 5001 -w 64K -i 1 -N {transport_alg} > {savedir}/iperf-recv.csv &'
        .format(transport_alg=transport_alg, savedir=savedir))
    
    # setup others
    for i in range(1, n):
        hi = net.getNodeByName('h{i}'.format(i=i))
        hi.cmd('iperf -c {j} -p 5001 -i 1 -w 64K -N {transport_alg} -t {a} -y C > {savedir}/iperf_h{i}.csv &'
            .format(j=recv.IP(), transport_alg=transport_alg, a=test_time + 10,savedir = savedir, i=i))

    atkr = net.getNodeByName('atkr')
    atkr.cmd('iperf -c {a} -p 5001 -i 1 -w 64K -N {transport_alg} -t {test_time} -y C > {savedir}/iperf_atkr.csv'
        .format(a=recv.IP(), transport_alg=transport_alg, test_time=test_time, savedir=savedir))

    print("[Info] Test Ended")
    # tests end

    # CLI(net) # comment out when running main test
    net.stop()


if __name__ == '__main__':
    timenow = time.strftime("%Y%b%d_%H%M%S")
    TransportAlgos = ['-Z reno', '-Z cubic', '-u']
    # [bw_infra, bw_atkr, bw_recv, bw_net]
    link_sizes_v2 = [
        [500, 100, 250, 100],
        [500, 200, 250, 100],
        [500, 300, 250, 100],
        [500, 400, 250, 100],
        [500, 500, 250, 100],
        [500, 600, 250, 100],
        [500, 700, 250, 100],
        [500, 800, 250, 100],
        [500, 900, 250, 100],
        [500, 1000, 250, 100],
        [500, 100, 500, 100],
        [500, 200, 500, 100],
        [500, 300, 500, 100],
        [500, 400, 500, 100],
        [500, 500, 500, 100],
        [500, 600, 500, 100],
        [500, 700, 500, 100],
        [500, 800, 500, 100],
        [500, 900, 500, 100],
        [500, 1000, 500, 100],
        [500, 100, 500, 50],
        [500, 200, 500, 50],
        [500, 300, 500, 50],
        [500, 400, 500, 50],
        [500, 500, 500, 50],
        [500, 600, 500, 50],
        [500, 700, 500, 50],
        [500, 800, 500, 50],
        [500, 900, 500, 50],
        [500, 1000, 500, 50],
    ]

    link_sizes_v3 = [
        [500, 100, 500, 10],
        [500, 200, 500, 10],
        [500, 300, 500, 10],
        [500, 400, 500, 10],
        [500, 500, 500, 10],
        [500, 600, 500, 10],
        [500, 700, 500, 10],
        [500, 800, 500, 10],
        [500, 900, 500, 10],
        [500, 1000, 500, 10],
    ]

    link_sizes = [
        [500, 100, 500, 25],
        [500, 200, 500, 25],
        [500, 300, 500, 25],
        [500, 400, 500, 25],
        [500, 500, 500, 25],
        [500, 600, 500, 25],
        [500, 700, 500, 25],
        [500, 800, 500, 25],
        [500, 900, 500, 25],
        [500, 1000, 500, 25],

        [500, 100, 1000, 25],
        [500, 200, 1000, 25],
        [500, 300, 1000, 25],
        [500, 400, 1000, 25],
        [500, 500, 1000, 25],
        [500, 600, 1000, 25],
        [500, 700, 1000, 25],
        [500, 800, 1000, 25],
        [500, 900, 1000, 25],
        [500, 1000, 1000, 25],

        [500, 100, 1000, 10],
        [500, 200, 1000, 10],
        [500, 300, 1000, 10],
        [500, 400, 1000, 10],
        [500, 500, 1000, 10],
        [500, 600, 1000, 10],
        [500, 700, 1000, 10],
        [500, 800, 1000, 10],
        [500, 900, 1000, 10],
        [500, 1000, 1000, 10],
    ]

    for links in link_sizes:
        for algo in TransportAlgos:
            bw_infra, bw_atkr, bw_recv, bw_net = links[0], links[1], links[2], links[3]
            links_str = []
            for link in links:
                links_str.append(str(link))
            ExperimentName = timenow + "_" + algo.replace(" ", "_") + "_" + "_".join(links_str)
            print('[Test] Running {ExperimentName} with {algo} CCalgo...'.format(ExperimentName=ExperimentName, algo=algo))
            ControlExperiment(expname=ExperimentName, hosts=8, transport_alg=algo, bw_infra=bw_infra, bw_atkr=bw_atkr, bw_recv=bw_recv, bw_net=bw_net)     
	        
            # os.system('zip ./results/{ExperimentName}.zip -r ./results/{ExperimentName}/'
            #     .format(ExperimentName=ExperimentName))
    	    # os.system('rm -rf ./results/{ExperimentName}'
            #     .format(ExperimentName=ExperimentName)) # remove small files so git doesnt get angry
