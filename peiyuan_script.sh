sudo mn -c


sudo ./simulate_optack.py -d peiyuan_results/1_1 --nb_attackers 1 --nb_receivers 1 -r 90 -t 30 


sudo ./simulate_optack.py -d peiyuan_results/1_20 --nb_attackers 1 --nb_receivers 20 -r 90 -t 30 
sudo ./simulate_optack.py -d peiyuan_results/5_20 --nb_attackers 1 --nb_receivers 20 -r 90 -t 30 
sudo ./simulate_optack.py -d peiyuan_results/10_20 --nb_attackers 1 --nb_receivers 20 -r 90 -t 30 

python plotting/total-bytes-per-sec.py peiyuan_results/1_20/*.csv > peiyuan_results/1_20.csv
python plotting/total-bytes-per-sec.py peiyuan_results/5_20/*.csv > peiyuan_results/5_20.csv
python plotting/total-bytes-per-sec.py peiyuan_results/10_20/*.csv > peiyuan_results/10_20.csv



for att in 1 3 5
do
    for recv in 19 17 15
    do
        for target_rate in 5 10 30 50 70
        do
            sudo ./simulate_optack.py -d peiyuan_results/${att}_${recv}_star --nb_attackers ${att} --nb_receivers ${recv} -r $target_rate -t 30 
        done
    done
done



