# Plugins and Commands #

Plugins are loaded at startup based on the value of 'plugins' in the global section of the config file.

Wherever `<server>` is specified, you may use partial names.  If multiple servers match, the command will execute on all of them.  You can also use `*` to indicate all servers.

## Command List ##

| Plugin | Command | Usage | Config File Options | Description |
|:-------|:--------|:------|:--------------------|:------------|
| (core - server manager) | start | `start <server>` | disabled (s) | Starts the specified server, unless disabled is 1.  |
|  | stop | `stop <server>` |  | Stops the specified server|
|  | restart | `restart <server>` | disabled (s) | Restarts the specified server|
| base | help | help |  | Lists available commands. |
|  | plugin | `plugin <load/unload/reload> <plugin name>` |  | Loads, unloads, or reloads a plugin. |
| configfile | cfgget | `cfgget <server> <option>` | cfgget\_allow (g/s) | Get an option from the config file of the named server, but only if the option is in the cfgget\_allow list. |
|  | cfgset | `cfgset <server> <option> <value>` | cfgset\_allow (g/s) | Set an option in the config file of the named server, but only if the option is in the cfgset\_allow list. |
| srcds\_map | addmap | `addmap <server> <map name>` | mapurl (g/s), map\_extra\_files (s) | Downloads and decompresses a map file called `<mapurl>/<map name>.bsp.bz2` into the server's maps directory.  If map\_extra\_files is present, it is a list of other extensions for files of the same name that must be downloaded with the map. If these files are also bz2 compressed, they will be decompressed. |
|  | delmap | `delmap <server> <map name>` |  | Remove a map from a server's maps directory. |
| srcds\_mapcycle | mapcycle\_list | `mapcycle_list <server>` |  | List the current mapcycle of the server.  Will attempt to read server.cfg and find a "mapcycle" directive if one exists. |
|  | mapcycle\_add | `mapcycle_add <server> <map name>` |  | Append the given map name to the end of the map cycle. |
|  | mapcycle\_del | `mapcycle_del <server> <map name>` |  | Remove the first instance of the named map from the server's map cycle. |
| srcds\_update | update | `update <server>` | update\_cmd (s) | Run the update command of the named server. |


Config File Option Legend:
```
g: Can be specified in the "global" section of the config file
s: Can be specified per-server
g/s: Can be specified either globally or per-server.  If the option is present in the server, it overrides the global option.
```

## Plugins Without Commands ##

  * srcds\_autoupdate - Uses the master server query protocol and the srcds\_update plugin to automatically update servers.

# Interfaces #

  * srcds\_rcon - an implementation of the srcds\_rcon protocol, which can be accessed by RCON tools, including HLSW and MaulRcon.
    * Adds commands log, logaddress\_add, and logaddress\_del
    * Uses global config file options rcon\_hostname, rcon\_mapname, rcon\_appid, rcon\_gamedir, rcon\_gamename, rcon\_port, rcon\_pwd

# Servers and Server Types #

All servers use the configuration options:

  * name - The name you will use to refer to this server at the SCI console.  Don't use spaces.
  * server\_cmd - The path and executable you wish to run.
  * server\_args - Any args that should be passed to the server\_cmd


## Available Server Types ##

  * srcds - A server type with specific bindings and support for the Source Dedicated Server.
    * On Windows, supports subtype 'svc' - see MaulSciWinService
    * Uses per-server configuration options:
      * 'ip' and 'port' to test connection to the server
      * 'dir' should be set to the 'main' server folder - ie, the one that contains 'cfg,' 'maps,' 'addons,' etc.