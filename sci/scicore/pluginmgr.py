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

import sys, imp;
import scicore.reloader;

class SCIPluginMgr:
	def __init__(self,state):
		self.state = state;
		
	def loadPlugins(self):
		config = self.state['config'];
		plugin_string = config.get('plugins');
		if(plugin_string == None):
			return;
		plugin_list = plugin_string.split(",");
		plugin_dict = dict();
		for pi_base_name in plugin_list:
			pi_name = "scix.plugins.%s"%(pi_base_name.strip(),);
			try:
				__import__(pi_name);
				plugin_dict[pi_name] = sys.modules[pi_name].plugin_object_type(self.state);
			except:
				print("Cannot load plugin %s, error follows:"%(pi_base_name));
				raise;
				
		self.state['plugins'] = plugin_dict;
		
	def reloadPlugin(self, pi_base_name, unload_only=False):
		router = self.state['router'];
		plugin_dict = self.state['plugins'];
		pi_name = "scix.plugins.%s"%(pi_base_name.strip(),);
		try:
			if(pi_name in plugin_dict):
				router.unregisterHandler(plugin_dict[pi_name]);
				del plugin_dict[pi_name];
			if(unload_only == True):
				return;
			if(pi_name in sys.modules):
				scicore.reloader.reload(sys.modules[pi_name]);
			else:
				__import__(pi_name);
			plugin_dict[pi_name] = sys.modules[pi_name].plugin_object_type(self.state);
		except:	
			print("Error (un)loading plugin %s."%(pi_base_name));
			raise;
			
			
	
