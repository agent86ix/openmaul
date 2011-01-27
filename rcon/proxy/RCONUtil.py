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
