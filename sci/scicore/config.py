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

import ConfigParser, os;
from twisted.internet import reactor;

class SCIConfig:
	def __init__(self, config_file_name):
		if(config_file_name[-1] == config_file_name[0] == '"'):
			# doing a 'stat' operation in Windows with a quoted
			# pathname fails, although actually OPENING the file
			# does not.  Sigh.
			config_file_name = config_file_name[1:-1];
		self.config_file_name = config_file_name; 
		# print self.config_file_name;
		self.old_mtime = os.stat(self.config_file_name).st_mtime;
		self.trap_dict = dict();
		self.server_trap_list = list();
		self.debug = True;
		self.load();
		
	def get(self, keyid):
		if(keyid in self.config_dict):
			return self.config_dict[keyid];
		else:
			return None;
	
	def getServer(self, server_key):
		if(server_key in self.server_dict):
			return self.server_dict[server_key];
		else:
			return None;
	
	def getServerList(self):
		return self.server_dict.keys();
	
	def reloadServer(self, server_key):
		try:
			config_obj = ConfigParser.ConfigParser();
			config_obj.read(self.config_file_name);
			cur_server_dict = dict();
			if(config_obj.has_section(server_key)):
				for (key, value) in config_obj.items(server_key):
					cur_server_dict[key] = value;
				self.server_dict[server_key] = cur_server_dict;
				return cur_server_dict;
			else:
				self.server_dict[server_key] = None;
				return None;
		except:
			return None;
	
	def load(self):
		config_obj = ConfigParser.ConfigParser();
		config_obj.read(self.config_file_name);
		config_dict = dict();

		# Read out the 'global' section
		for (key, value) in config_obj.items("global"):
			config_dict[key] = value;
		config_obj.remove_section("global");

		server_dict = dict();
		for section in config_obj.sections():
			cur_server = dict()
			for (key, value) in config_obj.items(section):
				cur_server[key] = value;
			server_dict[section] = cur_server;

		self.server_dict = server_dict;
		self.config_dict = config_dict;
		reactor.callLater(5, self.checkRefresh);
	
	def checkRefresh(self):
		cur_mtime = os.stat(self.config_file_name).st_mtime;
		if(cur_mtime > self.old_mtime):
			if(self.debug):
				print("Config file changed!");
			self.old_mtime = cur_mtime;
			old_server_dict = self.server_dict;
			old_config_dict = self.config_dict;
			
			config_obj = ConfigParser.ConfigParser();
			config_obj.read(self.config_file_name);
			config_dict = dict();
			
			updated_keys_list = list();
			
			for (key, value) in config_obj.items("global"):
				config_dict[key] = value;
				if(key not in self.config_dict or self.config_dict[key] != value):
					if(self.debug):
						print("global key %s changed"%(key,));
					updated_keys_list.append(key);
			
			for(key, value) in self.config_dict.items():
				if(key not in config_dict):
					if(self.debug):
						print("global key %s removed"%(key,));
					updated_keys_list.append(key);
				
			
			config_obj.remove_section("global");
						
			server_dict = dict();
			added_server_list = list();
			removed_server_list = list();
			updated_server_list = list();
			
			for server_key in config_obj.sections():
				cur_server = dict();
				old_server = None;
				# is this server new?
				if(server_key not in self.server_dict):
					added_server_list.append(server_key);
				else:
					old_server = self.server_dict[server_key];

				for (key, value) in config_obj.items(server_key):
					if(old_server != None):
						if(key not in old_server or old_server[key] != value):
							# new key or changed value
							if(key == 'type'):
								# type is a special case: treat it as if the server
								# was removed and re-added.
								if(server_key in updated_server_list):
									updated_server_list.remove(server_key);
								added_server_list.append(server_key);
								removed_server_list.append(server_key);								
							elif((server_key not in updated_server_list) and
								(server_key not in added_server_list) and
								(server_key not in removed_server_list)):
								updated_server_list.append(server_key);
					cur_server[key] = value;
				
				# last check for update - did a key get removed?
				if(old_server and server_key not in updated_server_list):
					for (key, value) in old_server.items():
						if(key not in cur_server):
							updated_server_list.append(server_key);						
						
				server_dict[server_key] = cur_server;

			# check for removed servers
			for server_key in old_server_dict.keys():
				if(server_key not in server_dict):
					removed_server_list.append(server_key);


			self.server_dict = server_dict;
			self.config_dict = config_dict;
			
			# config is finalized, fire any traps
			
			# global config section traps
			for key in updated_keys_list:
				if(key in self.trap_dict):
					for (callback, args, kw) in self.trap_dict[key]:
						callback(key, old_server_dict[key], new_server_dict[key], args, kw);
			
			# server specific traps
			
			# server removed
			for server_key in removed_server_list:
				old_server = old_server_dict[server_key];
				new_server = None;
				for (trap_key, trap_type, callback, args, kw) in self.server_trap_list:
					
					if(((trap_key == None) or (trap_key == server_key)) and
					   ((trap_type == None) or 
					    ('type' in old_server and (trap_type == old_server['type']))
					   )
					  ):
						callback(server_key, old_server, new_server, args, kw);			
			# server updated
			for server_key in updated_server_list:
				old_server = old_server_dict[server_key];
				new_server = server_dict[server_key];
				for (trap_key, trap_type, callback, args, kw) in self.server_trap_list:
					if(((trap_key == None) or (trap_key == server_key)) and
					   ((trap_type == None) or 
					    ('type' in new_server and (trap_type == new_server['type']))
					   )
					  ):
						callback(server_key, old_server, new_server, args, kw);
				
			# server added
			for server_key in added_server_list:
				old_server = None;
				new_server = server_dict[server_key];
				for (trap_key, trap_type, callback, args, kw) in self.server_trap_list:
					if(((trap_key == None) or (trap_key == server_key)) and
					   ((trap_type == None) or 
					    ('type' in new_server and (trap_type == new_server['type']))
					   )
					  ):
						callback(server_key, old_server, new_server, args, kw);
					
			
		reactor.callLater(5, self.checkRefresh);
		
	# callback args: config_key, old_value, new_value, args, kw
	def registerTrap(self, key, callback, *args, **kw):
		if(key in self.trap_dict):
			self.trap_dict[key].append((callback, args, kw));
		else:
			self.trap_dict[key] = [(callback, args, kw),];
			
	# callback args: server_key, old_server, new_server, args, kw
	def registerServerTrap(self, server_type, server_key, callback, *args, **kw):
		self.server_trap_list.append((server_key, server_type, callback, args, kw));
		
