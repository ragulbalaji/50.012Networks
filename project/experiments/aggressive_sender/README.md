# Aggressive Sender

Aggressive Sender experiments are built using Mininet. We simulate two networks with star and tree topology respectively.

## Dependencies

-   Ubuntu 14.04
-   Python 2.7
-   [Mininet](https://pypi.org/project/mininet/)
-   [iPerf2](https://iperf.fr/iperf-doc.php)

## Code

### Experiment on Star Topology:

-   Main Experiment Code: [star/AggroTest.py](star/AggroTest.py)

### Experiment on Tree Topology:

-   Tree Topology Defenition: [src/topo_tree_py2.py](src/topo_tree_py2.py)
-   Main Experiment Code: [src/exp_tree_tcp_py2.py](src/exp_tree_tcp_py2.py)

```bash
sudo python2 src/exp_tree_tcp_py2.py
```

Experimental results will be saved as a zip file in which containing all experimental artifacts

To graph for a set of experiments (a zip file), modify [results/graph.py](results/graph.py) at Line 357 to match the name of the zip file. Then run:

```bash
python3 results/graph.py
```

Some of the graphs can be found in:

-   [results/exp4/README.md](results/exp4/README.md)
-   [results/exp5/README.md](results/exp5/README.md)
-   [results/exp6/README.md](results/exp6/README.md)
