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
require_once "proxy.inc.php";
require_once "db.inc.php";

/* Authentication uses the user table, see also admin/users.inc.php
 */

$user_table_name = USER_TABLE_NAME;

class auth extends db {

   public $adminkey = NULL;
   public $sessid = NULL;
   public $maulid = -1;
   
   
   private function check_sessionid() {
      /* send reqid = 6 to the proxy */
      $req_arr = array("req_id"=>6, "sessid"=>$this->sessid);
      $res = proxy_send_command($req_arr);
      $response = json_decode($res, TRUE);
      //print_r($response);
      if(array_key_exists('admin', $response) && ($response['admin'] != 0)) {
         $this->maulid = $response['maul_id'];
         return TRUE;
      } 
      return FALSE;
   }
   
   function admin_validate() {
      global $user_table_name;

      if($this->adminkey) {
         /* Check database to see if this is in the valid window */
         try {
            if(!self::$dbh) $this->connect();
            $query = "select maulid 
               from `$user_table_name`
               where adminkey = :adminkey and adminkey_time > DATE_SUB(NOW(), INTERVAL 30 minute)";
         
            $params = array(':adminkey'=>$this->adminkey);
         
            $stmt = self::$dbh->prepare($query);
            $ret = $stmt->execute($params);
            if($ret && (count($stmt->fetchAll()))) {
               /* Yes?  Check passed. */
               return TRUE;
            }
            $stmt->closeCursor();
         } catch (PDOException $e) {
            $this->fatal_error($e->getMessage());
         }
      } 
      
      
      /* Admin key is not present, or is invalid. 
         Check session id and try to create new admin key */
      
      if($this->check_sessionid()) {
         try {
            $this->adminkey = uniqid();
            if(!self::$dbh) $this->connect();
            $query = "update `$user_table_name` set adminkey = :adminkey, adminkey_time = NOW() where maulid = :maulid";
         
            $params = array(':adminkey'=>$this->adminkey, ':maulid'=>$this->maulid);
         
            $stmt = self::$dbh->prepare($query);
            $ret = $stmt->execute($params);
            if($ret) {
               /* Yes?  Check passed. */
               return TRUE;
            }
         } catch (PDOException $e) {
            $this->fatal_error($e->getMessage());
         }
      }
      /* if this failed, kick them out! */      
      return FALSE;
   }

   function check_password($username, $password) {
      global $user_table_name;
      try {
         if(!self::$dbh) $this->connect();
         $query = "select maulid from `$user_table_name` where
            username = :username
            and password = MD5(:password)";
       
         $params = array(':username'=>$username, ':password'=>$password);
       
         $stmt = self::$dbh->prepare($query);
         $ret = $stmt->execute($params);
         if($ret) {
             $result = $stmt->fetch(PDO::FETCH_ASSOC);
             if($result) {
               return $result['maulid'];
             } else {
               return -1;
             }
         }
         $stmt->closeCursor();
      } catch (PDOException $e) {
         $this->fatal_error($e->getMessage());
      }
   }

}
?>
