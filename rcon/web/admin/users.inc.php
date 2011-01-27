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
* the 'basic' user table should return columns similar to:
* maulid - int, either a unique primary key, or perhaps 
*    a foreign key into another table where some of this other data resides
* username - the username used at the login screen
* password - the password used at the login screen (currently stored
*    as an unsalted hash)
* adminkey - used for authentication, set and used by this app
* adminkey_time - timestamp for the adminkey, same rules as above
*/
require_once "../config.inc.php";
require_once "../db.inc.php";

$user_table_name = USER_TABLE_NAME;

/* Check for advanced settings, and set sane defaults if they are missing */


/* Most of these defines have to do with:
 * a) how much control administrators have
 * b) integration into other authentication schemes (ie, forum integration)
 */

/* In the case where a view is used to select users, the table used
 * to update may need to be specified. */
if(!defined('UPDATE_USER_TABLE_NAME')) {
   $update_user_table_name = $user_table_name;
} else {
   $update_user_table_name = UPDATE_USER_TABLE_NAME;
}

/* Can admins reset passwords?  if this is tied to other credentials,
 * or it is considered a security risk, we might not want to allow it. */
if(!defined('ALLOW_ADMIN_USER_PASSWORD')) {
   define('ALLOW_ADMIN_USER_PASSWORD', TRUE);
}

/* Can admins specify user id's when creating new users?  This is
 * useful for linking to other credentials, but may create problems
 * if used poorly */
if(!defined('ALLOW_ADMIN_USER_ID')) {
   define('ALLOW_ADMIN_USER_ID', FALSE);
}

/* Can admins specify/change usernames when creating or updating users?
 * This data might come from elsewhere, but in the simplest case
 * it will need to be specified. */

if(!defined('ALLOW_ADMIN_USER_NAME')) {
   define('ALLOW_ADMIN_USER_NAME', TRUE);
}

if(!(ALLOW_ADMIN_USER_ID) && !(ALLOW_ADMIN_USER_NAME)) {
   /* If there's no way to specify either a username or a user ID, not sure
    * how to proceed... */
   die("Invalid configuration - can't admin users!");
}

class users extends db {
   
   public $maulid = -1;
   public $password = NULL;
   public $games = "";
   public $name = "";
   
   function load($id) {
      global $user_table_name;
      $ret = NULL;
      if($id <= 0) return FALSE;
      $this->maulid = $id;
      try {
         if(!self::$dbh) $this->connect();
         $query = "select maulid, games, username from $user_table_name where maulid = :id";
      
         $params = array(':id'=>$id);
      
         $stmt = self::$dbh->prepare($query);
         $ret = $stmt->execute($params);
         if($ret && ($stmt->rowCount > 0)) {
            $result = $stmt->fetch(PDO::FETCH_ASSOC);
            self::$games = $result['games'];
            self::$name = $result['name'];
            return TRUE;
         }
      } catch (PDOException $e) {
         $this->fatal_error($e->getMessage());
      }
      return FALSE;
   }
   
   function save($newid=-1) {
      $params = array(); 
      global $update_user_table_name;
      if($newid < 0) {
         /* Update or delete case */
         $params[':id'] = $this->maulid;
         if($this->games == "") {
            $query = "delete from $update_user_table_name where maulid = :id";
         } else {
            $params[':games'] = $this->games;  
            if((ALLOW_ADMIN_USER_PASSWORD) && $this->password != NULL) {
               $query = "update $update_user_table_name set password = MD5(:password), games = :games where maulid = :id"; 
               $params[':password'] = $this->password;
            } else {
               $query = "update $update_user_table_name set games = :games where maulid = :id";
            }
         }
      } else {
         $cols = array();
         $vals = array();
         /* Insert new user case */
         if((ALLOW_ADMIN_USER_ID) && $newid != 0) {
            $cols[] = "maulid";
            $vals[] = ":id";
            $params[":id"] = $newid;
         }
      
         if(ALLOW_ADMIN_USER_PASSWORD) {
            $cols[] = "password";
            $vals[] = "MD5(:password)";
            $params[":password"] = $this->password; 
         }
         
         if(ALLOW_ADMIN_USER_NAME) {
            $cols[] = "username";
            $vals[] = ":name";
            $params[":name"] = $this->name;
         }
         
         $cols[] = "games";
         $vals[] = ":games";
         $params[':games'] = $this->games;
         
         $insert_cols = implode(", ", $cols);
         $insert_vals = implode(", ", $vals);
         $query = "insert into $update_user_table_name ($insert_cols) values ($insert_vals)";
      }
      
      try {
         if(!self::$dbh) $this->connect();
         $stmt = self::$dbh->prepare($query);
         $ret = $stmt->execute($params);
      } catch (PDOException $e) {
         $this->fatal_error($e->getMessage());
         return FALSE;
      }
      return TRUE;      
   }
   
   function search($games = NULL) {
      $result = NULL;
      global $user_table_name;
      try {
         if($games != NULL) {
            $query = "select maulid, games, username from $user_table_name
               where games like :games order by username";
            $params = array(":games"=> "%".$games."%"); 
         } else {
            $query = "select maulid, games, username from $user_table_name
               order by username";
            $params = array();
         }
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
