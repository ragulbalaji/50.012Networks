#!/bin/bash

for i in {1..100}
do
    for j in {1..100}
    do
        python run_attacks.py --delay 375 --num-attack $i --opt-interval $j
        echo "Generating plots..."
        python plot.py --save --attack opt --output ./plots
        python plot_throughput.py --save --attack opt --output ./plots
        echo "Done! Please check ./plots for all generated plots."
        mv ./plots/opt_throughput.png ./plots/opt.png "./plots/${i}/${j}/"
        mn -c
    done
done
