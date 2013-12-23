"""
Created on Nov 12, 2013
@author: Frank Singel
FJS52@case.edu
This module measures the TTL, hop count, and geographic distance to a remote host
Use of raw sockets will require elevated privilidges
Running this on a network with private IPS (IE: 192.168.0.1) will yield an incorrect distance
as freegeoip won't have a location for it.
"""

import math
import socket
import sys
import time

import freegeoip

def main(dest_name):
	source_addr = gethostIP()
	dest_addr = socket.gethostbyname(dest_name)
	port = 33434
	ttl = 16
	max_hops = 0
	min_hops = 0
	target_hops = 0
	RTT = 0
	found = False
	print "Source: %s" % (source_addr)
	print "Destination: %s" % (dest_addr)

	while True:
		if not found: #look for it
			if ttl == 256:
				print "Maximum TTL reached. IP not found. Exiting."
				quit()

			curr_addr = connect(ttl, port, dest_name)

			#If target found, begin binary search
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
			recv_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.getprotobyname("icmp"))
			send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.getprotobyname("udp"))
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

				# print data of individual probe in format of TTL|Name|IP|RTT
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
					print "\nRTT = %sms" % (RTT)
					print "TTL = %s hops" % (max_hops)

					#calculate physical distances.
					src_response = freegeoip.get_geodata(source_addr)
					print "\nSource IP: %s" % source_addr
					print "Source Latitude: %s" % src_response["latitude"]
					print "Source Longitude: %s" % src_response["longitude"]

					dst_response = freegeoip.get_geodata(dest_addr)
					print "\nDestination IP: %s" % dest_addr
					print "Destination Latitude: %s" % dst_response["latitude"]
					print "Destination Longitude: %s" % dst_response["longitude"]
					print "Distance: %skm" % haversine(float(src_response["latitude"]),
														float(src_response["longitude"]), 
														float(dst_response["latitude"]),
														float(dst_response["longitude"]))
					break


def gethostIP():
	"""This returns the public IP address from where this is being called"""
	recv_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.getprotobyname("icmp"))
	send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.getprotobyname("udp"))
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

def connect(timetolive, port, dest_name):
	# open connections
	recv_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.getprotobyname("icmp"))
	send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.getprotobyname("udp"))
	send_socket.setsockopt(socket.SOL_IP, socket.IP_TTL, timetolive)		
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

	return curr_addr

if __name__ == "__main__":
	main(sys.argv[1])