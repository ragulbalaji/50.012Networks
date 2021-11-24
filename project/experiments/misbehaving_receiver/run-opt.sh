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
        zip "./plots/${i}/sequence_nums.zip" ./plots/opt.png
        zip "./plots/${i}/throughputs.zip" ./plots/opt_throughput.png
        rm ./plots/opt.png ./plots/opt_throughput.png
		mn -c
    done
done
