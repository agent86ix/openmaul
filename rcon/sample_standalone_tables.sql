
--
-- Table structure for table `maul_rcon_log`
--

CREATE TABLE IF NOT EXISTS `maul_rcon_log` (
  `maulid` int(11) NOT NULL,
  `msg` text NOT NULL,
  KEY `maulid` (`maulid`)
) ENGINE=MyISAM;

-- --------------------------------------------------------

--
-- Table structure for table `maul_rcon_servers`
--

CREATE TABLE IF NOT EXISTS `maul_rcon_servers` (
  `id` int(11) NOT NULL auto_increment,
  `address` text NOT NULL,
  `port` text NOT NULL,
  `rcon_password` text NOT NULL,
  `name` text NOT NULL,
  `game` text NOT NULL,
  PRIMARY KEY  (`id`)
) ENGINE=MyISAM;

-- --------------------------------------------------------

--
-- Table structure for table `maul_rcon_users`
--

CREATE TABLE IF NOT EXISTS `maul_rcon_users` (
  `maulid` int(11) NOT NULL auto_increment,
  `username` text NOT NULL,
  `password` varchar(32) NOT NULL,
  `games` text NOT NULL,
  `adminkey` text NOT NULL,
  `adminkey_time` datetime NOT NULL,
  PRIMARY KEY  (`maulid`)
) ENGINE=MyISAM;
