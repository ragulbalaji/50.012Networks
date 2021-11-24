# Attacks on Congestion Control by a Misbehaving TCP Receiver

This folder contains scripts for replicating the results in the paper ["TCP congestion control with a misbehaving receiver"](https://dl.acm.org/doi/10.1145/505696.505704) by Savage, Cardwell, et al. (SIGCOMM 99'). This project was done for the [50.012](https://istd.sutd.edu.sg/undergraduate/courses/50012-networks) (Networks) class at SUTD. The attacks are slightly modified and repurposed for the topic of focus of our project. This custom TCP implementation can be facetiously referred to as "TCP Daytona", following the name used in the original paper.

## Result Reproduction

We have provided one single shell script that reproduces all three attacks in one run. To reproduce the results, follow the following steps:

We need to somehow use Python 2, since running the scripts in Python 3 will break some things for some reason.

> Some weird persistent errors encountered during experimentation include `ValueError: Incorrect type of value for field ack` and `ValueError: min() arg is an empty sequence`.

My suspicion is that this might involve the different Scapy library versions (and hence, different data output formatting).

Seems like the results are also variable as they are quite dependent on hardware configuration and settings. For our results, they are generated in the Ubuntu 14.04 virtual machine environment used for Lab 4.

The results here can either be replicated on an EC2 instance or in VirtualBox. If you still have your virtual machine from Lab 4, then you should be able to use it without any problems (though the EC2 instance usually provides cleaner results). Note that when you SSH into your machine, you probably want to use the `-Y` flag (and have an X server running), in order to view the generated graphs. Once logged in, run the following commands:

1. Clone the Git repository:

```bash
$ git clone https://github.com/ragulbalaji/50.012Networks.git
$ cd 50.012Networks
$ git checkout jamestiotio
$ cd project/experiments/misbehaving_receiver/
```

2. Run the one-line shell (with **sudo**).

```bash
$ sudo ./run.sh
```

The default network topology consists of two end hosts connected via one switch. Default link delay for each link is 375ms, which amounts to a total round-trip delay of 1.5s. The whole process takes about 1 minute to run per set parameter value.

5. After the shell script finishes, check out the reproduced plots in the `./plots` directory. There are three plots generated, "div.png", "dup.png" and "opt.png", corresponding to ACK division, DupACK spoofing, and Optimistic ACKing attacks, respectively.

## Customizations

Several parameters related to the attack are customizable. Add flags in `run.sh` after `python run_attack.py` to explore.

Use `--delay` to specify per link delay in ms. The value we use in our reproduction is 375ms. Remember that an estimated round-trip delay is 4 times this per link delay. Because Scapy (a _Python_ package) is slow (it takes around 40ms to send one packet), use a higher link delay to see more evident attack outcomes.

Use `--data-size` to specify the total amount of data to send before tearing down the connection (in kB). We use 60kB as specified in the paper. Note that the default ssthread for TCP is 64kB. The attacks are most effective before TCP switches to congestion avoidance. Moreover, since our implementation for DupACK spoofing and Optimistic ACKing attacks only sends ACK flood on the first received data segment. The attack might not last long enough to let the sender send all data in one shot.

See the section on "Attack Commands" for flags `--num-attack` (equivalent to `--num`) and `--opt-interval` (equivalent to `--interval`).

## TCP Reno Client Commands

We built our own TCP Client (Reno) with Scapy in Python. To see the attack in live, you can run `reno.py` and `attacker.py` in Mininet XTerms.

To run Mininet with XTerm windows (**for regular TCP sawtooth**, with limited link capacity):

```
$ sudo mn --custom mn.py --topo congestion --link tc -x
```

To run Mininet **for attacks** (with Mininet default link capacity, sufficiently large):

```
$ sudo mn --custom mn.py --topo standard --link tc -x
```

First, run receiver on host h2:

```
$ python reno.py --role receiver --host h2 --verbose
```

Then, run sender on host h1:

```
$ python reno.py --role sender --host h1 --verbose
```

You should be able to see the changes of the sender's congestion control state and cwnd in its XTerm output.

Besides `--role` and `--host`, `reno.py` also provides other flags to customize its behaviour:

- Use `--verbose` to log all sent and received packets in the terminal window. Regardless of this flag, the receiver's SEQ/ACK will be logged to "log.txt" or "attack_log.txt" if the receiver is an attacker.

- Use `--limit` to specify the amount of data the _sender_ would send (in kB). Both clients would tear down the connection when the limit is reached. So that data ping-pong would not go on forever.

- Use `--rtt` to specify the round-trip delay (in ms). For simplicity, our TCP implementation does not dynamically estimate the retransmission timeout (RTO). It is set to 4 times RTT statically and is default to 2s. Setting `--rtt` will set RTO accordingly, but RTO will not be shorter than 1s.

## TCP Reno (with Defense)

We also implemented several defense mechanisms with a 32-bit nonce. Each TCP segment will be sent with a randomly generated nonce. Each ACK has to reply with one nonce, and the ACK is only valid (for the data sender) if its nonce matches one of the sent segments' nonce. _One nonce is only valid for one ACK._

Run sender/receiver with defense mechanisms (nonce layer) on:

```
$ python reno_enhanced.py --role sender --host h1 --verbose
$ python reno_enhanced.py --role receiver --host h2 --verbose
```

You should see no difference in the behavior for regular TCP communication, but if you try to run any attack against `reno_enhanced.py`, you will get "invalid ACK" all the time and the sender does not blow up its congestion window.

## Attacker Commands

Instead of running `reno.py` in receiver mode, run `attacker.py` to mount receiver attacks.

To run ACK Division attacker on host h2:

```
$ python attacker.py --attack div --num 50 --host h2 --verbose
```

To run DupACK Spoofing attacker on host h2:

```
$ python attacker.py --attack dup --num 50 --host h2 --verbose
```

To run Optimistic ACKing attacker on host h2:

```
$ python attacker.py --attack opt --num 50 --interval 10 --host h2 --verbose
```

The parameter `--num` specifies how many divided, spoofed, or optimistic ACKs to send on the first received data segment. The parameter `--interval` specifies the time between two optimistic ACKs in the Optimistic ACKing attack.

## Plot the Sequence / Acknowledge Numbers

After running a regular TCP ping-pong **and** one of the attacks (div, dup, opt), you can generate the comparison plot for the attack you just ran by executing:

```
$ python plot.py --attack THE_ATTACK_NAME_YOU_JUST_RAN (div, dup, opt)
```

A regular run (_reno.py_ versus _reno.py_) outputs `log.txt`.
An attack run (_reno.py_ versus _attacker.py_) outputs `attack_log.txt`.
**Please rename `attack_log.txt` into `{div, dup, opt}_attack_log.txt` depending on the attack that you have run.**
`plot.py` requires both `log.txt` and `{div, dup, opt}_attack_log.txt` to function properly, because the plot it generates is a comparison plot.

The parameter `--save` saves the plot instead of displaying it, and the parameter `--output` specifies the output directory.

## Files Breakdown

- [run.sh](./run.sh) - This file runs the entire experiment, generating all of the network traces and all of the graphs.
- [opt-ack-defense.diff](./opt-ack-defense.diff) - This is our defense against optimistic ACK attacks for the lwIP stack, displayed as a patch.
- [reno_enhanced.py](./reno_enhanced.py) - This is our defense against all of the ACK-related attacks for TCP Reno. Defenses are implemented as per the discussion in the original paper.
- [reno.py](./reno.py) - This is a simple TCP server. When a client makes a connection, the server immediately sends a large stream of data. Upon sending the data, the server closes the connection.
- [attacker.py](./attacker.py) - This file contains three classes, each of which implements one of the attacks mentioned in the original paper.
- [run_attacks.py](./run_attacks.py) - This script creates the Mininet topology and runs the client and server, logging packets.
- [plot.py](./plot.py) - This script creates the ACK and data segment graphs based off of the packet captures.

## Acknowledgements

Heavy references and inspirations were taken from the following repositories:

- [https://github.com/kreamkorokke/cs244-final-project](https://github.com/kreamkorokke/cs244-final-project)
- [https://github.com/lowkeyboard/TCP-Congestion-Attack](https://github.com/lowkeyboard/TCP-Congestion-Attack)
- [https://github.com/rameshvarun/misbehaving-receiver](https://github.com/rameshvarun/misbehaving-receiver)
- [https://github.com/pavmeh/cs244_TCPDaytona](https://github.com/pavmeh/cs244_TCPDaytona)
- [https://bitbucket.org/AlexCid/opt-ack](https://bitbucket.org/AlexCid/opt-ack)
