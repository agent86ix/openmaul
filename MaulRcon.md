# Introduction to OpenMAUL RCON #

OpenMAUL RCON is a tool for aggregating multiple RCON sessions into a single Web 2.0-enabled widget.  Think of it like [HLSW](http://www.hlsw.org) on the web.

The RCON protocol has many disadvantages:

  * Single password, no username - no access control or any way for multiple users to access the service without sharing the same password.  If you have many servers, managing the passwords is difficult and lends itself to poor security practices (ie, using a simple password or the same password on all servers)  **OpenMAUL RCON can give your users individual logins, and keep them from accessing the RCON passwords on each server.**
  * Viewing remote log data is difficult behind NAT or firewall.  The srcds log protocol requires clients to be able to open a UDP port that can receive data from the internet.  This may be difficult or impossible if you are behind a firewall or NAT. **OpenMAUL RCON's proxy solves this problem by centralizing and web-ifying the srcds protocols.**
  * Client availability is limited.  HLSW only works on Windows, and few alternatives exist.  Configuring multiple computers to access all of your servers is time consuming.  **OpenMAUL RCON avoids this by centralizing the configuration and letting you use the same client on all your PCs.**

# Prerequisites #

MAUL RCON is implemented in two parts, one in PHP and one in Python.  Both rely on a MySQL server to store data.

These may run on the same machine or on different machines.  They may be on the same machine as the servers you wish to administer, but they don't have to.

The web machine must have:
  * A web server (apache httpd or similar)
  * PHP 5
  * PECL JSON (or PHP >= 5.2.0)
  * PECL PDO (or PHP >= 5.1.0)
  * MySQL extensions for PHP

The database machine must have:
  * MySQL, most versions > 5.0 should be fine for basic installs.

These should be readily available as packages on most Linux distributions.  On Windows, you might consider something like [xampp](http://www.apachefriends.org/en/xampp.html), which installs apache, PHP, and MySQL as one install.

The proxy machine must have:
  * Python, a 2.x version, at least 2.4
  * [Twisted Framework](http://twistedmatrix.com/trac/wiki/Downloads), and make sure you install it's prerequisite, zope.interface. (and zope.interface, which Twisted requires)
  * MySQL-python

Most Linux distributions will install Python as part of a default install.  It should be possible to find packages for the other parts in the basic repository for your distribution.  On Windows, you can use a 'vanilla' 2.x Python from python.org, or [ActivePython Community Edition](http://www.activestate.com/activepython/downloads).

Again, these might not be separate machines per se, they might be the same box.

# Install/Configure #

MAUL RCON consists of two major parts:  the web interface, and the RCON proxy server.  The web interface is installed on a web server, and the proxy server must run on some system to which you have RDP or SSH access.

There is a sample database setup script included in the package, called sample\_standalone\_tables.sql.  You should create a new database and user for MAUL RCON, and then run sample\_standalone\_tables.sql on that database.  It will create some skeleton tables and some default values for basic usage.

To install the RCON proxy server, copy the contents of the proxy/ folder to some location on your server machine.  Copy the file maul\_rcon.cfg.example to maul\_rcon.cfg, and edit the configuration file.  There are comments in the file that explain the various options that can be set.

To install the web interface, copy the contents of the web/ folder (either from a clone of the repository or from a release) to some directory on your web machine where it can be served by your web server.

Next, copy config.inc.php.example to config.inc.php, and edit the values in the configuration file.  Much of this will be similar to what you used on the RCON proxy server.

# Running #

Start the proxy server with:
```
python maul_rcon.py --cfg=maul_rcon.cfg
```
You should then be able to navigate to the web interface via your browser.  If this is your first time installing MAUL RCON, the default login is 'admin' with no password.

You can then go into the "Edit Users" and "Edit Servers" panels on the web interface to change the available users and the available servers.  When you edit the server list, you will have to reset the proxy, via a button at the bottom of the "Edit Servers" page.  This will log everyone off of the interface.