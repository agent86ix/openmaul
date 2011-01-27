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
import sys, getopt, ConfigParser;

def load_config_file(filename):
	config_obj = ConfigParser.ConfigParser();
	config_obj.read(filename);
	config_dict = dict();
	for (key, value) in config_obj.items("global"):
		config_dict[key] = value;
	
	return config_dict;


def maul_rcon_main():
	
	cfg_file_name = os.path.join(os.path.dirname( os.path.realpath( __file__ ) ),'maul_rcon.cfg')
	opts = [];
	try:
		opts, args = getopt.getopt(args, "",["cfg=",])
	except getopt.error, details:
		print details
		sys.exit(-1);
		
	for opt,val in opts:
		if(opt=="--cfg"):
			cfg_file_name = val;
	
	state = load_config_file(cfg_file_name);
	state['server_list'] = dict();
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
