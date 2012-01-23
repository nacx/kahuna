#!/usr/bin/env jython

import sys
from kahuna.pluginmanager import PluginManager


class CLI:
    """ Main command line interface. """
    def __init__(self):
        """ Initialize the main command line interface. """
        self.__pluginmanager = PluginManager()
        self.__pluginmanager.load_plugins()

    def parse_input(self):
        """ Validates user input. """
        if len(sys.argv) < 3:
            print "Usage: %s <plugin> <command> [<options>]" % sys.argv[0]
            exit()
        else:
            self.__pluginmanager.call(sys.argv[1], sys.argv[2], sys.argv[3:])

if __name__ == "__main__":
    cli = CLI()
    cli.parse_input()

