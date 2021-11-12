from mininet.net import Mininet
from mininet.topo import Topo
from mininet.cli import CLI

class StarTopo(Topo):
  def build(self, num_hosts=4):
    centerSwitch = self.addSwitch( 's0' )

    hosts = []
    for i in range(num_hosts):
      hosts.append(self.addHost('h%d'%i))
    
    links = []
    for host in hosts:
      links.append(self.addLink(host, centerSwitch))


if __name__ == '__main__':
  topo = StarTopo(num_hosts=16)
  net = Mininet(topo)
  net.start()
  CLI(net)
  net.stop() 