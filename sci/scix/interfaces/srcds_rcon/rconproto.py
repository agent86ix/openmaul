# This file is part of the OpenMAUL project
# Copyright (C) 2011 agent86.ego@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from twisted.internet.protocol import Factory, Protocol
from struct import pack,unpack
from binascii import hexlify, unhexlify
from time import sleep

class SourceRCONProtocol(Protocol):

	def __init__(self):
		self.auth = False;

	def connectionMade(self):
		peer_addr = self.transport.getPeer();
		host = peer_addr.host;
		blacklist = self.factory.blacklist;
		
		if(host in blacklist):
			if(blacklist[host] > 5):
				# too many failed attempts, drop the connection.
				self.transport.close();


	def dataReceived(self, data):
		debug = False;
		peer_addr = self.transport.getPeer();
		host = peer_addr.host;
		blacklist = self.factory.blacklist;
		
		if(host in blacklist):
			if(blacklist[host] > 5):
				# too many failed attempts, drop the connection.
				self.transport.close();
		(reqsize, reqid, reqtype)  = unpack("iii", data[0:12]);
		if(debug):
			print(hexlify(data));
			print("reqsize: %d, reqid: %d, reqtype: %d"%(reqsize, reqid, reqtype));
		if(self.auth == False or reqtype == 3):
			resid = 2; # SERVERDATA_AUTH_RESPONSE
			ressize = 10;
			resid = -1;
			resstatus = 2;
			if(reqtype == 3): # SERVERDATA_AUTH
				client_pwd = data[12:-2];
				if(client_pwd == self.factory.rcon_pwd):
					if(debug):
						print("Successful authorization.");
					resid = reqid;
					self.auth = True;
				else:
					if(host in blacklist):
						blacklist[host] += 1;
					else:
						blacklist[host] = 1;
					if(debug):
						print("failed authorization, '%s' != '%s'"%(client_pwd, self.factory.rcon_pwd));
					sleep(3);
					
			response = pack("iiibb", ressize, resid, resstatus, 0, 0);
			self.transport.write(response);
		else:
			data = data[12:];
			while(len(data) != 0):
				next_cmd_end_idx = data.find("\x00\x00");
				if(next_cmd_end_idx <= 0):
					return;
				client_cmd = data[:next_cmd_end_idx];
				data = data[next_cmd_end_idx+2+12:];
				if(self.factory.router):
					try:
						str_output = self.factory.router.routeCommand((peer_addr.host, peer_addr.port), client_cmd);
					except:
						str_output = "An internal error occurred while processing your command."
						ressize = 10+len(str_output);
						resstatus = 0; # SERVERDATA_RESPONSE_VALUE
						response = "".join((pack("iii", ressize, reqid, resstatus), str_output, pack("bb",0,0)));
						self.transport.write(response);
						raise;
					
					if(str_output == None):
						str_output = "Command complete.";
				else:
					str_output = "".join("Request: %s"%(client_cmd));
				ressize = 10+len(str_output);
				resstatus = 0; # SERVERDATA_RESPONSE_VALUE
				response = "".join((pack("iii", ressize, reqid, resstatus), str_output, pack("bb",0,0)));
				if(debug):
					print("Command response: %s"%(hexlify(response)));
				self.transport.write(response);
			if(debug):
				print("Transaction complete.\n");
			
	def connectionMade(self):
		pass;
		
class SourceRCONProtocolFactory(Factory):
	protocol = SourceRCONProtocol;
	
	def __init__(self, rcon_pwd, router=None):
		self.rcon_pwd = rcon_pwd;
		self.router = router;
		self.blacklist = dict();
