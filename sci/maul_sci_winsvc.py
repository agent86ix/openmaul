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

import pythoncom
import win32serviceutil
import win32service
import win32event
import servicemanager
import winerror
from twisted.internet import reactor, threads
from maul_sci import run_maul_sci
import os, sys, getopt, pickle

class SCISvc (win32serviceutil.ServiceFramework):
	_svc_name_ = "maul_sci_main_default";
	def __init__(self,args):
		# You may think that the 'args' here would be the
		# values passed to exeArgs when we called InstallService
		# in the __main__ block below this class.
		# They are not - those arguments are consumed by pythonservice, I guess.
		# There's not any documentation on this, argh.
		# The ACTUAL args vector here has one entry in the 
		# 'real service' case (ie, not debug case)
		# and that is the 'id' of the service (what they call here
		# the _svc_name_.
		self._svc_name_ = args[0];
		self.cmd_line_args = None;
		if(len(args) > 1):
			# In the debug case, I will pass the pickled args
			# in the args list, to avoid having to muck about
			# in the registry when we're just debugging.
			self.cmd_line_args = args[1];
		win32serviceutil.ServiceFramework.__init__(self,args)
		self.hWaitStop = win32event.CreateEvent(None,0,0,None)

	def waitForStop(self):
		win32event.WaitForSingleObject(self.hWaitStop, win32event.INFINITE);
		reactor.stop();

	def SvcStop(self):
		self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
		win32event.SetEvent(self.hWaitStop)

	def SvcDoRun(self):
		servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
							  servicemanager.PYS_SERVICE_STARTED,
							  (self._svc_name_,''))
		self.main()

	def main(self):
		# Unpickle the ACTUAL arguments to the service, 
		if(self.cmd_line_args != None):
			# this handles the debug case where I passed the pickled
			# args in as a list item to DebugService (see __main__ below)
			pickled_args = self.cmd_line_args;
		else:
			# in the 'real service' case, args come from the registry
			# via GetServiceCustomOption.
			pickled_args = win32serviceutil.GetServiceCustomOption(self._svc_name_, "args");
		args = pickle.loads(pickled_args);
		threads.deferToThread(self.waitForStop);
		run_maul_sci(args);

if __name__ == '__main__':

	# Some convienence options for installing and debugging the
	# service.

	# read the argv, using a similar method to what would be done
	# in win32serviceutil.HandleCommandLine.
	# I roll my own here because that function does odd things
	# to command line arguments - try passing a quoted filename
	# with spaces and you'll see the bug it introduces.
	args = sys.argv[1:];
	opts = [];
	cmd = None;
	try:
		while(len(args) != 0):
			cur_opts, args = getopt.getopt(args, "",["cfg=", ])
			opts.extend(cur_opts);
			if(len(args) != 0):
				if(cmd == None):
					cmd = args[0];
					args = args[1:];
				else:
					print("Unknown argument: %s"%(args[0],))
					sys.exit(-1);
	except getopt.error, details:
		print details
		sys.exit(-1);
	
	# These are the default values that will be used, assuming
	# they are not overridden by entries in the config file.
	svcid = "maul_sci";
	svcname = "MAUL Server Control Interface";
	svcdesc = "Main service for MAUL SCI";

	# These are the args that I will store (for install) or pass
	# (for debug) to the service itself.
	# This is used so that the main routines don't have to know
	# that they are being run as a service.
	svcargs = [];
	
	# the default config file is maul_sci.cfg, in the same directory
	# where this module file is located.
	cfgfile_name = os.path.join(os.path.dirname( os.path.realpath( __file__ ) ),'maul_sci.cfg')
	
	# check and see if the configuration file location was overridden
	# on the command line.
	for opt, val in opts:
		if(opt == "--cfg"):
			cfgfile_name = os.path.abspath(val);
			svcargs.append("--cfg=\"%s\""%(cfgfile_name,));
	
	# Parse the config file, and look for [global] options that override
	# the defaults for installing this service.
	from scicore.config import SCIConfig;
	config = SCIConfig(cfgfile_name);
	cfg_svcid = config.get('svcid');
	if(cfg_svcid != None):
		svcid = "maul_sci_main_%s"%(cfg_svcid,);
	cfg_svcname = config.get('svcname');
	if(cfg_svcname != None):
		svcname = "MAUL Server Control Interface (%s)"%(cfg_svcname,);
	cfg_svcdesc = config.get('svcdesc');
	if(cfg_svcdesc != None):
		svcdesc = cfg_svcdesc;
	
	# This looks weird - I'm importing the file I'm already in.
	# however, I need this to be able to get introspective on the
	# SCISvc class that will be installed as a service.
	import maul_sci_winsvc
	svc_class_string =  os.path.splitext(maul_sci_winsvc.__file__)[0] + "."+ maul_sci_winsvc.SCISvc.__name__;
	
	if(cmd == "install"):
		# Try to install, and failing that, update the service configuration.
		try:
			win32serviceutil.InstallService(svc_class_string, svcid, svcname);
		except win32service.error, exc:
			if exc.winerror==winerror.ERROR_SERVICE_EXISTS:
				try:
					win32serviceutil.ChangeServiceConfig(svc_class_string, svcid, displayName=svcname);
				except win32service.error, exc:
					raise;
			elif exc.winerror == winerror.ERROR_ACCESS_DENIED:
				# Print a more descriptive message.  if you have UAC
				# version of windows (ie, vista/7) you must run the
				# command prompt as administrator.
				print("Access denied: Unable to install or change the service.  It is likely that you are not running as administrator.");
				sys.exit(-1);
			else:
				raise;
		# let the app know it is running as a service
		svcargs.append("--winsvc=1");
		win32serviceutil.SetServiceCustomOption(svcid, "args", pickle.dumps(svcargs));
	elif(cmd == "remove"):
		try:
			win32serviceutil.RemoveService(svcid);
		except win32service.error, exc:
			if exc.winerror == winerror.ERROR_ACCESS_DENIED:
				print("Access denied: Unable to remove the service.  It is likely that you are not running as administrator.");
	elif(cmd == "debug"):
		win32serviceutil.DebugService(SCISvc, (svcid,pickle.dumps(svcargs)))
	else:
		print("Unknown command: %s"%(cmd,))
		sys.exit(-1);
	
