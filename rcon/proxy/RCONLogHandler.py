

# store logs in buffers, and keep track of them per-server.
class RCONLogHandler:
	def __init__(self, server_list, buffer_limit):
		self.log_queue = {};
		for (id, server) in server_list.items():
			self.log_queue[id] = {};
			self.log_queue[id]['log'] = "";
			self.log_queue[id]['log_idx'] = 0;
		self.server_list = server_list;
		self.buffer_limit = buffer_limit;
	def add_to_log(self, server_id, msg):
		if(server_id not in self.log_queue):
			print "ERROR: No server found for server_id = %d"%(server_id);
			return;
		
		msg = msg.decode('utf-8','replace');
		#msg = unicode(msg, 'utf-8','replace').encode('utf-8','replace');
		self.log_queue[server_id]['log'] = "".join((self.log_queue[server_id]['log'],msg));
		self.log_queue[server_id]['log_idx'] = self.log_queue[server_id]['log_idx'] + len(msg);
		if(len(self.log_queue[server_id]['log'])>(self.buffer_limit)):
			self.log_queue[server_id]['log'] = self.log_queue[server_id]['log'][-(self.buffer_limit):];
		if(self.log_queue[server_id]['log_idx'] > 0xffffff):
			self.log_queue[server_id]['log_idx'] = self.log_queue[server_id]['log_idx'] - 0xffffff;
	def get_queued_log(self, server_id, last_log_idx):
		#print "client asked for server %d log, last_idx = %d, log_idx = %d" % (server_id, last_log_idx, self.log_queue[server_id]['log_idx']);
		log = "";
		log_buf_size = len(self.log_queue[server_id]['log']);
		log_req_size = self.log_queue[server_id]['log_idx'] - last_log_idx;
		log_start_idx = 0;
		
		if(log_req_size < 0):
			# rolled over the log_idx limit?
			log_req_size = log_req_size + 0xffffff;
		if(log_req_size > log_buf_size):
			# they're far behind, and there's going to be discontinuity
			log_req_size = log_buf_size;
		if(log_req_size < log_buf_size):
			# they need a small read, so start later in the buffer
			log_start_idx = log_buf_size - log_req_size;
		
		new_log_idx = self.log_queue[server_id]['log_idx'];
		#print "sending log starting idx %d, size %d"%(log_start_idx, log_req_size);
		log = self.log_queue[server_id]['log'][log_start_idx:log_start_idx+log_req_size];
		
		return (log, new_log_idx);
	def clear_queued_log(self, server_id):
		if(server_id in self.log_queue):
			self.log_queue[server_id]['log'] = "";
			self.log_queue[server_id]['log_idx'] = 0;
