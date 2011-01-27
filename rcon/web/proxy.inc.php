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

function proxy_send_command($req) {
   $sock = socket_create(AF_INET, SOCK_DGRAM, SOL_UDP);
   socket_set_option($sock, SOL_SOCKET, SO_RCVTIMEO, array("sec"=>10, "usec"=>0));

   $str = json_encode($req);
   $len = strlen($str);

   socket_sendto($sock, $str, $len, 0, PROXY_ADDR,PROXY_PORT);
   $res = socket_read($sock, 40960);
   if($res == FALSE) {
      $res = array();
      $res['status'] = 1;
      $res['text'] = "Network error connecting to RCON proxy.";
      $res = json_encode($res);
   } 

   socket_close($sock);
   return $res;
}

?>
