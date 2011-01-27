<?php

require_once "config.inc.php";
class db {
	protected static $dbh = false;
	
	function connect() {
		$host = DB_HOST;
		$dbname = DB_NAME;
		$user = DB_USER;
		$pass = DB_PASS;
		self::$dbh = new PDO("mysql:host=$host;dbname=$dbname", $user, $pass);
		self::$dbh->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
	}
	
	protected function fatal_error($msg) {
		$debug = DEBUG;
		if(!$debug) return;
		echo "<pre>ERROR: $msg\n";
		$bt = debug_backtrace();
		foreach($bt as $line) {
			$args = var_export($line['args'], true);
			echo "{$line['function']}($args) at {$line['file']}:{$line['line']}\n";
		}
		echo "</pre>";
		die();
	}
	
}
?>
