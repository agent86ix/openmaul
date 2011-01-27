<?php

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
