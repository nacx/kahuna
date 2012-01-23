#!/usr/bin/env jython

import os
import ConfigParser

class Config:
    """ Main configuration. """
    def __init__(self):
        config = ConfigParser.SafeConfigParser()
        file = '/usr/local/etc/kahuna.conf'
        if not os.path.exists(file):
            file = '/etc/kahuna.conf'
            if not os.path.exists(file):
                raise IOError("Configuration file not found")
        config.read(file)
        self.address = config.get("abiquo", "address")
        self.user = config.get("abiquo", "user")
        self.password = config.get("abiquo", "pass")

