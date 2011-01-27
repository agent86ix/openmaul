<?php if (!array_key_exists('sessid', $_POST)) header( 'Location: ./maul_rcon_login.php' ) ; ?>
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
<html>
	<head>
		<title>MAUL RCON Beta 4</title>
		<script type="text/javascript" src="http://ajax.googleapis.com/ajax/libs/jquery/1.3.2/jquery.min.js"></script>
		<script type="text/javascript" src="jquery.corner.js"></script>
		<script type="text/javascript" src="jquery.contextMenu.js"></script>
		<link rel="stylesheet" type="text/css" href="wc.css" />
<script type="text/javascript" language="javascript">

var session_id = "<?php 
	if(array_key_exists('sessid', $_POST)) echo $_POST['sessid']; 
	else echo "-1";
?>";
var server_id = -1;
var line_counter = 0;
var MAX_LINE_COUNT = 6000;

var log_refresh_time = 2000;
var status_refresh_time = 5000;
var log_refresh_timer_id = null;
var status_refresh_timer_id = null;

var auto_scroll = 1;
var server_events = 1;
var game_events = 1;
var ie_sucks = 0;

/* Functions for IE Suckage: */
var active_element = null;
var currently_focused = 1;
function maybe_blur_init() {
	active_element = document.activeElement;
	document.onfocusout = maybe_blur;
	document.onfocusin = maybe_focus;
}

/* Maybe they're not in the window???  WHO KNOWS?  Not IE! */
function maybe_blur() {
		if (active_element && active_element != document.activeElement) {
			active_element.onfocusout = null;
			active_element = document.activeElement;
			active_element.onfocusout = maybe_blur;
		} else {
			/* blur! */
			currently_focused = 0;
			//$("#statusline").html("BLUR");
			log_refresh_time = 20000;
			status_refresh_time = 40000;
		}
}

function maybe_focus() {
	if(currently_focused) return;
	currently_focused = 1;
	active_element.onfocusin = null;
	//$("#statusline").html("FOCUS");
	log_refresh_time = 2000;
	if(log_refresh_timer_id) {
		clearTimeout(log_refresh_timer_id);
		setTimeout ( "get_log_data()", log_refresh_time );
	}
	status_refresh_time = 5000;
	if(status_refresh_timer_id) {
		clearTimeout(status_refresh_timer_id);
		setTimeout ( "get_server_status()", status_refresh_time );
	}
}

/* End IE-specific crap that I shouldn't have to write in freaking 2009
   because wtf microsoft?  I mean seriously. */

function get_current_time() {
	var currentTime = new Date();
	var month = currentTime.getMonth() + 1;
	var day = currentTime.getDate();
	var year = currentTime.getFullYear();
	var hours = currentTime.getHours();
	var minutes = currentTime.getMinutes();
	if (minutes < 10){
		minutes = "0" + minutes;
	}
	var seconds = currentTime.getSeconds();
	
	return month+'/'+day+'/'+year+' '+hours+':'+minutes+':'+seconds+' ';

}

