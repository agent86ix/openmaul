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

import string, random
from twisted.internet import reactor
from twisted.internet.protocol import ProcessProtocol
from twisted.internet.defer import Deferred
from scicore.util import parseServer

class SCIUpdateProtocol(ProcessProtocol):
	def __init__(self, server_key, server_name, log):
		self.deferred = Deferred();
		self.server_key = server_key;
		self.log = log;
		self.server_name = server_name;
		
		
	def childDataReceived(self, childFD, data):
		data = data.replace("\r","");
		data_lines = data.split("\n");
		for line in data_lines:
			line = line.strip();
			if(len(line) == 0):
				continue;
			self.log.printStatus("[update %s]: %s"%(self.server_name, line));

	def processEnded(self, status):
		#print("process ended!");
		if(self.deferred):
			self.deferred.callback(self);
		
class SCIUpdatePI:
	def __init__(self, state):
		self.state = state;
		self.update_queue = dict();
		self.current_update = None;
		self.auth_key = None;
		self.auth_server_list = None;
		router = state['router'];
		router.registerRoute(self, ("update",));
		router.registerLocalRoute(self, ("autoupdate",));
	
	def processCommand(self, cmd, args):
		config = self.state['config']
		if(len(args) != 1):
			return "Usage: update <server>";
		
		if(cmd == "autoupdate"):
			all_servers = config.getServerList();
			if(args[0] in all_servers):
				server_list = [args[0]];
			else:
				return "Auto-update error, invalid server key: %s"%(args[0],);
		elif(args[0] != self.auth_key):
			all_servers = config.getServerList();
			server_name = args[0];
			server_key_list = parseServer(self.state, server_name);
			if(len(server_key_list) == 0):
				return "No server matched server name '%s'"%(server_name);
			auth_key = "".join(random.sample(string.letters+string.digits, 6))
			self.auth_key = auth_key;
			self.auth_server_list = server_key_list;
			server_names_list = list();
			for server_key in server_key_list:
				server = config.getServer(server_key);
				server_names_list.append(server['name']);
			return "***WARNING: Each server will shut down before it updates, \
if it is SCI controlled.\nDo NOT restart the server(s) until \
all updates are complete.\nWhen you are ready, proceed with the \
update by issuing the command: update %s\n\
Servers marked for update: %s"%(auth_key,", ".join(server_names_list));
		else:
			server_list = self.auth_server_list;
			self.auth_key = None;
			self.auth_server_list = None;
		
		rcon_result = "Server update request status:";
		for server_key in server_list:		
			server = config.getServer(server_key);
			if('update_cmd' not in server):
				rcon_result = "\n".join((rcon_result,"Can't update '%s' - no update command specified.."%(server['name'],)));
				continue;
			update_cmd = server['update_cmd'];
			if(server_key in self.update_queue or server_key == self.current_update):
				rcon_result = "\n".join((rcon_result,"Update process is already queued for '%s'."%(server['name'],)));
			else:
				self.update_queue[server_key] = (update_cmd,);
				rcon_result = "\n".join((rcon_result,"Server update for %s is now queued."%(server['name'],)));
		
		if(self.current_update == None and len(self.update_queue) > 0):	
			(server_key, (update_cmd,)) = self.update_queue.popitem();
			server = config.getServer(server_key);
			self.state['router'].routeLocalCommand("stop %s"%(server['name']));
			update_obj = SCIUpdateProtocol(server_key, server['name'], self.state['log']);
			update_obj.deferred.addCallback(lambda x, x_server_key: self.updateComplete(x_server_key), server_key);
			self.current_update = server_key;
			self.state['log'].printStatus("[update]: Starting update for %s, %d items left in queue."%(server['name'], len(self.update_queue)));
			try:
				p = reactor.spawnProcess(update_obj, update_cmd, (update_cmd,), env=None);
			except:
				self.state['log'].printStatus("[update %s]: Error starting update."%(server['name']));
				self.updateComplete(server_key);	

		return rcon_result
			
	def updateComplete(self, server_key):
		server = self.state['config'].getServer(server_key);
		self.state['log'].printStatus("[update %s]: Operation complete."%(server['name']));
		
		# Wait 1 second, in the event that the update stopped because the program is exiting.
		reactor.callLater(1, lambda x_server_name: self.state['router'].routeLocalCommand("start %s"%(x_server_name)), server['name']);
		
		self.current_update = None;
		if(len(self.update_queue) > 0):	
			(server_key, (update_cmd,)) = self.update_queue.popitem();
			server = self.state['config'].getServer(server_key);
			self.state['router'].routeLocalCommand("stop %s"%(server['name']));
			update_obj = SCIUpdateProtocol(server_key, server['name'], self.state['log']);
			update_obj.deferred.addCallback(lambda x, x_server_key: self.updateComplete(x_server_key), server_key);
			self.current_update = server_key;
			self.state['log'].printStatus("[update]: Starting update for %s, %d items left in queue."%(server['name'], len(self.update_queue)));
			try:
				p = reactor.spawnProcess(update_obj, update_cmd, (update_cmd,), env=None);
			except:
				self.state['log'].printStatus("[update %s]: Error starting update."%(server['name']));
				reactor.callLater(1, lambda x_server_key: self.updateComplete(x_server_key), server_key);
		#print(self.updates_in_progress);
