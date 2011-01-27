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
from twisted.internet import reactor
from twisted.internet.defer import Deferred
from scicore.util import parseServer
from scix.plugins.common import SCIXPlugin
		
class SCIServerConfigPI(SCIXPlugin):
	def __init__(self, state):
		self.state = state;
		router = state['router'];
		router.registerRoute(self, ("cfgget","cfgset"));
	
	def processCommand(self, cmd, args):
		config = self.state['config']
		if(cmd == "cfgget" and len(args) != 2):
			return "Usage: %s <server> <option>"%(cmd,);
		if(cmd == "cfgset" and len(args) < 3):
			return "Usage: %s <server> <option> <value>"%(cmd,);
					
		server_name = args[0];
		server_list = parseServer(self.state, server_name);
		# print server_list
		if(len(server_list) == 0):
			return "No server matched server name '%s'"%(server_name);
		
		option = args[1];
		if(cmd == "cfgset"):
			value = " ".join(args[2:]).strip().replace(";","");
			if(value[0] == "\"" and value[-1] == "\""):
				value = value[1:-1];
		# this would match when there are unbalanced " marks, although I'm not 100% sure
		# which way I want to go here:
		# ^\s*(\w*)\s+(\"{0,1})(.*)\2\s*$
		cfg_searcher = re.compile(r"^\s*(\w*)\s+(\"{0,1})((\\.|[^\"])*)\2\s*$", re.IGNORECASE);
		
		output = "[%s] Config query results:"%(cmd,);
		
		for server_key in server_list:
			server = config.getServer(server_key);
			if("%s_allow"%(cmd,) in server):
				allowed_cmd_list = server["%s_allow"%(cmd,)].split(",");
				map(str.strip, allowed_cmd_list);
				if(option not in allowed_cmd_list):
					output = "\n".join((output, "[%s %s]: You may not modify this option for this server."%(cmd, server['name'])));
					continue;
			else:
				output = "\n".join((output, "[%s %s]: You may not modify the server.cfg for this server."%(cmd, server['name'])));
				continue;
			
			success = False;
			cfgfile_name = os.path.join(server['dir'], "cfg", "server.cfg");
			cfgfile_new_name = os.path.join(server['dir'], "cfg", "server.cfg.tmp");
			try:
				cfgfile_old = open(cfgfile_name, 'r');
				if(cmd=="cfgset"):
					cfgfile_new = open(cfgfile_new_name, "w+");
				else:
					cfgfile_new = None;
			except:
				output = "\n".join((output, "[%s %s]: File system error trying to open config file."%(cmd, server['name'])));
				continue;
				
			for line in cfgfile_old:
				cur_match = cfg_searcher.match(line);
				if(cur_match == None):
					continue;
				#print("Read option '%s', value '%s'"%cur_match.group(1,3));
				if(cur_match.group(1) == option):
					success = True;
					cur_result = cur_match.group(3);
					if(cmd == "cfgget"):
						output = "\n".join((output, "[%s %s]: Current value of '%s': %s"%(cmd, server['name'], option, cur_result)));
						break;
					elif(cmd == "cfgset"):
						output = "\n".join((output, "[%s %s]: Update OK!  Previous value of '%s': %s"%(cmd, server['name'], option, cur_result)));
						cfgfile_new.write("%s \"%s\"\n"%(option, value))
				elif(cmd=="cfgset"):
					cfgfile_new.write(line);

					
			if(success == False):
				if(cmd=="cfgget"):
					output = "\n".join((output, "[%s %s]: Could not find option %s in the config file!"%(cmd, server['name'], option)));
				else:
					cfgfile_new.write("%s \"%s\"\n"%(option, value))
					output = "\n".join((output, "[%s %s]: Added %s to the config file, with value %s"%(cmd, server['name'], option, value)));
			cfgfile_old.close();
			if(cfgfile_new != None):
				cfgfile_new.close();
				try:
					os.remove("%s.old"%(cfgfile_name));
					os.rename(cfgfile_name, "%s.old"%(cfgfile_name));
					os.rename(cfgfile_new_name, cfgfile_name);
				except:
					output = "\n".join((output, "[%s %s]: ERROR overwriting config file!"%(cmd, server['name'])));
		return output;
				
		
