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
plot '64.csv' using 1:2 title "64 Victims", \
	 '32.csv' using 1:2 title "32 Victims", \
     '16.csv' using 1:2 title "16 Victims", \
     '8.csv' using 1:2 title "8 Victims", \
     '4.csv' using 1:2 title "4 Victims", \
     '2.csv' using 1:2 title "2 Victims", \
     '1.csv' using 1:2 title "1 Victim"
