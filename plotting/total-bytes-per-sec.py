#!/usr/bin/env python

import sys

BUCKETS = 29

totals = [0]*BUCKETS

for fname in sys.argv[1:]:
    i = 0
    with open(fname) as f:
        for line in f:
            if i >= BUCKETS:
                break
            time, bytes = line.split(',')
            if float(time) > i:
                if float(time) < i + 1:
                    totals[i] += int(bytes)
                i += 1

for i in range(1, BUCKETS):
    print("%d, %d" % (i, totals[i] - totals[i-1]))
