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

from RCONServerManager import RCONServerManager;
from RCONProxyServerProtocol import RCONProxyServerProtocol;
from RCONLogServerProtocol import RCONLogServerProtocol;
from RCONUtil import RCONDB,RCONActivityLog;
from twisted.internet import reactor
import sys;

def load_config_file(filename):
	conf_dict = {}
	server_list = {}
	id = 0;
	for line in open(filename):
		splitline = line.split(",")
		if(splitline[0].strip() == 'server'):
			server_list[id] = dict({'ip':splitline[1].strip(), 'port':splitline[2].strip(),
				'pass':splitline[3].strip(), 'desc':splitline[4].strip(), 'game':splitline[5].strip()});
			id += 1;
			continue;
		if(len(splitline) > 1):
			conf_dict[splitline[0].strip()] = ",".join(splitline[1:]).strip();
			print("conf: %s = %s"%(splitline[0], ",".join(splitline[1:]).strip()));
	return (conf_dict, server_list)


def maul_rcon_main():
	(state,server_list) = load_config_file(sys.argv[1]);
	state['server_list'] = server_list;
	state['db_obj'] = RCONDB(state['dbhost'], state['dbuser'], state['dbpass'], state['dbname']);
	svr_mgr = RCONServerManager(state);
	proxy_proto = RCONProxyServerProtocol(state);
	#proxy_proto.debug = True;
	log_proto = RCONLogServerProtocol(state);
	#log_proto.debug = True;
	state['act_log'] = RCONActivityLog(state['db_obj']);
	
	
	reactor.listenUDP(int(state['clientport']), proxy_proto, state['bindip']);
	reactor.listenUDP(int(state['logport']), log_proto, state['bindip']);
	
	reactor.run();


if __name__ == '__main__':
	maul_rcon_main();
