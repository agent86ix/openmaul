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

from twisted.internet.protocol import Factory, Protocol

import struct, binascii
from twisted.internet import reactor
from twisted.internet.error import ConnectionDone

class SourceRCONClientProtocol(Protocol):	

	def __init__(self, server, server_id, cmd):
		
		self.server = server;
		#self.client_sock = client_sock;
		#self.client_addr = client_addr;
		self.cmd = cmd;
		self.server_id = server_id;
		self.auth_rcvd = False;
		self.cmd_response_rcvd = False;
		self.output_buf = "";
		self.watchdog = None;
		self.debug = False;
		self.deferred = None;
		
	#def startProtocol(self): 
	#	self.transport.connect(self.server['ip'],int(self.server['port']));
	
	def connectionLost(self, reason):
		if(reason.check(ConnectionDone)):
			return;
		else:
			response = dict();
			response['text'] = "RCON connection failed to %s (%s:%s), reason: %s"% (self.server['desc'], 
				self.server['ip'], str(self.server['port']),reason.getErrorMessage());
			response['status'] = 1;
			if(self.deferred):
				self.deferred.callback(response);
			print(reason);
			print(response['text']);
			
		
	def timeout(self):
		self.transport.loseConnection();
		if(self.deferred):
			response = dict();
			response['text'] = "*** Proxy error - Timed out waiting for server to respond.";
			response['status'] = 1;
			self.deferred.callback(response);
			return;
			
	def connectionMade(self):
		
		s = self.transport.getHandle();
		s.settimeout(2);
		self.watchdog = reactor.callLater(5, self.timeout);
		
		# mark this server as not logging - we should get log lines
		# back from this operation if it is.
		self.server['logging'] = 0;
		# send the authorization packet
		reqid = 1;
		reqtype = 3;
		cmd = self.server['pass'];
		size = len(cmd) +2+8;
		buf = struct.pack("iii",size,reqid,reqtype);
		buf = "".join((buf, cmd, struct.pack("bb",0,0)));
		if(self.debug == True):
			print('sending: %s'% binascii.hexlify(buf));
		self.transport.write(buf);
	
	def dataReceived(self, data):
		if(self.debug == True):
			print('recv: %s'% binascii.hexlify(data));
		response = dict();
		if(self.auth_rcvd == False):
			# might be a packet or packet(s) that are just FYI
			# just an echo, ie, 'thanks for the auth request'
			reqtype = -1;
			reqid = -1;
			size = -1;
			if(self.debug == True):
				print('authcheck: %s'% binascii.hexlify(data));
			try:
				(size, reqid, reqtype ,z1,z2) = struct.unpack("iiibb",data);
			except struct.error:
				self.transport.loseConnection();
				if(self.deferred):
					response['text'] = "*** Proxy error - Server did not respond properly to RCON request!";
					response['status'] = 1;
					self.deferred.callback(response);
					self.watchdog.cancel();
					return;
			if(reqtype != 2):
				return;		
			
			# reqtype is 2, which is the auth response.
			# reqid should be 1, which is what we asked for earlier.
			if(reqid != 1):
				self.transport.loseConnection();
				if(self.deferred):
					response['text'] = "*** Proxy error - RCON Authorization failed.  Bad RCON password in MAUL RCON configuration!";
					response['status'] = 1;
					self.deferred.callback(response);
					self.watchdog.cancel();
					return;
			self.auth_rcvd = True;
			
			# send the command packet
			reqid = 0;
			reqtype = 2;
			cmd = self.cmd.encode("utf-8","replace");
			size = len(cmd) +2+8;
			buf = struct.pack("iii",size,reqid,reqtype);
			buf = "".join((buf,cmd,struct.pack("bb",0,0)));
			if(self.debug == True):
				print('sending: %s'% binascii.hexlify(buf));
			self.transport.write(buf);
			return;
		elif(self.auth_rcvd == True and self.cmd_response_rcvd == False):
			#print('got second response: %s'%(binascii.hexlify(response)));
		
			if(self.debug == True):
				print('response: %s'% binascii.hexlify(data));
			
			self.output_buf = "".join((self.output_buf, data[12:]))
			if(self.output_buf[-1] == '\0' and self.output_buf[-2] == '\0'):
				self.output_buf = self.output_buf[:-2];
				self.transport.loseConnection();
				if(self.deferred):
					response['text'] = self.output_buf.decode('utf-8', 'replace');
					response['server_id'] = self.server_id;
					response['status'] = 0;
					self.server['activity_flag'] = 5;
					self.deferred.callback(response);
					self.watchdog.cancel();
					return;

if __name__ == '__main__':
	from twisted.internet.defer import Deferred
	from twisted.internet.protocol import ClientCreator
	import sys
	
	def callbackfunc(response):
		print response;
		reactor.stop();
	
	def onconnect(p):
		p.debug = True;
		p.deferred = Deferred();
		p.deferred.addCallback(callbackfunc);
	
	server = {"ip": sys.argv[1], "port": int(sys.argv[2]),"activity_flag": 1, "pass":sys.argv[3] };
	
	c = ClientCreator(reactor, SourceRCONClientProtocol, server, 0, "status")
	c.connectTCP(server['ip'], server['port']).addCallback(onconnect)
	
	reactor.run();
