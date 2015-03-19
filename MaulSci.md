# Introduction to OpenMAUL SCI #

SCI is a tool for managing one or more server/daemon instances on a single machine.  Similar projects would include [FireDaemon](http://www.firedaemon.com/) or [ServerChecker](http://www.dumbclan.co.uk/downloads/serverchecker/).

SCI sets itself apart in several ways:

  * **Open source** - No licenses to buy, no cost to try it.  You can make changes to the code to suit your needs.
  * **Cross platform** - SCI is Python based, and runs on a variety of systems, including common OSes found on VPS instances.
  * **Plugin architecture** - The design of the code is such that there is a thin, light 'core' layer, which supports all manner of plugins to control the way daemons are handled, shell commands are processed, and users interact with the SCI daemon itself.
  * **Full Windows service integration** - install any program as a service, and monitor it as a SCI daemon.  SCI itself also can be run as a service, if you so choose.

SCI consists of four major types of modules:

  * Core - The core is a lightweight system designed to manage and properly route requests to the other modules.  In the code, it is found in the scicore package.
  * Servers - Server types live here.  A server type is generally designed to cater to the specific needs of a given server/daemon.  It may contain code for starting, stopping, capturing output, monitoring, or otherwise interacting with the processes themselves.
  * Plugins - Plugins generally create new commands for the SCI shell.  They are the part of the system that is designed to be the most configurable, and the part that most people will extend.
  * Interfaces - An interface describes the protocol by which users can access the shell.  Using the twisted framework in concert with SCI, it is possible to create interfaces that use the SSH protocol, or a Web-based protocol, or any protocol the user needs.

# Prerequisites #

Before installing SCI, you must have:
  * Python, versions 2.4-2.7.  Most modern Linux distributions ship with a version that fits.  Windows users can use a 'vanilla' 2.x Python from python.org, or [ActivePython Community Edition](http://www.activestate.com/activepython/downloads).
  * [Twisted Framework](http://twistedmatrix.com/trac/wiki/Downloads), and make sure you install it's prerequisite, zope.interface.

You should be able to open a shell (or windows command prompt) and type:
`python --version`
And get back something similar to:
`Python 2.6.5`
If you get something that starts with a 3, you installed the wrong version of python.  If you get an error, check your Python install and your path variables.

You should also be able to type
`python -c "import twisted"`
And nothing should print.  If you get an error, Twisted or zope.interface are not installed properly.

# Install/Configure #

Download or check out the latest version of SCI from this site.  Unpack or save it to the path of your choosing.  There is nothing further to do as far as installing is concerned.

By default, SCI looks for a file called maul\_sci.cfg in the directory where it is installed.  (You can override this behavior by specifying --cfg=file.cfg on the command line, see the next section about running SCI for more details).

An example configuration file is included in the distribution, as maul\_sci.cfg.example.  The configuration file is broken up into sections.

The `[global]` section contains configuration options that are not server specific.  For instance, the 'ip' option specifies the IP that SCI should bind to when it starts up.

Certain options may relate to plugins, interfaces, or server types.  For example, the srcds\_rcon interface uses a set of options that start with 'rcon' to determine how the server will respond when it is queried via the UDP and TCP RCON protocols.

Any other section name denotes a new server/daemon.  The names should be unique, and are used internally.  Generally, they should not change once they are set, as certain configuration and state information depends on these names.  Changing the name of the section appears to SCI as if the old sever was deleted, and a new one added.

The options vary depending on the server type and what other plugins are loaded, but they generally contain some options for the executable to run, what options to pass, it's working directory, and so forth.

# Running #

Once SCI is configured, run it with:

`python maul_sci.py`

If you wish, you can specify the configuration file to use with `--cfg=filename.cfg`.

Once SCI initializes, you can access the SCI console via the configured interfaces.  For instance, if the srcds\_rcon interface is loaded, you can use MAUL RCON or a tool like HLSW to send commands to SCI.

Status and error messages are printed to the console, and logged to the logfile specified in the configuration.  Status messages are routed to the loaded interfaces, and are handled in an interface-specific manner.

The available commands depend on what plugins are loaded.  Help for individual plugin commands is beyond the scope of this document.