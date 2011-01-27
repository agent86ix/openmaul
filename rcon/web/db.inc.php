<?php

/*
 * This file is part of the OpenMAUL project
 * Copyright (C) 2011 agent86.ego@gmail.com
 * 
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 * 
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */ 

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
