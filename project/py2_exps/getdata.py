from os import listdir
from os.path import isfile, join
import csv

respath = "./results/"
d = {}
# <algo, <recvlink, <net_bw, [atck_link]>>>
d["udp"] = {
    250: 
        {
            50: {}, 100: {}
        }, 
    500: 
        {
            50: {}, 100: {}
        }
    }

d["reno"] = {
    250: 
        {
            50: {}, 100: {}
        }, 
    500: 
        {
            50: {}, 100: {}
        }
    }

d["cubic"] = {
    250: 
        {
            50: {}, 100: {}
        }, 
    500: 
        {
            50: {}, 100: {}
        }
    }

targets = set()
for i in range(1, 9):
    targets.add("h{}".format(i))

for pathname in listdir(respath):
    if pathname == ".DS_Store":
        continue
    parts = pathname.split("_")
    algo = parts[-1]
    bw_infra, bw_atkr, bw_recv, bw_net = 0, 0, 0, 0
    if algo == "-u":
        algo = "udp"
        bw_infra, bw_atkr, bw_recv, bw_net = parts[-5], parts[-4], parts[-3], parts[-2]
    else:
        bw_infra, bw_atkr, bw_recv, bw_net = parts[-6], parts[-5], parts[-4], parts[-3]

    currdict = d[algo][int(bw_recv)][int(bw_net)]
    if bw_atkr not in currdict:
        currdict[bw_atkr] = {"count": 0, "sum": 0}

    count = 0
    sum = 0
    for filename in listdir(join(respath, pathname)):
        csvparts = filename.split(".")
        if csvparts[0][-2:] not in targets:
            continue
        
        filepath = join(respath, pathname, filename)
        
        with open(filepath, newline='') as file:
            reader = csv.reader(file, delimiter = ',')
            for row in reader:
                data = int(row[-2])
                # if bps != 0:
                count += 1
                sum += data
    currdict[bw_atkr]["count"] += count
    currdict[bw_atkr]["sum"] += sum


for algo in d.keys():
    print(algo)
    for recvlink in d[algo].keys():
        print("recvlink: " + str(recvlink))
        for normlink in d[algo][recvlink].keys():
            print("normal link bandwidth: " + str(normlink))
            for atklink in d[algo][recvlink][normlink].keys():
                print("attacker link: " + str(atklink))
                count = d[algo][recvlink][normlink][atklink]["count"]
                sum = d[algo][recvlink][normlink][atklink]["sum"]
                res = 0
                if count != 0:
                    res = sum / count
                print("data: " + str(sum))
    