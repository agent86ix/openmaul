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

import MySQLdb

class RCONDB:
	def __init__(self, dbhost, dbuser, dbpass, dbname):
		self.dbhost = dbhost;
		self.dbuser = dbuser;
		self.dbpass = dbpass;
		self.dbname = dbname;
	def get_db(self):
		try:
			self.db_conn.ping()
		except:
			self.db_conn = MySQLdb.connect(host=self.dbhost, user=self.dbuser, passwd=self.dbpass, db=self.dbname)
			self.db = self.db_conn.cursor();
		return self.db;
		
class RCONActivityLog:
	def __init__(self, db_obj):
		self.db_obj = db_obj;
	def log(self, maulid, msg):
		msg = msg.encode("ascii", "backslashreplace");
		self.db_obj.get_db().execute("insert into maul_rcon_log(maulid, msg) values(%s,%s)", (str(maulid), msg));
