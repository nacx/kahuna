#!/usr/bin/env jython

import os
import logging
import shutil
import ConfigParser
from utils.singleton import singleton

log = logging.getLogger('kahuna')
log.setLevel(logging.INFO)

@singleton
class Config:
    """ Main configuration. """
    def __init__(self):
        config = ConfigParser.SafeConfigParser() 
        user_dir = os.environ['HOME'] + "/.kahuna"
        user_config = user_dir + "/kahuna.conf"
        config_found = user_config
        # User config has precedence, then system
        files = [user_config, '/etc/kahuna.conf']
        for file in files:
            if os.path.exists(file):
                log.debug("Config found in %s" % file)
                config_found = file
                break

        # If no config file exists, copy the default one to the user config
        if not os.path.exists(config_found):
            log.warn("Kahuna config file not found. Creating the default one to %s" % user_config)
            if not os.path.isdir(user_dir):
                os.makedirs(user_dir)
            shutil.copy('config/kahuna.conf', user_config)
            config_found = user_config

        config.read(config_found)
        self.address = config.get("connection", "address")
        self.user = config.get("connection", "user")
        self.password = config.get("connection", "pass")
        
        try:
            self.loglevel = config.get("logging", "level")
            level = logging._levelNames[self.loglevel]
            log.setLevel(level)
        except ConfigParser.NoOptionError:
            pass

