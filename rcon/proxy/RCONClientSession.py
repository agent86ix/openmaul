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

#keep track of the pertinent variables for a client session
class RCONClientSession:
	def __init__(self, state, request):
		self.log_idx = {};
		self.activity_flag = 1;
		self.log_obj = state['server_log'];
		self.is_admin = False;
		
		
		self.state = state;
		self.maul_id = request['maul_id'];
		global_server_list = state['server_list'];
		password = request['password'];
		
		
		# get authorized server list for this maulid
		db = state['db_obj'].get_db();
		query = """select games from %s where maulid = %s and password=md5(%s)"""%(state['db_user_table_name'],"%s","%s")
		db.execute(query,(str(self.maul_id), password));
		result = db.fetchone();
		self.server_list = dict();
		if(result != None):
			games = result[0].split(",");
			for(game) in games:
				game = game.strip();
				print "user authorized for game %s"%(game);
				if(game == "*"):
					self.server_list = global_server_list;
					self.is_admin = True;
					break;
				for(id, server) in global_server_list.items():
					if('game' in server and server['game'] == game):
						self.server_list[id] = server;
					
		else:
			print "Failed to authorize user '%d'"%(maul_id);
			return;
		for (id, server) in self.server_list.items():
			self.log_idx[id] = 0;
		
	def get_client_log(self,server_id):
		if(server_id in self.log_idx):
			(log, new_log_idx) = self.log_obj.get_queued_log(server_id, self.log_idx[server_id]);
			self.log_idx[server_id] = new_log_idx;
			return log;
		else: 
			return "";
	def is_authorized(self, server_id):
		if(server_id in self.log_idx):
			return True;
		return False;
	def get_server_list(self):
		return self.server_list;
	def set_activity_flag(self, flag):
		self.activity_flag = flag;
	def get_activity_flag(self):
		return self.activity_flag;
