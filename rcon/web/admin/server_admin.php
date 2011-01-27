<head><title>MAUL RCON Server Admin Page</title></head>
<body>
<?php
include "servers.inc.php";
include "../auth.inc.php";
require_once "../proxy.inc.php";


$auth_obj = new auth();
if(array_key_exists("adminkey", $_REQUEST)) $auth_obj->adminkey = $_REQUEST['adminkey'];
if(array_key_exists("sessid", $_REQUEST)) $auth_obj->sessid = $_REQUEST['sessid'];
if(!$auth_obj->admin_validate()) {
?>
You are not authorized to view this page, or your session timed out.  Please <a href="../maul_rcon_login.php">log in again.</a>
<?php
   die();
}

if(array_key_exists("proxyreset", $_POST)) {
   $req = array("sessid"=>$auth_obj->sessid, "req_id"=>7);
   $res = proxy_send_command($req);
   $res_arr = json_decode($res, TRUE);
   if($res_arr['status'] == 0) {
      die("Success!  Close this window and log in to MAUL RCON again to continue.");
   } else {
      die("Error: unable to restart RCON proxy...");
   }
}

if(array_key_exists("request", $_POST)) {
   $request = $_POST['request'];
   
   $server = new servers();
   $server->name = $_POST['name'];
   $server->address = $_POST['address'];
   $server->port = $_POST['port'];
   $server->game = $_POST['game'];
   if(array_key_exists('table_id_idx', $_POST)) {
	   $server->table_id_idx = $_POST['table_id_idx'];
   }

   if(($_POST['rcon_password'] != "********") && ($_POST['rcon_password'] != "")) $server->rcon_password = $_POST['rcon_password'];
   if($request != "Add") {
      $server->serverid = $_POST['serverid'];
   }

   $result = $server->save();
   
   if($result == TRUE) {
      print "UPDATE OK!";
   } else {
      print "UPDATE FAILED!";
   }
   
}
?>
<h3>Existing Servers</h3>
<table border=1 width=100%>
<tr><td>Server</td><td>Address</td><td>Port</td><td>Game</td><td>RCON Password</td><td>Save</td></tr>
<?php
$server = new servers();
$serverlist = $server->search();
$odd = TRUE;
foreach($serverlist as $key=>$server) {
   
?>
   <tr <?if($odd)echo("bgcolor=gray")?>>
   <form method=post action="server_admin.php">
   <input type=hidden name=serverid value="<? echo $server['id']?>">
   <?php if(array_key_exists('table_id_idx', $server)) { ?>
       <input type=hidden name=table_id_idx value="<? echo $server['table_id_idx']?>">
   <?php } ?>
   <input type=hidden name=adminkey value="<? echo $auth_obj->adminkey?>">
   <input type=hidden name=sessid value="<? echo $auth_obj->sessid?>">
   <td><input type=text name="name" value="<? echo $server['name']?>"></td>
   <td><input type=text name="address" value="<? echo $server['address']?>"></td>
   <td><input type=text name="port" value="<? echo $server['port']?>"></td>
   
   <td><input type=text name="game" value="<? echo $server['game']?>"></td>
   
   <td><input type=password name="rcon_password" value="********"></td>
   
   <td><input type=submit name="request" value="Update">
   </form>
   </tr>
<?
   if($odd) $odd = FALSE;
   else $odd = TRUE;
}

?>
</table>

<h3>Add New Server</h3>
<form action="server_admin.php" method=post>
<input type=hidden name=adminkey value="<? echo $auth_obj->adminkey?>">
<input type=hidden name=sessid value="<? echo $auth_obj->sessid?>">
<table>
<tr><td>Name:</td><td><input type=text name="name"></td></tr>
<tr><td>Address:</td><td><input type=text name="address"></td></tr>
<tr><td>Port:</td><td><input type=text name="port"></td></tr>
<tr><td>Game:</td><td><input type=text name="game"></td></tr>
<tr><td>RCON Password:</td><td><input type=text name="rcon_password"></td></tr>
<tr><td><input type=submit name="request" value="Add"></td><td></td></tr>
</table>
</form>

<h3>Reset Proxy</h3>
(Do this after you make server changes to update the server list.  This will log everyone off!)
<form action="server_admin.php" method=post>
<input type=hidden name=adminkey value="<? echo $auth_obj->adminkey?>">
<input type=hidden name=sessid value="<? echo $auth_obj->sessid?>">
<input type=submit name="proxyreset" value="Reset Proxy">
</form>
</body>
</html>
