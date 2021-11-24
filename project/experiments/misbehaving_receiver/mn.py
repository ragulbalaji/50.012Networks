from mininet.topo import Topo


class CongestionTopo(Topo):
    def __init__(self):
        Topo.__init__(self)
        h1 = self.addHost("h1", ip="10.0.0.1")
        h2 = self.addHost("h2", ip="10.0.0.2")
        s1 = self.addSwitch("s1")
        self.addLink(h1, s1, bw=5, delay="50ms")
        self.addLink(h2, s1, bw=0.054, delay="50ms", max_queue_size=10)


class StandardTopo(Topo):
    def __init__(self, link_delay):
        Topo.__init__(self)
        h1 = self.addHost("h1", ip="10.0.0.1")
        h2 = self.addHost("h2", ip="10.0.0.2")
        s1 = self.addSwitch("s1")
        self.addLink(h1, s1, delay="%dms" % link_delay)
        self.addLink(h2, s1, delay="%dms" % link_delay)


class StarTopo(Topo):
    def __init__(
        self,
        n=10,
        cpu=None,
        bw_atkr=10,
        bw_recv=10,
        bw_net=10,
        delay="100",
        maxq=None,
        diff=False,
    ):
        Topo.__init__(self)
        s0 = self.addSwitch("s0", fail_mode="open")
        h1 = self.addHost("h1", ip="10.0.0.1", cpu=cpu)
        h2 = self.addHost("h2", ip="10.0.0.2", cpu=cpu)
        self.addLink(h1, s0, delay="%dms" % delay)
        self.addLink(h2, s0, delay="%dms" % delay)
        for i in range(3, n + 1):
            self.addHost("h%s" % i, ip="10.0.0.%s" % i, cpu=cpu)
        for i in range(3, n + 1):
            self.addLink("h%s" % i, s0, bw=bw_net, delay=delay)


topos = {
    "standard": (lambda: StandardTopo(250)),
    "congestion": (lambda: CongestionTopo()),
    "star": (lambda: StarTopo()),
}
