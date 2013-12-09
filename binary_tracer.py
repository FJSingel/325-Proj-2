"""
Created on Nov 12, 2013
@author: Frank Singel
FJS52@case.edu
This module measures the TTL and hop count to a remote host
"""

import math
import socket
import sys
import time

import freegeoip

def gethostIP():
	"""This returns the public IP address from where this is being called"""
	icmp = socket.getprotobyname("icmp")
	udp = socket.getprotobyname("udp")
	recv_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)
	send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, udp)
	send_socket.setsockopt(socket.SOL_IP, socket.IP_TTL, 1)
	recv_socket.bind(("", 33434))
	recv_socket.settimeout(10)
	send_socket.sendto("", ("google.com", 33434))
	_, curr_addr = recv_socket.recvfrom(1024)
	return curr_addr[0]

def haversine(lat1, lon1, lat2, lon2):
	"""
	Calculates the haversine distance between 2 points in km
	d = asin(sqrt(sin2((lat2-lat1)/2)+cos(lat1)cos(lat2)sin2((long2-long1)/2)))
	"""
	# lat = math.sin(math.sin((lat2/180-lat1/180)/2))
	# lon = math.cos(lat1/180)*math.cos(lat2/180)*math.sin(math.sin((lon2/180-lon1/180)/2))
	# print lat
	# print lon
	# d = 2*6371*math.asin(math.sqrt(math.fabs(lat+lon)))
	# print d
	r = 6371 #in km
	dlat = math.radians(lat2-lat1)
	dlon = math.radians(lon2-lon1)
	lat1 = math.radians(lat1)
	lat2 = math.radians(lat2)
	a = (math.sin(dlat/2) * math.sin(dlat/2) + 
		math.sin(dlon/2) * math.sin(dlon/2) * math.cos(lat1) * math.cos(lat2))
	c = 2*math.atan2(math.sqrt(a), math.sqrt(1-a))
	d = r * c
	return d


def main(dest_name):
	port = 33434
	source_addr = gethostIP()
	dest_addr = socket.gethostbyname(dest_name)
	icmp = socket.getprotobyname("icmp")
	udp = socket.getprotobyname("udp")
	ttl = 16
	max_hops = 0
	min_hops = 0
	target_hops = 0
	RTT = 0
	found = False

	print "Source: %s" % (source_addr)
	print "Destination: %s" % (dest_addr)

	# while True:
		
	# 	# open connections
	# 	recv_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)
	# 	send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, udp)
	# 	send_socket.setsockopt(socket.SOL_IP, socket.IP_TTL, ttl)
	# 	# send_socket.setsockopt(socket.SOL_IP, socket.IP_TTL, 32)
		
	# 	recv_socket.bind(("", port))
	# 	recv_socket.settimeout(10)
	# 	start_time = time.time()
	# 	send_socket.sendto("", (dest_name, port))
	# 	curr_addr = None
	# 	curr_name = None

	# 	try:
	# 		#Throw away the packet into _ and extract IP
	# 		_, curr_addr = recv_socket.recvfrom(1024)
	# 		end_time = time.time()
	# 		curr_addr = curr_addr[0]
	# 		try:
	# 			#Try to get host name by IP
	# 			curr_name = socket.gethostbyaddr(curr_addr)[0]
	# 		except socket.error:
	# 			#If it has no name, just use it's IP
	# 			curr_name = curr_addr
	# 	except socket.timeout:
	# 		print "Socket timed out"
	# 	except socket.error:
	# 		print "Socket error"
	# 	finally:
	# 		send_socket.close()
	# 		recv_socket.close()

	# 	# print data
	# 	if curr_addr is not None:
	# 		RTT = end_time-start_time
	# 		curr_host = "%s (%s) %fs" % (curr_name, curr_addr, RTT)
	# 	else:
	# 		curr_host = "*"
	# 	print "%d\t%s" % (ttl, curr_host)

	while True:
		if not found: #look for it
		
			# open connections
			recv_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)
			send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, udp)
			send_socket.setsockopt(socket.SOL_IP, socket.IP_TTL, ttl)
			# send_socket.setsockopt(socket.SOL_IP, socket.IP_TTL, 32)
			
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

			if curr_addr == dest_addr:
				max_hops = ttl
				min_hops = ttl/2
				print "Initial server found with ttl = %i" % (ttl)
				print "Beginning Binary search of ttls from %i to %i\n" % (min_hops, max_hops)
				found = True
			else:
				ttl *= 2
				print "Server not found. Doubling TTL to %i." % (ttl)
		else: #Now start binary searching
			
			# open connections
			recv_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)
			send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, udp)
			send_socket.setsockopt(socket.SOL_IP, socket.IP_TTL, (max_hops+min_hops)/2)
			
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
					RTT = (end_time-start_time)*1000
					curr_host = "%s (%s) %fms" % (curr_name, curr_addr, RTT)
				else:
					curr_host = "*"
				print "%d\t%s" % ((min_hops+max_hops)/2, curr_host)

				if curr_addr == dest_addr: #You found it in the range. Check lower
					max_hops = (min_hops+max_hops)/2
					print "Found server-Checking ttl from %i to %i." % (min_hops, max_hops)
				else: #Not in range. Check higher.
					min_hops = (min_hops+max_hops)/2
					print "Server not found-Checking ttl from %i to %i." % (min_hops, max_hops)

				# break if search over
				if min_hops+1 == max_hops: #Binary search over. Now return 
					print "RTT = %sms" % (RTT)
					print "TTL = %s hops" % (max_hops)
					src_response = freegeoip.get_geodata(source_addr)
					print "\nSource Location: %s" % source_addr
					print "Source Latitude: %s" % src_response["latitude"]
					print "Source Longitude: %s" % src_response["longitude"]

					dst_response = freegeoip.get_geodata(dest_addr)
					print "\nDestination Location: %s" % dest_addr
					print "Destination Latitude: %s" % dst_response["latitude"]
					print "Destination Longitude: %s" % dst_response["longitude"]
					print "Distance: %skm" % haversine(float(src_response["latitude"]),
														float(src_response["longitude"]), 
														float(dst_response["latitude"]),
														float(dst_response["longitude"]))
					break

if __name__ == "__main__":
	main(sys.argv[1])

	"""
	Questions:
	1. How do you know if your TTL is too small?
		You get an ICMP datagram signifying this.

	2. How do you know it's too long?
		You need to figure it out through binary searching. Half the TTL until it stops working,
		then you know it's somewhere in that range. Search this range recursively.

	3. How do you match ICMP responses with probes?
		You just match the IP addresses. ICMP datagrams also contain the original UDP packet that
		was sent to it.

	4. List reasons you might not get an answer.
		Data Corruption
		If the router wants to remain anonymous
		If target doesn't exist		
	"""