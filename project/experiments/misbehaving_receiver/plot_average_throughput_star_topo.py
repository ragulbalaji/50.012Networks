import os
import matplotlib.pyplot as plt
import pandas as pd

topology_name = "StarTopo"
input_filename = "results/%s/data.csv" % topology_name
norm_output_filename = "results/%s/norm_output.png" % topology_name
div_output_filename = "results/%s/div_output.png" % topology_name
dup_output_filename = "results/%s/dup_output.png" % topology_name
opt_output_filename = "results/%s/opt_output.png" % topology_name


def main():
    role_list = ["attacker", "h3", "h4", "h5", "h6", "h7", "h8", "h9", "h10"]
    data = pd.read_csv(input_filename)
    for i in ["norm", "div", "dup", "opt"]:
        for j in role_list:
            data["%s_%s_throughput" % (i, j)] = (
                data["data_size"] / data["%s_%s_time" % (i, j)]
            )
        data["%s_total_throughput" % i] = sum(
            data["%s_%s_throughput" % (i, j)] for j in role_list
        )

    role_columns = ["total_throughput"] + [item + "_throughput" for item in role_list]

    norm_ax = data.plot.line(
        x="num",
        y=["norm_" + item for item in role_columns],
    )
    norm_ax.set_xlabel("Parameter Value")
    norm_ax.set_ylabel("Average Throughput (Bytes / s)")

    plt.savefig(norm_output_filename)

    div_ax = data.plot.line(
        x="num",
        y=["div_" + item for item in role_columns],
    )
    div_ax.set_xlabel("Parameter Value")
    div_ax.set_ylabel("Average Throughput (Bytes / s)")

    plt.savefig(div_output_filename)

    dup_ax = data.plot.line(
        x="num",
        y=["dup_" + item for item in role_columns],
    )
    dup_ax.set_xlabel("Parameter Value")
    dup_ax.set_ylabel("Average Throughput (Bytes / s)")

    plt.savefig(dup_output_filename)

    opt_ax = data.plot.line(
        x="num",
        y=["opt_" + item for item in role_columns],
    )
    opt_ax.set_xlabel("Parameter Value")
    opt_ax.set_ylabel("Average Throughput (Bytes / s)")

    plt.savefig(opt_output_filename)


if __name__ == "__main__":
    main()
