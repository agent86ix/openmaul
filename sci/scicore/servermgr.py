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

import string, random, sys
from twisted.internet import reactor
import scicore.reloader

from scicore.util import parseServer

from datetime import datetime


class SCIServerMgr:
	def __init__(self, state):
		self.state = state;
		router = state['router'];
		router.registerRoute(self, ("start","stop","restart","status"));
		config = state['config'];
		self.config = config;
		self.server_status = dict();
		for server_key in config.getServerList():
			self.startServer(server_key);
		reactor.addSystemEventTrigger('before', 'shutdown', lambda: self.handleShutdown()) 
	
	def handleShutdown(self):
		for server_key in self.server_status.keys():
			svr_dict = self.config.getServer(server_key);
			if(self.server_status[server_key]['obj'] != None):
				server_obj = self.server_status[server_key]['obj'];
				if(hasattr(server_obj, 'persists')):
					if(server_obj.persists):
						continue;					
			self.stopServer(server_key);

	def startServer(self, server_key):
		svr_dict = self.config.getServer(server_key);
		if(server_key in self.server_status):
			if(self.server_status[server_key]['obj'] != None):
				self.state['log'].printStatus("[server %s]: Server is running already.  Use restart instead."%(svr_dict['name'],));
				return False;
				
		# reload server config...
		svr_dict = self.config.reloadServer(server_key);
		if(svr_dict == None):
			if(server_key in self.server_status):
				del self.server_status[server_key];
			self.state['log'].printStatus("[server %s]: Unable to start this server, It does not appear to be configured."%(svr_dict['name'],));
			return False;
		if(('type' not in svr_dict) or ('server_cmd' not in svr_dict) or ('server_args' not in svr_dict)):
			self.state['log'].printStatus("[server %s]: Unable to start this server, server type, command or args missing."%(svr_dict['name'],));
			return False;
		
		if('disabled' in svr_dict and int(svr_dict['disabled']) != 0):
			self.state['log'].printStatus("[server %s]: This server is marked as disabled in the configuration file."%(svr_dict['name'],));
			return;
			
		server_type = "scix.servers.%s"%(svr_dict['type'].strip(),);
		try:
			if(server_type not in sys.modules):
				__import__(server_type);
			else:
				scicore.reloader.reload(sys.modules[server_type]);
			server_obj_type = sys.modules[server_type].getServerObjType(svr_dict);
			server_obj = server_obj_type(self.state, server_key, svr_dict);
		except:
			print("Cannot load server %s, unable to import module type (%s)."%(svr_dict['name'], server_type));
			raise;
		
		
		cmd = svr_dict['server_cmd'];
		arg_str = svr_dict['server_args'];
		arg_list = [cmd];
		arg_list.extend(arg_str.strip().split(" "));
		
		server_obj.deferred.addCallback(lambda x, y: self.serverExit(y), server_key);
		
		server_status = dict();
		server_status['obj'] = server_obj;
		server_status['restart'] = 1;
		server_status['laststart'] = datetime.now();
		
		self.server_status[server_key] = server_status;
		
		self.state['log'].printStatus("[server %s]: Starting server."%(svr_dict['name'],));
		# p = reactor.spawnProcess(server_obj, cmd, arg_list, env=None);
		server_obj.launchServer(cmd, arg_list);
		return True;
		
	def stopServer(self, server_key):
		svr_dict = self.config.getServer(server_key);
		if(server_key not in self.server_status):
			self.state['log'].printStatus("[server %s]: Can't stop this server, it was never started."%(svr_dict['name'],));
			return False;
		
		
		server_status = self.server_status[server_key];
		if(server_status['obj'] == None):
			self.state['log'].printStatus("[server %s]: Server is already stopped."%(svr_dict['name'],));
			return True;
			
		server_status['restart'] = 0;
		server_status['obj'].killServer();		
		self.state['log'].printStatus("[server %s]: Stopping server."%(svr_dict['name'],));
		return True;
		
		
	def restartServer(self, server_key):
		if(server_key not in self.server_status):
			self.startServer(server_key);
			return True;
		svr_dict = self.config.getServer(server_key);
		server_status = self.server_status[server_key];
		server_status['restart'] = 1;
		if(server_status['obj'] == None):
			self.startServer(server_key);
		else:
			server_status['obj'].killServer();		
		self.state['log'].printStatus("[server %s]: Server restart requested."%(svr_dict['name'],));
		return True;
		
	def getStatus(self, server_key):
		state = '(status unknown)';
		last_start = '(unknown)';
		svr_dict = self.config.getServer(server_key);
		if(server_key not in self.server_status):
			state = 'down';
			last_start = 'never';
		else:
			server_status = self.server_status[server_key];
			if(server_status['obj'] == None):
				state = 'down';
			else:
				state = 'up';
			if('laststart' in server_status):
				try:
					last_start = server_status['laststart'].strftime("%A, %B %d %Y %I:%M%p")
				except:
					pass;
			
		return "%s: currently %s, last started %s"%(svr_dict['name'], state, last_start)
	
	def processCommand(self, cmd, args):
		if(args == None and cmd == "status"):
			server_name = '*';
		elif(len(args) != 1):
			return "Usage: %s <server>"%(cmd);
		else:
			server_name = args[0];
			
		server_list = parseServer(self.state, server_name);
		if(len(server_list) == 0):
			return "No server matched server name '%s'"%(server_name);
			
		if(cmd == "start"):
			for server_key in server_list:
				self.startServer(server_key);		
				
		elif(cmd == "stop"):
			for server_key in server_list:
				self.stopServer(server_key);
		elif(cmd == "restart"):
			for server_key in server_list:
				self.restartServer(server_key);
		elif(cmd == "status"):
			result = "";
			for server_key in server_list:
				result = "\n".join((result,self.getStatus(server_key)));
			return result;
		
		return "Operation complete, check log for details";		
			
	def serverExit(self, server_key):
		
		# print(self.server_status);
		if(server_key not in self.server_status.keys()):
			# print("not in server_status...");
			return;
		server_status = self.server_status[server_key];
		# print(server_status);
		server_status['obj'] = None;
		svr_dict = self.config.getServer(server_key);
		if(server_status['restart'] == 1):
			self.state['log'].printStatus("[server %s]: Server has shut down, and will be auto-restarted."%(svr_dict['name'],));
			reactor.callLater(5, lambda x_server_key: self.startServer(x_server_key), server_key);
