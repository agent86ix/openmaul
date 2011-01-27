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

def parseServer(state, arg, server_list=None):
	if(server_list == None):
		server_list = state['config'].getServerList();
	arg = arg.strip();
	match_list = list();
	for server_key in server_list:
		server = state['config'].getServer(server_key);
		name = server['name'];
		if(arg == "*" or name.find(arg) != -1):
			match_list.append(server_key);
	return match_list;
	

