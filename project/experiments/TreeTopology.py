from mininet.link import TCLink
from mininet.topo import Topo

class TreeTopoTCPv2(Topo):
    def __init__(
        self,
        n=2,
        cpu=None,
        delay=10,  # delay in ms
        bw_consumer=2,
        bw_producer=10,
        bw_infra=1000
    ):
        super(TreeTopoTCPv2, self).__init__()

        infra_link_params = dict(
            bw=bw_infra,  # bandwidth in Mbps
            delay="{}ms".format(delay),
            # max_queue_size=(21 * delay * 20) / 100,
            # use_htb=True,
        )

        server_link_params = dict(
            bw=bw_producer,  # bandwidth in Mbps
            delay="{}ms".format(delay),
            # max_queue_size=(21 * delay * 20) / 100,
            # use_htb=True,
        )

        normal_user_link_params = dict(
            bw=bw_consumer,  # bandwidth in Mbps
            delay="{}ms".format(delay),
            # max_queue_size=80 * delay,
            # use_htb=True,z
        )

        attacker_params = dict(
            bw=bw_consumer,  # bandwidth in Mbps
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
        self.addHost('atkr', cpu=cpu)
        self.addHost('recv', cpu=cpu)
        for i in range(n):
            self.addHost(f'h{i}', cpu=cpu)

        # client - consumer
        self.addLink(s2, 'atkr', cls=TCLink, **attacker_params)

        # client - normal users
        for i in [0, 1]:
            hostname = "h{}".format(i)
            self.addLink(s2, hostname, cls=TCLink, **normal_user_link_params)

        for i in [2, 3, 4]:
            hostname = "h{}".format(i)
            self.addLink(s3, hostname, cls=TCLink, **normal_user_link_params)

        for i in [5, 6, 7]:
            hostname = "h{}".format(i)
            self.addLink(s4, hostname, cls=TCLink, **normal_user_link_params)

        # server - producer
        self.addLink(s5, 'recv', cls=TCLink, **server_link_params)