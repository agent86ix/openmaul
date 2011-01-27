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
?>

<head><title>MAUL RCON User Admin Page</title></head>
<body>
<?php
require_once "../config.inc.php";
include "users.inc.php";
include "../auth.inc.php";

$auth_obj = new auth();
if(array_key_exists("adminkey", $_REQUEST)) $auth_obj->adminkey = $_REQUEST['adminkey'];
if(array_key_exists("sessid", $_REQUEST)) $auth_obj->sessid = $_REQUEST['sessid'];
if(!$auth_obj->admin_validate()) {
?>
You are not authorized to view this page, or your session timed out.  Please <a href="../maul_rcon_login.php">log in again.</a>
<?php
   die();
}

if(array_key_exists("request", $_POST)) {
   $request = $_POST['request'];
   
   $user = new users();
   $user->games = $_POST['games'];
   
   if(array_key_exists('maulid', $_POST)) {
      $user->maulid = $_POST['maulid'];
   } else {
      $user->maulid = 0;
   }
   
   if(array_key_exists('username', $_POST)) {
      $user->name = $_POST['username'];
   }
   
   if(array_key_exists('password', $_POST)) {
      if(($_POST['password'] != "********") && ($_POST['password'] != "")) 
         $user->password = $_POST['password'];
   }
   
   if($request == "Add") {
      $result = $user->save($user->maulid);
   } else {
      $result = $user->save();
   }
   
   if($result == TRUE) {
      print "UPDATE OK!";
   } else {
      print "UPDATE FAILED!";
   }
   
}
?>
<h3>Existing Users</h3>
<table border=1 width=100%>
<tr><td>Name</td><td>Access</td><td>Password</td><td>Save</td></tr>
<?php
$user = new users();
$userlist = $user->search();
$odd = TRUE;

foreach($userlist as $key=>$user) {
   $gameselect = "";
   foreach($gameopt as $name=>$val) {
      if($user['games'] == $val) $selected = " selected";
      else $selected = "";
      $gameselect = $gameselect."<option value=\"$val\"$selected>$name</option>";
   }
?>
   <tr <?if($odd)echo("bgcolor=gray")?>>
   <form method=post action="user_admin.php">
   <input type=hidden name=maulid value="<? echo $user['maulid']?>">
   <input type=hidden name=adminkey value="<? echo $auth_obj->adminkey?>">
   <input type=hidden name=sessid value="<? echo $auth_obj->sessid?>">
   <?php if(ALLOW_ADMIN_USER_NAME) { ?>
      <td><input type=text name="username" value="<? echo $user['username']?>"></td>
   <?php } else { ?>
      <td><? echo $user['username']?></td>
   <?php } ?>
   
   <td><select name="games"><? echo $gameselect?></select></td>
   <?php if(ALLOW_ADMIN_USER_PASSWORD) { ?>
      <td><input type=password name="password" value="********"></td>
   <?php } ?>
   
   <td><input type=submit name="request" value="Update">
   </form>
   </tr>
<?
   if($odd) $odd = FALSE;
   else $odd = TRUE;
}

?>
</table>

<?php
   $gameselect = "";
   unset($gameopt['(delete user)']);
   foreach($gameopt as $name=>$val) {
      $gameselect = $gameselect."<option value=\"$val\">$name</option>";
   }
?>

<h3>Add New User</h3>
<form action="user_admin.php" method=post>
<input type=hidden name=adminkey value="<? echo $auth_obj->adminkey?>">
<input type=hidden name=sessid value="<? echo $auth_obj->sessid?>">
<table>

<?php if(ALLOW_ADMIN_USER_ID) { ?>
   <tr><td>MAUL ID:</td><td><input type=text name="maulid"></td></tr>
<?php } ?>

<?php if(ALLOW_ADMIN_USER_NAME) { ?>
   <tr><td>Username:</td><td><input type=text name="username"></td></tr>
<?php } ?>

<?php if(ALLOW_ADMIN_USER_PASSWORD) { ?>
   <tr><td>Password:</td><td><input type=text name="password"></td></tr>
<?php } ?>

<tr><td>Access:</td><td><select name=games><? echo $gameselect; ?></select></td></tr>
<tr><td><input type=submit name="request" value="Add"></td><td></td></tr>
</table>
</form>
</body>
</html>
