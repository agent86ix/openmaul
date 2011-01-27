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

import sys, os;
from struct import pack,unpack;
from binascii import hexlify, unhexlify;
from datetime import datetime;

from twisted.internet import reactor;


class SCILog:
	def __init__(self, state):
		config = state['config'];
		self.debug = False;
		self.debug_log = True;
		self.status_list = list();
		log_filename = 'maul_sci.log';
		cfg_log_filename = config.get('logfile');
		self.log_sock = None;

		if(cfg_log_filename == None):
			self.log_file = open('maul_sci.log', 'a');
		else:
			self.log_file = open(cfg_log_filename, 'a');
		self.old_stdout = sys.stdout;
		self.old_stderr = sys.stderr; # save so it doesn't close?
		sys.stdout = self;
		sys.stderr = self;
		
	def write(self, data):
		data = "%s\n"%(data.rstrip());
		if(data.strip() == ""):
			return;
		# this is for things that would normally go to stdout/sterr 
		self.printDebug(0,data);
	
	def flush(self):
		self.old_stdout.flush();
				
	def registerInterface(self, ifc):
		self.status_list.append(ifc);


	# Print status messages, ie, things that must be sent to the interface.
	# Messages will also print to the log.
	def printStatus(self, data):
		for ifc in self.status_list:
			ifc.processStatus(data);
			
		timestamp = datetime.now().strftime("%m/%d/%Y - %H:%M:%S");
		output = "S %s: %s\n"%(timestamp,data,);
		self.log_file.write(output);
		self.old_stdout.write(output);
		
	# Print debug messages, ie, things that must be sent to the 
	# local log file only.
	def printDebug(self, level, data):
		timestamp = datetime.now().strftime("%m/%d/%Y - %H:%M:%S");
		output = "D %s: %s\n"%(timestamp,data,);
		self.log_file.write(output);
		self.old_stdout.write(output);