var kill_str = '" killed "';
var trig_str = '" triggered "';
var rcon_str = ': rcon from "';
var class_str = '" changed role to "';
var team_str = '" joined team "';
var suicide_str = " committed suicide with ";
var attack_str = '" attacked "';
var world_str = 'World triggered';
var dfens_str = ': [D-FENS] "';
var admin_str = ' triggered sm_chat ';
var allchat_str = ' triggered sm_say ';
function print_results_to_console(output_server_id, result_string, is_command_output) {
	if(result_string) {
		var result_array = result_string.split('\n');
		var output = '';
		var display_count = 0;
		for (var line_index in result_array) {
			var cur_line = result_array[line_index];
			if(cur_line.length == 0) continue;
			var pre_class = "command_output";
			var pre_style = "";
			display_count++;
			if(!is_command_output) {
				pre_class = "default";
				if((cur_line.indexOf(rcon_str) != -1) || (cur_line.indexOf(dfens_str) != -1)) {
					pre_class = "svr";
					if(!server_events) {
						pre_style = "display:none";
						display_count--;
					}
				} else if((cur_line.indexOf(kill_str)!=-1) || (cur_line.indexOf(trig_str)!=-1)
					|| (cur_line.indexOf(suicide_str)!=-1) || (cur_line.indexOf(class_str)!=-1)
					|| (cur_line.indexOf(team_str)!=-1) || (cur_line.indexOf(attack_str)!=-1)
					|| (cur_line.indexOf(world_str)!=-1)) {
					pre_class = "game";
					if(!game_events) {
						pre_style = "display:none";
						display_count--;
					}

				} else if((cur_line.indexOf(allchat_str)!= -1) || (cur_line.indexOf(admin_str) != -1)) {
					pre_class= "greenchat";
				}
			}
			cur_line = cur_line.replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");
			output += "<pre class="+pre_class+" style=\""+pre_style+"\" count="+line_counter+">"+cur_line+"\n</pre>";
			line_counter++;
			//$("[count='"+(line_counter-MAX_LINE_COUNT)+"']").remove();
		}
			
		$("#con"+output_server_id).append(output);	
		var cur_line_count = $('#con'+output_server_id).find("pre").size(); 
		if(cur_line_count > MAX_LINE_COUNT) {
			var lines_to_delete = cur_line_count - MAX_LINE_COUNT;
			$("#con"+output_server_id).find("pre:lt("+lines_to_delete+")").remove();
		}

		if(auto_scroll && (display_count > 0)) {
			var console = $("#con"+output_server_id);
			$(console).attr('scrollTop', $(console).attr('scrollHeight')+10);
		}
	}
}
var log_request_pending = 0;
function get_log_data() {
	if(log_request_pending) return;
	log_request_pending = 1;
	if(log_refresh_timer_id) {
		clearTimeout(log_refresh_timer_id);
		log_refresh_timer_id = null;
	}
	$.ajax({
		type: "GET",
		url: "maul_rcon_exec3.php",
		data: {getlog: '1', sessid: session_id, serverid: server_id}, 
		success: function(json) {
			log_request_pending = 0;

			var status = $(json).attr('status');
			if(status != 0) {
				$("#statusline").html(get_current_time()+"Error retrieving log data:"+$(json).attr('text'));
				if(status == 1) {
					log_refresh_timer_id = setTimeout ( "get_log_data()", log_refresh_time );
				}
				return;
			}
			var result_string = $(json).attr('text');
			print_results_to_console(json.server_id, result_string, false);
			log_refresh_timer_id = setTimeout ( "get_log_data()", log_refresh_time );
		},
		dataType: "json",
		error: function(request, status, error) {
			if(status == "timeout") {
				$("#statusline").html(get_current_time()+"Error retrieving log data.  Network timeout.");
			}
			log_request_pending = 0;
			log_refresh_timer_id = setTimeout ( "get_log_data()", log_refresh_time );
		}
	});
}

