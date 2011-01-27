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

from twisted.python.rebuild import rebuild;
from twisted.internet import reactor;
import sys;

class SCIBasePI:
	def __init__(self, state):
		self.state = state;
		state['router'].registerRoute(self, ("help","plugin"));
		
	def processCommand(self, cmd, args):
		config = self.state['config'];
		if(cmd == "plugin"):
			if(args == None or len(args) != 2):
				return "[plugin]: Usage: %s <load/unload/reload> <plugin name>"%(cmd,);
			plugin_mgr = self.state['pluginmgr'];
			if(args[0] == "load" or args[0] == "reload"):
				plugin_mgr.reloadPlugin(args[1]);
				return "[plugin]: Plugin load complete."
			elif(args[0] == "unload"):
				plugin_mgr.reloadPlugin(args[1], unload_only = True);
				return "[plugin]: Plugin unload complete."
			else:
				return "[plugin]: Usage: %s <load/unload/reload> <plugin name>"%(cmd,);
			
		elif(cmd == "help"):
			commands = self.state['router'].cmd_dict.keys();
			commands.sort();
			commands_str = ", ".join(commands);
			return "Available commands: %s"%(commands_str);

