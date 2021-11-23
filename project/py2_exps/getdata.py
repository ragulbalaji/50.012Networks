from os import listdir
from os.path import isfile, join
import csv

respath = "./v5_star/"
d = {}
# <algo, <recvlink, <net_bw, [atck_link]>>>
d["udp"] = {
    400: 
        {
            25: {}, 1: {} 
        }, 
    50: 
        {
            25: {}, 1: {} 
        },
    5: 
        {
            25: {}, 1: {} 
        }
    }

d["reno"] = {
    400: 
        {
            25: {}, 1: {} 
        }, 
    50: 
        {
            25: {}, 1: {} 
        },
    5: 
        {
            25: {}, 1: {} 
        }
    }

d["cubic"] = {
    400: 
        {
            25: {}, 1: {} 
        }, 
    50: 
        {
            25: {}, 1: {} 
        },
    5: 
        {
            25: {}, 1: {} 
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

    if int(bw_infra) != 1000:
        continue

    currdict = d[algo][int(bw_recv)][int(bw_net)]
    if bw_atkr not in currdict:
        currdict[bw_atkr] = {"count": 0, "sum": 0, "total": 0}

    count = 0
    sum = 0
    found = False
    for filename in listdir(join(respath, pathname)):
        filepath = join(respath, pathname, filename)

        csvparts = filename.split(".")
        if csvparts[0][-2:] == 'cv':
            with open(filepath, newline='') as file:
                reader = csv.reader(file, delimiter = ',')
                for row in reader:
                    row_content = row[0].split(" ")
                    if len(row_content) < 2:
                        continue
                    
                    if row_content[-1] == "Bandwidth":
                        found = True
                        continue
                    if found:
                        for i in range(len(row_content)):
                            if row_content[i] == "MBytes" or row_content[i] == "KBytes":
                                unit = row_content[i]
                                val = row_content[i-1]
                        # val = row_content[-5]
                        # unit = row_content[-4]
                        if unit == "MBytes":
                            currdict[bw_atkr]["total"] += float(val) * 1000000
                        elif unit == "KBytes":
                            currdict[bw_atkr]["total"] += float(val) * 1000
                        else:
                            currdict[bw_atkr]["total"] += float(val)

        if csvparts[0][-2:] not in targets:
            continue
        
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
            print(d[algo][recvlink][normlink].keys())
            for atklink in d[algo][recvlink][normlink].keys():
                print("attacker link: " + str(atklink))
                count = d[algo][recvlink][normlink][atklink]["count"]
                sum = d[algo][recvlink][normlink][atklink]["sum"]
                res = 0
                total = d[algo][recvlink][normlink][atklink]["total"]

                if total != 0:
                    res = sum / total
                print("data: " + str(sum) + " total:" + str(total) + " ratio: " + str(res))
    