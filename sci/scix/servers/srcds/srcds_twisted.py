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

from twisted.internet import reactor
from twisted.internet.protocol import ProcessProtocol
from srcds_base import SrcdsServerBase

class SrcdsServerProcessTwisted(SrcdsServerBase, ProcessProtocol):
	def launchServer(self, cmd, arg_list):
		self.is_stopped = False;
		reactor.spawnProcess(self, cmd, arg_list, env=None);
	def killServer(self):
		if(self.is_stopped == False):
			self.transport.write("quit\n");
			self.transport.loseConnection();
			self.transport.signalProcess("KILL");
			self.is_stopped = True;
		#try:
		#	self.transport.signalProcess("KILL");
		#except:
		#	raise;
	def launchInit(self):
		pass;
		
