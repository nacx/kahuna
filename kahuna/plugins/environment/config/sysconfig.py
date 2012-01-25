#!/usr/bin/env jython

class SystemConfig:
    """ Provides access to configuration features.

    This class creates and manages the internal configuration
    elements used by the platform.
    """

    def __init__(self, context):
        """ Initialize with an existing context. """
        self.__context = context

    def set(self, property_name, property_value):
        """ Set a value to a given confioguration property. """
        admin = self.__context.getAdministrationService()
        prop = admin.getSystemProperty(property_name)
        prop.setValue(property_value)
        prop.update()

def apply_default_configuration(context):
    """ Applies the default platform configuration.
    
    Hides the initial popup shown after a new Abiquo isntallation.
    """
    print "### Applying default configuration ###"
    sysconf = SystemConfig(context)
    print "Disabling initial popup..."
    sysconf.set("client.dashboard.showStartUpAlert", "0")

