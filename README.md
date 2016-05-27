Setup
-----
First, launch an Amazon AWS instance, with the vanilla CS244 Mininet AMI (CS244-Spr15-Mininet or ami-cba48cfb). **Important** : make sure to choose at least a c3.large instance as the simulation performance is heavily CPU-dependent. Also, if possible, choose an instance in the us-west-2c region.

Then, get the code for the experiment from Bitbucket and cd into the directory:

	git clone https://AlexCid@bitbucket.org/AlexCid/opt-ack.git
	cd opt-ack


Also, install gnuplot-pox to be able to generate the plot:

	sudo apt-get update
	sudo apt-get install gnuplot-nox

Finally, run the script:

	sudo ./run.sh

And relax while the experiment is taking place ! (5-10 minutes in total)

After this, the graph is available under ~/opt-ack/results/output.png

Note : Please ignore any "*** gave up after 3 retries" messages. This seems to be a Mininet bug when stopping the network.

Troubleshooting
---------------

Check that window scaling is enabled:

    cat /proc/sys/net/ipv4/tcp_window_scaling