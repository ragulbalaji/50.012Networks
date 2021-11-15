#! /usr/bin/env python
from scapy.all import *
import random
import sys
import numpy as np
import subprocess as sp

IP_DST = sys.argv[1]
DST_PORT = int(sys.argv[2])

congestion_control = "cubic"

if len(sys.argv) > 3:
    congestion_control = sys.argv[3]


IP_SRC = None
SRC_PORT = random.randint(1024, 65535)
data = list()
FileName = "splitACK." + congestion_control + ".npy"

FIN = 0x01

socket = conf.L2socket(iface="client-eth0")

syn = IP(dst=IP_DST) / TCP(window=65535, sport=SRC_PORT, dport=DST_PORT, flags="S")
IP_SRC = syn[IP].src
SRC_PORT = syn[TCP].sport

print("sending SYN.....")
syn_ack = sr1(syn)
initialTs = syn_ack.time
initialSeq = syn_ack[TCP].seq
print("Received SYN_ACK!")
getStr = "GET / HTTP/1.1\r\n\r\n"
request = (
    IP(dst=IP_DST)
    / TCP(
        window=65535,
        dport=DST_PORT,
        sport=SRC_PORT,
        seq=(syn_ack[TCP].ack),
        ack=(syn_ack[TCP].seq + 1),
        flags="FA",
    )
    / getStr
)

print("Sending Request...")
socket.send(Ether() / request)


def addACKs(pkt):
    global DST_PORT, IP_DST, data, socket
    if IP not in pkt:
        return
    if TCP not in pkt:
        return
    if pkt[IP].src != IP_DST:
        return
    if pkt[TCP].sport != DST_PORT:
        return

    data.append((pkt.time - initialTs, pkt[TCP].seq - initialSeq))

    ip_total_len = pkt.getlayer(IP).len
    ip_header_len = pkt.getlayer(IP).ihl * 32 / 8
    tcp_header_len = pkt.getlayer(TCP).dataofs * 32 / 8
    tcp_seg_len = ip_total_len - ip_header_len - tcp_header_len
    ACK_delta = tcp_seg_len / 3  # use 3 for now

    add = 0
    if pkt.flags & FIN:
        add = 1

    nextACK_num = pkt[TCP].seq + tcp_seg_len + add

    ACK_nums = list()
    if ACK_delta != 0:
        ACK_nums = range(pkt[TCP].seq + ACK_delta, nextACK_num, ACK_delta)

    if nextACK_num not in ACK_nums:
        ACK_nums.append(nextACK_num)

    # print("received seq no")
    # print(pkt[TCP].seq)
    # print(ACK_nums)

    for ACK_num in ACK_nums:
        ack_pkt = IP(dst=IP_DST) / TCP(
            window=65535,
            dport=DST_PORT,
            sport=SRC_PORT,
            seq=pkt[TCP].ack,
            ack=ACK_num,
            flags="A",
        )
        socket.send(Ether() / ack_pkt)


print("Sniffing......")
sniff(iface="client-eth0", prn=addACKs, filter="tcp and ip", timeout=4)
numbas = np.asarray(zip(*data))
sp.call(["rm", "-f", FileName], shell=True)
np.save(FileName, numbas)
