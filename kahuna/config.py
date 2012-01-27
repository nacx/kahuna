#!/usr/bin/env jython

import os
import logging
import shutil
import ConfigParser
from utils.singleton import singleton

log = logging.getLogger('kahuna')
log.setLevel(logging.INFO)

class ConfigLoader:
    """ Loads configuration files from a given location. """
    def __init__(self, basedir = "kahuna"):
        """ Initializes the ConfigLoader. """
        self.user_dir = os.environ['HOME'] + "/." + basedir
        self.sys_dir = "/etc/" + basedir

    def load(self, file_name, default=None):
        """ Loads the given configuration file ftom the default locations. """
        user_config = self.user_dir + "/" + file_name
        sys_config = self.sys_dir + "/" + file_name
        config_found = user_config

        # User config has precedence, then system
        files = [user_config, sys_config]
        for file in files:
            if os.path.exists(file):
                log.debug("Config found in %s" % file)
                config_found = file
                break

        if not os.path.exists(config_found):
            # Fail if config file is not found and do not want to create the default one
            if not default:
                raise IOError("Configuration file not found. " +
                        "Please, make sure that %s or %s exist" % (user_config, sys_config));
            # Create the default config file if nexessary
            log.warn("Kahuna config file not found. Creating the default one to %s" % user_config)
            if not os.path.isdir(self.user_dir):
                os.makedirs(self.user_dir)
            shutil.copy(default, user_config)
            config_found = user_config

        config = ConfigParser.SafeConfigParser() 
        config.read(config_found)
        return config

@singleton
class Config:
    """ Main configuration. """
    def __init__(self):
        loader = ConfigLoader()
        config = loader.load("kahuna.conf", "config/kahuna.conf")

        self.address = config.get("connection", "address")
        self.user = config.get("connection", "user")
        self.password = config.get("connection", "pass")
        try:
            self.loglevel = config.get("logging", "level")
            level = logging._levelNames[self.loglevel]
            log.setLevel(level)
        except ConfigParser.NoOptionError:     
            # Ignore errors if no logging level has been defined
            pass

