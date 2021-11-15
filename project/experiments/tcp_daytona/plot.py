#!/usr/bin/python3

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np

i = 0

for cong_control in ["cubic", "reno", "vegas"]:
    i += 1
    DupFileName = "dupACK." + cong_control + ".npy"
    SplitFileName = "splitACK." + cong_control + ".npy"
    NormalFileName = "normal." + cong_control + ".npy"
    OpFileName = "opACK." + cong_control + ".npy"

    dupACKs = np.load(DupFileName)
    splitACKs = np.load(SplitFileName)
    normalACKs = np.load(NormalFileName)
    opACKs = np.load(OpFileName)

    plt.figure(i)
    plt.subplot(311)
    plt.title("Duplicate ACKs (%s)" % cong_control)
    plt.scatter(*zip(dupACKs), label="Duplicate ACKs")
    plt.scatter(*zip(normalACKs), label="Normal")
    plt.xlabel("time (s)")
    plt.ylabel("Seq Number")
    plt.legend(loc="lower right")

    plt.subplot(312)
    plt.title("Split ACKs (%s)" % cong_control)
    plt.scatter(*zip(splitACKs), label="Split ACKs")
    plt.scatter(*zip(normalACKs), label="Normal")
    plt.xlabel("time (s)")
    plt.ylabel("Seq Number")
    plt.legend(loc="lower right")

    plt.subplot(313)
    plt.title("Optimistic ACKs (%s)" % cong_control)
    plt.scatter(*zip(opACKs), label="Optimistic ACKs")
    plt.scatter(*zip(normalACKs), label="Normal")
    plt.xlabel("time (s)")
    plt.ylabel("Seq Number")
    plt.legend(loc="lower right")

    plt.tight_layout(pad=0.4, w_pad=0.5, h_pad=1.0)
    plt.savefig("data.%s.png" % cong_control)
