

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
	

