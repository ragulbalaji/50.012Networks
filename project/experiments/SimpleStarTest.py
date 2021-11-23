from mininet.topo import Topo
from mininet.node import CPULimitedHost
from mininet.link import TCLink
from mininet.net import Mininet
from mininet.cli import CLI
from mininet.node import OVSController

# from subprocess import Popen, PIPE
# from multiprocessing import Process
# from argparse import ArgumentParser

import time
import os

class TopoStar(Topo):
  def __init__(self, n=2, cpu=None, bw_consumer=2, bw_producer=10, delay='50', maxq=None, diff=False):
    super(TopoStar, self ).__init__()
    self.addSwitch('s0', fail_mode='open')
    self.addHost('atkr', cpu=cpu)
    self.addHost('recv', cpu=cpu)
    self.addLink('atkr', 's0', bw=bw_consumer, delay=delay)
    self.addLink('recv', 's0', bw=bw_producer, delay=delay)
    for i in range(n): self.addHost(f'h{i}', cpu=cpu)
    for i in range(n): self.addLink(f'h{i}', 's0', bw=bw_consumer, delay=delay)

def ControlExperiment(expname=f'EXP_{time.time()}', bw_consumer=2, bw_producer=20, window_size="64K", hosts=8, test_time=10, transport_alg=('-Z reno', 'TCPreno'), attacker_parallel_connections=2):
  topo = TopoStar(n=hosts, bw_consumer=bw_consumer, bw_producer=bw_producer)
  net = Mininet(topo=topo, host=CPULimitedHost, link=TCLink, autoPinCpus=True, controller=OVSController)
  net.start()
  net.pingAll()

  print(f'[Test] Running {expname} with CBW-{bw_consumer}, PBW-{bw_producer}, CWND-{window_size}, {transport_alg[1]}, {attacker_parallel_connections} atkr_para_conn...')
  # start tests
  savedir = f'./results/{expname}/CBW-{bw_consumer}/PBW-{bw_producer}/CWND-{window_size}/{transport_alg[1]}/{attacker_parallel_connections}conn'
  atkr = net.getNodeByName('atkr')
  # setup recv
  recv = net.getNodeByName('recv')
  recv.cmd(f'mkdir -p {savedir}')
  recv.cmd(f'iperf -s -p 5001 -w {window_size} -i 1 -N {transport_alg[0]} > {savedir}/iperf-recv.csv &')
  # setup others
  for i in range(hosts):
    hi = net.getNodeByName(f'h{i}')
    hi.cmd(f'iperf -c {recv.IP()} -p 5001 -i 1 -w {window_size} -N {transport_alg[0]} -t {test_time} -y C > {savedir}/iperf_h{i}.csv &')
  atkr.cmd(f'iperf -c {recv.IP()} -p 5001 -i 1 -w {window_size} -N {transport_alg[0]} -t {test_time} -P {attacker_parallel_connections} -y C > {savedir}/iperf_atkr.csv')
  print("[Info] Test Ended")
  # tests end

  # CLI(net) # comment out when running main test
  net.stop()

if __name__ == '__main__':
  transport_algos = [
    ('-Z reno', 'TCPreno'),
    ('-Z cubic', 'TCPcubic'),
    # ('-u', 'UDP')
  ]

  # window_sizes = ["64K", "128K", "256K"]
  # consumer_bandwidths = [2, 4, 6]
  # producer_bandwidths = [10, 16, 20]
  window_sizes = ["16K", "64K", "128K", "256K", "512K", "1024K"]
  consumer_bandwidths = [6]
  producer_bandwidths = [24]
  NUM_START = 1
  NUM_END = 512
  STEP = "exp"
  NUM_EXPS = f"{NUM_START}-{NUM_END}"
  TEST_TIME = 10

  ExperimentName = f"NUMEXP-{NUM_EXPS}_TTIME-{TEST_TIME}_STEP-{STEP}"

  for CONSUMER_BW in consumer_bandwidths:
    for PRODUCER_BW in producer_bandwidths:
      for WINDOW_SIZE in window_sizes:
        for ATKR_PARA_CONN in [2**i for i in range(10)]:# range(NUM_START, NUM_END + 2, STEP):
          for ALGO in transport_algos:
            # reset
            time.sleep(1)
            os.system('sudo mn -c')

            # test
            ControlExperiment(expname=ExperimentName, window_size=WINDOW_SIZE,bw_consumer=CONSUMER_BW, bw_producer=PRODUCER_BW, transport_alg=ALGO, attacker_parallel_connections=ATKR_PARA_CONN, test_time=TEST_TIME)

  print("[Info] All Tests Ended!")

  # os.system(f'zip ./results/{ExperimentName}.zip -r ./results/{ExperimentName}/')
  # os.system(f'rm -rf ./results/{ExperimentName}') # remove small files so git doesnt get angry