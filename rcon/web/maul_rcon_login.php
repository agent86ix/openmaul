<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
<!--
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
-->
<html>
	<head>
		<title>MAUL RCON Login</title>
		<script type="text/javascript" src="http://ajax.googleapis.com/ajax/libs/jquery/1.3.2/jquery.min.js"></script>
		<script type="text/javascript" src="jquery.form.js"></script>
		<link rel="stylesheet" type="text/css" href="wc.css" />
<script type="text/javascript" language="javascript">

function login_done(json, ajax_status) {
	if(json.status && json.text) {
		$("#status").text(json.text);
	} else if(json.status == 0) {
		if(json.sessid) {
			var postdata = "<input type=hidden name=sessid value=\""+json.sessid+"\">"
				+"<input type=hidden name=password value=\""+$("#password").val()+"\">"
				+"<input type=hidden name=admin value=\""+json.admin+"\">";
			$("#redirectform").html(postdata);
			$("#redirectform").submit();
			return;
		} else {
			$("#status").text("An unknown error occurred...");
		}
	} else {
		$("#status").text("An unknown error occurred...");
	}
	$('#loginbutton').removeAttr('disabled');
}
function login_start(data, form, options) {
	$('#loginbutton').attr('disabled', 'disabled');
	$("#status").text("Please wait...");
}

$(document).ready(function() {
	var options = {
		beforeSubmit: login_start,
		success: login_done,
		dataType: 'json'
	};
	$('#loginform').ajaxForm(options); 
	$('#loginbutton').removeAttr('disabled');
	if (navigator.appName == 'Microsoft Internet Explorer') {
		$("#status").text("WARNING: This application does not work properly with Internet Explorer.  You may encounter unusual behavior or missing features.  You have been warned!");
	}
	
});


</script>
</head>
<body>
<div class=loginform>
<h3><img src="network-server.png">MAUL RCON Beta</h3>
<form id=loginform method=POST action="maul_rcon_exec3.php">
<table>
<tr><td align=right>Username:</td><td><input type=text name=username value="<?php if(array_key_exists('maul_rcon_username', $_COOKIE)) echo $_COOKIE['maul_rcon_username'];?>"></td></tr>
<tr><td align=right>Password:</td><td><input id=password type=password name=password></td></tr>
<tr><td colspan=2 align=center><input type=submit value="Login" id=loginbutton disabled="disabled"></td></tr>
</table>
</form>
</div>
<div style="clear:both"></div>

<div id=status></div>

<form id=redirectform method=POST action="maul_rcon3.php">
</form>
<noscript>
<p><font color=red>Javascript is disabled on this browser.  You will not be able to use MAUL RCON until Javascript is enabled.</font>

</noscript>
</body>
</html>
