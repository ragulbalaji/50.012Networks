sudo mn -c


sudo ./simulate_optack.py -d peiyuan_results/2att_10server --num_attackers 2 --nb_servers 10 -r 90 -t 30 --use_ring_topo


 
python plotting/total-bytes-per-sec.py peiyuan_results/2att_10server/*.csv > peiyuan_results/2att_10server.csv


gnuplot peiyuan_plotting.plt





sudo ./simulate_optack.py -d peiyuan_results/1att_10server --num_attackers 1 --nb_servers 10 -r 90 -t 30 --use_ring_topo



python plotting/total-bytes-per-sec.py peiyuan_results/1att_10server/*.csv > peiyuan_results/1att_10server.csv


gnuplot peiyuan_plotting.plt







sudo ./simulate_optack.py -d peiyuan_results/2att_50server --num_attackers 2 --nb_servers 50 -r 90 -t 30 --use_ring_topo

python plotting/total-bytes-per-sec.py peiyuan_results/2att_50server/*.csv > peiyuan_results/2att_50server.csv





sudo ./simulate_optack.py -d peiyuan_results/2att_10server_5normal --num_attackers 2 --nb_servers 10 -r 90 -t 30 --use_ring_topo --num_normal_receivers 5
 
python plotting/total-bytes-per-sec.py peiyuan_results/2att_10server_5normal/*.csv > peiyuan_results/2att_10server_5normal.csv