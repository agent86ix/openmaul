
class SCIRoute:
	def __init__(self, state):
		self.cmd_dict = dict();
		self.local_cmd_dict = dict();
		self.hidden_cmd_dict = dict();
		self.handler_dict = {'cmd':{},'local':{},'hidden':{}};
		self.state = state;
		
	def unregisterHandler(self, handler):
		if(handler in self.handler_dict['cmd']):
			for cmd in self.handler_dict['cmd'][handler]:
				del self.cmd_dict[cmd];
			del self.handler_dict['cmd'][handler];
			
		if(handler in self.handler_dict['local']):
			for cmd in self.handler_dict['local'][handler]:
				del self.local_cmd_dict[cmd];
			del self.handler_dict['local'][handler];
						
		if(handler in self.handler_dict['hidden']):
			for cmd in self.handler_dict['hidden'][handler]:
				del self.hidden_cmd_dict[cmd];	
			del self.handler_dict['hidden'][handler];		
		
	def registerRoute(self, handler, cmds):
		for cmd in cmds:
			self.cmd_dict[cmd] = handler;
		if(handler in self.handler_dict['cmd']):
			self.handler_dict['cmd'][handler].append(cmds);
		else:
			self.handler_dict['cmd'][handler] = list(cmds);
			
	# register a route that cannot be called
	# via RCON, for internal use only
	def registerLocalRoute(self, handler, cmds):
		for cmd in cmds:
			self.local_cmd_dict[cmd] = handler;
		if(handler in self.handler_dict['local']):
			self.handler_dict['local'][handler].append(cmds);
		else:
			self.handler_dict['local'][handler] = list(cmds);
		
	# register a route that will not be shown
	# in help commands, for instance.
	# used for emulated commands like 'log' which are important
	# for clients to access, but not really
	# help-worthy
	def registerHiddenRoute(self, handler, cmds):
		for cmd in cmds:
			self.hidden_cmd_dict[cmd] = handler;
		if(handler in self.handler_dict['hidden']):
			self.handler_dict['hidden'][handler].append(cmds);
		else:
			self.handler_dict['hidden'][handler] = list(cmds);
			
	def routeLocalCommand(self, data):
		split_data = data.split(" ");
		if(split_data and len(split_data) > 0):
			cmd = split_data[0];
			if(len(split_data) > 1):
				args = split_data[1:];
			else:
				args = None;
			if(cmd in self.local_cmd_dict):
				return self.local_cmd_dict[cmd].processCommand(cmd, args);
			elif(cmd in self.cmd_dict):
				return self.cmd_dict[cmd].processCommand(cmd, args);		
			elif(cmd in self.hidden_cmd_dict):
				return self.hidden_cmd_dict[cmd].processCommand(cmd, args);		
		
	def routeCommand(self, source, data):
		src = "%s:%d"%(source[0], source[1]);
		split_data = data.split(" ");
		if(split_data and len(split_data) > 0):
			cmd = split_data[0];
			if(len(split_data) > 1):
				args = split_data[1:];
			else:
				args = None;
			if(cmd in self.cmd_dict):
				result = self.cmd_dict[cmd].processCommand(cmd, args);
				self.state['log'].printStatus("rcon from \"%s\": command \"%s\""%(src, data));
				return result;
			elif(cmd in self.hidden_cmd_dict):
				result = self.hidden_cmd_dict[cmd].processCommand(cmd, args);
				self.state['log'].printStatus("rcon from \"%s\": command \"%s\""%(src, data));
				return result;
			else:	
				# print(self.cmd_dict);
				return "Unrecognized command: '%s'"%(cmd);
		
		
