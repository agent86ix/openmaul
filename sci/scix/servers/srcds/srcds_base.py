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

import string, random, re, os
from binascii import unhexlify
from twisted.internet import reactor
from twisted.internet.protocol import ProcessProtocol, DatagramProtocol
from twisted.internet.defer import Deferred

class SrcdsPingProtocol(DatagramProtocol):
	def __init__(self, host, port):
		self.host = host;
		self.port = int(port);
		self.deferred = None;
		self.timeout = 0;
		
	def startProtocol(self):
		# print("Watchdog started...");
		self.watchdog = reactor.callLater(10,self.handleTimeout)
		self.transport.connect(self.host, self.port);
		self.transport.write(unhexlify("FFFFFFFF55FFFFFFFF"));
	
	def datagramReceived(self, data, (host, port)):
		# print("Watchdog cancel.");

		self.transport.stopListening();
		self.watchdog.cancel();
		if(self.deferred != None):
			self.deferred.callback(self);
	
	def handleTimeout(self):
		# print("Watchdog fired - timeout");
		self.transport.stopListening();
		self.timeout = 1;
		if(self.deferred != None):
			# print("firing callback...");
			self.deferred.callback(self);
		

class SrcdsServerBase(object):
	def __init__(self, state, server_key, server_dict):
		self.deferred = None;
		self.server_key = server_key;
		self.server_dict = server_dict;
		self.log = state['log'];
		self.timeout_count = 0;
		self.nextping = None;
		self.deferred = Deferred();
		self.checkMapArg();
		self.launchInit();
	
	def checkMapArg(self):
		if(self.server_dict['server_args'].find("+map ") == -1):
			cfgfile_name = os.path.join(self.server_dict['dir'], "cfg", "server.cfg");
			try:
				cfgfile = open(cfgfile_name, 'r');
			except:
				self.log.printStatus("[server %s]: No map specified in server args, and can't open server.cfg.  Server may not start up properly!"%(self.server_dict['name']));
				return;
			mapcyclefile = "mapcycle.txt"
			cfg_searcher = re.compile(r"^\s*(\w*)\s+(\"{0,1})((\\.|[^\"])*)\2\s*$", re.IGNORECASE);
			for line in cfgfile:
				cur_match = cfg_searcher.match(line);
				if(cur_match == None):
					continue;
				if(cur_match.group(1) == "mapcyclefile"):
					mapcyclefile = cur_match.group(3);
					break;
			mapfile = None;
			try:
				mapfile = open(os.path.join(self.server_dict['dir'], mapcyclefile), 'r');
			except:
				self.log.printStatus("[server %s]: No map specified in server args, and can't open mapcyclefile %s.  Server may not start up properly!"%(self.server_dict['name'], mapcyclefile));
				return;
			mapname = mapfile.readline().strip();
			self.server_dict['server_args'] = " ".join((self.server_dict['server_args'], "+map", mapname));
			self.log.printStatus("[server %s]: Added '+map %s' to server args."%(self.server_dict['name'], mapname));
		
	def connectionMade(self):
		self.nextping = reactor.callLater(120, self.pingStart);

	def pingStart(self):
		if(("ip" not in self.server_dict) or ("port" not in self.server_dict)):
			self.log.printStatus("[server %s]: No 'ip' or 'port' in config file for this server, network monitoring disabled."%(self.server_dict['name'],))
			return;
		self.pingproto = SrcdsPingProtocol(self.server_dict['ip'], self.server_dict['port']);
		self.pingproto.deferred = Deferred();
		self.pingproto.deferred.addCallback(self.pingComplete);
		reactor.listenUDP(0, self.pingproto);
	
	def pingComplete(self, junk):
		if(self.nextping == None):
			self.log.printStatus("[server %s]: Aborting ping, server has terminated."%(self.server_dict['name'],));
			return;
		self.nextping = None;
		if(self.pingproto.timeout == 1):
			self.timeout_count = self.timeout_count +1;
			if(self.timeout_count >= 3):
				self.log.printStatus("[server %s]: Server failed to respond to 3 pings, auto-restarting."%(self.server_dict['name'],))
				self.killServer();
				return;
			else:
				self.log.printStatus("[server %s]: Server failed to respond to a ping, %d/3 retries."%(self.server_dict['name'],self.timeout_count))
		else:
			self.timeout_count = 0;
		self.pingproto = None;
		# print("Ping complete, restarting...");
		self.nextping = reactor.callLater(60, self.pingStart);

	def processEnded(self, status): 
		self.log.printStatus("[server %s]: Server has stopped."%(self.server_dict['name']));
		#print("process ended!");
		if(self.nextping != None):
			try:
				self.nextping.cancel();
			except:
				pass;
			self.nextping = None;
		if(self.deferred != None):
			self.deferred.callback(self);
			self.deferred = None;
		
