import binascii
from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor

class SourceUDPClientProtocol(DatagramProtocol):
	# Get the player information, adds/modifies server['player_names'] server['player_count']
	QUERY_PLAYER_INFO = 1;
	
	# Get the server information, adds/modifies server['desc']
	QUERY_SERVER_INFO = 2;
	
	FLAG_LIST = [QUERY_PLAYER_INFO, QUERY_SERVER_INFO];
	
	def __init__(self, server, flags):
		self.server = server;
		self.challenge = None;
		self.debug = False;
		self.flags = flags;
		self.flags_complete = 0;
		self.current_flag = 0;
		self.retry_count = 0;
	
	def startProtocol(self):
		# send 'getchallenge'
		buf = binascii.unhexlify('FFFFFFFF57');
		if(self.debug):
			print(self.server);
		addr = (self.server['ip'], int(self.server['port']));
		self.watchdog = reactor.callLater(5, self.operationComplete);
		self.transport.write(buf, addr);		
	
	def operationComplete(self, error=False):
		if(self.watchdog):
			if(self.watchdog.active()):
				try:
					self.watchdog.cancel();
				except:
					pass;
			else:
				error = True;
		if(error):
			print("UDP connection error to %s (%s:%s)!"%(self.server['desc'], 
				self.server['ip'], str(self.server['port'])));
			self.server['logging'] = 0;
		self.watchdog = None;
		self.transport.stopListening();
		if(self.deferred):
			self.deferred.callback(0);
	
		
	def datagramReceived(self, data, addr):
		if(data[4] == 'A'):
			self.challenge = data[5:9];
		if(self.challenge == None):
			self.retry_count += 1;
			if(self.retry_count >= 3):
				self.operationComplete(True);
				return;
			else:
				# retry the getchallenge
				buf = binascii.unhexlify('FFFFFFFF57');
				self.transport.write(buf, (self.server['ip'],int(self.server['port'])));
				return;
		# handle result from one of the things we were asked to do
		elif(data[4] == 'I'):
			# grab the server's latest name
			end_idx = data[6:].find('\0');
			(svr_name) = data[6:end_idx+6].strip();
			if(self.debug):
				print("%s: Updating name to %s"%(self.server['desc'], svr_name));
			self.server['desc'] = svr_name;
			self.flags_complete = self.flags_complete | SourceUDPClientProtocol.QUERY_SERVER_INFO;
		elif(data[4] == 'D'):
			if(self.debug):
				print("Player packet:");
				print(binascii.hexlify(data));
			player_count = ord(data[5]);
			# parse player data			
			player_names = [];
			# skip the first bytes, they're the headers: 4bytes of FF, 1 byte type, 1 byte count
			# and then the first index byte -> 7 total to skip
			startidx = 7;
			# discard the last few bytes - they're guaranteed to be score/conn time
			data = data[:-7];
			while(startidx<len(data) and data[startidx] == '\0'):
				startidx += 1;
			endidx = startidx;
			while(endidx < len(data)):
				# is this the end of a string?
				if(data[endidx] == '\0'):
					# the data buffer is considered to be ascii, but it's actually utf-8
					# so translate it as such.  
					playername = data[startidx:endidx].strip().decode('utf-8','replace');
					if(self.debug):
						print playername;
					if(len(playername)==0 or playername[0] == '\0'):
						if(self.debug):
							print("error parsing player names string, 0-byte name... (%d:%d of %d, %s)"%(startidx, endidx, len(data), binascii.hexlify(data)));
					else:
						player_names.append(playername);
					# 1 byte null, 4 byte score, 4 byte connect time, 1 byte next index
					startidx = endidx + 10;
					while(startidx<len(data) and data[startidx] == '\0'):
						startidx += 1;
					endidx = startidx;
				endidx += 1;
			self.server['player_names'] = player_names;
			self.server['player_count'] = player_count;
			self.flags_complete = self.flags_complete | SourceUDPClientProtocol.QUERY_PLAYER_INFO;
		
		else:
			if(data[4] != 'A'):
				if(self.debug):
					print("Bad packet from server: %s"%(binascii.hexlify(data),));
		
		if(self.flags != self.flags_complete):
			self.current_flag = 0;
			for flag in SourceUDPClientProtocol.FLAG_LIST:
				if((self.flags_complete & flag) == 0):
					self.current_flag = flag;
					break;
			if(self.current_flag == 0):
				# uh...  one or more flags passed in was invalid, so I guess we're done.
				self.operationComplete();
			if(self.current_flag == SourceUDPClientProtocol.QUERY_PLAYER_INFO):
				buf = "".join((binascii.unhexlify('FFFFFFFF55'),self.challenge));
				self.transport.write(buf, (self.server['ip'],int(self.server['port'])));
			elif(self.current_flag == SourceUDPClientProtocol.QUERY_SERVER_INFO):
				buf = buf = binascii.unhexlify('FFFFFFFF54536F7572636520456E67696E6520517565727900');
				self.transport.write(buf, (self.server['ip'],int(self.server['port'])));
		else:
			# all updates complete, finish up.
			self.operationComplete();
			
if __name__ == '__main__':
	import sys
	from twisted.internet.defer import Deferred
	
	server_list = {0:{'desc':"default_name", 'activity_flag': 0, 
		'player_count':-1, 'logging':0, 'player_names':None,
		'ip': sys.argv[1], 'port': int(sys.argv[2]), 'pass': 'n/a'}};
	state = {'bindip': '0.0.0.0', 'statusport': 47015, 'server_list': server_list};
	
	proto = SourceUDPClientProtocol(server_list[0], 0xFFFF);
	proto.debug = True;
	proto.deferred = Deferred();
	
	def testComplete(dummy):
		print server_list[0];
		print proto.flags_complete;
		reactor.stop();
	
	proto.deferred.addCallback(testComplete);
	reactor.listenUDP(int(state['statusport']), proto, state['bindip']);
	reactor.run();
