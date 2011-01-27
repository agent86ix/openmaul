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

import string, random, os
from twisted.internet import reactor
from twisted.internet.protocol import DatagramProtocol, ClientCreator
from SourceRCONClientProtocol import SourceRCONClientProtocol

# Handles incoming log data
class RCONLogServerProtocol(DatagramProtocol):
		
	def __init__(self, state):
		self.state = state;
		self.debug = False;
		
	def startProtocol(self):
		pass;

	def datagramReceived(self, data, (host, port)):		
		#print "from: %s, data: %s" % (addr, data)
		server_list = self.state['server_list'];
		
		server_id = -1;
		source_server = "%s:%d" % (host, port);
		
		for (id,server) in server_list.items():
			servername = ":".join((server['ip'],str(server['port'])))
			if servername == source_server:
				server_id = id;
				break
			#else:
			#	print "not: %s" % (servername)
		if(server_id == -1):
			print "Couldn't find appropriate server for addr: %s" % (source_server);
			if(self.debug):
				print(server_list);
			return;
		
		server = server_list[server_id];
		if(server['activity_flag'] < 2):
			server['activity_flag'] = 2;
		server['logging'] = 1;
		
		if('server_log' in self.state):
			self.state['server_log'].add_to_log(server_id, data[4:]);
		elif(self.debug):
			print "log data: %s"%(data[4:],);


if __name__ == '__main__':
	import sys
	
	server_list = {0:{'desc':"test source server", 'activity_flag': 0, 
		'player_count':16, 'logging':0, 
		'ip': sys.argv[1], 'port': int(sys.argv[2]), 'pass': sys.argv[3]}};
	state = {'logip': '127.0.0.1', 'logport': 47015, 'server_list': server_list};
	log_proto = RCONLogServerProtocol(state);
	log_proto.debug = True;
	reactor.listenUDP(int(state['logport']), log_proto, state['logip']);
	reactor.run();
