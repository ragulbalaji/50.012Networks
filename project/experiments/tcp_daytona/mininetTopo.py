#!/usr/bin/python3

import argparse
import time
import os
from mininet.topo import Topo
from mininet.node import CPULimitedHost
from mininet.link import TCLink
from mininet.net import Mininet
from mininet.log import lg, info
from mininet.util import dumpNodeConnections
from mininet.cli import CLI
from mininet.node import OVSController

parser = argparse.ArgumentParser(description="Run experiment")
parser.add_argument(
    "--client",
    type=str,
    choices=["normal", "opACK", "splitACK", "dupACK"],
    default="normal",
)
parser.add_argument("--server", type=str, choices=["linux", "lwip"], default="linux")
parser.add_argument(
    "--cong-control", type=str, choices=["reno", "cubic", "vegas"], default="cubic"
)
parser.add_argument("--manual", help="Manual mininet commands", action="store_true")
args = parser.parse_args()

PORT = 8888


class DaytonaTopo(Topo):
    "Simple topology for bufferbloat experiment."

    def build(self, n=2):
        client = self.addHost("client")
        server = self.addHost("server")
        switch = self.addSwitch("s0")
        self.addLink(client, switch, bw=100, delay="32ms", max_queue_size=128, loss=0)
        self.addLink(server, switch, bw=100, delay="32ms", max_queue_size=128, loss=0)
        return


topo = DaytonaTopo()
net = Mininet(topo=topo, host=CPULimitedHost, link=TCLink, controller=OVSController)
net.start()
dumpNodeConnections(net.hosts)
# This performs a basic all pairs ping test.
net.pingAll()

client = net.get("client")
server = net.get("server")

client.cmd("iptables -A OUTPUT -p tcp --tcp-flags RST RST -j DROP")
os.system("sysctl -w net.ipv4.tcp_congestion_control=%s" % args.cong_control)

if args.manual:
    CLI(net)
else:
    if args.server == "linux":
        server.popen("python3 webserver.py", shell=True)
    elif args.server == "lwip":
        server.popen("./lwip-contrib/ports/unix/unixsim/simhost", shell=True)
    time.sleep(0.5)

    if args.client == "normal":
        client.popen(
            "python3 normalTransmission.py %s %s %s"
            % (server.IP(), PORT, args.cong_control),
            shell=True,
        ).wait()
    elif args.client == "dupACK":
        client.popen(
            "python3 dupACKs.py %s %s %s" % (server.IP(), PORT, args.cong_control),
            shell=True,
        ).wait()
    elif args.client == "splitACK":
        client.popen(
            "python3 splitACK.py %s %s %s" % (server.IP(), PORT, args.cong_control),
            shell=True,
        ).wait()
    elif args.client == "opACK":
        client.popen(
            "python3 opACKs.py %s %s %s" % (server.IP(), PORT, args.cong_control),
            shell=True,
        ).wait()

    if args.server == "linux":
        server.popen("pgrep -f webserver.py | xargs kill -9", shell=True).wait()

net.stop()
