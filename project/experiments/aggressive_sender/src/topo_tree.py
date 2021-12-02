from mininet.link import TCLink
from mininet.topo import Topo


class TreeTopoTCP(Topo):
    def __init__(
        self,
        delay: int = 2,  # delay in ms
        bw_infra: int = 500,  # bandwidth in Mbps
        bw_user: int = 20,  # bandwidth in Mbps
        bw_attack: int = 1000,  # bandwidth in Mbps
    ):
        super(TreeTopoTCP, self).__init__()

        infra_link_params = dict(
            bw=bw_infra,  # bandwidth in Mbps
            delay=f"{delay}ms",
            max_queue_size=(21 * delay * 20) / 100,
            use_htb=True,
        )

        normal_user_link_params = dict(
            bw=bw_user,  # bandwidth in Mbps
            delay=f"{delay}ms",
            max_queue_size=80 * delay,
            use_htb=True,
        )

        attacker_params = dict(
            bw=bw_attack,  # bandwidth in Mbps
            delay=f"{delay}ms",
            max_queue_size=80 * delay,
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
            hostname = f"h{i+1}"
            hosts[hostname] = self.addHost(hostname)

        # client - attacker
        self.addLink(s2, hosts["h1"], cls=TCLink, **attacker_params)

        # client - normal users
        for i in range(2, 5):
            hostname = f"h{i}"
            self.addLink(s2, hosts[hostname], cls=TCLink, **normal_user_link_params)

        for i in range(5, 9):
            hostname = f"h{i}"
            self.addLink(s3, hosts[hostname], cls=TCLink, **normal_user_link_params)

        for i in range(9, 13):
            hostname = f"h{i}"
            self.addLink(s4, hosts[hostname], cls=TCLink, **normal_user_link_params)

        for i in range(13, 16):
            hostname = f"h{i}"
            self.addLink(s5, hosts[hostname], cls=TCLink, **normal_user_link_params)

        # server - receiver
        self.addLink(s5, hosts["h16"], cls=TCLink, **infra_link_params)
