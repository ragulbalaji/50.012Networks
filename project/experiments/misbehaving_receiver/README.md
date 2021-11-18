# Attacks on Congestion Control by a Misbehaving TCP Receiver

This folder contains scripts for replicating the results in the paper ["TCP congestion control with a misbehaving receiver"](https://dl.acm.org/doi/10.1145/505696.505704) by Savage, Cardwell, et. al. This project was done for the [50.012](https://istd.sutd.edu.sg/undergraduate/courses/50012-networks) (Networks) class at SUTD. The attacks are slightly modified and repurposed for the topic of focus of our project. This custom TCP implementation can be facetiously referred to as "TCP Daytona", following the name used in the original paper.

## Replicating Results

We need to somehow use Python 2, since running the scripts in Python 3 will break some things for some reason.

> Some weird persistent errors encountered during experimentation include `ValueError: Incorrect type of value for field ack` and `ValueError: min() arg is an empty sequence`.

My suspicion is that this might involve the different Scapy library versions (and hence, different data output formatting).

The results here can either be replicated on an EC2 instance or in VirtualBox. If you still have your virtual machine from Lab 4, then you should be able to use it without any problems (though the EC2 instance usually provides cleaner results). Note that when you SSH into your machine, you probably want to use the `-Y` flag (and have an X server running), in order to view the generated graphs. Once logged in, run the following commands.

```bash
cd misbehaving-receiver
sudo ./run-experiment.sh
```

The graphs should now be in the `graphs/` folder. The images that appear in our report are `graphs/opt-ack-lwip.png`, `graphs/opt-ack-lwip-defended.png`, and `graphs/opt-ack-kernel.png`. If you have X11 forwarding working, just use `xdg-open`. Otherwise, you should `scp -r` the folder.

## Files Breakdown

- [run-experiment.sh](./run-experiment.sh) - This file runs the entire experiment, generating all of the network traces and all of the graphs.
- [opt-ack-defense.diff](./opt-ack-defense.diff) - This is our defense against optimistic ACK attacks, displayed as a patch.
- [server.py](./server.py) - This is a simple TCP server. When a client makes a connection, the server immediately sends a large stream of data. Upon sending the data, the server closes the connection.
- [attackers/](./attackers) - This folder contains three scripts, each of which implements one of the attacks mentioned in the original paper.
- [runner.py](./runner.py) - This script creates the mininet topology and runs the client and server, logging packets.
- [create_graph.py](./create_graph.py) - This script creates the ACK and data segment graphs based off of the packet captures.

## Acknowledgements

Heavy references and inspirations were taken from the following repositories:

- [https://github.com/rameshvarun/misbehaving-receiver](https://github.com/rameshvarun/misbehaving-receiver)
- [https://bitbucket.org/AlexCid/opt-ack](https://bitbucket.org/AlexCid/opt-ack)
- [https://github.com/pavmeh/cs244_TCPDaytona](https://github.com/pavmeh/cs244_TCPDaytona)
