# What is OpenMAUL? #

OpenMAUL is a collection of tools that are designed to ease common issues with managing server or daemon processes.  It is a server-side application written in Python using the Twisted framework.  It was developed originally for managing game server instances for a large gaming organization.

# What tools comprise OpenMAUL? #

## SCI ##

OpenMAUL Server Control Interface (SCI) is a tool that can be used to:
  * Automatically monitor and restart server/daemon tasks that have crashed, with more control and customization ability than generally afforded via other tools.
  * Automate or simplify common server/daemon tasks via a plugin driven shell
  * Expose new interfaces for accessing this shell (ie, web, ssh, RCON, etc)

It's historical goal was to manage instances of srcds (Valve's Source Dedicated Server) on Windows and Linux hosts.

**For more information about SCI, visit the MaulSci page.**

## RCON ##

OpenMAUL RCON is a tool that is designed to take legacy console daemon interfaces that require proprietary or otherwise restrictive protocols and enable them to be administered via an embeddable Web 2.0 'widget' console that has improved access control and is capable of aggregating multiple servers/daemons into a single, central console for cleaner, simplified management.

It's original design was to take dozens of srcds RCON interfaces and allow for them to be managed via a web interface.