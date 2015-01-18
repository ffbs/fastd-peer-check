import socket
import sys
import os
import json
import yaml
from sets import Set
from Alfred import Channel



# Create a UDS socket
sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)



# Connect the socket to the port where the server is listening
sock_addr = '/tmp/fastd_status.socket'
print >>sys.stderr, 'connecting to %s' % sock_addr
try:
	sock.connect(sock_addr)
except socket.error, msg:
	print >>sys.stderr, msg
	sys.exit(1)


try:
	# Send data
	#message = 'This is the message.  It will be repeated.'
	#print >>sys.stderr, 'sending "%s"' % message
	#sock.sendall(message)
	try:
		f = open("nodes.yaml",'r')
		nodes = yaml.load(f.read())
		f.close()
		connected = Set(nodes["connected"])
		disconnected = Set(nodes["disconnected"])
	except:
		connected = Set([])
		disconnected = Set([])
		nodes = {'connected': [], "disconnected": []}


	channel = False
	try:
		channel = Channel(142)
		tmp = channel.request()
		alfred_data = []
		for t in tmp:
			connected = connected | Set(yaml.load(t["data"])["connected"])
			disconnected = disconnected | Set(yaml.load(t["data"])["disconnected"])
	except Exception, msg:
		print >>sys.stderr, msg
		print("alfred Failed")
		sys.exit(1)
	amount_received = 0
	#amount_expected = len(message)
	data = "start" 
	all_data = ""
	while data:
		data = sock.recv(100)
		all_data +=data
	#print >>sys.stderr, '"%s"' % all_data
	j = json.loads(all_data)
	for peer in j["peers"]:
		p = j["peers"][peer]
		if  p["connection"]:
			connected.add(p["name"].encode("utf8"))
		else:
			disconnected.add(str(p["name"]))
	disconnected = disconnected - connected
	nodes["connected"] = list(connected)
	nodes["disconnected"] = list(disconnected)
	yaml.safe_dump(nodes, file("nodes.yaml",'w'), encoding='utf-8', allow_unicode=True)
	#f = open("nodes.yaml",'w')
	#f.write(yaml.dump(nodes))
	#f.close()
	#print yaml.safe_dump(nodes, encoding='utf-8', allow_unicode=True)
	channel.set(yaml.safe_dump(nodes, encoding='utf-8', allow_unicode=True))
	print len(connected)
	print len(disconnected)

finally:
	print >>sys.stderr, 'closing socket'
	sock.close()
 
