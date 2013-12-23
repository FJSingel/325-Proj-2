325-Proj-2
==========

Measures TTL and hop count to a remote server. Also calculates geographical distance for bonus.
This uses a binary search on the range of possible TTLs to reduce the number of requests required.

This module measures the TTL, hop count, and geographic distance to a remote host
Use of raw sockets will require elevated priviliges.
Running this on a network with private IPS (IE: 192.168.0.1) will yield an incorrect physical
 distance as freegeoip won't have a location for it.
The module used to parse freegeoip info was written by Victor Fontes and can be found
 here: https://github.com/victorfontes/python-freegeoip
Websites with multiple servers (like google) may return incorrect results.
This is because each request to such sites gets redirected to different servers each time.
If there are any routers that do not return ICMP packets on TTL=0 packets will also warp results.

An example usage:
      > sudo python binary_tracer.py whois.net
