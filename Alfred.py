import json 
import sys
import subprocess
import zlib
import binascii

class Channel:
	#TODO use the alfred socket /var/run/alfred.sock instead of the alfred binarys
	def __init__(self, channel):
		self.channel = channel

	def compress(self,data):
		return zlib.compress(data)

	def decompress(self,data):
		return zlib.decompress(data)

	def request(self):
		data = subprocess.check_output(["alfred", "-r", str(self.channel)])
		data = data.split('\n')
		dataList = []
		for entry in data:
			if entry != '':
				try:
					d = self.decompress(binascii.unhexlify(entry[24:-8]))
					dataList.append({"host":entry[3:20], "data":d})
				except:
					pass
		return dataList
	
	def set(self, data):
		data =self.compress(data)
		data =binascii.hexlify( data )
		echo = subprocess.Popen(('echo',data),stdout = subprocess.PIPE)
		alfred = subprocess.Popen(('alfred', '-s', str(self.channel)), stdin = echo.stdout, stdout = subprocess.PIPE )
		echo.stdout.close()
		output = alfred.communicate()[0]
		echo.wait()
