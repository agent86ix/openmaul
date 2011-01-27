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

/* 
* Administer server table entries. The schema should resemble:
* id - unique identifier (usually an int, auto_increment)
* address - the IP address of the server, in some sort of string format
* port - the numerical port of the server
* rcon_password - the server's RCON password, in plain text
* name - Server's name, for description purposes
* game - the server's game, used primarily for grouping servers & setting access rights
*
* table_id (OPTIONAL) - in the special case of multiple tables unioned into
* a single view, this represents the source table and it's id column name
* , with a comma in between.  This used to determine which table to update
* when a server is changed.  If that was gibberish, then you can probably
* safely ignore this column :)  Otherwise, you will need to specify this
* in the create view statement, and specify INSERT_SERVER_TABLE_NAME
* in the config file.
*/
require_once "../db.inc.php";
require_once "../config.inc.php";


$select_server_table_name = SERVER_TABLE_NAME;

/* In the case where the select table is a view, potentially
 * a union of multiple source tables, we need to specify the
 * default table to insert into.  Normal users should not
 * need to specify this, and so it will default to the server
 * table name spec'ed in the config.
 */

if(!defined('INSERT_SERVER_TABLE_NAME')) {
   $insert_server_table_name = $select_server_table_name;
} else {
   $insert_server_table_name = INSERT_SERVER_TABLE_NAME;
}


class servers extends db {
   
   public $address = -1;
   public $rcon_password = NULL;
   public $game = "";
   public $name = "";
   public $port = 0;
   public $table_id_idx = NULL;
   public $serverid = -1;
   
   function save() {
      $params = array(); 
      $tablename = NULL;
      $idcolname = NULL;
      global $insert_server_table_name;
      global $select_server_table_name;
      
      if($this->table_id_idx != NULL) {
         try {
            $query = "select distinct table_id from `$select_server_table_name`
               where table_id_idx = :table_id_idx";
            if(!self::$dbh) $this->connect();
            $stmt = self::$dbh->prepare($query);
            $ret = $stmt->execute(array(":table_id_idx"=>$this->table_id_idx));
            if($ret) {
               $result = $stmt->fetch(PDO::FETCH_ASSOC);
               if($result) {
                  $table_id_arr = explode(',',$result['table_id']);
                  $tablename = $table_id_arr[0];
                  $idcolname = $table_id_arr[1];
               }
               
            }
            if(($tablename == NULL) || ($idcolname == NULL)) {
               return FALSE;
            }
         } catch (PDOException $e) {
            $this->fatal_error($e->getMessage());
            return FALSE;
         }
      } else {
         $tablename = $insert_server_table_name;
         $idcolname = "id";
      }

      $params[':address'] = $this->address;
      $params[':port'] = $this->port;
      $params[':name'] = $this->name;
      
      if($this->serverid > 0) {
         $params[':serverid'] = $this->serverid;
         if($this->game == "") {
            $params = array(':serverid'=>$this->serverid);
            $query = "delete from $tablename where `$idcolname` = :serverid ";
         } else {
            $params[':game'] = $this->game;  
            if($this->rcon_password != NULL) {
               $query = "update $tablename set name = :name, address = :address, port = :port, rcon_password = :rcon_password, game = :game where `$idcolname` = :serverid"; 
               $params[':rcon_password'] = $this->rcon_password;
            } else {
               $query = "update $tablename set name = :name, address = :address, port = :port, game = :game where `$idcolname` = :serverid";
            }
         }
      } else {
         $query = "insert into $tablename (name, address, port, rcon_password, game) values(:name, :address, :port, :rcon_password, :game)";

         $params[':game'] = $this->game;  
         $params[':rcon_password'] = $this->rcon_password;
      }
      
      try {
         if(!self::$dbh) $this->connect();
         $stmt = self::$dbh->prepare($query);
         $ret = $stmt->execute($params);
      } catch (PDOException $e) {
         print($query);
         print_r($params);
         $this->fatal_error($e->getMessage());
         return FALSE;
      }
      return TRUE;      
   }
   
   function search() {
      global $select_server_table_name;
      
      $result = NULL;
      try {
         $query = "select * from `$select_server_table_name`";
         $params = array();
         if(!self::$dbh) $this->connect();
         $stmt = self::$dbh->prepare($query);
         $ret = $stmt->execute($params);
         $result = $stmt->fetchAll(PDO::FETCH_ASSOC);
      } catch (PDOException $e) {
         $this->fatal_error($e->getMessage());
         return NULL;
      }
      return $result;
      
   }
   
   
   
}
?>
