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

import sys;

class SCIInterfaceMgr:
	def __init__(self,state):
		self.state = state;
		
	def loadInterfaces(self):
		config = self.state['config'];
		interface_string = config.get('interfaces');
		if(interface_string == None):
			return;
		interface_list = interface_string.split(",");
		interface_dict = dict();
		
		for ifc_base_name in interface_list:
			ifc_name = "scix.interfaces.%s"%(ifc_base_name.strip(),);
			try:
				__import__(ifc_name);
				interface_dict[ifc_name] = sys.modules[ifc_name].interface_object_type(self.state);
			except:
				print("Cannot load interface %s, error follows:"%(ifc_base_name));
				raise;
		self.state['interfaces'] = interface_dict;
	
