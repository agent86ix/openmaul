from twisted.internet import reactor
from twisted.internet.defer import Deferred
from twisted.internet.protocol import ClientCreator
from SourceUDPClientProtocol import SourceUDPClientProtocol
from SourceRCONClientProtocol import SourceRCONClientProtocol
from RCONLogHandler import RCONLogHandler
from twisted.internet.error import *

class RCONServerManager:
	def __init__(self, state):
		self.state = state;
		self.debug = False;
		reactor.callLater(1, self.updateServerList, 0);
		reactor.callLater(1, self.checkServers);
		self.server_queue = [];
		for (server_id, server) in self.state['server_list'].items():
			self.server_queue.append(server)
		# init this high, so that we update names quickly
		self.update_count = 59;
		self.loadServers();
	
	def loadServers(self):
		db = self.state['db_obj'].get_db();
		server_list = dict();
		query = """select address, port, rcon_password, name, game from %s"""%(self.state['db_server_table_name']);
		db.execute(query)
		if(db.rowcount != 0):
			while(True):
				result = db.fetchone();
				if(result == None):
					break;
				ip,port,passwd,desc,game = result
				if(ip is None):
					break;
				server_list[len(server_list)] = dict({'ip':ip, 'port':str(port), 
					'pass': passwd, 'desc':desc, 'game':game, 'logging':0, 'activity_flag':0,
					'player_count':0, 'player_names':[]});
		self.state['server_list'] = server_list;
		self.state['server_log'] = RCONLogHandler(server_list, 32*1024);
		
	
	def logaddressConnect(self, rconproto):
		pass;	
	
	def rconFailed(self, server, reason):
		reason_type = reason.trap(ConnectError, ConnectionRefusedError, TimeoutError);
		print("(ServerManager) RCON connection failed to %s (%s:%s), reason: %s"% (server['desc'], 
			server['ip'], str(server['port']),reason.getErrorMessage()));
		server['logging'] = 0;
		
	def checkServers(self):
		for (id,server) in self.state['server_list'].items():
			player_count = 0;
			if('player_count' in server):
				try:
					player_count = int(server['player_count']);
				except:
					pass;
			if((int(server['logging']) != 1) or (int(server['activity_flag']) <= 0 and player_count > 0)):
				print("Idle server '%s': (lg=%d,af=%d) checking logaddress"%( server['desc'],int(server['logging']),int(server['activity_flag'])))
				# kick off RCON connection to logaddress_add
				cmd = "logaddress_add %s:%s"%(self.state['logip'], int(self.state['logport']));
				c = ClientCreator(reactor, SourceRCONClientProtocol, server, 0, cmd);
				d = c.connectTCP(server['ip'], int(server['port']), 5, (self.state['bindip'], 0)); #.addCallback(self.logaddressConnect)
				d.addErrback(lambda reason,bad_server: self.rconFailed(bad_server, reason), server);
			else:
				server['activity_flag'] -= 1 # = 0;
		reactor.callLater(60, self.checkServers);
	
	def updateServerList(self, result=0):
		if(len(self.server_queue) == 0):
			for (server_id, server) in self.state['server_list'].items():
				self.server_queue.append(server);
			reactor.callLater(5, self.updateServerList);
			if(self.debug):
				print("Update cycle complete, sleeping...");
			self.update_count += 1;
			if(self.update_count == 61):
				self.update_count = 0;
			return;
		
		flags = SourceUDPClientProtocol.QUERY_PLAYER_INFO;
		if(self.update_count == 60):
			flags = flags | SourceUDPClientProtocol.QUERY_SERVER_INFO;
		server = self.server_queue.pop();
		if(self.debug):
			print("Updating server %s"%(server['desc'],));
		proto = SourceUDPClientProtocol(server, flags);
		#proto.debug = True;
		proto.deferred = Deferred();
		proto.deferred.addCallback(self.updateServerComplete);
		proto.deferred.addErrback(self.updateServerComplete);
		reactor.listenUDP(int(self.state['statusport']), proto, self.state['bindip']);
	
	def updateServerComplete(self, result=0):
		reactor.callLater(.1, self.updateServerList);
		
	
	