var status_request_pending = 0;
function get_server_status() {
	if(status_request_pending) return;
	status_request_pending = 1;
	if(status_refresh_timer_id) {
		clearTimeout(status_refresh_timer_id);
		status_refresh_timer_id = null;
	}
	$.ajax({
		type: "GET",
		url: "maul_rcon_exec3.php", 
		data: {getstatus:1, serverid:server_id, sessid:session_id}, 
		success: function(json) {
			
			if(json.status != 0) {
				$("#statusline").html(get_current_time()+"Error retrieving status data: "+$(json).attr('text'));
				if(status == 1) {
					log_refresh_timer_id = setTimeout ( "get_server_status()", status_refresh_time );
				}
				return;
			}
			for(var id in json.player_counts) {
				var opt_obj = $("#server_select").find("[value="+id+"]");
				var output = $(opt_obj).text();
				output = output.substr(0,output.lastIndexOf('('));
				$(opt_obj).text(output+'('+json.player_counts[id]+')');
			}
			var playernames = '';
			for(var playeridx in json.player_names) {
				cur_player_name = json.player_names[playeridx];
				cur_player_name = cur_player_name.replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");
				playernames += '<pre class=playername>'+cur_player_name+'</pre><br>';
			}
			if(playernames == '') {
				playernames = '<pre>(Server Empty)</pre>';
			}
			$("#usr"+json.server_id).html(playernames);	
			$("#usr"+json.server_id).find(".playername").contextMenu({menu: 'playermenu'}, playermenu_handler);	

			status_request_pending = 0;
			status_refresh_timer_id = setTimeout("get_server_status()", status_refresh_time);
		},
		dataType:"json",
		error: function(request, status, error) {
			if(status == "timeout") {
				$("#statusline").html(get_current_time()+"Error retrieving status data.  Network timeout.");
			}
			status_refresh_timer_id = setTimeout("get_server_status()", status_refresh_time);
			status_request_pending = 0;
		}
	});
}

function refresh_connection() {
	$.get("maul_rcon_exec3.php" ,{serverlist: '1', sessid: session_id}, function(json) {
		var status = $(json).attr('status');
		if(status != 0) {
			$("#statusline").html(get_current_time()+$(json).attr('text'));
			return;
		}
		
		var server_opts = '';
		var consoles = '';
		var userlists = '';
		var con_height = $(window).height() - 165;
		var sorted_servers = new Array();
		for(var id in json.server_list) {
			sorted_servers.push(new Array(id, json.server_list[id]));
		}
		sorted_servers.sort(function(a,b) {
			if(a[1]>b[1]) return 1;
			if(b[1]>a[1]) return -1;
			return 0;
		});
		for(var i in sorted_servers) {
			id = sorted_servers[i][0];
			name = sorted_servers[i][1];
			if(server_id == -1) server_id = id;
			server_opts += '<option value="'+id+'">'+name+' (?)</option>';
			consoles += '<div class=server_console style="height:'+con_height+'px;" id=con'+id+'/>';
			userlists += '<div class=user_list style="height:'+con_height+'px; " id=usr'+id+'/>';
		}
		$("#consoles").html(consoles);
		$(".server_console").hide();
		$("#con"+server_id).show();
		
		$("#userlists").html(userlists);
		$(".user_list").hide();
		$("#usr"+server_id).show();
		
		
		$("#server_select").html(server_opts);
		
		$("#server_select").change(function(e) {
			
			var new_server_id = $(this).val();
			if(new_server_id == server_id) return;
			
			$("#con"+server_id).hide();
			$("#usr"+server_id).hide();
			
			$("#con"+new_server_id).show();
			$("#usr"+new_server_id).show();
			$("#usr"+new_server_id).html("<pre>Loading...</pre>");
			server_id = new_server_id;
			if(log_refresh_timer_id) {
				clearTimeout(log_refresh_timer_id);
				setTimeout ( "get_log_data()", 1000 );
			}
			
			if(status_refresh_timer_id) {
				clearTimeout(status_refresh_timer_id);
				setTimeout ( "get_server_status()", 1000 );
			}
		});
		$(".server_console").contextMenu({menu: 'servermenu'}, servermenu_handler);
		
		get_log_data();
		get_server_status();
	}, "json");
}

var command_history = [];
var command_history_pos = 0;

function handle_command_history(e) {
	if(e.keyCode == '38') { // up arrow
		if(command_history_pos <= 0) {
			return;
		}
		command_history_pos--;
		$("#command_input").val(command_history[command_history_pos]);
	} else if (e.keyCode == '40') {  // down arrow
		if(command_history_pos >= (command_history.length-1)) {
			return;
		}
		command_history_pos++;
		$("#command_input").val(command_history[command_history_pos]);
	}
}

