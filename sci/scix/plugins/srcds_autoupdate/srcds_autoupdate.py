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

import string, random, os
from binascii import unhexlify
from struct import unpack

from twisted.internet import reactor
from twisted.internet.protocol import DatagramProtocol
from twisted.internet.defer import Deferred

class SCIAutoUpdateCheckProtocol(DatagramProtocol):
	def __init__(self, master_host, loc_host, loc_port, version, gamename, appid):
		self.host = master_host;
		self.port = 27011;
		self.loc_host = loc_host;
		self.loc_port = int(loc_port);
		self.version = version;
		self.gamename = gamename;
		self.appid = appid;
		self.deferred = None;
		self.timeout = 0;
		self.needs_update = False;
		
	def startProtocol(self):
		# print("Watchdog started...");
		self.watchdog = reactor.callLater(5,self.handleTimeout)
		self.transport.connect(self.host, self.port);
		# 'q' is the byte to write to request a challenge
		self.transport.write("q");
	
	def datagramReceived(self, data, (host, port)):
		# print("Watchdog cancel.");
		if(ord(data[4]) == 0x73 and ord(data[5]) == 0x0a):
			# challenge recv'd!  send join command.
			challenge = unpack("I", data[6:10])[0];
			command = "".join((
				"\x30\x0A\\protocol\\7\\challenge\\%u\\players\\0\\max\\1"%(challenge,),
				"\\bots\\0\\gamedir\\%s\\map\\null\\password\\0\\os\\l\\lan\\0\\region"%(self.gamename,),
				"\\255\\gameport\\%i\\specport\\0\\dedicated\\1\\gametype\\null\\appid"%(self.loc_port,),
				"\\%s\\type\\d\\secure\\1\\version\\%s\\product\\%s\x0A"%(self.appid, self.version, self.gamename)
				));
			self.transport.write(command);
		elif(ord(data[4]) == 0x4f):
			# out of date message, this is what we're looking for!
			self.transport.stopListening();
			self.watchdog.cancel();
			self.needs_update = True;
			if(self.deferred != None):
				self.deferred.callback(self);
	
	def handleTimeout(self):
		#print("Update watchdog fired - timeout");
		self.transport.stopListening();
		self.timeout = 1;
		if(self.deferred != None):
			# print("firing callback...");
			self.deferred.callback(self);
		
class SRCDSAutoUpdate:
	def __init__(self, state):
		self.state = state;
		self.appid_dict = None;
		self.master_host = "";
		self.debug = False;
		self.launchUpdateCheck();
		
	def launchUpdateCheck(self):
		d = reactor.resolve("hl2master.steampowered.com");
		d.addCallback(lambda x: self.resolveComplete(x));
	
	def resolveComplete(self, master_host):
		self.master_host = master_host;
		reactor.callLater(1, self.executeUpdateCheck);
		
	def executeUpdateCheck(self):
		if(self.debug == True):
			print("Resolved master as: %s"%(self.master_host,))
		config = self.state['config'];
		server_list = config.getServerList();
		self.autoupdate_dict = dict();
		loc_host = config.get('ip');
		
		for server_key in server_list:
			server = config.getServer(server_key);
			if('autoupdate' not in server or server['autoupdate'] != '1'):
				if(self.debug == True):
					print("Skipping %s, not marked for autoupdate"%(server_key));
				continue;
			gamename = None;
			version = None;
			appid = None;
			try:
				# open file
				inffile = open(os.path.join(server['dir'],"steam.inf"),"r");
				
				# read game directory, app id, and version
				for line in inffile:
					(key, value) = line.split("=");
					if(key == "PatchVersion"):
						version = value.strip();
					elif(key == "ProductName"):
						gamename = value.strip();
					elif(key == "appID"):
						appid = value.strip();
					elif(self.debug == True):
						print("server %s, Bad key: %s"%(server_key, key));
			except:
				if(self.debug == True):
					print("Error while reading steam.inf file");
				
			if(gamename == None or version == None or appid == None):
				if(self.debug == True):
					print("[aupdate %s]: Can't read steam.inf!"%(server_key));
				continue;
			# is appid unique?
			autoupdate_key = "%s/%s/%s"%(appid,gamename,version);
			if(autoupdate_key not in self.autoupdate_dict):
				loc_port = random.randint(40000,60000);
				update_checker = SCIAutoUpdateCheckProtocol(self.master_host, loc_host, loc_port, version, gamename, appid);
				update_checker.deferred = Deferred();
				update_checker.deferred.addCallback(lambda x, x_autoupdate_key, x_update_checker: self.updateCheckCallback(x_autoupdate_key, x_update_checker), autoupdate_key, update_checker);
				self.autoupdate_dict[autoupdate_key] = list();
				# create new SCIAutoUpdateCheckProtocol instance
				reactor.listenUDP(int(loc_port), update_checker, config.get('ip'));
			self.autoupdate_dict[autoupdate_key].append(server_key);
		reactor.callLater(10*60,self.launchUpdateCheck);
		
	def updateCheckCallback(self, autoupdate_key, update_checker):
		log = self.state['log'];
		router = self.state['router'];
		if(autoupdate_key in self.autoupdate_dict):
			if(update_checker.needs_update == True):
				for server_key in self.autoupdate_dict[autoupdate_key]:
					server = self.state['config'].getServer(server_key);
					log.printStatus("[aupdate %s]: Master server says this instance is out of date.  Queuing for update..."%(server['name']))
					log.printStatus(router.routeLocalCommand("autoupdate %s"%(server_key)));
			elif(self.debug == True):
				print("Autoupdate timeout, assuming up to date.");
			del(self.autoupdate_dict[autoupdate_key]);
