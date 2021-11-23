from mininet.net import Mininet
from mininet.topo import Topo
from mininet.cli import CLI

class Ring( Topo ):
  def __init__( self ):
    Topo.__init__( self )
    HA1 = self.addHost( 'HA1' )
    HB1 = self.addHost( 'HB1' )
    HC1 = self.addHost( 'HC1' )
    HD1 = self.addHost( 'HD1' )
    HE1 = self.addHost( 'HE1' )
    HF1 = self.addHost( 'HF1' )
    HG1 = self.addHost( 'HG1' )
    HH1 = self.addHost( 'HH1' )
    S1 = self.addSwitch( 'S1' )
    S2 = self.addSwitch( 'S2' )
    S3 = self.addSwitch( 'S3' )
    S4 = self.addSwitch( 'S4' )
    S5 = self.addSwitch( 'S5' )
    S6 = self.addSwitch( 'S6' )
    S7 = self.addSwitch( 'S7' )
    S8 = self.addSwitch( 'S8' )

    #links
    self.addLink( S1, S2 )
    self.addLink( S2, S3 )
    self.addLink( S3, S4 )
    self.addLink( S4, S5 )
    self.addLink( S5, S6 )
    self.addLink( S6, S7 )
    self.addLink( S7, S8 )
    self.addLink( S8, S1 )
    self.addLink( S1, HA1 )
    self.addLink( S2, HB1 )
    self.addLink( S3, HC1 )
    self.addLink( S4, HD1 )
    self.addLink( S5, HE1 )
    self.addLink( S6, HF1 )
    self.addLink( S7, HG1 )
    self.addLink( S8, HH1 )

topo = Ring()
net = Mininet(topo=topo)
net.start()
CLI(net)
net.stop()