#!/usr/bin/env gnuplot

set term png
set output 'output.png'
set datafile separator ','
set logscale y
set xrange [0:30]
set xlabel 'Seconds'
set ylabel 'Bytes/s (log scale)'
set title 'Maximum Traffic Induced Over Time'
set key outside right center box 3
plot 'peiyuan_results/2att_10server.csv' using 1:2 title "2att_10server", \
    'peiyuan_results/1att_10server.csv' using 1:2 title "1att_10server",\
    'peiyuan_results/2att_50server.csv' using 1:2 title "2att_50server",\
    'peiyuan_results/2att_50server_5normal.csv' using 1:2 title "2att_50server_5normal"

