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

import os, sys, getopt;

from twisted.internet import reactor;

from scicore.log import SCILog;
from scicore.router import SCIRoute;
from scicore.config import SCIConfig;
from scicore.pluginmgr import SCIPluginMgr;
from scicore.ifcmgr import SCIInterfaceMgr;
from scicore.servermgr import SCIServerMgr;
import scicore.reloader 

def run_maul_sci(args):
	scicore.reloader.enable();
	
	state = dict();
	# by default, read maul_sci.cfg in the current directory.
	cfg_file_name = os.path.join(os.path.dirname( os.path.realpath( __file__ ) ),'maul_sci.cfg')
	register_signal_handlers = 1;
	opts = [];
	try:
		opts, args = getopt.getopt(args, "",["cfg=", "winsvc="])
	except getopt.error, details:
		print details
		sys.exit(-1);
	
	for opt,val in opts:
		if(opt=="--cfg"):
			cfg_file_name = val;
		elif(opt == "--winsvc"):
			# the windows service doesn't run this on the 'main thread'
			# so signal handlers will fail to install.
			register_signal_handlers = 0;
	
	config = SCIConfig(cfg_file_name);
	state['config'] = config;

	log = SCILog(state);
	state['log'] = log;
	
	router = SCIRoute(state);	
	state['router'] = router;

	plugin_obj = SCIPluginMgr(state);
	plugin_obj.loadPlugins();
	state['pluginmgr'] = plugin_obj;

	ifc_obj = SCIInterfaceMgr(state);
	ifc_obj.loadInterfaces();
	state['ifcmgr'] = ifc_obj;
	
	server_obj = SCIServerMgr(state);
	state['servermgr'] = server_obj;
	reactor.run(installSignalHandlers=register_signal_handlers);
	
if __name__ == '__main__':
	run_maul_sci(sys.argv);
    
