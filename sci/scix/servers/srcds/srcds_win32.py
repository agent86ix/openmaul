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

from twisted.internet import reactor, threads
from twisted.internet.protocol import ProcessProtocol
import pywintypes
import win32con
import win32process
import win32api
import win32pipe
import win32file
import pythoncom
import win32serviceutil
import win32service
import win32event
import servicemanager
import winerror
import pickle, os
from srcds_base import SrcdsServerBase;


class SrcdsServerServiceWin32(SrcdsServerBase):
	def launchInit(self):
		self.persists = True;
		self.nextpoll = None;
		self.ended = 0;
		
		self.service_name = "maul_sci_service_%s"%(self.server_key,);
		self.service_display_name = "MAUL SCI (%s)"%(self.server_dict['name'],);
		
		import srcds_win32_service
		self.service_class_string = os.path.splitext(srcds_win32_service.__file__)[0] + "."+ srcds_win32_service.SrcdsWinSvc.__name__;
		try:
			win32serviceutil.InstallService(self.service_class_string, self.service_name, self.service_display_name, exeArgs=self.service_name);
		except win32service.error, exc:
			if exc.winerror==winerror.ERROR_SERVICE_EXISTS:
				try:
					win32serviceutil.ChangeServiceConfig(self.service_class_string, self.service_name, displayName=self.service_display_name, exeArgs=self.service_name);
				except win32service.error, exc:
					raise;
			else:
				raise;
		
		
	def pollServiceStatus(self):
		self.nextpoll = None;
		status = win32serviceutil.QueryServiceStatus(self.service_name);
		service_state = status[1];
		if(service_state == None or service_state != win32service.SERVICE_RUNNING):
			#self.log.printStatus("service is dead, state = %d"%(service_state,));
			self.killServer();
		else:			
			self.nextpoll = reactor.callLater(5, self.pollServiceStatus);
		
	def killServer(self):
		if(self.nextpoll):
			self.nextpoll.cancel();
			self.nextpoll = None;
		if(self.ended == 0):
			self.ended = 1;
			self.processEnded(0);
		try:
			win32serviceutil.StopService(self.service_name)			
		except Exception:
			pass;
		
	def launchServer(self, cmd, arg_list):
		self.server_dict['launch_cmd'] = cmd;
		self.server_dict['launch_args'] = arg_list;
		win32serviceutil.SetServiceCustomOption(self.service_name, "server_dict", pickle.dumps(self.server_dict));
		try:
			win32serviceutil.StartService(self.service_name)
		except win32service.error, exc:
			if exc.winerror==winerror.ERROR_SERVICE_ALREADY_RUNNING:
				self.log.printStatus("[server %s] Attached to a running service."%(self.server_dict['name'],));
			else:
				raise;
		self.nextpoll = reactor.callLater(5, self.pollServiceStatus);
		self.connectionMade();
	

class SrcdsServerProcessWin32(SrcdsServerBase):

	def launchInit(self):
		self.startupinfo = win32process.STARTUPINFO();
		self.startupinfo.dwFlags = 0; #win32con.STARTF_USESHOWWINDOW;
		self.startupinfo.wShowWindow = win32con.SW_NORMAL;
		self.r_pipe = None;
		self.w_pipe = None;
		self.process = None;
		self.nextpoll = None;
		self.ended = 0;

	def pollExitCode(self):
		self.nextpoll = None;
		status = 0;
		bytes_avail = 0;
		if(self.r_pipe != None):
			try:
				bad_buf, bytes_avail, bytes_read = win32pipe.PeekNamedPipe(self.r_pipe, 0)
			except:
				pass;
			#print "pid: %s, read: %s, avail: %s\n"%(self.process_id, bytes_read, bytes_avail);
			if(bytes_avail > 0):
				bufsize, buf = win32file.ReadFile(self.r_pipe, bytes_avail);
			# print(buf);

		exit_code = 0;
		try:
			exit_code = win32process.GetExitCodeProcess(self.process)
		except:
			exit_code = -1
			pass
			
		if(259 != exit_code):
			if(self.r_pipe != None):
				self.r_pipe.close();
			if(self.w_pipe != None):
				self.w_pipe.close();
			self.r_pipe = None;
			self.w_pipe = None;
			if(self.ended == 0):
				self.ended = 1;
				self.processEnded(exit_code);
		else:
			self.nextpoll = reactor.callLater(5, self.pollExitCode);

	def killServer(self):
		if(self.process == None):
			if(self.ended == 0):
				self.ended = 1;
				self.processEnded(-1);
			return;
		try:
			win32process.TerminateProcess(self.process, 1);
		except:
			pass;
		self.process = None
		if(self.r_pipe != None):
			self.r_pipe.close();
		if(self.w_pipe != None):
			self.w_pipe.close();
		self.r_pipe = None;
		self.w_pipe = None;
		if(self.nextpoll != None):
			self.nextpoll.cancel();
			self.nextpoll = None;
		if(self.ended == 0):
			self.ended = 1;
			self.processEnded(-1);

	def launchServer(self, cmd, arg_list):
		sec = pywintypes.SECURITY_ATTRIBUTES();
		sec.bInheritHandle = 1;
		self.r_pipe, self.w_pipe = win32pipe.CreatePipe(sec, 64*1024);
		self.startupinfo.dwFlags = 0; #win32con.STARTF_USESTDHANDLES;
		self.startupinfo.hStdOutput = self.w_pipe;
		self.startupinfo.hStdError = self.w_pipe;
		self.startupinfo.hStdInput = win32api.GetStdHandle(win32api.STD_INPUT_HANDLE);
		flags = win32con.CREATE_NEW_CONSOLE;
		
		cmd = " ".join(arg_list);
		# print(cmd);
		
		try:
			(self.process, self.thread, self.process_id, self.thread_id) = win32process.CreateProcess(None, cmd, None, None, 1, flags, None, None, self.startupinfo);
		except win32api.error, details:
			# maul_proc_event
			# task_id, event_time, event_type, event_text
			#  event_type - 0 = info, 1 = warn, 2 = error
			self.log.printStatus( "Failed to launch process.  Error in function %s: %s (Windows error code %d)"%
					(details[1], details[2], details[0]))
			self.ended = 1;
			self.processEnded(-2);
			return;
		
		svr_dict  = self.server_dict;
		if('server_cpus' in svr_dict):
			server_cpu_list = svr_dict['server_cpus'].split(',');
			cpu_mask = 0;
			for cpu_str in server_cpu_list:
				cpu_mask = cpu_mask | 1<<(int(cpu_str));
			(paff,saff) = win32process.GetProcessAffinityMask(self.process);
			cpu_mask = cpu_mask & paff;
			if(cpu_mask != 0):
				self.log.printStatus("[server %s]: Setting CPU affinity mask to 0x%x."%(self.server_dict['name'],cpu_mask));
				win32process.SetProcessAffinityMask(self.process, cpu_mask);
		if('server_highpriority' in svr_dict):
			if(svr_dict['server_highpriority'].strip() == '1'):
				self.log.printStatus("[server %s]: Setting high priority flag."%(self.server_dict['name'],));
				win32process.SetPriorityClass(self.process, 0x80);	
		self.nextpoll = reactor.callLater(5, self.pollExitCode);
		self.connectionMade();



