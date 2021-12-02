#!/bin/bash

for i in {1..100}
do
    python run_attacks.py --delay 375 --num-attack $i
    echo "Generating plots..."
    python plot.py --save --attack div --output ./plots
    python plot.py --save --attack dup --output ./plots
    python plot.py --save --attack opt --output ./plots
    python plot_throughput.py --save --attack div --output ./plots
    python plot_throughput.py --save --attack dup --output ./plots
    python plot_throughput.py --save --attack opt --output ./plots
    echo "Done! Please check ./plots for all generated plots."
    zip "./plots/${i}/sequence_nums.zip" ./plots/div.png ./plots/dup.png ./plots/opt.png
    zip "./plots/${i}/throughputs.zip" ./plots/div_throughput.png ./plots/dup_throughput.png ./plots/opt_throughput.png
    rm ./plots/div.png ./plots/dup.png ./plots/opt.png ./plots/div_throughput.png ./plots/dup_throughput.png ./plots/opt_throughput.png
    mn -c
done
