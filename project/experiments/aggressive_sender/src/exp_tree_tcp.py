import argparse
import csv
import subprocess
from datetime import datetime
from pathlib import Path
from time import mktime, sleep

from mininet.link import TCLink
from mininet.log import info, lg, setLogLevel
from mininet.net import Mininet
from mininet.topo import Topo
from mininet.util import dumpNodeConnections, quietRun
from topo_tree import TreeTopoTCP
from utils import clean_tcpprobe_procs, start_tcpprobe

output_dir = "out"
if not Path(output_dir).is_dir():
    Path(output_dir).mkdir(parents=True)


def tcp_tests(algs=["reno"], delays=2, iperf_runtime=10):
    """Run the TCP congestion control tests.

    :param  algs                List of strings with the TCP congestion control algorithms to test.
    :param  delays              List of integers with the one-directional propagation delays to test.
    :param  iperf_runtime       Time to run the iperf clients in seconds.
    """
    print(
        f"*** Tests settings:\n - Algorithms: {algs}\n - delays: {delays}\n - Iperf runtime: {iperf_runtime}"
    )
    for alg in algs:
        print(f"*** Starting test for algorithm={alg}...")
        for delay in delays:
            print(f"*** Starting test for delay={delay}ms...")

            # Start tcp probe process
            print("*** Starting tcpprobe recording...")
            tcpprobe_proc = start_tcpprobe(f"{output_dir}/tcpprobe_{alg}_{delay}ms.txt")

            # Create the net topology
            print(f"*** Creating topology for delay={delay}ms...")
            topo = TreeTopoTCP(delay=delay)

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

            print(f"*** Starting server h16...")
            popens["h16"] = hosts["h16"].popen(
                [
                    "iperf",
                    "-s",
                    "-p",
                    "5001",
                    "-w",
                    "64K",
                    "-y",
                    "C",
                    ">",
                    f"{output_dir}/iperf_{alg}_server_{delay}ms.txt",
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
                print(f"*** Starting normal client h{i}...")
                hostname = f"h{i}"
                _host = hosts[hostname]
                _server_addr = host_addrs["h16"]
                popens[hostname] = _host.popen(
                    f"iperf -c {_server_addr} -p 5001 -i 1 -w 64K -M 1460 -N -Z {alg} -t {iperf_runtime} -y C > {output_dir}/iperf_{alg}_{hostname}_{delay}ms.txt",
                    shell=True,
                )

            print(f"*** Starting attacking client h1...")
            attacker_hostname = "h1"
            attacker_host = hosts[attacker_hostname]

            popens[attacker_hostname] = attacker_host.popen(
                f"iperf -c {_server_addr} -p 5001 -i 1 -w 64K -M 1460 -N -Z {alg} -t {iperf_runtime} -y C > {output_dir}/iperf_{alg}_{attacker_hostname}_{delay}ms.txt",
                shell=True,
            )

            print(f"*** Waiting {iperf_runtime}sec for iperf clients to finish...")
            for i in range(1, 10):
                hostname = f"h{i}"
                popens[hostname].wait()

            print("*** Terminate the iperf servers and tcpprobe processes...")
            popens["h16"].terminate()
            tcpprobe_proc.terminate()

            popens["h16"].wait()
            tcpprobe_proc.wait()

            print("*** Cleaning tcp probe processes...")
            clean_tcpprobe_procs()

            print("*** Stopping test...")
            net.stop()


def main():
    import subprocess

    from puts import timestamp_seconds

    parser = argparse.ArgumentParser(description="TCP Test")
    parser.add_argument(
        "-a",
        "--algorithms",
        nargs="+",
        default=["reno", "cubic"],
        help="List TCP Congestion Control algorithms to test.",
    )
    parser.add_argument(
        "-d",
        "--delays",
        nargs="+",
        type=int,
        default=[21, 81, 162],
        help="List of backbone router one-way propagation delays to test.",
    )
    parser.add_argument(
        "-i",
        "--iperf-runtime",
        type=int,
        default=30,
        help="Time to run the iperf clients.",
    )
    args = parser.parse_args()
    setLogLevel("info")
    tcp_tests(args.algorithms, args.delays, args.iperf_runtime)
    export_name = f"result_{timestamp_seconds()}.zip"
    cmd = f"zip -r {export_name} {output_dir} && rm -rf {output_dir}"
    subprocess.run(cmd, shell=True)


if __name__ == "__main__":
    main()
