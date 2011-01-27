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

class RCONServerMgr:
	def __init__(self, state):
		self.state = state;
	
	def update_server_list(self):
		db = self.state['db_obj'].get_db();
		server_list = dict();
		query = """select address, port, rcon_password, name, game from maul_rcon_servers_union"""
		db.execute(query)
		if(db.rowcount != 0):
			while(True):
				result = db.fetchone();
				if(result == None):
					break;
				ip,port,passwd,desc,game = result
				if(ip is None):
					break;
				server_list[len(server_list)] = dict({'ip':ip, 'port':str(port), 'pass': passwd, 'desc':desc, 'game':game});
		self.state['server_list'] = server_list;

	def update_server_info(self):
		pass;
	

