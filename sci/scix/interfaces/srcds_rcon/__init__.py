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

from rconproto import SourceRCONProtocolFactory
from udpproto import SourceUDPProtocol
from scix.interfaces.common import SCIXInterface
from twisted.internet import reactor

class SourceRCONInterface(SCIXInterface):
	def __init__(self, state):
		self.state = state;
		config = state['config'];
		router = state['router'];
		
		udp_proto = SourceUDPProtocol(state);
		
		print("[maul_sci]: Setting up server '%s' on %s:%s"%
			(config.get('rcon_hostname'),config.get('ip'), config.get('rcon_port')));
		
		reactor.listenUDP(int(config.get('rcon_port')), udp_proto, config.get('ip'));
		reactor.listenTCP(int(config.get('rcon_port')), 
			SourceRCONProtocolFactory(config.get('rcon_pwd'), router), 
			50, config.get('ip'));

interface_object_type = SourceRCONInterface;
