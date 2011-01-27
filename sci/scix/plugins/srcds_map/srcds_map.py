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

import bz2, os, urllib2
from twisted.internet import threads
from scicore.util import parseServer


# invoke with:
# d = threads.deferToThread(decompressMap, inputfile)
# d.addCallback(on_decompress_complete)

def getFile(url, filename, log, servername, short_filename):
	try:
		output = file(filename, "w+b");
	except:
		log.printStatus("[%s] %s download: Error: Could not open output file for writing"%(servername,short_filename));
		return;

	try:
		input = urllib2.urlopen(url);
	except:
		output.close();
		os.remove(filename);
		log.printStatus("[%s] %s download: Error: Could not open URL for reading"%(servername, short_filename));
		return;

	if(url.endswith(".bz2")):
		parser = bz2.BZ2Decompressor();
	else:
		parser = None;

	count = 0;
	bytes = 0;
	while(True):
		try:
			data = input.read(500*1024);
			count = count + 1;
			bytes = bytes + len(data);
			if(count % 4 == 0 and log):
				log.printStatus("[%s] %s download: %dMB complete"%(servername, short_filename, bytes/(1024*1024)))

			if(len(data) == 0):
				break;
			if(parser != None):
				output.write(parser.decompress(data));
			else:
				output.write(data);
		except:
			input.close();
			output.close();
			try:
				os.remove(filename);
			except:
				pass;
			log.printStatus("[%s] %s download: Error downloading and/or decompressing map."%(servername, short_filename));
			return;
			
	input.close();
	output.close();
	log.printStatus("[%s] %s download: Completed."%(servername, short_filename));

# getMap("http://www.egoadmins.com/orangebox/tf/maps/koth_oilfield.bsp.bz2", "koth_oilfield.bsp", None, "test");

class SCIMapPI:
	def __init__(self, state):
		self.state = state;
		self.download_queue = dict();
		self.active_download = None;
		router = state['router'];
		router.registerRoute(self, ("addmap","delmap"));
		self.debug = False;

	def processCommand(self, cmd, args):
		config = self.state['config'];
		if(len(args) != 2):
			return "Usage: addmap <server> <mapname>";
		server_name = args[0];

		# remove any other path elements before we build the url!
		
		if(args[1].rfind("/") != -1):
			map_name = args[1][args[1].rfind("/"):];
		else:
			map_name = args[1];
			
		server_list = parseServer(self.state, server_name);
		# print server_list
		if(len(server_list) == 0):
			return "No server matched server name '%s'"%(server_name);
		if(cmd == "addmap"):
			
			rcon_result = "Map download request status:";

			for server_key in server_list:
				server = config.getServer(server_key);
				ext_list = ['bsp.bz2'];
				if('map_extra_files' in server):
					extra_ext_list = server['map_extra_files'].split(",");
					ext_list.extend(extra_ext_list);
				for ext in ext_list:
					if('mapurl' in server):
						mapurl = "%s/%s.%s"%(server['mapurl'], map_name, ext)
					else:
						mapurl = "%s/%s.%s"%(config.get('mapurl'), map_name, ext)
					print mapurl;
					# maybe use the os.pathsep or whatever here?
					# mappath = "%s/maps/%s"%(self.config_dict['servers'][server_key]['dir'],map_name);
					if(ext.endswith(".bz2")):
						output_ext = ext[:-4];
					else:
						output_ext = ext;
					mappath = os.path.join(server['dir'], "maps", ".".join((map_name,output_ext)));
					# print mappath
					queue_key = "%s%s.%s"%(server_key,map_name,ext);
					file_name = ".".join((map_name, ext));
					if(queue_key in self.download_queue):
						rcon_result = "\n".join((rcon_result, "File (%s) is already queued for download on %s"%(file_name,server['name'])))
					else:		
						self.download_queue[queue_key] = (mapurl, mappath, server['name'], file_name);
						rcon_result = "\n".join((rcon_result, "File (%s) added to queue for download on %s"%(file_name,server['name'])))
				
			if(self.debug):
				print self.download_queue
			if(self.active_download == None	 and len(self.download_queue) != 0):
				(key, (mapurl,mappath,server_key,map_name)) = self.download_queue.popitem();
				self.active_download = key;
				d = threads.deferToThread(getFile, mapurl, mappath, self.state['log'], server_key, map_name);
				d.addCallback(lambda x, x_key: self.downloadComplete(x_key), key)
		elif(cmd == "delmap"):
			for server_key in server_list:
				server = config.getServer(server_key);
				mappath = os.path.join(server['dir'], "maps", ".".join((map_name,"bsp")));
				cur_result = "[delmap %s]: Deleted map %s."%(server['name'],map_name);
				try:
					os.remove(mappath);
				except:
					cur_result = "[delmap %s]: Failed to delete map %s."%(server['name'],map_name);
				rcon_result = "\n".join((rcon_result, cur_result));
		return rcon_result;
	
	def downloadComplete(self, queue_key):
		self.active_download = None;
		if(len(self.download_queue) != 0):
			(key, (mapurl,mappath,server_name,file_name)) = self.download_queue.popitem();
			self.active_download = key;
			d = threads.deferToThread(getFile, mapurl, mappath, self.state['log'], server_name, file_name);
			d.addCallback(lambda x, x_key: self.downloadComplete(x_key), key)

	
