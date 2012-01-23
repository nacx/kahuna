#!/usr/bin/env jython

from optparse import OptionParser
from pluginmanager import PluginManager


DESCRIPTION = "Abiquo command line interface"
VERSION = "%prog 2.0-SNAPSHOT"

class CLI:
    """ Main command line interface. """
    def __init__(self):
        """ Initialize the main Option parser. """
        self.__parser = OptionParser(description=DESCRIPTION, version=VERSION)
        self.__pluginmanager = PluginManager()

    def read_options(self):
        """ Parses user input and calls the plugins. """
        self.__parser.parse_args()

