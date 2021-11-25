import os
import matplotlib.pyplot as plt
import pandas as pd

topology_name = "StandardTopo"
input_filename = "results/%s/data.csv" % topology_name
output_filename = "results/%s/output.png" % topology_name


def main():
    data = pd.read_csv(input_filename)
    data["norm_throughput"] = data["data_size"] / data["norm_time"]
    data["div_throughput"] = data["data_size"] / data["div_time"]
    data["dup_throughput"] = data["data_size"] / data["dup_time"]
    data["opt_throughput"] = data["data_size"] / data["opt_time"]

    ax = data.plot.line(
        x="num",
        y=["norm_throughput", "div_throughput", "dup_throughput", "opt_throughput"],
    )
    ax.set_xlabel("Parameter Value")
    ax.set_ylabel("Average Throughput (Bytes / s)")

    plt.savefig(output_filename)


if __name__ == "__main__":
    main()
