from pathlib import Path
from typing import List

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def main(datafile: Path, topo_name: str):
    with datafile.open() as f:
        lines = f.readlines()
        lines = [line.strip() for line in lines]

    reno_start_idx = lines.index("reno")
    cubic_start_idx = lines.index("cubic")

    reno_data = lines[reno_start_idx:cubic_start_idx]
    cubic_data = lines[cubic_start_idx:]

    reno_data = parse_tcp_data(reno_data)
    cubic_data = parse_tcp_data(cubic_data)

    plot_tcp_data(reno_data, save_name=f"v6_reno_{topo_name}.png")
    plot_tcp_data(cubic_data, save_name=f"v6_cubic_{topo_name}.png")


def parse_tcp_data(lines):
    header = [
        "protocol",
        "recv_link",
        "norm_link",
        "atkr_link",
        "user_data",
        "atkr_data",
    ]
    all_data = [header]

    protocol = lines[0]

    for line in lines[1:]:
        if line.startswith("recvlink"):
            recv_link = int(line.split()[1])
        if line.startswith("normal"):
            norm_link = int(line.split()[3])
        elif line.startswith("dict_keys"):
            ...
        elif line.startswith("attacker"):
            atkr_link = int(line.split()[2])
        elif line.startswith("data"):
            user_data = int(line.split()[1])
            total = int(float(line.split()[2][6:]))
            atkr_data = total - user_data

            data = [protocol, recv_link, norm_link, atkr_link, user_data, atkr_data]
            all_data.append(data)

    return all_data


def plot_tcp_data(data: List[list], save_name: str = "gragh.png"):
    df = pd.DataFrame(data[1:], columns=data[0])

    all_recv_links = list(df["recv_link"].unique())
    all_norm_links = list(df["norm_link"].unique())

    fig, axs = plt.subplots(len(all_recv_links), len(all_norm_links), figsize=(16, 12))

    for recv_link in all_recv_links:
        df_0 = df[df["recv_link"] == recv_link]
        for norm_link in all_norm_links:
            df_1 = df_0[df_0["norm_link"] == norm_link]
            df_1.sort_values(by="atkr_link", inplace=True)
            print(df_1.head())
            ax_i = axs[all_recv_links.index(recv_link)][all_norm_links.index(norm_link)]
            ax_i.set_title(f"recv_link: {recv_link} norm_link: {norm_link}")
            ax_i.plot(df_1["atkr_link"], df_1["user_data"], label="user_data")
            ax_i.plot(df_1["atkr_link"], df_1["atkr_data"], label="atkr_data")

            ax_i.legend()
            ax_i.set_xlabel("atkr_link")
            ax_i.set_ylabel("transferred_bytes")

    plt.savefig(save_name)


if __name__ == "__main__":
    # "v5_star_infra1000_8hosts.txt"
    datafile = Path("v6_star_more.txt")
    assert datafile.is_file()
    main(datafile, "star")

    # datafile = Path("v5_tree_infra1000_8hosts.txt")
    # assert datafile.is_file()
    # main(datafile, "tree")