$(document).ready(function() {
	/* Check for IE, prepare to handle its issues if so. */
	if (navigator.appName == 'Microsoft Internet Explorer') ie_sucks = 1;
	refresh_connection();
	$("#commandline").submit(function(e) {
		// handle add to command history
		var new_command = $("#command_input").val();
		command_history.push(new_command);
		command_history_pos = command_history.length;
		$.get("maul_rcon_exec3.php", {command:new_command, 
			serverid:server_id, sessid:session_id}, function(json) {
			
			var status = $(json).attr('status');
			if(status != 0) {
				$("#statusline").html(get_current_time()+$(json).attr('text'));
				return;
			}
			
			var result_string = $(json).attr('text');
			print_results_to_console(json.server_id, result_string, true);
			$("#command_input").val('');
			
		}, "json");
		e.preventDefault();
	});
	$("#commandline").keyup(handle_command_history);
	$(".toggle_button").click(function(e) {
		var varid = $(this).attr('varid');
		if(varid == 0) {
			if(game_events) {
				game_events = 0;
				$(this).text('Show Game Events');
				$(".game").hide();
			} else {
				game_events = 1;
				$(this).text('Hide Game Events');
				$(".game").show();
				$("#con"+server_id).attr('scrollTop', $("#con"+server_id).attr('scrollHeight')+10);
			}
		} else if(varid == 1) {
			if(server_events) {
				server_events = 0;
				$(this).text('Show Server Events');
				$(".svr").hide();
			} else {
				server_events = 1;
				$(this).text('Hide Server Events');
				$(".svr").show();
				$("#con"+server_id).attr('scrollTop', $("#con"+server_id).attr('scrollHeight')+10);
			}
		} else if(varid == 2) {
			if(auto_scroll) {
				auto_scroll = 0;
				$(this).text('Start Auto Scroll');
			} else {
				auto_scroll = 1;
				$(this).text('Stop Auto Scroll');
				$("#con"+server_id).attr('scrollTop', $("#con"+server_id).attr('scrollHeight')+10);
			}		
		}
		e.preventDefault();
	});

	$("#prevlink").click(function(e) {
		var selected_opt = $('option:selected', '#server_select');
		if($(selected_opt).prev('option').length) {
			$(selected_opt).removeAttr('selected').prev('option').attr('selected', 'selected'); 
		}
		$("#server_select").change();
		e.preventDefault();
	});
	$("#nextlink").click(function(e) {
		var selected_opt = $('option:selected', '#server_select');
		if($(selected_opt).next('option').length) {
			$(selected_opt).removeAttr('selected').next('option').attr('selected', 'selected'); 
		}
		$("#server_select").change();
		e.preventDefault();
	});
	if(!ie_sucks) {
	$(window).focus(function () {
		log_refresh_time = 2000;
		if(log_refresh_timer_id) {
			clearTimeout(log_refresh_timer_id);
			setTimeout ( "get_log_data()", log_refresh_time );
		}
		status_refresh_time = 5000;
		if(status_refresh_timer_id) {
			clearTimeout(status_refresh_timer_id);
			setTimeout ( "get_server_status()", status_refresh_time );
		}
	});
	$(window).blur(function () {
		log_refresh_time = 20000;
		status_refresh_time = 40000;
	});
	} else {
		maybe_blur_init();
	}

});

function servermenu_handler(action, el, pos) {
	switch(action) {
		case "smsay":
			$("#command_input").val('sm_say "');
			break;
		case "smchat":
			$("#command_input").val('sm_chat "');
			break;
		case "smwho":
			$("#command_input").val('sm_who');
			break;
		case "status":
			$("#command_input").val('status');
			break;
		case "smcsay":
			$("#command_input").val('sm_csay "');
			break;
		case "smmsay":
			$("#command_input").val('sm_msay "');
			break;
		case "kickall":
			$("#command_input").val('sm_kick @all "');
			break;
		case "nextmap":
			$("#command_input").val('nextmap');
			break;
		case "smnextmap":
			$("#command_input").val('sm_nextmap "');
			break;
		case "changelevel":
			$("#command_input").val('changelevel "');
			break;
		case "pass":
			$("#command_input").val('sv_password "');
			break;
		case "nopass":
			$("#command_input").val('sv_password ""');
			break;
	}
	$("#command_input").focus();
}

