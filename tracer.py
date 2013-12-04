"""
Created on Nov 12, 2013
@author: Frank Singel
FJS52@case.edu
This module measures the TTL and hop count to a remote host
"""

# from struct import unpack
import socket
import sys
import time

def main(dest_name):
	port = 33434
	dest_addr = socket.gethostbyname(dest_name)
	icmp = socket.getprotobyname("icmp")
	udp = socket.getprotobyname("udp")
	ttl = 1
	max_hops = 255
	RTT = 0

	print "Destination: %s" % (dest_addr)

	while True:
		# open connections
		recv_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)
		send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, udp)
		send_socket.setsockopt(socket.SOL_IP, socket.IP_TTL, 255)
		recv_socket.bind(("", port))
		recv_socket.settimeout(10)
		start_time = time.time()
		send_socket.sendto("", (dest_name, port))
		curr_addr = None
		curr_name = None
		try:
			#Throw away the packet into _ and extract IP
			_, curr_addr = recv_socket.recvfrom(1024)
			end_time = time.time()
			curr_addr = curr_addr[0]
			try:
				#Try to get host name by IP
				curr_name = socket.gethostbyaddr(curr_addr)[0]
			except socket.error:
				#If it has no name, just use it's IP
				curr_name = curr_addr
		except socket.timeout:
			print "Socket timed out"
		except socket.error:
			print "Socket error"
		finally:
			send_socket.close()
			recv_socket.close()

		# print data
		if curr_addr is not None:
			RTT = end_time-start_time
			curr_host = "%s (%s) %fs" % (curr_name, curr_addr, RTT)
		else:
			curr_host = "*"
		print "%d\t%s" % (ttl, curr_host)

		ttl += 1

		# break if useful
		if curr_addr == dest_addr or ttl > max_hops:
			print "RTT = %ss" % (RTT)
			print "TTL = %ss" % (ttl)
			break

if __name__ == "__main__":
	main(sys.argv[1])

	# HOST = "google.com"	#remote host name
	# PORT = 9001

	# s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	# s.connect((HOST, PORT))
	# s.sendall('Hello, world')
	# data = s.recv(1024)
	# s.close()
	# print 'Received', repr(data)

	# print socket.SOCK_DGRAM
	# #setsockopt() to change TTL field of datagram
	# #send it with socket.sendto()
	"""
	Questions:
	1. How do you know if your TTL is too small?
		You get an ICMP datagram signifying this.

	2. How do you know it's too long?
		You need to figure it out through binary searching. Half the TTL until it stops working,
		then you know it's somewhere in that range. Search this range recursively.

	3. How do you match ICMP responses with probes?
		.

	4. List reasons you might not get an answer.
		Data Corruption
		If the router wants to remain anonymous
		If target doesn't exist		
	"""