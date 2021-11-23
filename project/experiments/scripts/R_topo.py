from mininet.net import Mininet
from mininet.topo import Topo
from mininet.cli import CLI

class TopoStar(Topo):
  def build(self, num_hosts=4):
    hosts = []

    centerSwitch = self.addSwitch('s0')
    
    for i in range(num_hosts):
      hosts.append(self.addHost('h%d'%i))
    
    for host in hosts:
      self.addLink(host, centerSwitch)


if __name__ == '__main__':
  topo = TopoStar(num_hosts=8)
  net = Mininet(topo)
  net.start()
  net.pingAll()
  CLI(net)
  net.stop() 