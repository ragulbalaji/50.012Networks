import argparse
import csv
import subprocess
from datetime import datetime
from pathlib import Path
from time import mktime, sleep

import matplotlib

matplotlib.use("Agg")  # Force matplotlib to not use any Xwindows backend.
import matplotlib.pyplot as plt
from mininet.link import TCLink
from mininet.log import info, lg, setLogLevel
from mininet.net import Mininet
from mininet.topo import Topo
from mininet.util import dumpNodeConnections, quietRun

##
# Globals
##########
# time (sec), cwnd (MSS)
tcpprobe_csv_header = [
    "time",
    "src_addr_port",
    "dst_addr_port",
    "bytes",
    "next_seq",
    "unacknowledged",
    "cwnd",
    "slow_start",
    "swnd",
    "smoothedRTT",
    "rwnd",
]
# time (YYYYMMDDHHMMSS), interval (S.S-S.S), bps (bps)
iperf_csv_header = [
    "time",
    "src_addr",
    "src_port",
    "dst_addr",
    "dst_port",
    "other",
    "interval",
    "B_sent",
    "bps",
]


def clean_tcpprobe_procs():
    """Serach and kill any running tcpprobe processes."""
    # Search and kill any running tcpprobe procs
    print("Killing any running tcpprobe processes...")
    procs = quietRun("pgrep -f /proc/net/tcpprobe").split()

    for proc in procs:
        output = quietRun("sudo kill -KILL {0}".format(proc.rstrip()))
        if output != "":
            print(output)


def start_tcpprobe(filename):
    """Install tcp_pobe module and dump to file.

    :param  filename    Path to the file where to dump the tcpprobe data.
    """
    print("Unloading tcp_probe module...")
    clean_tcpprobe_procs()

    # Unload the module
    output = quietRun("sudo rmmod tcp_probe")
    if output != "":
        print(output.rstrip())

    print("Loading tcp_probe module...")
    # TODO: why do we use the full=1 arg? Do not filter to port=5001, but use the IP of the sender instead.
    output = quietRun("sudo modprobe tcp_probe full=1")
    if output != "":
        print(output.rstrip())

    print("Saving tcpprobe output to: {0}".format(filename))
    return subprocess.Popen(
        "sudo cat /proc/net/tcpprobe > {0}".format(filename), shell=True
    )
