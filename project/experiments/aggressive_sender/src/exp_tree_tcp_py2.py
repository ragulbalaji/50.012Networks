from __future__ import print_function

import argparse
import os
import subprocess

import mininet.log
import mininet.net

# from mininet.link import TCLink
from mininet.log import setLogLevel
from mininet.net import Mininet

# from mininet.topo import Topo
# from mininet.util import dumpNodeConnections, quietRun
from topo_tree_py2 import TreeTopoTCP, TreeTopoTCPv2
from utils import clean_tcpprobe_procs, start_tcpprobe

output_dir = "out"


def tcp_tests(
    algs=["reno"],
    delays=[2],
    iperf_runtime=10,
    bw_infra=100,
    bw_server=10,
    bw_user=10,
    bw_attack=500,
    mix_protocol=False,
    normal_window_size="32K",
    attacker_window_size="1M",
):
    """Run the TCP congestion control tests.

    :param  algs                List of strings with the TCP congestion control algorithms to test.
    :param  delays              List of integers with the one-directional propagation delays to test.
    :param  iperf_runtime       Time to run the iperf clients in seconds.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    # print(
    #     f"*** Tests settings:\n - Algorithms: {algs}\n - delays: {delays}\n - Iperf runtime: {iperf_runtime}"
    # )
    for alg in algs:
        # print(f"*** Starting test for algorithm={alg}...")
        if alg == "cubic":
            attacker_algo = "reno" if mix_protocol else alg
        elif alg == "reno":
            attacker_algo = "cubic" if mix_protocol else alg

        for delay in delays:
            # print(f"*** Starting test for delay={delay}ms...")

            # Start tcp probe process
            print("*** Starting tcpprobe recording...")
            tcpprobe_proc = start_tcpprobe(
                "{}/tcpprobe_{}_{}ms.txt".format(output_dir, alg, delay)
            )

            # Create the net topology
            # print(f"*** Creating topology for delay={delay}ms...")
            topo = TreeTopoTCPv2(
                delay=delay,
                bw_infra=bw_infra,
                bw_user=bw_user,
                bw_attack=bw_attack,
                bw_server=bw_server,
            )

            # Start mininet
            net = Mininet(topo)
            net.start()

            # Get the hosts
            hosts = {}
            host_addrs = {}
            for i in range(1, 11):
                hostname = "h{}".format(i)
                hosts[hostname] = net.get(hostname)
                host_addrs[hostname] = hosts[hostname].IP()

            print("Host addrs: {0}".format(host_addrs))

            # Run iperf
            popens = dict()

            print("*** Starting server h10...")
            popens["h10"] = hosts["h10"].popen(
                [
                    "iperf",
                    "-s",
                    "-p",
                    "5001",
                    "-w",
                    normal_window_size,
                    "-y",
                    "C",
                    ">",
                    "{}/iperf_{}_server_{}ms.txt".format(output_dir, alg, delay),
                ],
                shell=True,
            )

            # Client options:
            # -i: interval between reports set to 1sec
            # -l: length read/write buffer set to default 8KB
            # -w: TCP window size (socket buffer size) set to 64K
            # -M: TCP MSS (MTU-40B) set to 1460B for an MTU of 1500B
            # -N: disable Nagle's Alg
            # -Z: select TCP Congestion Control alg
            # -t: transmission time
            # -f: format set to kilobits
            # -y: report style set to CSV

            print("*** Starting iperf clients...")
            for i in range(2, 10):
                # print(f"*** Starting normal client h{i}...")
                hostname = "h{}".format(i)
                _host = hosts[hostname]
                _server_addr = host_addrs["h10"]
                popens[hostname] = _host.popen(
                    "iperf -c {} -p 5001 -i 1 -w {} -M 1460 -N -Z {} -t {} -y C > {}/iperf_{}_{}_{}ms.txt".format(
                        _server_addr,
                        normal_window_size,
                        alg,
                        iperf_runtime,
                        output_dir,
                        alg,
                        hostname,
                        delay,
                    ),
                    shell=True,
                )

            print("*** Starting attacking client h1...")
            attacker_hostname = "h1"
            attacker_host = hosts[attacker_hostname]

            popens[attacker_hostname] = attacker_host.popen(
                "iperf -c {} -p 5001 -i 1 -w {} -M 1460 -N -Z {} -t {} -y C > {}/iperf_{}_{}_{}ms.txt".format(
                    _server_addr,
                    attacker_window_size,
                    attacker_algo,
                    iperf_runtime,
                    output_dir,
                    alg,  # not changing filename for graphing convinience
                    attacker_hostname,
                    delay,
                ),
                shell=True,
            )

            # print(f"*** Waiting {iperf_runtime}sec for iperf clients to finish...")
            for i in range(1, 10):
                hostname = "h{}".format(i)
                popens[hostname].wait()

            print("*** Terminate the iperf servers and tcpprobe processes...")
            popens["h10"].terminate()
            tcpprobe_proc.terminate()

            popens["h10"].wait()
            tcpprobe_proc.wait()

            print("*** Cleaning tcp probe processes...")
            clean_tcpprobe_procs()

            print("*** Stopping test...")
            net.stop()


def main():
    """Run the tests."""
    setLogLevel("info")
    algs = ["reno", "cubic"]
    delays = [2, 50]
    iperf_runtime = 30

    bw_infra = 500
    bw_servers = [100, 500]
    bw_user = 10
    bw_attack = [10, 20, 800]
    mix_protocols = [False, True]
    normal_window_size = "128K"
    attacker_window_sizes = ["128K", "1M"]

    for bw_server in bw_servers:
        for mix_protocol in mix_protocols:
            for attacker_window_size in attacker_window_sizes:
                for bw_attack_i in bw_attack:
                    tcp_tests(
                        algs=algs,
                        delays=delays,
                        iperf_runtime=iperf_runtime,
                        bw_infra=bw_infra,
                        bw_server=bw_server,
                        bw_user=bw_user,
                        bw_attack=bw_attack_i,
                        mix_protocol=mix_protocol,
                        normal_window_size=normal_window_size,
                        attacker_window_size=attacker_window_size,
                    )

                    export_name = "result_{}-{}-{}-{}-{}-{}-{}.zip".format(
                        bw_infra,
                        bw_server,
                        bw_user,
                        bw_attack_i,
                        "Mix" if mix_protocol else "NoMix",
                        normal_window_size,
                        attacker_window_size,
                    )

                    cmd = "zip -r {} {} && rm -rf {}".format(
                        export_name, output_dir, output_dir
                    )
                    subprocess.call(cmd, shell=True)


if __name__ == "__main__":
    main()
