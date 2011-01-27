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