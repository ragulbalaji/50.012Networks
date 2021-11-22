from __future__ import print_function

import mininet.link
import mininet.topo
from mininet.link import TCLink
from mininet.topo import Topo


class TreeTopoTCPv2(Topo):
    def __init__(
        self,
        delay=2,  # delay in ms
        bw_infra=1000,  # bandwidth in Mbps
        bw_user=20,  # bandwidth in Mbps
        bw_attack=500,  # bandwidth in Mbps
        bw_server=200,  # bandwidth in Mbps
    ):
        super(TreeTopoTCPv2, self).__init__()

        infra_link_params = dict(
            bw=bw_infra,  # bandwidth in Mbps
            delay="{}ms".format(delay),
            # max_queue_size=(21 * delay * 20) / 100,
            # use_htb=True,
        )

        server_link_params = dict(
            bw=bw_server,  # bandwidth in Mbps
            delay="{}ms".format(delay),
            # max_queue_size=(21 * delay * 20) / 100,
            # use_htb=True,
        )

        normal_user_link_params = dict(
            bw=bw_user,  # bandwidth in Mbps
            delay="{}ms".format(delay),
            # max_queue_size=80 * delay,
            # use_htb=True,z
        )

        attacker_params = dict(
            bw=bw_attack,  # bandwidth in Mbps
            delay="{}ms".format(delay),
            # max_queue_size=80 * delay,
            # use_htb=True,
        )

        # Create routers s1 to s5
        s1 = self.addSwitch("s1")
        s2 = self.addSwitch("s2")
        s3 = self.addSwitch("s3")
        s4 = self.addSwitch("s4")
        s5 = self.addSwitch("s5")

        # connect Layer 0 switch to Layer 1 switches
        self.addLink(s1, s2, cls=TCLink, **infra_link_params)
        self.addLink(s1, s3, cls=TCLink, **infra_link_params)
        self.addLink(s1, s4, cls=TCLink, **infra_link_params)
        self.addLink(s1, s5, cls=TCLink, **infra_link_params)

        # connect Layer 1 switches to Layer 2 hosts
        hosts = {}
        for i in range(1, 11):
            hostname = "h{}".format(i)
            hosts[hostname] = self.addHost(hostname)

        # client - attacker
        self.addLink(s2, hosts["h1"], cls=TCLink, **attacker_params)

        # client - normal users
        for i in [2, 3]:
            hostname = "h{}".format(i)
            self.addLink(s2, hosts[hostname], cls=TCLink, **normal_user_link_params)

        for i in [4, 5, 6]:
            hostname = "h{}".format(i)
            self.addLink(s3, hosts[hostname], cls=TCLink, **normal_user_link_params)

        for i in [7, 8, 9]:
            hostname = "h{}".format(i)
            self.addLink(s4, hosts[hostname], cls=TCLink, **normal_user_link_params)

        # server - receiver
        self.addLink(s5, hosts["h10"], cls=TCLink, **server_link_params)


class TreeTopoTCP(Topo):
    def __init__(
        self,
        delay=2,  # delay in ms
        bw_infra=500,  # bandwidth in Mbps
        bw_user=20,  # bandwidth in Mbps
        bw_attack=1000,  # bandwidth in Mbps
    ):
        super(TreeTopoTCP, self).__init__()

        infra_link_params = dict(
            bw=bw_infra,  # bandwidth in Mbps
            delay="{}ms".format(delay),
            # max_queue_size=(21 * delay * 20) / 100,
            use_htb=True,
        )

        normal_user_link_params = dict(
            bw=bw_user,  # bandwidth in Mbps
            delay="{}ms".format(delay),
            # max_queue_size=80 * delay,
            use_htb=True,
        )

        attacker_params = dict(
            bw=bw_attack,  # bandwidth in Mbps
            delay="{}ms".format(delay),
            # max_queue_size=80 * delay,
            use_htb=True,
        )

        # Create routers s1 to s5
        s1 = self.addSwitch("s1")
        s2 = self.addSwitch("s2")
        s3 = self.addSwitch("s3")
        s4 = self.addSwitch("s4")
        s5 = self.addSwitch("s5")

        # connect Layer 0 switch to Layer 1 switches
        self.addLink(s1, s2, cls=TCLink, **infra_link_params)
        self.addLink(s1, s3, cls=TCLink, **infra_link_params)
        self.addLink(s1, s4, cls=TCLink, **infra_link_params)
        self.addLink(s1, s5, cls=TCLink, **infra_link_params)

        depth = 2
        fanout = 4

        # connect Layer 1 switches to Layer 2 hosts
        hosts = {}
        for i in range(fanout ** depth):
            hostname = "h{}".format(i + 1)
            hosts[hostname] = self.addHost(hostname)

        # client - attacker
        self.addLink(s2, hosts["h1"], cls=TCLink, **attacker_params)

        # client - normal users
        for i in range(2, 5):
            hostname = "h{}".format(i)
            self.addLink(s2, hosts[hostname], cls=TCLink, **normal_user_link_params)

        for i in range(5, 9):
            hostname = "h{}".format(i)
            self.addLink(s3, hosts[hostname], cls=TCLink, **normal_user_link_params)

        for i in range(9, 13):
            hostname = "h{}".format(i)
            self.addLink(s4, hosts[hostname], cls=TCLink, **normal_user_link_params)

        for i in range(13, 16):
            hostname = "h{}".format(i)
            self.addLink(s5, hosts[hostname], cls=TCLink, **normal_user_link_params)

        # server - receiver
        self.addLink(s5, hosts["h16"], cls=TCLink, **infra_link_params)
