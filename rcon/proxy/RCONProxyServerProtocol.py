import socket, random, string, sys;
import simplejson as json
from SourceRCONClientProtocol import SourceRCONClientProtocol
from RCONClientSession import RCONClientSession
from twisted.internet import reactor
from twisted.internet.defer import Deferred
from twisted.internet.protocol import ClientCreator, DatagramProtocol
from twisted.internet.error import *
#the main 'listen' loop that waits on sockets

class RCONProxyServerProtocol(DatagramProtocol):
	
	def __init__(self, state):
		self.state = state;
		state['client_dict'] = dict();
		self.debug = False;
		self.forbidden_cmds = state['forbidden_cmds'].split(',');

	def checkPlayers(self):
		client_dict = self.state['client_dict'];
		del_client_list = [];
		for client in client_dict:
			if(not client_dict[client].get_activity_flag()):
				print("Removing client %s due to inactivity"%(client));
				del_client_list.append(client);
			else:
				client_dict[client].set_activity_flag(0);
		for client in del_client_list:
			del client_dict[client];
		reactor.callLater(60, self.checkPlayers);
		
	def startProtocol(self):
		reactor.callLater(60, self.checkPlayers);
	
	def newSessionRequest(self, request):
		response = dict();
		maul_id = request['maul_id']; 
		password = request['password'];
		client_dict = self.state['client_dict'];
		new_client = RCONClientSession(self.state, request);
		
		client_server_list = new_client.get_server_list();
		if(len(client_server_list) == 0):
			response['sessid'] = -1;
			response['status'] = 2;	
		else:
			new_sessid = "".join([random.choice(string.ascii_letters + string.digits + ".-") for i in xrange(21)])
			
			while new_sessid in client_dict:
				new_sessid = "".join([random.choice(string.ascii_letters + string.digits + ".-") for i in xrange(21)])
				
			client_dict[new_sessid] = new_client;
			if(new_client.is_admin == True):
				response['admin'] = 1;
			else:
				response['admin'] = 0;
			response['sessid'] = new_sessid;
			response['status'] = 0;
			self.state['act_log'].log(new_client.maul_id, "New session started. (%d total)"%(len(client_dict)));
		print response
		return response;
	
	# Callback from RCON object when it is finished.
	def rconComplete(self, response, addr):
		buf = json.dumps(response, indent=4, ensure_ascii=True);
		self.transport.write(buf, addr);
	
	# Callback from the RCON object when it is ready
	def rconConnected(self, rcon_obj, addr):
		rcon_obj.deferred = Deferred();
		rcon_obj.deferred.addCallback(lambda response, x_addr: self.rconComplete(response, x_addr),addr);
	
	def rconFailed(self, reason, server, addr):
		reason_type = reason.trap(ConnectError, ConnectionRefusedError, TimeoutError);
		response = dict();
		response['text'] = "RCON connection failed to %s (%s:%s), reason: %s"% (server['desc'], 
			server['ip'], str(server['port']),reason.getErrorMessage());
		response['status'] = 1;
		print(response['text']);
		buf = json.dumps(response, indent=4, ensure_ascii=True);
		self.transport.write(buf, addr);
	
	
	def datagramReceived(self, data, addr):

		request = json.loads(data);
		if(self.debug):
			print(request);
		req_id = request['req_id'];
		sess_id = -1;
		server_id = -1;
		response = dict();
		
		if('server_id' in request):
			server_id = int(request['server_id']);
		if('sessid' in request):
			sess_id = request['sessid'];
		if(self.debug):
			print("new request:");
			print(request);
		
		# Verify the client
		client = None;
					
		if(req_id == 0):
			response = self.newSessionRequest(request);
		else:
			if(sess_id in self.state['client_dict']):
				client = self.state['client_dict'][sess_id];
			else:
				if(self.debug == True):
					print(request);
					print(self.state['client_dict']);
				response['status'] = 2;
				response['text'] = "Bad session ID: Proxy restarted or session timeout.	 Please log in again.";
				buf = json.dumps(response, indent=4, ensure_ascii=True);
				self.transport.write(buf, addr);
				return;
				
		# 4 is logout
		if (req_id == 4):
			(sess_id) = request['sessid'] 
			if(sess_id in self.client_dict):
				del self.client_dict[sess_id];
		# 5 = get server list
		elif(req_id==5):
			response['server_list'] = dict();
			response['status'] = 0;
			client_server_list = client.get_server_list();
			#from operator import attrgetter
			for (id,server) in client_server_list.items():
				response['server_list'][id] = "(%s) %s"%(server['game'],server['desc']);
			if(self.debug):
				print("server list for client:");
				print(response);
		# 6 = are they admin?  7 = reset proxy
		elif((req_id == 6) or (req_id == 7)):
			response['maul_id'] = client.maul_id; 
			if(client.is_admin == True):
				response['admin'] = 1;
				if(req_id == 7):
					response['status'] = 0;
					response['text'] = "Reset in progress...";
					buf = json.dumps(response, indent=4,ensure_ascii=False);
					self.transport.write(buf, addr);
					self.state['act_log'].log(client.maul_id, "Admin reset requested...");								
					reactor.stop();
			else:
				response['admin'] = 0;	
		# 1 = rcon from client, 2 = get log, 3 = get status, 
		elif ((req_id == 1) or (req_id == 2) or (req_id==3)):
			response['server_id'] = server_id;
			if((server_id not in self.state['server_list']) or (not client.is_authorized(server_id)) ):
				response['status'] = 1;
				response['text'] = "Bad or unauthorized server ID ";
				buf = json.dumps(response, indent=4,ensure_ascii=False);
				self.transport.write(buf, addr);
				if(self.debug):
					print("rejecting server request:");
					print(server_id);
					print(self.state['server_list']);
					
				return;
			
			server = self.state['server_list'][server_id];
			response['status'] = 0;
			client.set_activity_flag(1);
			if(req_id == 1):
				msg = request['command'];
				self.state['act_log'].log(client.maul_id, "RCON command sent to server (%s:%s): %s"% (server['ip'], str(server['port']), msg));
				for item in self.forbidden_cmds:
					if(msg.find(item)!=-1):
						response['status'] = 1;
						response['text'] = "Forbidden command '%s' "%(item);
						buf = json.dumps(response, indent=4,ensure_ascii=False);
						self.transport.write(buf, addr);
						return;
				c = ClientCreator(reactor, SourceRCONClientProtocol, server, server_id, msg);
				d = c.connectTCP(server['ip'], int(server['port']), 5, (self.state['bindip'], 0));
				d.addCallback(lambda p, x_addr: self.rconConnected(p,x_addr),addr);
				d.addErrback(lambda reason, x_server, x_addr: self.rconFailed(reason,x_server, x_addr), server,addr);
				
				# skip the response - handled in the callbacks
				return;
			elif (req_id == 3):
				player_counts = dict();
				server_list = self.state['server_list'];
				
				for (id,server) in server_list.items():
					if('player_count' in server):
						player_counts[id] = server['player_count']
					else:
						player_counts[id] = '-';
				response['player_counts'] = player_counts;
				if('player_names' in server_list[server_id]):
					response['player_names'] = server_list[server_id]['player_names'];
				else:
					response['player_names'] = [];
			elif(req_id == 2):
				response['text'] = client.get_client_log(server_id);
				if(self.debug):
					print("Sending log data, length %d"%(len(response['text']),));
				s = self.transport.getHandle();
				s.setsockopt(socket.SOL_SOCKET,socket.SO_SNDBUF, 512*1024);
		
		
		buf = json.dumps(response, indent=4, ensure_ascii=True);
		self.transport.write(buf, addr);


if __name__ == '__main__':
	import sys
	from RCONUtil import RCONDB, RCONActivityLog
	
	class dummy_log_obj:
		def __init__(self):
			self.i = 0;
		def get_queued_log(self, server_id, idx):
			self.i += 1;
			return ("Log request %d\n"%(self.i,),0);
	
	server_list = {0:{'desc':"test source server", 'activity_flag': 0, 
		'player_count':16, 'logging':0, 'game':'tf',
		'ip': sys.argv[1], 'port': int(sys.argv[2]), 'pass': sys.argv[3]}};
	state = {'logip': '127.0.0.1', 'logport': 47015, 'bindip':'0.0.0.0', 'clientport': 57015, 'server_list': server_list};
	
	state['db_obj'] = RCONDB(sys.argv[4], sys.argv[5], sys.argv[6]);
	state['act_log'] = RCONActivityLog(state['db_obj']);
	state['log_obj'] = dummy_log_obj();
	
	proxy_proto = RCONProxyServerProtocol(state);
	proxy_proto.debug = True;
	reactor.listenUDP(int(state['clientport']), proxy_proto, state['bindip']);
	reactor.run();
