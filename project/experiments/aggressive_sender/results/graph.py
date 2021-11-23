import subprocess
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

zip_name = "result_500-10-10"

zip_path = Path(zip_name + ".zip")
if zip_path.exists():
    subprocess.run(f"unzip -q {zip_path}", shell=True)


basedir = "out"
# hostnames = ["server"] + [f"h{i}" for i in range(1, 10)]
hostnames = [f"h{i}" for i in range(1, 10)]
# delays = [21, 81, 162]
# delays = [50, 100]
delays = [2, 50]
transport_algos = ["reno", "cubic"]
test_time = 30

iperf_header = [
    "timestamp",
    "src_addr",
    "src_port",
    "dest_addr",
    "dest_port",
    "transferID",
    "interval",
    "transferred_bytes",
    "bits_per_second",
]


def main():
    df_all = []
    for hostname in hostnames:
        for delay in delays:
            for transport_algo in transport_algos:
                df = pd.read_csv(
                    f"{basedir}/iperf_{transport_algo}_{hostname}_{delay}ms.txt",
                    names=iperf_header,
                )
                df["host"] = hostname
                df["transport"] = transport_algo
                df["delay"] = delay
                df_all.append(df)

    df_all = pd.concat(df_all)
    # print(df_all.head)

    fig, axs = plt.subplots(len(delays), len(transport_algos), figsize=(10, 10))
    missing_data = 0
    for delay in delays:
        df_0 = df_all[df_all["delay"] == delay]
        for transport_algo in transport_algos:
            df1 = df_0[df_0["transport"] == transport_algo]
            axi = axs[delays.index(delay)][transport_algos.index(transport_algo)]
            axi.set_title(f"TCP {transport_algo} {delay}ms delay")
            for host in hostnames:
                df2 = df1[df1["host"] == host]
                t_axis = []
                bytes_tx = []
                for t in range(test_time):
                    tint = f"{t:.1f}-{t+1:.1f}"
                    df3 = df2[df2["interval"] == tint]
                    if df3.shape[0] > 1:
                        df3 = df3[df3["transferID"] == -1]
                    t_axis.append(t + 1)
                    try:
                        bytes_tx.append(df3["transferred_bytes"].values[0])
                    except:
                        bytes_tx.append(-1)
                        missing_data += 1
                    # if bytes_tx[-1] <= 0:
                    #     bytes_tx[-1] = 1
                axi.plot(t_axis, bytes_tx, label=host)
            axi.legend()
            axi.set_xlabel("time")
            axi.set_ylabel("transferred_bytes")

    plt.savefig(Path(zip_name + ".png"))
    # plt.show()
    subprocess.run(f"rm -rf {basedir}", shell=True)


def main2():
    pd.set_option("display.max_rows", None)
    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", None)
    try:
        df_all = []
        for hostname in hostnames:
            for delay in delays:
                for transport_algo in transport_algos:
                    df = pd.read_csv(
                        f"{basedir}/iperf_{transport_algo}_{hostname}_{delay}ms.txt",
                        names=iperf_header,
                    )
                    df["host"] = hostname
                    df["transport"] = transport_algo
                    df["delay"] = delay
                    df_all.append(df)

        df_all = pd.concat(df_all)

        df_headers = list(df_all.columns.values)
        # print(df_all.head)
        target_index = df_headers.index("transferred_bytes")
        host_index = df_headers.index("host")
        interval_index = df_headers.index("interval")

        fig, axs = plt.subplots(len(delays), len(transport_algos), figsize=(10, 10))
        missing_data = 0
        for delay in delays:
            df_0 = df_all[df_all["delay"] == delay]
            for transport_algo in transport_algos:
                df1 = df_0[df_0["transport"] == transport_algo]
                axi = axs[delays.index(delay)][transport_algos.index(transport_algo)]
                axi.set_title(f"TCP {transport_algo} {delay}ms delay")

                # convert df to list of lists
                master_list = df1.values.tolist()
                # separate lists to host lists
                attacker_list = [x for x in master_list if x[host_index] == "h1"]
                normal_hosts = [f"h{i}" for i in range(2, 10)]
                normal_list = [x for x in master_list if x[host_index] in normal_hosts]

                # interval - string values
                intervals = [f"{t:.1f}-{t+1:.1f}" for t in range(test_time)]
                # interval - numerical values
                t_axis = [t + 1 for t in range(test_time)]

                # plot attacker data
                bytes_tx = []
                for interval in intervals:
                    interval_bytes = [
                        x[target_index]
                        for x in attacker_list
                        if x[interval_index] == interval
                    ][0]
                    bytes_tx.append(interval_bytes)
                axi.plot(t_axis, bytes_tx, label="attacker")

                # plot normal user average data
                bytes_tx = []
                for interval in intervals:
                    interval_bytes = [
                        x[target_index]
                        for x in normal_list
                        if x[interval_index] == interval
                    ]
                    interval_avg_bytes = int(sum(interval_bytes) / len(interval_bytes))
                    bytes_tx.append(interval_avg_bytes)
                axi.plot(t_axis, bytes_tx, label="normal user avg")

                # set labels
                axi.legend()
                axi.set_xlabel("time (seconds)")
                axi.set_ylabel("transferred bytes")

        plt.savefig(Path(zip_name + ".png"))
        # plt.show()
    except Exception as e:
        print(e)
    finally:
        subprocess.run(f"rm -rf {basedir}", shell=True)


if __name__ == "__main__":
    main2()
