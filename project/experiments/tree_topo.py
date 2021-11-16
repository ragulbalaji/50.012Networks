import argparse
import csv
import subprocess
from datetime import datetime
from time import mktime, sleep

import matplotlib

matplotlib.use("Agg")  # Force matplotlib to not use any Xwindows backend.
import matplotlib.pyplot as plt
from mininet.link import TCLink
from mininet.log import info, lg, setLogLevel
from mininet.net import Mininet
from mininet.topo import Topo
from mininet.util import dumpNodeConnections, quietRun

##
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
        # br_params = dict(
        #     bw=984,
        #     delay="{0}ms".format(delay),
        #     max_queue_size=82 * delay,
        #     use_htb=True,
        # )  # backbone router interface tc params
        ar_params = dict(
            bw=1000,
            delay="0ms",
            max_queue_size=(21 * delay * 20) / 100,
            use_htb=True,
        )  # access router intf tc params
        # TODO: remove queue size from hosts and try.
        hi_params = dict(
            bw=500,
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
            hostname = f"h{i+1}"
            hosts[hostname] = self.addHost(hostname)

        # Link the hosts to router
        for i in range(1, 5):
            hostname = f"h{i}"
            self.addLink(s2, hosts[hostname], cls=TCLink, **hi_params)

        for i in range(5, 9):
            hostname = f"h{i}"
            self.addLink(s3, hosts[hostname], cls=TCLink, **hi_params)

        for i in range(9, 13):
            hostname = f"h{i}"
            self.addLink(s4, hosts[hostname], cls=TCLink, **hi_params)

        for i in range(13, 17):
            hostname = f"h{i}"
            self.addLink(s5, hosts[hostname], cls=TCLink, **hi_params)


def clean_tcpprobe_procs():
    """Serach and kill any running tcpprobe processes."""
    # Search and kill any running tcpprobe procs
    print("Killing any running tcpprobe processes...")
    procs = quietRun("pgrep -f /proc/net/tcpprobe").split()

    for proc in procs:
        output = quietRun("sudo kill -KILL {0}".format(proc.rstrip()))
        if output != "":
            print(output)


def start_tcpprobe(filename):
    """Install tcp_pobe module and dump to file.

    :param  filename    Path to the file where to dump the tcpprobe data.
    """
    print("Unloading tcp_probe module...")
    clean_tcpprobe_procs()

    # Unload the module
    output = quietRun("sudo rmmod tcp_probe")
    if output != "":
        print(output.rstrip())

    print("Loading tcp_probe module...")
    # TODO: why do we use the full=1 arg? Do not filter to port=5001, but use the IP of the sender instead.
    output = quietRun("sudo modprobe tcp_probe full=1")
    if output != "":
        print(output.rstrip())

    print("Saving tcpprobe output to: {0}".format(filename))
    return subprocess.Popen(
        "sudo cat /proc/net/tcpprobe > {0}".format(filename), shell=True
    )


def tcp_tests(algs, delays, iperf_runtime, iperf_delayed_start):
    """Run the TCP congestion control tests.

    :param  algs                List of strings with the TCP congestion control algorithms to test.
    :param  delays              List of integers with the one-directional propagation delays to test.
    :param  iperf_runtime       Time to run the iperf clients in seconds.
    :param  iperf_delayed_start Time to wait before starting the second iperf client in seconds.
    """
    print(
        "*** Tests settings:\n - Algorithms: {0}\n - delays: {1}\n - Iperf runtime: {2}\n - Iperf delayed start: {3}".format(
            algs, delays, iperf_runtime, iperf_delayed_start
        )
    )
    for alg in algs:
        print("*** Starting test for algorithm={0}...".format(alg))
        for delay in delays:
            print("*** Starting test for delay={0}ms...".format(delay))

            # Start tcp probe process
            print("*** Starting tcpprobe recording...")
            tcpprobe_proc = start_tcpprobe("tcpprobe_{0}_{1}ms.txt".format(alg, delay))

            # Create the net topology
            print("*** Creating topology for delay={0}ms...".format(delay))
            topo = TreeTopo(delay=delay)

            # Start mininet
            net = Mininet(topo)
            net.start()

            # Get the hosts
            hosts = {}
            host_addrs = {}
            for i in range(1, 17):
                hostname = f"h{i}"
                hosts[hostname] = net.get(hostname)
                host_addrs[hostname] = hosts[hostname].IP()

            print("Host addrs: {0}".format(host_addrs))

            # Run iperf
            popens = dict()
            print("*** Starting iperf servers h2 and h4...")

            popens["h16"] = hosts["h16"].popen(
                ["iperf", "-s", "-p", "5001", "-w", "16m"]
            )

            # Client options:
            # -i: interval between reports set to 1sec
            # -l: length read/write buffer set to default 8KB
            # -w: TCP window size (socket buffer size) set to 16MB
            # -M: TCP MSS (MTU-40B) set to 1460B for an MTU of 1500B
            # -N: disable Nagle's Alg
            # -Z: select TCP Congestion Control alg
            # -t: transmission time
            # -f: format set to kilobits
            # -y: report style set to CSV
            # TODO: run iperfs without the -y C to see if we get errors setting the MSS. Use sudo?
            print("*** Starting iperf client h1...")
            for i in range(2, 10):
                hostname = f"h{i}"
                _host = hosts[hostname]
                _server_addr = host_addrs["h16"]
                _client_sending_rate = "50M"

                popens[hostname] = _host.popen(
                    f"iperf -c {_server_addr} -p 5001 -b {_client_sending_rate} -i 1 -w 16m -M 1460 -N -Z {alg} -t {iperf_runtime} -y C > iperf_{alg}_{hostname}_{delay}ms.txt",
                    shell=True,
                )

            # Delay before starting the second iperf proc
            # print("*** Waiting for {0}sec...".format(iperf_delayed_start))
            # sleep(iperf_delayed_start)

            print("*** Starting iperf attacking client h1...")
            attacker_hostname = "h1"
            attacker_host = hosts[attacker_hostname]
            _aggressive_sending_rate = "1000M"

            popens[attacker_hostname] = attacker_host.popen(
                f"iperf -c {_server_addr} -p 5001 -b {_aggressive_sending_rate} -i 1 -w 16m -M 1460 -N -Z {alg} -t {iperf_runtime} -y C > iperf_{alg}_{attacker_hostname}_{delay}ms.txt",
                shell=True,
            )

            # Wait for clients to finish sending data
            print(f"*** Waiting {iperf_runtime}sec for iperf clients to finish...")
            for i in range(1, 10):
                hostname = f"h{i}"
                popens[hostname].wait()

            # Terminate the servers and tcpprobe subprocesses
            print("*** Terminate the iperf servers and tcpprobe processes...")
            popens["h16"].terminate()
            tcpprobe_proc.terminate()

            popens["h16"].wait()
            tcpprobe_proc.wait()

            clean_tcpprobe_procs()

            print("*** Stopping test...")
            net.stop()

            # print("*** Processing data...")
            # data_cwnd = parse_tcpprobe_data(alg, delay, host_addrs)
            # data_fairness = parse_iperf_data(alg, delay, host_addrs)

            # draw_cwnd_plot(
            #     data_cwnd["h1"]["time"],
            #     data_cwnd["h1"]["cwnd"],
            #     data_cwnd["h3"]["time"],
            #     data_cwnd["h3"]["cwnd"],
            #     alg,
            #     delay,
            # )
            # draw_fairness_plot(
            #     data_fairness["h1"]["time"],
            #     data_fairness["h1"]["Mbps"],
            #     data_fairness["h3"]["time"],
            #     data_fairness["h3"]["Mbps"],
            #     alg,
            #     delay,
            # )
