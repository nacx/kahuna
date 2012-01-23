#!/usr/bin/env jython

import sys
from pluginmanager import PluginManager


class CLI:
    """ Main command line interface. """
    def __init__(self):
        """ Initialize the main command line interface. """
        self.__pluginmanager = PluginManager()

    def parse_input(self):
        """ Validates user input. """
        if len(sys.argv) < 3:
            print "Usage: kahuna.sh <plugin> <command> [<options>]"
            print "The following plugins are available:\n"
            self.__pluginmanager.help_all()
        else:
            # Call the command in the given plugin with the remaining of the arguments
            return self.__pluginmanager.call(sys.argv[1], sys.argv[2], sys.argv[3:])

if __name__ == "__main__":
    cli = CLI()
    ret = cli.parse_input()
    if ret:
        exit(ret)
    else:
        exit()
