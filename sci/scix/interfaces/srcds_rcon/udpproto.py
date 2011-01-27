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

from twisted.internet.protocol import DatagramProtocol
from struct import pack,unpack
from binascii import hexlify, unhexlify
from datetime import datetime;

class SourceUDPProtocol(DatagramProtocol):
	def __init__(self, state):
		self.config = state['config'];
		router = state['router'];
		router.registerHiddenRoute(self, ("logaddress_add","log", "logaddress_del"));
		log = state['log'];
		log.registerInterface(self);
		self.rlog_clients = dict();

	def startProtocol(self):
		
		config = self.config;
		hostname = config.get('rcon_hostname');
		if(hostname == None):
			hostname = "(No Hostname!)";
		
		port = config.get('rcon_port');
		if(port == None):
			port = 27015;
		else:
			port = int(port);
			
		mapname = config.get('rcon_mapname');
		if(mapname == None):
			mapname = 'map_not_set';
			
		gamedir = config.get('rcon_gamedir');
		if(gamedir == None):
			gamedir = 'default_dir';
			
		gamename = config.get('rcon_gamename');
		if(gamename == None):
			gamename = 'Default Game Name';
			
		appid = config.get('rcon_appid');
		if(appid == None):
			appid = 0x1ff;
		else:
			appid = int(appid);
		
		key = -1;    # always -1
		type = 73;   # always 'l'
		netver = 0x7; # constant for source servers
		
		hn_len = len(hostname)+1;
		mn_len = len(mapname)+1;
		gd_len = len(gamedir)+1;
		gn_len = len(gamename)+1;

		id1 = (appid&0xff);
		id2 = (appid&0xff00)>>8;
		
		
		curplayers = 0;
		maxplayers = 32;
		numbots = 0;
		dedicated = ord('d');
		os = ord('w'); 
		passreq = 0;
		secure = 1;
		gamever = "1.0.0.0";
		gv_len = len(gamever)+1;
		edf = 0x80;  # port number follows 
		
		self.status_response = pack("ibb%ds%ds%ds%dsBBbbbbbbb%dsBH"%(hn_len,mn_len,gd_len,gn_len,gv_len), 
			key, type, netver, hostname, mapname, gamedir, gamename,id1,id2,
			curplayers, maxplayers, numbots, dedicated, os, passreq, secure, gamever, edf, port);
		
	
	def datagramReceived(self, data, (host, port)):
		debug = False;
		try:
			#print("New packet len: %d, parsing first %d bytes."%( len(data), len(data[0:9])));
			type = ord(data[4]);
			#print("New request type: 0x%x"%(type));
			if(type != 0x57):
				challenge = unpack("I", data[5:9]);
		
		#(junk, type, challenge) = unpack("lcl", data[0:9]);
		except(Exception):
			if(debug):
				print("Failed to parse packet: %s (%s)"%(hexlify(data),hexlify(data[5:9])));
			
			return;
		if(debug):
			print("Parsed packet \"%s\", type = 0x%x"%(hexlify(data), type));
		response = None;
		if(type == 0x54):
			# print "Sending Source Engine Query reply to " . $socket->peerhost . ":" . $socket->peerport . "\n";
			# &replyStatus($socket, %server_status);
			response = self.status_response;
		elif(type == 0x57):
			# challenge request
			response = pack("ibi",-1,0x41,123456);
		elif(type == 0x56):
			# rules
			if(challenge == -1):
				response = pack("ibi",-1,0x41,0);
			else:
				# this isn't the right format...	
				response = pack("ibb",-1,0x45,0);
		elif(type == 0x55):
			# players
			if(challenge == -1):
				response = pack("ibi",-1,0x41,0);
			else:
				# this isn't the right format...
				response = pack("ibb",-1,0x44,0);
		else:
			if(debug):
				print("Unimplemented UDP query recv'd: 0x%x"%(type));
		
		if(response):  
			if(debug):
				print("Request handled successfully!");
			self.transport.write(response, (host, port));
		
	def connectionRefused(self):
		pass
	
	def processStatus(self, data):
		if(self.transport == None):
			return;
		timestamp = datetime.now().strftime("%m/%d/%Y - %H:%M:%S");
		output = "RL %s: %s\n"%(timestamp,data,);
		log_data = "".join((pack("i",-1), output));
		
		for idx in self.rlog_clients:
			client = self.rlog_clients[idx];
			self.transport.write(log_data, (client[0], int(client[1])));
	
			
	def processCommand(self, command, args):
		#self.printStatus("Router has routed to log...");
		if(command == "logaddress_add"):
			result = "Usage:  logaddress_add ip:port";
			if(args and len(args) > 0):
				logaddr = args[0].strip("\"")
				split_args = logaddr.split(":");
				if(len(split_args) == 2):
					ip = split_args[0].strip("\"");
					port = int(split_args[1].strip("\""));
					
					self.rlog_clients[logaddr] = (ip, port);
					return "logaddress_add:  %s"%(args[0]);
			return result;
		elif(command == "log"):
			return "Usage:  log < on | off >\ncurrently logging to: file, console, udp";
		elif(command == "logaddress_del"):
			logaddr = args[0].strip("\"")
			del(self.rlog_clients[logaddr]);
			return "logaddress_del:  %s"%(args[0]);
			
		
