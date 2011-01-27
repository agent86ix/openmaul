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
import pickle
from twisted.internet import reactor, threads
import os, sys



class SrcdsWinSvc (win32serviceutil.ServiceFramework):
	_svc_name_ = "maul_sci_service_debug";
	_svc_display_name_ = "DEBUG";
	def __init__(self,args):
		if(len(args) > 0):
			self._svc_name_ = args[0];

		win32serviceutil.ServiceFramework.__init__(self,args)
		self.hWaitStop = win32event.CreateEvent(None,0,0,None)
		

	def waitForStop(self):
		win32event.WaitForSingleObject(self.hWaitStop, win32event.INFINITE);
		reactor.stop();

	def SvcStop(self):
		self.server_obj.killServer();
		self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
		win32event.SetEvent(self.hWaitStop)

	def SvcDoRun(self):
		servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
							  servicemanager.PYS_SERVICE_STARTED,
							  (self._svc_name_,''))
		self.main()

	def printStatus(self, msg):
		servicemanager.LogInfoMsg(msg);

	def main(self):
		state = {'log':self};
		pickled_server = win32serviceutil.GetServiceCustomOption(self._svc_name_, "server_dict");
		server_dict = pickle.loads(pickled_server);
		server_key = "SERVICE";
		
		from srcds_win32 import SrcdsServerProcessWin32
		
		self.server_obj = SrcdsServerProcessWin32(state, server_key, server_dict);
		self.server_obj.deferred.addCallback(lambda x: self.SvcStop());
		self.server_obj.launchServer(server_dict['launch_cmd'], server_dict['launch_args']);
		
		threads.deferToThread(self.waitForStop);
		reactor.run(installSignalHandlers=0);

if __name__ == '__main__':
	win32serviceutil.HandleCommandLine(SrcdsWinSvc)
