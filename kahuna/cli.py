#!/usr/bin/env jython

import sys
from pluginmanager import PluginManager


class CLI:
    """ Main command line interface. """
    def __init__(self):
        """ Initialize the plugin manager. """
        self.__pluginmanager = PluginManager()

    def parse_input(self):
        """ Validates user input and delegates to the plugin manager. """
        if len(sys.argv) < 2:
            print "Usage: kahuna <plugin> <command> [<options>]"
            print "The following plugins are available:\n"
            self.__pluginmanager.help_all()
        elif len(sys.argv) == 2:
            print "Usage: kahuna <plugin> <command> [<options>]"
            # Call the given plugin without command to print
            # the help of the plugin
            return self.__pluginmanager.call(sys.argv[1], None, None)
        else:
            # Call the command in the given plugin with the
            # remaining of the arguments
            return self.__pluginmanager.call(sys.argv[1], sys.argv[2],
                    sys.argv[3:])

if __name__ == "__main__":
    cli = CLI()
    ret = cli.parse_input()
    exit(ret) if ret else exit()
