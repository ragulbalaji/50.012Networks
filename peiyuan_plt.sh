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
plot 'peiyuan_results/1_20.csv' using 1:2 title "1_20.csv", \
    'peiyuan_results/5_20.csv' using 1:2 title "5_20.csv",\
    'peiyuan_results/10_20.csv' using 1:2 title "10_20.csv",\
    