function playermenu_handler(action, el, pos) {
	switch(action) {
		case "psay":
			$("#command_input").val('sm_psay "'+$(el).text()+'" "');
			break;
		case "pgod":
			$("#command_input").val('sm_pgod "'+$(el).text()+'" "');
			break;
		case "kick":
			$("#command_input").val('sm_kick "'+$(el).text()+'" "');
			break;
		case "banhr":
			$("#command_input").val('sm_ban "'+$(el).text()+'" 60 "');
			break;
		case "banday":
			$("#command_input").val('sm_ban "'+$(el).text()+'" 1440 "');
			break;
		case "banweek":
			$("#command_input").val('sm_ban "'+$(el).text()+'" 10080 "');
			break;
		case "banperm":
			$("#command_input").val('sm_ban "'+$(el).text()+'" 0 "');
			break;
	}
	$("#command_input").focus();
}

$(document).ajaxError(function(){
    if (window.console && window.console.error) {
        console.error(arguments);
    }
});

</script>

</head>

<body>
<div id=server_picker colspan=2><a href="#" id=prevlink>< Previous</a>
<select id=server_select></select>
<a href="#" id=nextlink>Next ></a>
</div>

<div class=twocol>
	<div id=consoles class=leftcol>Loading, please wait...</div>
	<div id=userlists class=rightcol></div>
	<div class=clear></div>
</div>
<!--<div id=tabs></div>
<div id=consoles><p>Loading, please wait...</div>-->
<form id=commandline>
<input id=command_input class=command_input>
</form>
<a href="#" class="toggle_button" varid=0>Hide Game Events</a> 
<a href="#" class="toggle_button" varid=1>Hide Server Events</a>
<a href="#" class="toggle_button" varid=2>Stop Auto-scroll</a>
<?php
if($_REQUEST['admin'] == 1) {
   ?>
   <a href="admin/server_admin.php?sessid=<?php echo $_POST['sessid'] ?>" target="_blank">Edit Servers</a>
   <a href="admin/user_admin.php?sessid=<?php echo $_POST['sessid'] ?>" target="_blank">Edit Users</a>
   <?php
}
?>
<a href="maul_rcon_login.php">Return to Login Screen</a>
<br><br><div id=statusline class=statusline></div>

<ul id=playermenu class=contextMenu>
<li><a href="#psay">PSay</a>
<li><a href="#pgod">PGod</a>
<li><a href="#kick">Kick</a>
<li><a href="#banhr">Ban (1 hr)</a>
<li><a href="#banday">Ban (1 day)</a>
<li><a href="#banweek">Ban (1 wk)</a>
<li><a href="#banperm">Ban (Perm)</a>
</ul>

<ul id=servermenu class=contextMenu>
<li><a href="#smwho">Show Admins</a>
<li><a href="#status">Show Players</a>
<li><a href="#smsay">Allchat Message</a>
<li><a href="#smchat">Admin Message</a>
<li><a href="#smcsay">Godchat Message (All)</a>
<li><a href="#smmsay">Menu Message (All)</a>
<li><a href="#kickall">Kick (All)</a>
<li><a href="#nextmap">Check Next Map</a>
<li><a href="#smnextmap">Set Next Map</a>
<li><a href="#changelevel">Change Map</a>
<li><a href="#pass">Set Server Password</a>
<li><a href="#nopass">Clear Server Password</a>
</ul>

</body>
</html>
