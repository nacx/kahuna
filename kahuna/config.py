#!/usr/bin/env jython

import os
import ConfigParser
import logging
log = logging.getLogger('kahuna')

class Config:
    """ Main configuration. """
    def __init__(self):
        config = ConfigParser.SafeConfigParser()
        configFound = ""
        # User config has precedence, then system then /usr/local
        files = [os.environ['HOME'] + '/.kahuna.conf', '/etc/kahuna.conf', '/usr/local/etc/kahuna.conf']
        for file in files:
            if os.path.exists(file):
                #some debugging
                log.debug("Config found in %s" % file)
                configFound = file
                break

        if not os.path.exists(configFound):
            raise IOError("Configuration file not found. " +
                    "Please, make sure /etc/kahuna.conf exists");
        
        config.read(file)
        self.address = config.get("connection", "address")
        self.user = config.get("connection", "user")
        self.password = config.get("connection", "pass")

