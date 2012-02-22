#!/usr/bin/env jython

import logging

log = logging.getLogger('kahuna')


class SystemConfig:
    """ Provides access to configuration features.

    This class creates and manages the internal configuration
    elements used by the platform.
    """

    def __init__(self, context):
        """ Initialize with an existing context. """
        self.__context = context

    def get(self, property_name):
        """ Returns value if a given configuration property. """
        admin = self.__context.getAdministrationService()
        return admin.getSystemProperty(property_name)

    def set(self, property_name, property_value):
        """ Set a value to a given configuration property. """
        admin = self.__context.getAdministrationService()
        prop = admin.getSystemProperty(property_name)
        prop.setValue(property_value)
        prop.update()


def apply_default_configuration(config, context):
    """ Applies the default platform configuration. """
    log.info("### Applying default configuration ###")
    sysconf = SystemConfig(context)
    log.info("Disabling initial popup...")
    sysconf.set("client.dashboard.showStartUpAlert", "0")
    log.info("Setting volume size values...")
    sysconf.set("client.storage.volumeMaxSizeValues",
            "0.032,0.064,0.128,0.256,0.512,1,2,4,8,16,32,64,128,256")
