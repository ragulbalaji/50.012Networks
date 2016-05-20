#!/usr/bin/python
"""Data generator : sends data to one connect client forever, or until stopped."""

from argparse import ArgumentParser
import socket
import time
import sys

BYTES_PER_ROUND = 4096

parser = ArgumentParser(description="Data generator")
parser.add_argument('--port', '-p',
                    type=int,
                    help="Local port to listen to",
                    default=80)
parser.add_argument('--duration', '-d',
				 	type=int,
				 	help="Duration after which the stream stops",
				 	default=-1)
parser.add_argument('--dir', 
					type=str,
					help="Directory in which to save the trace",
					default=None)

# Expt parameters
args = parser.parse_args()


def serve(port):
	while True:
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		s.bind(("localhost", port))
		s.listen(1)
		(conn, _) = s.accept()
		start = time.time()
		save_file = open(args.dir+"/%f.csv" % start, 'a+') if args.dir is not None else sys.stdout
		
		save_file.write("time, sent\n")

		data_sent = 0

		while True:
			now = time.time()
			if args.duration > 0 and now - start >= args.duration:
				break
			conn.send("1"*BYTES_PER_ROUND)
			data_sent += BYTES_PER_ROUND
			save_file.write("%f, %d\n" % (now-start, data_sent))

		# Could do something cleaner. Have to wait for all the data to get sent
		time.sleep(2)
		conn.close()
		s.close()
		if save_file is not sys.stdout:
			save_file.close()

if __name__ == "__main__":
	serve(args.port)