#!/bin/bash

sudo apt-get update
sudo apt-get -y install python2.7 python-pip python-matplotlib python-numpy python-scapy mininet openvswitch-testcontroller
sudo cp /usr/bin/ovs-testcontroller /usr/bin/ovs-controller

sudo modprobe tcp_vegas
sudo modprobe tcp_cubic
