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

require_once "proxy.inc.php";
require_once "auth.inc.php";
header('Content-Type: text/html'); 
header('Pragma: no-cache');
header('Cache-Control: no-cache, no-store, max-age=0, must-revalidate');

$serverlist = null;
if(array_key_exists('serverlist',$_GET)) {
    $serverlist = true;
}
$command = null;
if(array_key_exists('command',$_GET)) {
    $command = $_GET['command'];
}
$getlog = null;
if(array_key_exists('getlog',$_GET)) {
    $getlog = $_GET['getlog'];
}
$getstatus = null;
if(array_key_exists('getstatus',$_GET)) {
    $getstatus = $_GET['getstatus'];
}
$serverid = null;
if(array_key_exists('serverid', $_GET)) {
    $serverid = $_GET['serverid'];
}

if(array_key_exists('sessid', $_REQUEST)) $sessid = $_REQUEST['sessid'];
else $sessid = NULL;


if(!$sessid) {
    /* Authenticate the user, and get a session ID */
    $arr = array();
    $arr['status'] = 1;
    $arr['text'] = "Incorrect login.";
    
    $auth_obj = new auth();
    $maulid = $auth_obj->check_password($_POST['username'], $_POST['password']);
    if($maulid > 0) {
       $req_arr = array("req_id"=>0, "maul_id"=>$maulid, "password"=>$_POST['password']);
       $res = proxy_send_command($req_arr);
       setcookie("maul_rcon_username", $_POST['username']);
       die($res);
    } else {
        /* Failed auth check on the server side, delay to avoid hammering */
        sleep(2);
    }
    die(json_encode($arr)); 
}

if($serverlist) {
   $req_arr = array("req_id"=>5, "sessid"=>$sessid);
   $res = proxy_send_command($req_arr);
   die($res);
}

if($command) {
   $req_arr = array("req_id"=>1, "sessid"=>$sessid, "server_id"=>$serverid, "command"=>$command);
   $res = proxy_send_command($req_arr);
   die($res);
}
if($getlog) {
   $req_arr = array("req_id"=>2, "sessid"=>$sessid, "server_id"=>$serverid);
   $res = proxy_send_command($req_arr);
   die($res);
}
if($getstatus) {
   $req_arr = array("req_id"=>3, "sessid"=>$sessid, "server_id"=>$serverid);
   $res = proxy_send_command($req_arr);
   die($res);
}

?>
