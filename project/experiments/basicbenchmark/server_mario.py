#!/usr/bin/env python3

import socket
import argparse
import threading

parser = argparse.ArgumentParser(description='At your service')
parser.add_argument('--port',   type=int)
parser.add_argument('--tcp',    type=str)
parser.add_argument('--chunk',  type=int)
args = parser.parse_args()

HOST = ''
PORT = args.port
TCPALGO = args.tcp.encode()
CHUNKSIZE = args.chunk

class ThreadedServer(object):
	def __init__(self, host, port):
		self.host = host
		self.port = port
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_CONGESTION, TCPALGO)
		self.sock.bind((self.host, self.port))

	def listen(self):
		self.sock.listen(16)
		while True:
			client, address = self.sock.accept()
			client.settimeout(1)
			threading.Thread(target = self.listenToClient,args = (client,address)).start()

	def listenToClient(self, client, address):
		size = CHUNKSIZE
		while True:
			try:
				data = client.recv(size)
				if data:
					# Set the response to echo back the recieved data 
					response = data
					client.send(response)
				else:
					raise error('Client disconnected')
			except:
				client.close()
				return False

ThreadedServer(HOST,PORT).listen()