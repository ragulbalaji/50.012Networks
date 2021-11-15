#!/usr/bin/env python2
"""Data generator: sends data to one connected client forever, or until stopped."""

from argparse import ArgumentParser
import socket
import time
import sys
import struct
import os

BYTES_PER_ROUND = 20000

def parse_args():
	parser = ArgumentParser(description="Data generator")
	parser.add_argument('--port', '-p',
			    type=int,
			    help="Local port to listen to",
			    default=80)
	parser.add_argument('--ipaddr', '-i',
						type=str,
						help="Local ip address to bind to",
						default="localhost")
	parser.add_argument('--duration', '-d',
						type=int,
						help="Duration after which the stream stops",
						default=-1)
	parser.add_argument('--dir', 
						type=str,
						help="Directory in which to save the trace",
						default=None)
	return parser.parse_args()


def serve(ipaddr, port, directory, duration):
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	s.settimeout(5)
	timeval = struct.pack('ll', 5, 0)
	s.setsockopt(socket.SOL_SOCKET, socket.SO_SNDTIMEO, timeval)
	if directory is not None:
		try:
			os.makedirs(directory)
		except OSError:
			pass
	s.bind((ipaddr, port))
	s.listen(1)
	(conn, _) = s.accept()
	start = time.time()

	save_file = open(directory+"/%s.csv" % ipaddr, 'w+') if directory is not None else sys.stdout
	data_sent = 0
	while True:
		now = time.time()
		if duration > 0 and now - start >= duration:
			break
		try:
			conn.send("1"*BYTES_PER_ROUND)
		except:
			break
		data_sent += BYTES_PER_ROUND
		save_file.write("%f, %d\n" % (now-start, data_sent))
	conn.close()
	s.close()
	if save_file is not sys.stdout:
		save_file.close()

if __name__ == "__main__":
	args = parse_args()
	serve(args.ipaddr, args.port, args.dir, args.duration)

