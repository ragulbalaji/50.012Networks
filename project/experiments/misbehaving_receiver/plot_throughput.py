import os
import matplotlib.pyplot as plt
import argparse
from attacker import check_attack_type

IMG_DIR = "./plots"


def read_lines(f, d):
    lines = f.readlines()[:-1]
    for line in lines:
        typ, time, num = line.split(",")
        if typ == "seq":
            d["seq"]["time"].append(float(time))
            d["seq"]["num"].append(float(num))
        elif typ == "ack":
            continue
        else:
            raise Exception("Unknown type read while parsing log file: %s" % typ)


def main():
    parser = argparse.ArgumentParser(
        description="Plot script for plotting sequence numbers."
    )
    parser.add_argument(
        "--save",
        dest="save_imgs",
        action="store_true",
        help="Set this to true to save images under specified output directory.",
    )
    parser.add_argument(
        "--attack",
        dest="attack",
        nargs="?",
        const="",
        type=check_attack_type,
        help="Attack name (used in plot names).",
    )
    parser.add_argument(
        "--output", dest="output_dir", default=IMG_DIR, help="Directory to store plots."
    )
    args = parser.parse_args()
    save_imgs = args.save_imgs
    output_dir = args.output_dir
    attack_name = args.attack

    if save_imgs and attack_name not in ["div", "dup", "opt"]:
        print("Attack name needed for saving plot figures.")
        return

    normal_log = {
        "seq": {"time": [], "num": []},
        "throughput": {"time": [], "num": []},
    }
    attack_log = {
        "seq": {"time": [], "num": []},
        "throughput": {"time": [], "num": []},
    }
    normal_f = open("log.txt", "r")
    attack_f = open("%s_attack_log.txt" % attack_name, "r")

    read_lines(normal_f, normal_log)
    read_lines(attack_f, attack_log)

    for i in range(1, len(normal_log["seq"]["time"])):
        normal_log["throughput"]["time"].append(normal_log["seq"]["time"][i])
        normal_log["throughput"]["num"].append(
            (normal_log["seq"]["num"][i] - normal_log["seq"]["num"][i - 1])
            / (normal_log["seq"]["time"][i] - normal_log["seq"]["time"][i - 1])
        )

    for i in range(1, len(attack_log["seq"]["time"])):
        attack_log["throughput"]["time"].append(attack_log["seq"]["time"][i])
        attack_log["throughput"]["num"].append(
            (attack_log["seq"]["num"][i] - attack_log["seq"]["num"][i - 1])
            / (attack_log["seq"]["time"][i] - attack_log["seq"]["time"][i - 1])
        )

    if attack_name == "div":
        attack_desc = "ACK Division"
    elif attack_name == "dup":
        attack_desc = "DupACK Spoofing"
    elif attack_name == "opt":
        attack_desc = "Optimistic ACKing"
    else:
        raise "Unknown attack type: %s" % attack_name
    norm_throughput_time, norm_throughput_num = (
        normal_log["throughput"]["time"],
        normal_log["throughput"]["num"],
    )
    atck_throughput_time, atck_throughput_num = (
        attack_log["throughput"]["time"],
        attack_log["throughput"]["num"],
    )
    plt.plot(norm_throughput_time, norm_throughput_num, label="Regular TCP Throughput")
    plt.plot(
        atck_throughput_time,
        atck_throughput_num,
        label="%s Attack Throughput" % attack_desc,
    )
    plt.legend(loc="upper left")
    plt.xlim(
        [
            0,
            max(
                (
                    max(norm_throughput_time),
                    max(atck_throughput_time),
                )
            )
            + 1.5,
        ]
    )
    plt.ylim(
        [
            0,
            max(
                (
                    max(norm_throughput_num),
                    max(atck_throughput_num),
                )
            )
            + 50000,
        ]
    )
    plt.xlabel("Time (s)")
    plt.ylabel("Throughput (Bytes / s)")

    if save_imgs:
        # Save images to plots/
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        plt.savefig(output_dir + "/" + attack_name + "_throughput")
    else:
        plt.show()

    normal_f.close()
    attack_f.close()


if __name__ == "__main__":
    main()
