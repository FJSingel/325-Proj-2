"""
Created on Nov 12, 2013
@author: Frank Singel
FJS52@case.edu
This module measures the TTL and hop count to a remote host
"""

import socket

def main():
	HOST = "google.com"	#remote host name
	PORT = 9001

	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.connect((HOST, PORT))
	s.sendall('Hello, world')
	data = s.recv(1024)
	s.close()
	print 'Received', repr(data)

	print socket.SOCK_DGRAM
	#setsockopt() to change TTL field of datagram
	#send it with socket.sendto()


if __name__ == "__main__":
	main()