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
from scicore.util import parseServer

class SrcdsMapcycle:
	
	def __init__(self, state):
		self.state = state;
		state['router'].registerRoute(self, ("mapcycle_list","mapcycle_del", "mapcycle_add"));
	
	def getMapcycleFile(self, server):
		mapcyclefile = "mapcycle.txt"
		cfgfile_name = os.path.join(server['dir'], "cfg", "server.cfg");
		try:
			cfgfile = open(cfgfile_name, 'r');
		except:
			self.state['log'].printStatus("[mapcycle %s]: Can't find server.cfg, the SCI config needs to be updated."%(server['name']));
			return mapcyclefile;
		
		cfg_searcher = re.compile(r"^\s*(\w*)\s+(\"{0,1})((\\.|[^\"])*)\2\s*$", re.IGNORECASE);
		for line in cfgfile:
			cur_match = cfg_searcher.match(line);
			if(cur_match == None):
				continue;
			if(cur_match.group(1) == "mapcyclefile"):
				mapcyclefile = cur_match.group(3);
				break;
		return mapcyclefile;
		
	def readMapcycleFile(self,server, mapcyclefile):
		mapfile = None;
		try:
			mapfile = open(os.path.join(server['dir'], mapcyclefile), 'r');
		except:
			self.state['log'].printStatus("[mapcycle %s]: Can't read old mapcyclefile %s."%(server['name'], mapcyclefile));
			return None;
		maplist = [];
		for line in mapfile:
			mapname = line.strip();
			maplist.append(mapname);
		mapfile.close();
		return maplist;
		
	def writeMapcycleFile(self, server, mapcyclefile, map_list):
		mapfile = None;
		try:
			mapfile = open(os.path.join(server['dir'], mapcyclefile), 'w');
			mapfile.write(os.linesep.join(map_list));
			mapfile.close();
		except:
			self.state['log'].printStatus("[mapcycle %s]: Can't write new mapcyclefile %s."%(server['name'], mapcyclefile));
			return False;
		return True;
		
		
	def processCommand(self, cmd, args):
		config = self.state['config'];
		if(cmd == "mapcycle_list"):
			if(len(args) != 1):
				return "[mapcycle]: Usage: mapcycle_list <server>";
			else:
				server_name = args[0];
				server_list = parseServer(self.state, server_name);
				if(len(server_list) == 0):
					return "[mapcycle]: No server matched server name '%s'"%(server_name);
				result = "[mapcycle]: Map cycle, by server:";
				for server_key in server_list:
					server = config.getServer(server_key);
					mapcyclefile = self.getMapcycleFile(server);
					if(mapcyclefile == None):
						result = "\n".join((result, "[mapcycle %s]: Unable to complete mapcycle operation.  Check the log for details."%(server['name'])));
						continue;
					map_list = self.readMapcycleFile(server, mapcyclefile);
					if(map_list == None):
						result = "\n".join((result, "[mapcycle %s]: Unable to complete mapcycle operation.  Check the log for details."%(server['name'])));
						continue;
					map_text = "";
					i = 1;
					for mapname in map_list:
						map_text = "%s #%d) %s,"%(map_text, i, mapname);
						i = i+1;
					result = "\n".join((result, "[mapcycle %s]: Current map cycle: %s"%(server['name'], map_text)));
				return result;
		elif(cmd == "mapcycle_add" or cmd == "mapcycle_del"):
			if(len(args) < 2):
				return "[mapcycle]: Usage: %s <server> <map>";
			else:
				server_name = args[0];
				server_list = parseServer(self.state, server_name);
				if(len(server_list) == 0):
					return "[mapcycle]: No server matched server name '%s'"%(server_name);
				result = "[mapcycle]: Mapcycle update results, by server:";
				target_map = args[1];
				for server_key in server_list:
					server = config.getServer(server_key);
					mapcyclefile = self.getMapcycleFile(server);
					if(mapcyclefile == None):
						result = "\n".join((result, "[mapcycle %s]: Unable to complete mapcycle operation.  Check the log for details."%(server['name'])));
						continue;
					map_list = self.readMapcycleFile(server, mapcyclefile);
					if(map_list == None):
						result = "\n".join((result, "[mapcycle %s]: Unable to complete mapcycle operation.  Check the log for details."%(server['name'])));
						continue;
					if(cmd=="mapcycle_del"):
						if(target_map[0] == '#'):
							try:
								target_map_idx = int(target_map[1:]) - 1;
								if(len(map_list) <= target_map_idx):
									result = "\n".join((result, "[mapcycle %s]: Invalid map number specified."%(server['name'])));
									continue;
								else:
									del map_list[target_map_idx];
									if(self.writeMapcycleFile(server, mapcyclefile, map_list) == True):
										result = "\n".join((result, "[mapcycle %s]: Removed map %s."%(server['name'], target_map)));
									else:
										result = "\n".join((result, "[mapcycle %s]: Error occured writing map file.  Check the logs for more information."%(server['name'])));
									continue;
							except:
								pass;
						if(target_map not in map_list):
							result = "\n".join((result, "[mapcycle %s]: Map (%s) not in the mapcycle."%(server['name'],target_map)));
							continue;
						map_list.remove(target_map);
						if(self.writeMapcycleFile(server, mapcyclefile, map_list) == True):
							result = "\n".join((result, "[mapcycle %s]: Removed map %s."%(server['name'], target_map)));
						else:
							result = "\n".join((result, "[mapcycle %s]: Error occured writing map file.  Check the logs for more information."%(server['name'])));
					elif(cmd == "mapcycle_add"):
						map_list.append(target_map);
						if(self.writeMapcycleFile(server, mapcyclefile, map_list) == True):
							result = "\n".join((result, "[mapcycle %s]: Added map %s."%(server['name'], target_map)));
						else:
							result = "\n".join((result, "[mapcycle %s]: Error occured writing map file.  Check the logs for more information."%(server['name'])));

				return result;
